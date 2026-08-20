"""Numerical Tolerance and Unit Consistency Validator.

Performs deterministic numerical extraction and tolerance comparison between
atomic claims and evidence passages to prevent hallucinations in numerical claims.
"""

import re
from typing import NamedTuple


class NumericalValidationResult(NamedTuple):
    """Result of numerical comparison."""

    is_compatible: bool
    discrepancy_ratio: float
    claim_numbers: list[float]
    evidence_numbers: list[float]
    validation_status: str


def _extract_numbers(text: str) -> list[float]:
    """Extract raw float numbers from text, removing commas and percent signs."""
    # Find all float and integer representations
    matches = re.findall(r"\b\d+(?:[.,]\d+)?\b", text)
    numbers: list[float] = []
    for m in matches:
        cleaned = m.replace(",", "")
        try:
            numbers.append(float(cleaned))
        except ValueError:
            continue
    return numbers


def validate_numerical_consistency(
    claim_text: str,
    evidence_text: str,
    relative_tolerance: float = 0.05,  # 5% default relative tolerance
) -> NumericalValidationResult:
    """Validate whether numerical values in claim are corroborated by evidence text.

    Args:
        claim_text: The atomic claim proposition.
        evidence_text: The evidence passage text.
        relative_tolerance: Allowed relative error percentage (default 5%).

    Returns:
        NumericalValidationResult: Compatibility boolean, discrepancy ratio, and status.
    """
    c_nums = _extract_numbers(claim_text)
    e_nums = _extract_numbers(evidence_text)

    # If claim has no numerical assertions, validation trivially passes
    if not c_nums:
        return NumericalValidationResult(
            is_compatible=True,
            discrepancy_ratio=0.0,
            claim_numbers=[],
            evidence_numbers=e_nums,
            validation_status="NO_NUMERICAL_ASSERTION",
        )

    # If claim has numbers but evidence has none, evidence cannot corroborate the numbers
    if not e_nums:
        return NumericalValidationResult(
            is_compatible=False,
            discrepancy_ratio=1.0,
            claim_numbers=c_nums,
            evidence_numbers=[],
            validation_status="MISSING_EVIDENCE_NUMBERS",
        )

    # For each claim number, find the closest matching number in evidence
    max_discrepancy = 0.0
    all_matched = True

    for c_val in c_nums:
        if c_val == 0.0:
            # Exact zero match check
            min_diff = min(abs(e_val) for e_val in e_nums)
            rel_error = min_diff
        else:
            rel_error = min(abs(c_val - e_val) / abs(c_val) for e_val in e_nums)

        if rel_error > relative_tolerance:
            all_matched = False
        max_discrepancy = max(max_discrepancy, rel_error)

    status = "VALID" if all_matched else "NUMERICAL_MISMATCH"

    return NumericalValidationResult(
        is_compatible=all_matched,
        discrepancy_ratio=round(max_discrepancy, 4),
        claim_numbers=c_nums,
        evidence_numbers=e_nums,
        validation_status=status,
    )
