"""Evidence Assessment and Epistemic Stance Subsystem."""

from verifact.evidence.conflict_detector import ConflictDetector
from verifact.evidence.engine import EvidenceAssessmentEngine
from verifact.evidence.provenance import ProvenanceClusterer
from verifact.evidence.validators.numerical_validator import (
    NumericalValidationResult,
    validate_numerical_consistency,
)
from verifact.evidence.validators.temporal_validator import (
    TemporalValidationResult,
    validate_temporal_alignment,
)

__all__ = [
    "ConflictDetector",
    "EvidenceAssessmentEngine",
    "NumericalValidationResult",
    "ProvenanceClusterer",
    "TemporalValidationResult",
    "validate_numerical_consistency",
    "validate_temporal_alignment",
]
