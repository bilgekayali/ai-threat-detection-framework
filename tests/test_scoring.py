import pandas as pd

from ai_threat_detection.scoring import (
    assign_risk_levels,
    build_reason_codes,
    calculate_rule_scores,
)
from ai_threat_detection.validation import validate_alerts


def test_rule_scores_are_bounded(synthetic_frame):
    alerts = validate_alerts(synthetic_frame)

    scores = calculate_rule_scores(alerts)

    assert scores.between(0, 1).all()


def test_reason_codes_expose_observable_signals(synthetic_frame):
    alerts = validate_alerts(synthetic_frame)
    alerts.loc[0, "anomaly_score"] = 0.9
    alerts.loc[0, "proc_injection_flag"] = 1

    reasons = build_reason_codes(alerts)

    assert "HIGH_ANOMALY_SCORE" in reasons.iloc[0]
    assert "PROCESS_INJECTION_SIGNAL" in reasons.iloc[0]


def test_risk_bands_have_stable_boundaries():
    levels = assign_risk_levels(pd.Series([0.44, 0.45, 0.69, 0.70]))

    assert levels.tolist() == ["Low", "Medium", "Medium", "High"]
