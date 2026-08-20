"""Materiality-Weighted Parent Claim Aggregator.

Aggregates atomic claim verdicts into canonical InternalVerdict and PublicVerdict
according to the truth table specified in verifact_docs/00-canonical-enums.md.
"""

from typing import NamedTuple

from episteme.common.enums import (
    INTERNAL_TO_PUBLIC_VERDICT,
    AtomicClaimVerdict,
    ClaimVerifiability,
    InternalVerdict,
    Materiality,
    PublicVerdict,
)
from episteme.common.models.claim import AtomicClaim


class ParentAggregationResult(NamedTuple):
    """Result of parent claim verdict aggregation."""

    internal_verdict: InternalVerdict
    public_label: PublicVerdict
    framing_concerns: bool
    rationale: str


class ParentVerdictAggregator:
    """Aggregates atomic claim proposition evaluations into parent claim verdicts."""

    def aggregate_verdicts(
        self,
        atomic_evaluations: list[tuple[AtomicClaim, AtomicClaimVerdict]],
        claim_verifiability: ClaimVerifiability = ClaimVerifiability.VERIFIABLE,
    ) -> ParentAggregationResult:
        """Aggregate atomic claim truth states into a canonical parent verdict.

        Args:
            atomic_evaluations: List of (AtomicClaim, AtomicClaimVerdict) pairs.
            claim_verifiability: Pre-classified claim verifiability.

        Returns:
            ParentAggregationResult: internal verdict, public label, and framing flags.
        """
        if claim_verifiability == ClaimVerifiability.UNVERIFIABLE:
            return ParentAggregationResult(
                internal_verdict=InternalVerdict.UNVERIFIABLE,
                public_label=PublicVerdict.UNVERIFIABLE,
                framing_concerns=False,
                rationale="Claim is intrinsically subjective, opinion-based, or normative.",
            )

        if not atomic_evaluations:
            return ParentAggregationResult(
                internal_verdict=InternalVerdict.INSUFFICIENT_EVIDENCE,
                public_label=PublicVerdict.UNVERIFIED,
                framing_concerns=False,
                rationale="No atomic claims evaluated.",
            )

        # Single atomic claim case
        if len(atomic_evaluations) == 1:
            _, verdict = atomic_evaluations[0]
            if verdict == AtomicClaimVerdict.SUPPORTED:
                iv = InternalVerdict.SUPPORTED
            elif verdict == AtomicClaimVerdict.REFUTED:
                iv = InternalVerdict.REFUTED
            elif verdict == AtomicClaimVerdict.UNVERIFIABLE:
                iv = InternalVerdict.UNVERIFIABLE
            else:
                iv = InternalVerdict.INSUFFICIENT_EVIDENCE

            return ParentAggregationResult(
                internal_verdict=iv,
                public_label=INTERNAL_TO_PUBLIC_VERDICT[iv],
                framing_concerns=False,
                rationale=f"Single atomic proposition evaluated as {verdict.value}.",
            )

        # Multi-claim compound aggregation logic
        critical_evals = [
            v for ac, v in atomic_evaluations if ac.materiality == Materiality.CRITICAL
        ]
        all_verdicts = [v for _, v in atomic_evaluations]

        # Count occurrences
        support_count = all_verdicts.count(AtomicClaimVerdict.SUPPORTED)
        refute_count = all_verdicts.count(AtomicClaimVerdict.REFUTED)
        insufficient_count = all_verdicts.count(AtomicClaimVerdict.INSUFFICIENT)

        # 1. Check if all critical and material propositions are supported
        if all(v == AtomicClaimVerdict.SUPPORTED for v in all_verdicts):
            return ParentAggregationResult(
                internal_verdict=InternalVerdict.SUPPORTED,
                public_label=PublicVerdict.LIKELY_TRUE,
                framing_concerns=False,
                rationale="All atomic propositions independently corroborated.",
            )

        # 2. Check if all propositions are refuted
        if all(v == AtomicClaimVerdict.REFUTED for v in all_verdicts):
            return ParentAggregationResult(
                internal_verdict=InternalVerdict.REFUTED,
                public_label=PublicVerdict.LIKELY_FALSE,
                framing_concerns=False,
                rationale="All atomic propositions decisively refuted by evidence.",
            )

        # 3. Check for mixed truth values (Some supported, some refuted/insufficient)
        if support_count > 0 and (refute_count > 0 or insufficient_count > 0):
            # Compound claim with partially true facts
            return ParentAggregationResult(
                internal_verdict=InternalVerdict.PARTIALLY_SUPPORTED,
                public_label=PublicVerdict.PARTIALLY_TRUE,
                framing_concerns=True,
                rationale=f"Compound claim contains verified facts ({support_count}) alongside inaccurate/unverified elements.",
            )

        # 4. Critical proposition refuted with no support
        if any(v == AtomicClaimVerdict.REFUTED for v in critical_evals) and support_count == 0:
            return ParentAggregationResult(
                internal_verdict=InternalVerdict.REFUTED,
                public_label=PublicVerdict.LIKELY_FALSE,
                framing_concerns=False,
                rationale="Critical core proposition refuted by evidence.",
            )

        # 5. Default to INSUFFICIENT_EVIDENCE
        return ParentAggregationResult(
            internal_verdict=InternalVerdict.INSUFFICIENT_EVIDENCE,
            public_label=PublicVerdict.UNVERIFIED,
            framing_concerns=False,
            rationale="Insufficient evidence retrieved to establish truth or falsity.",
        )
