# Model Card

## Model details

The reference evaluator compares three alert-triage signals:

1. a transparent weighted-rule baseline;
2. a scikit-learn `RandomForestClassifier`;
3. a bounded blend of the rule and model probabilities.

The supervised model uses 300 estimators, balanced class weights, a minimum leaf size
of three, one worker and a caller-recorded random seed. Numeric fields pass through
unchanged. `event_type` is one-hot encoded. Synthetic user and asset identifiers are
excluded from model features.

## Intended use

The model demonstrates leakage-aware evaluation, evidence generation and analyst-facing
reason codes on synthetic SIEM/XDR-style telemetry. It is intended for research,
education, pipeline testing and governance demonstrations.

It is not intended to make access, employment, disciplinary or containment decisions;
to rank real people; or to establish production detection performance.

## Data and evaluation

The first 75% of records by timestamp form the default training window and the final
25% form the holdout window. Metrics are computed only on the holdout. Outputs label
every row as `train` or `holdout` so in-sample scores cannot be silently mistaken for
holdout evidence.

Reported metrics are precision, recall, F1, ROC AUC, average precision, Brier score and
confusion-matrix counts. Ranking metrics are null when a holdout contains one class.

## Explainability

Rule reason codes identify observable signals that raised the deterministic baseline.
The feature-importance table is global impurity-based importance from the fitted random
forest. It is not causal explanation and does not explain an individual model score.

## Limitations and risks

- All labels and identifiers are synthetic.
- The label-generating process is simpler than real adversarial behaviour.
- The model is not calibrated for any institution, product or threat environment.
- Global feature importance can be unstable and biased toward some feature types.
- The implementation does not measure subgroup fairness or concept drift.
- Dependency changes may alter exact floating-point results; runtime versions are
  therefore recorded with every report.
- Scores must not trigger autonomous containment.

## Human oversight and change control

An operational adaptation requires named model ownership, independent validation,
threshold approval, data-quality monitoring, drift and calibration review, case-level
human adjudication, response logging, rollback and periodic revalidation. Changes to
the stable input/output contract follow `COMPATIBILITY.md`.
