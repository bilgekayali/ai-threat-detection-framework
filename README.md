# AI-Augmented Threat Detection Framework

An explainable alert-risk evaluation framework for synthetic security telemetry. It
compares a transparent rule baseline with a supervised model, produces analyst-facing
reason codes and writes reproducible evidence artifacts.

This repository is a public research reference. It contains no customer data, bank
configuration, detection rule or production architecture. Scores are intended to
support human triage, never autonomous containment.

## Why this project exists

Security teams need more than a model prediction. They need to know which observable
signals influenced a score, how performance was measured and whether the evidence can
be reproduced later. This project demonstrates those controls in a deliberately small,
inspectable pipeline.

The current implementation provides:

- strict schema, type and range validation
- a bounded and fully documented rule baseline
- a deterministic random-forest model with categorical event handling
- a chronological holdout that reduces future-to-past leakage
- rule, model and blended holdout metrics
- per-alert risk bands and reason codes
- dataset hashing and machine-readable evaluation evidence
- automated linting, tests, coverage and a full-dataset smoke run

## Evaluation flow

~~~mermaid
flowchart LR
    A[Synthetic XDR/SIEM alerts] --> B[Schema and range validation]
    B --> C[Transparent rule baseline]
    B --> D[Chronological train/test split]
    D --> E[Supervised risk model]
    C --> F[Blended risk score]
    E --> F
    F --> G[Risk band and reason codes]
    G --> H[CSV and JSON evidence]
    H --> I[Human analyst review]
~~~

The original conceptual architecture is retained in
[Architecture Diagram](./Architecture%20Diagram.png). The accompanying 2025 whitepaper
is available as
[AI Threat Detection Framework for Financial Institutions](./AI_Threat_Detection_Framework_Financial_Institution_29102025.pdf).

## Quickstart

Python 3.10 or newer is required.

~~~bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .

ai-threat-eval \
  --data synthetic_alerts.csv \
  --output-dir artifacts/latest
~~~

The committed CSV is the original 2025 synthetic snapshot. A documented, deterministic
scenario can also be generated for fresh experiments:

~~~bash
ai-threat-generate --rows 2000 --seed 42 --out artifacts/generated_alerts.csv
ai-threat-eval \
  --data artifacts/generated_alerts.csv \
  --output-dir artifacts/generated-evaluation
~~~

The legacy file remains as a compatibility entry point after installation:

~~~bash
python ai_risk_model.py --data synthetic_alerts.csv --output-dir artifacts/latest
~~~

## Evidence produced

| Artifact | Purpose |
| --- | --- |
| scored_alerts.csv | Rule, model and blended scores; risk bands; prediction and reason codes |
| evaluation_report.json | Dataset digest, split configuration, metrics, confusion matrices and limitations |
| feature_importance.csv | Ranked global feature importance from the fitted model |

The report compares the rule baseline, supervised model and blended score using
precision, recall, F1, ROC AUC, average precision and a confusion matrix. Metrics are
calculated only on the final chronological holdout window.

## Development

~~~bash
python -m pip install -e ".[dev]"
ruff check .
pytest
~~~

The test suite covers validation failures, score boundaries, explanations,
reproducibility and CLI artifact generation. CI also evaluates the repository's full
synthetic dataset as a smoke test.

## Method and control boundary

The model is not presented as a production detector. Synthetic labels are suitable for
testing pipeline behaviour, not for making claims about real detection accuracy.
Thresholds, features, response actions and acceptable false-positive rates would all
need to be validated against an organisation's own telemetry and risk appetite.

See [Methodology](docs/METHODOLOGY.md) for the split design, scoring logic, metrics,
limitations and framework mapping.

## Repository structure

~~~text
.
├── .github/workflows/ci.yml
├── docs/METHODOLOGY.md
├── src/ai_threat_detection/
│   ├── cli.py
│   ├── config.py
│   ├── evaluation.py
│   ├── generator.py
│   ├── scoring.py
│   └── validation.py
├── tests/
├── ai_risk_model.py
├── synthetic_alerts.csv
├── Architecture Diagram.png
├── AI_Threat_Detection_Framework_Financial_Institution_29102025.pdf
└── pyproject.toml
~~~

## Responsible use

- Do not use the synthetic model or thresholds to make employment, access or
  disciplinary decisions.
- Do not connect the example directly to automated blocking or containment.
- Do not upload real identifiers, credentials, security logs or customer data to a
  public fork.
- Record local validation, approvals and rollback procedures before adapting the
  design to an operational environment.

## Author and license

Bilge Kayalı — [LinkedIn](https://www.linkedin.com/in/bilge-kayali-9a1232149/)

MIT License. See [LICENSE.txt](LICENSE.txt).
