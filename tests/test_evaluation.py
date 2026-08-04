import pytest

from ai_threat_detection.config import EvaluationConfig
from ai_threat_detection.evaluation import evaluate_alerts
from ai_threat_detection.validation import DataValidationError


def test_evaluation_produces_holdout_metrics_and_evidence(synthetic_frame):
    artifacts = evaluate_alerts(synthetic_frame, source_sha256="abc123")
    report = artifacts.report

    assert report["dataset"]["source_sha256"] == "abc123"
    assert report["evaluation"]["split_strategy"] == "chronological_holdout"
    assert report["evaluation"]["training_rows"] == 90
    assert report["evaluation"]["test_rows"] == 30
    assert set(report["holdout_metrics"]) == {
        "rule_baseline",
        "supervised_model",
        "blended_score",
    }
    assert artifacts.scored_alerts["blend_score"].between(0, 1).all()
    assert artifacts.feature_importance["importance"].sum() == pytest.approx(1.0)


def test_evaluation_is_reproducible(synthetic_frame):
    first = evaluate_alerts(synthetic_frame)
    second = evaluate_alerts(synthetic_frame)

    assert first.report == second.report
    assert first.scored_alerts["model_probability"].equals(
        second.scored_alerts["model_probability"]
    )


def test_evaluation_rejects_insufficient_windows(synthetic_frame):
    with pytest.raises(DataValidationError, match="At least 40"):
        evaluate_alerts(synthetic_frame.iloc[:30])

    with pytest.raises(DataValidationError, match="enough train/test"):
        evaluate_alerts(
            synthetic_frame.iloc[:40],
            evaluation_config=EvaluationConfig(test_size=0.10),
        )


def test_evaluation_rejects_single_class_training_window(synthetic_frame):
    invalid = synthetic_frame.copy()
    invalid.loc[:89, "label"] = 0

    with pytest.raises(DataValidationError, match="both label classes"):
        evaluate_alerts(invalid)


def test_single_class_holdout_omits_ranking_metrics(synthetic_frame):
    data = synthetic_frame.copy()
    data.loc[90:, "label"] = 0

    report = evaluate_alerts(data).report

    assert report["holdout_metrics"]["blended_score"]["roc_auc"] is None
    assert report["holdout_metrics"]["blended_score"]["average_precision"] is None
