"""Adaptive Research Orchestration Engine.

High-level interface coordinating iterative research, evidence acquisition,
and epistemic decision synthesis across depth configurations.
"""

from uuid import UUID

from verifact.common.enums import ResearchDepth
from verifact.common.models.research import ResearchState
from verifact.common.models.verdict import VerdictDecision
from verifact.evidence.engine import EvidenceAssessmentEngine
from verifact.orchestration.graph import ResearchGraphRunner
from verifact.retrieval.interfaces import DocumentFetcher, SearchProvider


class AdaptiveResearchEngine:
    """Orchestrates adaptive, multi-depth research and claim verification."""

    def __init__(
        self,
        search_provider: SearchProvider | None = None,
        document_fetcher: DocumentFetcher | None = None,
        evidence_engine: EvidenceAssessmentEngine | None = None,
    ) -> None:
        self.graph_runner = ResearchGraphRunner(
            search_provider=search_provider,
            document_fetcher=document_fetcher,
            evidence_engine=evidence_engine,
        )

    async def verify(
        self,
        claim_text: str,
        depth: ResearchDepth = ResearchDepth.STANDARD,
        request_id: UUID | None = None,
    ) -> tuple[VerdictDecision, ResearchState]:
        """Execute adaptive research verification.

        Args:
            claim_text: Raw input claim text.
            depth: Research depth (FAST, STANDARD, DEEP).
            request_id: Optional client request UUID.

        Returns:
            tuple: (VerdictDecision, ResearchState)
        """
        return await self.graph_runner.execute_research(
            claim_text=claim_text,
            depth=depth,
            request_id=request_id,
        )
