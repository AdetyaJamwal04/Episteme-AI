"""Verdict Engine and Pipeline Package."""

from verifact.verdict.aggregator import ParentAggregationResult, ParentVerdictAggregator
from verifact.verdict.atomic_evaluator import AtomicClaimVerdictEvaluator, AtomicVerdictEvaluation
from verifact.verdict.calibrator import ConfidenceCalibrator
from verifact.verdict.explainer import GroundedExplanationBuilder
from verifact.verdict.pipeline import VeriFactPipeline
from verifact.verdict.sufficiency import SufficiencyResult, calculate_evidence_sufficiency

__all__ = [
    "AtomicClaimVerdictEvaluator",
    "AtomicVerdictEvaluation",
    "ConfidenceCalibrator",
    "GroundedExplanationBuilder",
    "ParentAggregationResult",
    "ParentVerdictAggregator",
    "SufficiencyResult",
    "VeriFactPipeline",
    "calculate_evidence_sufficiency",
]
