"""Configuration objects for deterministic scoring and evaluation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RuleConfig:
    """Weights and risk bands for the transparent rule baseline."""

    anomaly_weight: float = 0.50
    off_hours_weight: float = 0.10
    failed_logins_weight: float = 0.15
    geo_distance_weight: float = 0.10
    process_injection_weight: float = 0.15
    medium_threshold: float = 0.45
    high_threshold: float = 0.70

    def __post_init__(self) -> None:
        weights = (
            self.anomaly_weight,
            self.off_hours_weight,
            self.failed_logins_weight,
            self.geo_distance_weight,
            self.process_injection_weight,
        )
        if any(weight < 0 for weight in weights):
            raise ValueError("Rule weights must be non-negative.")
        if abs(sum(weights) - 1.0) > 1e-9:
            raise ValueError("Rule weights must sum to 1.0.")
        if not 0 < self.medium_threshold < self.high_threshold < 1:
            raise ValueError("Risk thresholds must satisfy 0 < medium < high < 1.")


@dataclass(frozen=True)
class EvaluationConfig:
    """Controls for the chronological holdout and blended score."""

    test_size: float = 0.25
    random_seed: int = 42
    model_weight: float = 0.60
    decision_threshold: float = 0.50

    def __post_init__(self) -> None:
        if not 0.10 <= self.test_size <= 0.50:
            raise ValueError("test_size must be between 0.10 and 0.50.")
        if not 0 <= self.model_weight <= 1:
            raise ValueError("model_weight must be between 0 and 1.")
        if not 0 < self.decision_threshold < 1:
            raise ValueError("decision_threshold must be between 0 and 1.")
