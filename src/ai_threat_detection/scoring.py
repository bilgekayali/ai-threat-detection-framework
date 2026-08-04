"""Transparent baseline scoring and analyst-facing reason codes."""

import numpy as np
import pandas as pd

from ai_threat_detection.config import RuleConfig


def calculate_rule_scores(
    alerts: pd.DataFrame,
    config: RuleConfig | None = None,
) -> pd.Series:
    """Calculate a bounded 0-1 rule score for each validated alert."""

    rule = config or RuleConfig()
    failed_login_factor = alerts["failed_logins_24h"].clip(0, 10) / 10
    geo_distance_factor = alerts["geo_distance_km"].clip(0, 5_000) / 5_000

    score = (
        rule.anomaly_weight * alerts["anomaly_score"]
        + rule.off_hours_weight * alerts["off_hours"]
        + rule.failed_logins_weight * failed_login_factor
        + rule.geo_distance_weight * geo_distance_factor
        + rule.process_injection_weight * alerts["proc_injection_flag"]
    )
    return score.clip(0, 1).rename("rule_score")


def assign_risk_levels(
    scores: pd.Series,
    config: RuleConfig | None = None,
) -> pd.Series:
    """Map a numeric score to stable Low, Medium and High bands."""

    rule = config or RuleConfig()
    values = np.select(
        [scores >= rule.high_threshold, scores >= rule.medium_threshold],
        ["High", "Medium"],
        default="Low",
    )
    return pd.Series(values, index=scores.index, dtype="string")


def build_reason_codes(alerts: pd.DataFrame) -> pd.Series:
    """Explain which observable signals raised the deterministic baseline."""

    reasons: list[str] = []
    for row in alerts.itertuples(index=False):
        row_reasons: list[str] = []
        if row.anomaly_score >= 0.70:
            row_reasons.append("HIGH_ANOMALY_SCORE")
        if row.off_hours == 1:
            row_reasons.append("OFF_HOURS_ACTIVITY")
        if row.failed_logins_24h >= 5:
            row_reasons.append("REPEATED_AUTH_FAILURES")
        if row.geo_distance_km >= 1_000:
            row_reasons.append("LONG_DISTANCE_LOGIN")
        if row.proc_injection_flag == 1:
            row_reasons.append("PROCESS_INJECTION_SIGNAL")
        reasons.append(";".join(row_reasons) or "NO_ELEVATED_RULE_SIGNAL")
    return pd.Series(reasons, index=alerts.index, dtype="string", name="reason_codes")
