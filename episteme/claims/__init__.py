"""Claim Intelligence Package."""

from episteme.claims.classifier import ClassificationResult, classify_claim
from episteme.claims.decomposer import decompose_claim
from episteme.claims.entity_extractor import extract_named_entities
from episteme.claims.language import LanguageDetectionResult, detect_language, enforce_language_gate
from episteme.claims.normalizer import NormalizedClaimResult, normalize_claim_text
from episteme.claims.pipeline import ClaimIntelligencePipeline
from episteme.claims.temporal_extractor import extract_temporal_constraints

__all__ = [
    "ClaimIntelligencePipeline",
    "ClassificationResult",
    "LanguageDetectionResult",
    "NormalizedClaimResult",
    "classify_claim",
    "decompose_claim",
    "detect_language",
    "enforce_language_gate",
    "extract_named_entities",
    "extract_temporal_constraints",
    "normalize_claim_text",
]
