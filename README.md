# AI-Augmented Threat Detection Framework

An explainable alert-risk evaluation framework for synthetic security telemetry. It
compares a transparent rule baseline with a supervised model, produces analyst-facing
reason codes and writes reproducible evidence artifacts.

Current source boundary: **v1.0.0 stable research reference**.

> [!IMPORTANT]
> Stable package/API status does not establish production detection performance,
> production readiness, regulatory compliance, certification or authority for
> autonomous containment. Owner-authorized GitHub publication is gated on successful
> CI, CodeQL and Stable Release Gate runs on the exact `main` commit. Package-index
> publication and deployment remain out of scope.

The immutable release, once published, is available at
[v1.0.0](https://github.com/bilgekayali/ai-threat-detection-framework/releases/tag/v1.0.0).
See [Release Process](docs/RELEASE_PROCESS.md) for the publication boundary.

This repository is a public research reference. It contains no customer data, bank
configuration, detection rule or production architecture. Scores are intended to
support human triage, never autonomous containment.

## Summary

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
- Brier score and explicit train/holdout partition labels
- per-alert risk bands and reason codes
- dataset hashing and a deterministic artifact-hash manifest
- deterministic CycloneDX dependency SBOM generation for release evidence
- five public Draft 2020-12 input/output schemas
- automated linting, tests, coverage, CodeQL and clean-wheel release gates

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
| evidence_manifest.json | Exact artifact hashes, schema identities and package/source binding |

The report compares the rule baseline, supervised model and blended score using
precision, recall, F1, ROC AUC, average precision and a confusion matrix. Metrics are
calculated only on the final chronological holdout window. Brier score provides a
bounded probability-error measure, and each scored row is marked `train` or `holdout`.

## Stable v1 contract

The v1 compatibility boundary covers the six names exported through
`ai_threat_detection.__all__`, the two installed CLI commands, the normalized input
contract and the exact public output schemas. The committed API/schema/reference-data
fingerprints are verified by:

~~~bash
python tools/release_contract.py --emit --verify
~~~

See [Compatibility Policy](COMPATIBILITY.md), [Model Card](docs/MODEL_CARD.md),
[Dataset Card](docs/DATASET_CARD.md), [Threat Model](docs/THREAT_MODEL.md) and
[Release Process](docs/RELEASE_PROCESS.md).

## Development

~~~bash
python -m pip install -e ".[dev]"
ruff check .
pytest
~~~

The test suite covers validation failures, score boundaries, explanations,
reproducibility, schema contracts and CLI artifact generation. CI runs on Python 3.10,
3.11 and 3.12, evaluates the full synthetic dataset and builds a clean-wheel smoke
environment. All third-party workflow actions are pinned to exact commits.

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
├── .github/workflows/codeql.yml
├── .github/workflows/stable-release.yml
├── docs/
├── release/
├── schemas/
├── src/ai_threat_detection/
│   ├── cli.py
│   ├── config.py
│   ├── evaluation.py
│   ├── generator.py
│   ├── scoring.py
│   └── validation.py
├── tests/
├── tools/
│   ├── build_sbom.py
│   └── release_contract.py
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
