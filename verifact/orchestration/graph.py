"""LangGraph Stateful Research Graph for Fact Verification.

Coordinates the iterative research cycle (decompose -> formulate -> retrieve ->
evaluate -> decide loop -> synthesize verdict) operating on ResearchState.
"""

from uuid import UUID, uuid4

from verifact.claims.pipeline import ClaimIntelligencePipeline
from verifact.common.enums import (
    AtomicClaimVerdict,
    ClaimVerifiability,
    InternalVerdict,
    PublicVerdict,
    ResearchDepth,
    ResearchLoopDecision,
    ResearchStateStatus,
)
from verifact.common.logging import get_logger
from verifact.common.models.claim import AtomicClaim
from verifact.common.models.evidence import Evidence, EvidenceState
from verifact.common.models.provenance import ProvenanceGroup
from verifact.common.models.research import ResearchState
from verifact.common.models.source import Document, Passage
from verifact.common.models.verdict import Citation, VerdictDecision
from verifact.evidence.engine import EvidenceAssessmentEngine
from verifact.orchestration.budget import BudgetTracker
from verifact.orchestration.controller import AdaptiveLoopController
from verifact.orchestration.formulator import QueryFormulator
from verifact.retrieval.fetcher import HTTPDocumentFetcher
from verifact.retrieval.interfaces import DocumentFetcher, SearchProvider
from verifact.retrieval.providers.manager import SearchProviderManager
from verifact.retrieval.segmenter import segment_document_text
from verifact.verdict.aggregator import ParentVerdictAggregator
from verifact.verdict.atomic_evaluator import AtomicClaimVerdictEvaluator
from verifact.verdict.calibrator import ConfidenceCalibrator
from verifact.verdict.explainer import GroundedExplanationBuilder
from verifact.verdict.sufficiency import calculate_evidence_sufficiency

logger = get_logger("research_graph")


