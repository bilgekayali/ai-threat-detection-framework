"""Explainable alert-risk evaluation for synthetic security telemetry."""

from ai_threat_detection.config import EvaluationConfig, RuleConfig
from ai_threat_detection.evaluation import EvaluationArtifacts, evaluate_alerts
from ai_threat_detection.validation import DataValidationError, validate_alerts
from ai_threat_detection.version import PACKAGE_VERSION

__all__ = [
    "DataValidationError",
    "EvaluationArtifacts",
    "EvaluationConfig",
    "RuleConfig",
    "evaluate_alerts",
    "validate_alerts",
]

__version__ = PACKAGE_VERSION
