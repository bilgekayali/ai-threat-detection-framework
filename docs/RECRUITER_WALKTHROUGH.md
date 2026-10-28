# Two-minute reviewer walkthrough — AI Threat Detection Framework

**Audience:** security operations, CISO, AI-security and technical hiring reviewers.

**In one sentence:** This research reference tests whether a transparent rule baseline and a supervised risk score can produce interpretable alert-prioritisation evidence on synthetic security telemetry.

## 1. Read the scoring logic (30 seconds)

Review [scoring.py](../src/ai_threat_detection/scoring.py) for bounded input factors, risk bands and analyst-facing reason codes. The purpose is explainability, **not** automatic alert containment.

## 2. Run the local synthetic-data evaluation (60 seconds)

With Python 3.10+ available, from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
ai-threat-eval --data synthetic_alerts.csv --output-dir artifacts/latest
```

Windows users should activate the virtual environment using PowerShell or their local shell. These are README-documented commands; **this walkthrough update does not claim they were executed here**.

## 3. Inspect the reproducibility artifacts (30 seconds)

The evaluation is designed to produce:

- `scored_alerts.csv` — scores, risk bands and reason codes;
- `evaluation_report.json` — partition information, evaluation metrics and limitations;
- `feature_importance.csv` — ranked model feature importance;
- `evidence_manifest.json` — checksums and source/schema binding.

Read the [methodology](METHODOLOGY.md), [model card](MODEL_CARD.md) and [tests](../tests/) to assess the validation boundary.

## What this does *not* demonstrate

Synthetic labels do not prove live SOC detection quality, calibrated production alert thresholds or regulatory compliance. The project is a stable **research reference**, not a deployed detection system.

[Back to repository README](../README.md)