class ResearchGraphRunner:
    """Executes stateful multi-step iterative research graph."""

    def __init__(
        self,
        search_provider: SearchProvider | None = None,
        document_fetcher: DocumentFetcher | None = None,
        evidence_engine: EvidenceAssessmentEngine | None = None,
    ) -> None:
        self.claim_pipeline = ClaimIntelligencePipeline()
        self.search_manager = SearchProviderManager(primary_provider=search_provider)
        self.fetcher = document_fetcher or HTTPDocumentFetcher()
        self.evidence_engine = evidence_engine or EvidenceAssessmentEngine()
        self.formulator = QueryFormulator()
        self.controller = AdaptiveLoopController()
        self.atomic_evaluator = AtomicClaimVerdictEvaluator()
        self.aggregator = ParentVerdictAggregator()
        self.calibrator = ConfidenceCalibrator()
        self.explainer = GroundedExplanationBuilder()

    async def execute_research(
        self,
        claim_text: str,
        depth: ResearchDepth = ResearchDepth.STANDARD,
        request_id: UUID | None = None,
    ) -> tuple[VerdictDecision, ResearchState]:
        """Execute end-to-end stateful research graph on claim.

        Args:
            claim_text: Raw input claim text.
            depth: Research depth (FAST, STANDARD, DEEP).
            request_id: Optional client request UUID.

        Returns:
            tuple: (VerdictDecision, final ResearchState)
        """
        req_id = request_id or uuid4()
        budget = BudgetTracker(depth=depth)

        logger.info(
            "Executing research graph", request_id=str(req_id), depth=depth.value, claim=claim_text
        )

        # 1. Decomposition Node
        analysis = self.claim_pipeline.analyze(claim_text, request_id=req_id)
        claim = analysis.claim
        atomic_claims = analysis.atomic_claims

        state = ResearchState(
            verification_id=req_id,
            claim=claim,
            atomic_claims=atomic_claims,
            current_iteration=0,
            status=ResearchStateStatus.ANALYZING,
        )

        # Fast-path for opinion/normative claims
        if claim.verifiability == ClaimVerifiability.UNVERIFIABLE:
            unverifiable_citations: list[Citation] = []
            summary = self.explainer.generate_summary(
                claim_text=claim.normalized_text,
                verdict=InternalVerdict.UNVERIFIABLE,
                citations=unverifiable_citations,
                rationale=analysis.verifiability_reasoning,
            )
            decision = VerdictDecision(
                verdict=InternalVerdict.UNVERIFIABLE,
                public_label=PublicVerdict.UNVERIFIABLE,
                framing_concerns=False,
                confidence=1.0,
                evidence_sufficiency=1.0,
                stop_reason="UNVERIFIABLE",
                summary_text=summary,
                citations=unverifiable_citations,
            )
            state.status = ResearchStateStatus.COMPLETED
            return decision, state

        state.status = ResearchStateStatus.RESEARCHING

        # Track documents and passages across iterations
        docs_by_id: dict[UUID, Document] = {}
        passages_by_id: dict[UUID, Passage] = {}
        all_evidence: list[Evidence] = []
        all_clusters: list[ProvenanceGroup] = []
        executed_queries: list[str] = []
        latest_evidence_states: dict[UUID, EvidenceState] = {}
        atomic_claims_by_id = {ac.atomic_claim_id: ac for ac in atomic_claims}

        # 2. Iterative Adaptive Loop
        while True:
            budget.record_iteration()
            iteration = budget.iterations_completed
            state.current_iteration = iteration

            # Formulate queries
            if iteration == 1:
                queries_to_run = self.formulator.formulate_initial_queries(
                    atomic_claims, max_queries=budget.limits.max_queries
                )
            else:
                # Refinement or conflict queries
                unresolved = [
                    atomic_claims_by_id[ac_id]
                    for ac_id, st in latest_evidence_states.items()
                    if st.coverage_score < 0.60
                ]
                queries_to_run = self.formulator.formulate_refinement_queries(
                    unresolved_atomic_claims=unresolved or atomic_claims,
                    past_queries=executed_queries,
                    max_queries=3,
                )

            if not queries_to_run:
                break

            # Retrieval & Fetching Node
            for _ac_id, query_str in queries_to_run:
                if not budget.can_consume_queries(1):
                    break

                executed_queries.append(query_str)
                budget.record_query(1)

                search_resp = await self.search_manager.search(query_str, max_results=3)
                for item in search_resp.results:
                    try:
                        fetched = await self.fetcher.fetch(item.url)
                        doc_id = uuid4()
                        doc = Document(
                            document_id=doc_id,
                            source_id=uuid4(),
                            url=fetched.url,
                            canonical_url=fetched.canonical_url,
                            content_hash=fetched.content_hash,
                            title=fetched.title or item.title,
                            author=fetched.author,
                        )
                        docs_by_id[doc_id] = doc

                        doc_passages = segment_document_text(
                            doc_id, fetched.main_text, target_token_size=300
                        )
                        for p in doc_passages:
                            passages_by_id[p.passage_id] = p
                    except Exception as e:
                        logger.warning(
                            "Failed to fetch search document", url=item.url, error=str(e)
                        )
                        continue

            # Assessment Node: Evaluate all atomic claims against acquired pool
            all_passages = list(passages_by_id.values())
            current_conflicts = []

            for ac in atomic_claims:
                (
                    ev_state,
                    clusters,
                    confs,
                ) = await self.evidence_engine.evaluate_atomic_claim_evidence(
                    atomic_claim=ac,
                    passages=all_passages,
                    documents_by_id=docs_by_id,
                    top_k=3,
                )
                latest_evidence_states[ac.atomic_claim_id] = ev_state
                current_conflicts.extend(confs)
                all_clusters.extend(clusters)
                all_evidence.extend(ev_state.supporting_evidence + ev_state.contradicting_evidence)

            state.unresolved_conflicts = current_conflicts
            state.provenance_clusters = all_clusters

            # Controller Decision Node
            loop_decision = self.controller.evaluate_loop_state(
                evidence_states=list(latest_evidence_states.values()),
                conflicts=current_conflicts,
                budget_tracker=budget,
            )

            logger.info(
                "Orchestrator loop decision",
                iteration=iteration,
                decision=loop_decision.decision.value,
                rationale=loop_decision.rationale,
            )

            if loop_decision.decision == ResearchLoopDecision.TERMINATE:
                break

        # 3. Synthesis Node: Compute final parent verdict
        state.status = ResearchStateStatus.VERDICT
        atomic_evaluations: list[tuple[AtomicClaim, AtomicClaimVerdict]] = []
        for ac in atomic_claims:
            ev_state_item = latest_evidence_states.get(ac.atomic_claim_id)
            if ev_state_item is not None:
                res = self.atomic_evaluator.evaluate_atomic_claim(ev_state_item)
                atomic_evaluations.append((ac, res.verdict))
            else:
                atomic_evaluations.append((ac, AtomicClaimVerdict.INSUFFICIENT))

        agg_result = self.aggregator.aggregate_verdicts(
            atomic_evaluations=atomic_evaluations,
            claim_verifiability=claim.verifiability,
        )

        suff_result = calculate_evidence_sufficiency(all_evidence)
        calibrated_conf = self.calibrator.calibrate(
            raw_confidence=0.85,
            sufficiency_score=suff_result.sufficiency_score,
            has_temporal_discrepancy=False,
            has_unresolved_conflict=len(current_conflicts) > 0,
        )

        citations = self.explainer.build_citations(
            evidence_items=all_evidence,
            passages_by_id=passages_by_id,
            documents_by_id=docs_by_id,
            max_citations=5,
        )

        summary = self.explainer.generate_summary(
            claim_text=claim.normalized_text,
            verdict=agg_result.internal_verdict,
            citations=citations,
            rationale=agg_result.rationale,
        )

        supporting_ids = [e.evidence_id for e in all_evidence if "SUPPORT" in e.relationship.value]
        contradicting_ids = [
            e.evidence_id for e in all_evidence if "CONTRADICT" in e.relationship.value
        ]

        final_verdict = VerdictDecision(
            verdict=agg_result.internal_verdict,
            public_label=agg_result.public_label,
            framing_concerns=agg_result.framing_concerns,
            confidence=calibrated_conf,
            evidence_sufficiency=suff_result.sufficiency_score,
            stop_reason="SUFFICIENT_EVIDENCE"
            if suff_result.is_sufficient
            else "EVALUATION_COMPLETE",
            summary_text=summary,
            citations=citations,
            supporting_evidence_ids=supporting_ids,
            contradicting_evidence_ids=contradicting_ids,
            unresolved_atomic_claim_ids=[
                ac.atomic_claim_id
                for ac, v in atomic_evaluations
                if v in (AtomicClaimVerdict.INSUFFICIENT, AtomicClaimVerdict.CONFLICTED)
            ],
        )

        state.status = ResearchStateStatus.COMPLETED
        return final_verdict, state
