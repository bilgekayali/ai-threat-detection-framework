# Methodology

## Scope

The framework evaluates an explainable alert-triage layer above synthetic XDR, EDR or
SIEM-style telemetry. It is designed to demonstrate evaluation and evidence controls,
not to reproduce any real financial institution's environment.

The input contains five event families: login, process, network, file and registry.
User and asset identifiers are synthetic. The label is a generated research label and
must not be interpreted as an adjudicated incident outcome.

The committed CSV is retained as the original 2025 research snapshot. The
ai-threat-generate command provides a reproducible alternative: it samples event types,
anomaly values and supporting signals from documented probability distributions, then
draws a noisy binary label from a latent risk function. The added noise is intentional;
it avoids making the synthetic task perfectly separable.

## Input contract

The evaluator requires:

| Field | Validation |
| --- | --- |
| timestamp | Parseable timestamp; normalised to UTC |
| user_id, asset_id | Non-negative integer identifiers |
| event_type | One of file, login, network, process or registry |
| anomaly_score | Numeric value from 0 to 1 |
| off_hours | Binary value |
| failed_logins_24h | Non-negative numeric count |
| geo_distance_km | Non-negative numeric distance |
| proc_injection_flag | Binary value |
| label | Binary research label |

Invalid data fails closed with a clear error. The evaluator does not silently impute
missing values or clip invalid source fields.

## Transparent rule baseline

The baseline is a weighted sum constrained to the range 0 to 1:

| Signal | Weight | Normalisation |
| --- | ---: | --- |
| anomaly_score | 0.50 | Already bounded to 0-1 |
| off_hours | 0.10 | Binary |
| failed_logins_24h | 0.15 | Capped at 10, then divided by 10 |
| geo_distance_km | 0.10 | Capped at 5,000 km, then divided by 5,000 |
| proc_injection_flag | 0.15 | Binary |

Risk bands are Low below 0.45, Medium from 0.45 to below 0.70 and High at or above
0.70. These are example triage bands, not production severity definitions.

Reason codes expose observable rule signals:

- HIGH_ANOMALY_SCORE
- OFF_HOURS_ACTIVITY
- REPEATED_AUTH_FAILURES
- LONG_DISTANCE_LOGIN
- PROCESS_INJECTION_SIGNAL

## Supervised model

The model is a random forest with 300 estimators, balanced class weights, a minimum leaf
size of three and a fixed random seed. Numeric features pass through unchanged.
`event_type` is one-hot encoded after the closed v1 event taxonomy has been validated.

The model deliberately excludes synthetic user and asset identifiers. Treating those
identifiers as predictive features could encourage memorisation and reduce portability.

## Leakage control and evaluation

Rows are sorted by timestamp. The earliest 75% form the training window and the final
25% form the holdout window by default. This chronological split is closer to an
operational deployment question than a random split: train on earlier events, evaluate
on later events.

The same holdout window is used to compare:

1. the transparent rule baseline;
2. the supervised model probability;
3. a blend with 60% model weight and 40% rule weight.

The default binary decision threshold is 0.50. The report includes precision, recall,
F1, ROC AUC, average precision, Brier score and the four confusion-matrix counts. ROC
AUC and average precision are reported as null if the holdout contains only one class.
Every scored row is marked `train` or `holdout` so in-sample probabilities cannot be
silently presented as holdout evidence.

## Reproducibility and evidence

Each run records:

- SHA-256 of the source CSV;
- row count, positive rate and event-time boundaries;
- chronological split sizes;
- model configuration and random seed;
- feature list and blend weights;
- package, Python, NumPy, pandas and scikit-learn versions;
- holdout metrics and confusion matrices;
- explicit limitations.

Outputs use stable field ordering and a fixed model seed. Model execution is restricted
to one worker to reduce nondeterministic parallel behaviour. `evidence_manifest.json`
binds the three primary evidence artifacts to exact SHA-256 digests and public schema
identities. Exact numeric reproducibility is scoped to the runtime versions recorded in
the report; compatible dependency updates can change floating-point model output.

The normalized input and generated evidence contracts are published as Draft 2020-12
JSON Schemas under `schemas/` and are checked in CI.

## Governance boundary

This implementation supports analyst prioritisation. It does not implement automated
account suspension, endpoint isolation, evidence deletion or any other containment
action. A production adaptation would require at least:

- source-specific data quality monitoring;
- label governance and adjudication criteria;
- threshold calibration by use case;
- drift, calibration and subgroup analysis;
- human approval and separation of duties for material actions;
- immutable decision and response logging;
- documented rollback and incident procedures;
- privacy, employment-law and model-risk review.

## Framework mapping

The conceptual design is informed by ISO/IEC 27001:2022 logging, monitoring and incident
management controls; the Detect and Respond functions of NIST CSF 2.0; and MITRE ATT&CK
as a contextual threat taxonomy.

This is an interpretive engineering mapping. Running this repository does not confer
certification, demonstrate compliance or replace a formal control assessment.

## Known limitations

- All data and labels are synthetic.
- The dataset is small compared with operational security telemetry.
- Labels are generated and are not analyst-adjudicated ground truth.
- Results can vary materially between the legacy snapshot and a newly generated
  scenario because their label-generation processes differ.
- The global feature-importance table is not a causal explanation.
- The example does not measure calibration, drift or subgroup performance.
- The framework has no direct SIEM, XDR, SOAR or case-management integration.
- Public holdout metrics cannot support claims about a real institution's detection
  performance.
