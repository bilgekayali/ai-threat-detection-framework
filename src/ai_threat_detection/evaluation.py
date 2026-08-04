"""Leakage-aware model evaluation and evidence artifact generation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from ai_threat_detection.config import EvaluationConfig, RuleConfig
from ai_threat_detection.scoring import (
    assign_risk_levels,
    build_reason_codes,
    calculate_rule_scores,
)
from ai_threat_detection.validation import (
    CATEGORICAL_FEATURES,
    DataValidationError,
    FEATURE_COLUMNS,
    LABEL_COLUMN,
    NUMERIC_FEATURES,
    validate_alerts,
)


@dataclass(frozen=True)
class EvaluationArtifacts:
    """In-memory artifacts produced by one deterministic evaluation run."""

    scored_alerts: pd.DataFrame
    feature_importance: pd.DataFrame
    report: dict[str, Any]


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest for a source dataset."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _build_model(seed: int) -> Pipeline:
    preprocess = ColumnTransformer(
        transformers=[
            ("numeric", "passthrough", list(NUMERIC_FEATURES)),
            (
                "event",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                list(CATEGORICAL_FEATURES),
            ),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )
    classifier = RandomForestClassifier(
        n_estimators=300,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=seed,
        n_jobs=1,
    )
    return Pipeline([("preprocess", preprocess), ("classifier", classifier)])


def _binary_metrics(
    labels: pd.Series,
    probabilities: pd.Series,
    threshold: float,
) -> dict[str, Any]:
    predictions = (probabilities >= threshold).astype("int8")
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels,
        predictions,
        average="binary",
        zero_division=0,
    )
    matrix = confusion_matrix(labels, predictions, labels=[0, 1])
    has_both_classes = labels.nunique() == 2
    return {
        "decision_threshold": threshold,
        "precision": round(float(precision), 6),
        "recall": round(float(recall), 6),
        "f1": round(float(f1), 6),
        "roc_auc": (
            round(float(roc_auc_score(labels, probabilities)), 6)
            if has_both_classes
            else None
        ),
        "average_precision": (
            round(float(average_precision_score(labels, probabilities)), 6)
            if has_both_classes
            else None
        ),
        "confusion_matrix": {
            "true_negative": int(matrix[0, 0]),
            "false_positive": int(matrix[0, 1]),
            "false_negative": int(matrix[1, 0]),
            "true_positive": int(matrix[1, 1]),
        },
    }


def _positive_probability(model: Pipeline, features: pd.DataFrame) -> pd.Series:
    classifier = model.named_steps["classifier"]
    positive_index = list(classifier.classes_).index(1)
    probabilities = model.predict_proba(features)[:, positive_index]
    return pd.Series(probabilities, index=features.index, dtype="float64")


def evaluate_alerts(
    data: pd.DataFrame,
    evaluation_config: EvaluationConfig | None = None,
    rule_config: RuleConfig | None = None,
    source_sha256: str | None = None,
) -> EvaluationArtifacts:
    """Evaluate rule, model and blended scores on a chronological holdout."""

    evaluation = evaluation_config or EvaluationConfig()
    rule = rule_config or RuleConfig()
    alerts = validate_alerts(data)
    if len(alerts) < 40:
        raise DataValidationError("At least 40 alerts are required for temporal evaluation.")

    split_index = int(len(alerts) * (1 - evaluation.test_size))
    if split_index < 20 or len(alerts) - split_index < 10:
        raise DataValidationError("The configured split does not leave enough train/test rows.")

    train = alerts.iloc[:split_index]
    test = alerts.iloc[split_index:]
    if train[LABEL_COLUMN].nunique() != 2:
        raise DataValidationError("The training window must contain both label classes.")

    model = _build_model(evaluation.random_seed)
    model.fit(train.loc[:, FEATURE_COLUMNS], train[LABEL_COLUMN])

    rule_scores = calculate_rule_scores(alerts, rule)
    model_probabilities = _positive_probability(model, alerts.loc[:, FEATURE_COLUMNS])
    blend_scores = (
        evaluation.model_weight * model_probabilities
        + (1 - evaluation.model_weight) * rule_scores
    ).clip(0, 1)

    scored = alerts.copy()
    scored["rule_score"] = rule_scores
    scored["rule_risk"] = assign_risk_levels(rule_scores, rule)
    scored["model_probability"] = model_probabilities
    scored["model_risk"] = assign_risk_levels(model_probabilities, rule)
    scored["blend_score"] = blend_scores
    scored["blend_risk"] = assign_risk_levels(blend_scores, rule)
    scored["predicted_label"] = (
        blend_scores >= evaluation.decision_threshold
    ).astype("int8")
    scored["reason_codes"] = build_reason_codes(alerts)

    feature_names = model.named_steps["preprocess"].get_feature_names_out()
    importances = model.named_steps["classifier"].feature_importances_
    feature_importance = (
        pd.DataFrame({"feature": feature_names, "importance": importances})
        .sort_values("importance", ascending=False, kind="stable")
        .reset_index(drop=True)
    )

    test_slice = slice(split_index, None)
    test_labels = alerts.loc[test_slice, LABEL_COLUMN]
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "dataset": {
            "source_sha256": source_sha256,
            "rows": len(alerts),
            "positive_rate": round(float(alerts[LABEL_COLUMN].mean()), 6),
            "first_event_utc": alerts["timestamp"].min().isoformat(),
            "last_event_utc": alerts["timestamp"].max().isoformat(),
        },
        "evaluation": {
            "split_strategy": "chronological_holdout",
            "training_rows": len(train),
            "test_rows": len(test),
            "test_size": evaluation.test_size,
            "random_seed": evaluation.random_seed,
            "features": list(FEATURE_COLUMNS),
            "model": {
                "algorithm": "RandomForestClassifier",
                "estimators": 300,
                "min_samples_leaf": 3,
                "class_weight": "balanced",
            },
            "blend": {
                "model_weight": evaluation.model_weight,
                "rule_weight": round(1 - evaluation.model_weight, 6),
            },
        },
        "risk_bands": {
            "low": f"score < {rule.medium_threshold}",
            "medium": f"{rule.medium_threshold} <= score < {rule.high_threshold}",
            "high": f"score >= {rule.high_threshold}",
        },
        "holdout_metrics": {
            "rule_baseline": _binary_metrics(
                test_labels,
                rule_scores.loc[test_slice],
                evaluation.decision_threshold,
            ),
            "supervised_model": _binary_metrics(
                test_labels,
                model_probabilities.loc[test_slice],
                evaluation.decision_threshold,
            ),
            "blended_score": _binary_metrics(
                test_labels,
                blend_scores.loc[test_slice],
                evaluation.decision_threshold,
            ),
        },
        "limitations": [
            "All telemetry and labels are synthetic.",
            "Holdout metrics do not establish production detection performance.",
            "Scores support analyst triage and must not trigger autonomous containment.",
            "Thresholds require validation against each organisation's risk appetite.",
        ],
    }
    return EvaluationArtifacts(scored, feature_importance, report)


def write_artifacts(artifacts: EvaluationArtifacts, output_dir: Path) -> None:
    """Write deterministic CSV and JSON evidence artifacts."""

    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts.scored_alerts.to_csv(output_dir / "scored_alerts.csv", index=False)
    artifacts.feature_importance.to_csv(
        output_dir / "feature_importance.csv",
        index=False,
    )
    report_path = output_dir / "evaluation_report.json"
    report_path.write_text(
        json.dumps(artifacts.report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
