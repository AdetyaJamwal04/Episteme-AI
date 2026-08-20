"""Atomic Claim Verdict Evaluator.

Evaluates an EvidenceState for an individual proposition and assigns an
AtomicClaimVerdict (SUPPORTED, REFUTED, CONFLICTED, INSUFFICIENT, UNVERIFIABLE).
"""

from typing import NamedTuple

from episteme.common.enums import AtomicClaimVerdict
from episteme.common.models.evidence import EvidenceState


class AtomicVerdictEvaluation(NamedTuple):
    """Result of atomic claim proposition evaluation."""

    verdict: AtomicClaimVerdict
    support_weight: float
    contradiction_weight: float
    confidence: float
    rationale: str


class AtomicClaimVerdictEvaluator:
    """Evaluates the epistemic evidence state for an individual atomic claim proposition."""

    def evaluate_atomic_claim(
        self,
        evidence_state: EvidenceState,
        is_subjective_or_opinion: bool = False,
    ) -> AtomicVerdictEvaluation:
        """Determine truth status of an atomic claim from its supporting and contradicting evidence.

        Args:
            evidence_state: Aggregated evidence items for this proposition.
            is_subjective_or_opinion: If proposition was pre-classified as OPINION/NORMATIVE.

        Returns:
            AtomicVerdictEvaluation: Assigned verdict, weights, and rationale.
        """
        if is_subjective_or_opinion:
            return AtomicVerdictEvaluation(
                verdict=AtomicClaimVerdict.UNVERIFIABLE,
                support_weight=0.0,
                contradiction_weight=0.0,
                confidence=1.0,
                rationale="Proposition is a subjective opinion or normative statement.",
            )

        # 1. Check for unresolved direct empirical conflicts
        if evidence_state.unresolved_conflict:
            return AtomicVerdictEvaluation(
                verdict=AtomicClaimVerdict.CONFLICTED,
                support_weight=0.0,
                contradiction_weight=0.0,
                confidence=0.5,
                rationale="Unresolved direct contradiction detected between retrieved evidence sources.",
            )

        # 2. Compute independent evidence weights
        w_sup = sum(
            e.independence_score * e.entailment_score * e.relevance_score
            for e in evidence_state.supporting_evidence
        )
        w_con = sum(
            e.independence_score * e.contradiction_score * e.relevance_score
            for e in evidence_state.contradicting_evidence
        )

        # 3. Decision threshold logic
        if w_con >= 0.50 and w_con >= 1.5 * max(w_sup, 0.01):
            conf = min(0.99, 0.60 + (w_con / (w_con + w_sup + 0.1)) * 0.38)
            return AtomicVerdictEvaluation(
                verdict=AtomicClaimVerdict.REFUTED,
                support_weight=round(w_sup, 4),
                contradiction_weight=round(w_con, 4),
                confidence=round(conf, 4),
                rationale=f"Contradicting evidence mass ({w_con:.2f}) decisively refutes proposition.",
            )

        if w_sup >= 0.50 and w_sup >= 1.5 * max(w_con, 0.01):
            conf = min(0.99, 0.60 + (w_sup / (w_sup + w_con + 0.1)) * 0.38)
            return AtomicVerdictEvaluation(
                verdict=AtomicClaimVerdict.SUPPORTED,
                support_weight=round(w_sup, 4),
                contradiction_weight=round(w_con, 4),
                confidence=round(conf, 4),
                rationale=f"Supporting evidence mass ({w_sup:.2f}) independently corroborates proposition.",
            )

        if w_sup >= 0.40 and w_con >= 0.40:
            return AtomicVerdictEvaluation(
                verdict=AtomicClaimVerdict.CONFLICTED,
                support_weight=round(w_sup, 4),
                contradiction_weight=round(w_con, 4),
                confidence=0.50,
                rationale=f"Evidence is divided between support ({w_sup:.2f}) and refutation ({w_con:.2f}).",
            )

        # Default fallback when evidence is insufficient
        return AtomicVerdictEvaluation(
            verdict=AtomicClaimVerdict.INSUFFICIENT,
            support_weight=round(w_sup, 4),
            contradiction_weight=round(w_con, 4),
            confidence=0.30,
            rationale=f"Insufficient corroborating or refuting evidence (sup={w_sup:.2f}, con={w_con:.2f}).",
        )
