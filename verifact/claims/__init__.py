"""Claim Intelligence Package."""

from verifact.claims.classifier import ClassificationResult, classify_claim
from verifact.claims.decomposer import decompose_claim
from verifact.claims.entity_extractor import extract_named_entities
from verifact.claims.language import LanguageDetectionResult, detect_language, enforce_language_gate
from verifact.claims.normalizer import NormalizedClaimResult, normalize_claim_text
from verifact.claims.pipeline import ClaimIntelligencePipeline
from verifact.claims.temporal_extractor import extract_temporal_constraints

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
