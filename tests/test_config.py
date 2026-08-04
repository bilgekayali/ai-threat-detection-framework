import pytest

from ai_threat_detection.config import EvaluationConfig, RuleConfig


def test_rule_config_rejects_invalid_weights_and_thresholds():
    with pytest.raises(ValueError, match="non-negative"):
        RuleConfig(anomaly_weight=-0.1, off_hours_weight=0.2)
    with pytest.raises(ValueError, match="sum to 1.0"):
        RuleConfig(anomaly_weight=0.4)
    with pytest.raises(ValueError, match="medium < high"):
        RuleConfig(medium_threshold=0.8, high_threshold=0.7)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("test_size", 0.05),
        ("model_weight", 1.2),
        ("decision_threshold", 0),
    ],
)
def test_evaluation_config_rejects_invalid_values(field, value):
    with pytest.raises(ValueError):
        EvaluationConfig(**{field: value})
