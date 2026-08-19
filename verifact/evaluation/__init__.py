"""Evaluation and Benchmarking Subsystem."""

from verifact.evaluation.metrics import (
    BenchmarkMetricsResult,
    PerClassMetrics,
    calculate_brier_score,
    calculate_confusion_matrix,
    calculate_expected_calibration_error,
    calculate_per_class_metrics,
    evaluate_benchmark_predictions,
)
from verifact.evaluation.reporter import BenchmarkReporter
from verifact.evaluation.runner import BenchmarkRunner

__all__ = [
    "BenchmarkMetricsResult",
    "BenchmarkReporter",
    "BenchmarkRunner",
    "PerClassMetrics",
    "calculate_brier_score",
    "calculate_confusion_matrix",
    "calculate_expected_calibration_error",
    "calculate_per_class_metrics",
    "evaluate_benchmark_predictions",
]
