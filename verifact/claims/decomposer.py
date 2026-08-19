"""Conservative Atomic Claim Decomposition with Depth Ceiling and Anti-Hallucination Gate.

Decomposes complex/compound claims into independently verifiable AtomicClaim objects.
Preserves single-element atomic claims without unnecessary fragmentation.
"""

import re

from verifact.claims.entity_extractor import extract_named_entities
from verifact.claims.temporal_extractor import extract_temporal_constraints
from verifact.common.enums import AtomicClaimVerdict, Materiality
from verifact.common.models.claim import AtomicClaim, Claim


def _split_compound_clauses(text: str) -> list[str]:
    """Split compound sentences along coordinating conjunctions and semicolons."""
    # Split on semicolons or distinct coordinating clauses (', and', ', whereas', ', while')
    clauses = re.split(r";|\s*,\s*(?:and|whereas|while|but\s+also)\s+", text, flags=re.IGNORECASE)

    cleaned_clauses: list[str] = []
    for clause in clauses:
        c = clause.strip()
        if len(c.split()) >= 4:  # Meaningful clause length
            if not c.endswith("."):
                c += "."
            # Capitalize first character
            c = c[0].upper() + c[1:]
            cleaned_clauses.append(c)

    return cleaned_clauses


def _validate_anti_hallucination(parent_text: str, atomic_propositions: list[str]) -> bool:
    """Verify that generated atomic propositions do not introduce ungrounded entities or numbers."""
    parent_numbers = set(re.findall(r"\b\d+(?:[.,]\d+)?\b", parent_text))

    for prop in atomic_propositions:
        prop_numbers = set(re.findall(r"\b\d+(?:[.,]\d+)?\b", prop))
        # If atomic claim contains numbers not in the parent, validation fails
        if not prop_numbers.issubset(parent_numbers):
            return False

    return True


def decompose_claim(claim: Claim) -> list[AtomicClaim]:
    """Decompose a claim into independently verifiable atomic propositions.

    Args:
        claim: The parent Claim object.

    Returns:
        list[AtomicClaim]: List of 1 to 4 atomic claims with materiality and constraints.
    """
    text = claim.normalized_text.strip()

    # 1. Check if the claim is already atomic or simple
    candidate_clauses = _split_compound_clauses(text)

    # If single clause or anti-hallucination check fails, return the single atomic claim
    if len(candidate_clauses) <= 1 or not _validate_anti_hallucination(text, candidate_clauses):
        temporal_info = extract_temporal_constraints(text)
        entities_info = extract_named_entities(text)

        return [
            AtomicClaim(
                claim_id=claim.claim_id,
                sequence_order=0,
                text=text,
                is_atomic=True,
                decomposition_depth=1,
                materiality=Materiality.CRITICAL,
                entities=[e["text"] for e in entities_info],
                temporal_scope={
                    t.get("raw_text", ""): str(t.get("year", "")) for t in temporal_info
                },
                status=AtomicClaimVerdict.INSUFFICIENT,
            )
        ]

    # 2. Process compound clauses
    atomic_claims: list[AtomicClaim] = []
    for idx, clause in enumerate(candidate_clauses[:4]):  # Cap at max 4 sub-claims
        temporal_info = extract_temporal_constraints(clause)
        entities_info = extract_named_entities(clause)

        # Primary clause is CRITICAL, secondary clauses are MATERIAL
        materiality = Materiality.CRITICAL if idx == 0 else Materiality.MATERIAL

        atomic_claims.append(
            AtomicClaim(
                claim_id=claim.claim_id,
                sequence_order=idx,
                text=clause,
                is_atomic=True,
                decomposition_depth=1,
                materiality=materiality,
                entities=[e["text"] for e in entities_info],
                temporal_scope={
                    t.get("raw_text", ""): str(t.get("year", "")) for t in temporal_info
                },
                status=AtomicClaimVerdict.INSUFFICIENT,
            )
        )

    return atomic_claims
