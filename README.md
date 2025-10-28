# AI-Augmented Threat Detection Architecture (Conceptual)

This repository accompanies the whitepaper:
**"AI-Augmented Threat Detection Architecture for Financial Institutions – A Synthetic Framework Based on ISO 27001 and XDR Principles"**  
Author: **Bilge Kayalı** • Date: **October 2025**  
LinkedIn: https://www.linkedin.com/in/bilge-kayali-9a1232149/

> Compliance notice: This repo uses **entirely synthetic data** and a **generic** architecture.
> It **does not** disclose or represent any real systems or configurations.

## Repository structure

```
ai-threat-detection-framework/
├── README.md
├── LICENSE.txt
├── architecture_diagram.png
├── synthetic_alerts.csv
├── ai_risk_model.py
└── report.pdf
```

## Overview

- **Goal**: Demonstrate a safe, conceptual example of AI-assisted detection above an XDR layer.
- **Key idea**: Blend rule-based signals with a lightweight ML model for **risk scoring** and **explainable** decisions.
- **Framework alignment**: ISO 27001 (Annex A), NIST CSF (Detect/Respond), MITRE ATT&CK for tactics mapping.

## Synthetic dataset

`syn thetic_alerts.csv` includes the following columns:

- `timestamp` (ISO8601)
- `user_id` (anonymised integer)
- `asset_id` (anonymised integer)
- `event_type` (login, process, network, file, registry)
- `anomaly_score` (0.0–1.0)
- `off_hours` (0/1)
- `failed_logins_24h` (0..50)
- `geo_distance_km` (0..12000)
- `proc_injection_flag` (0/1)
- `label` (0 benign, 1 suspicious) — weakly correlated for demo purposes

## Quickstart

1. Install Python 3.10+ and `pip install scikit-learn pandas numpy` (optional — the script has a no-deps fallback).
2. Run:
   ```bash
   python ai_risk_model.py --data synthetic_alerts.csv --train
   python ai_risk_model.py --data synthetic_alerts.csv --score --out results.csv
   ```
3. Review `results.csv` and feature importances printed to console.

> Note: This is a **toy** implementation to illustrate approach, not production code.

## Architecture (conceptual)

- **Telemetry** (XDR/EDR/SIEM) → **Data Lake/ETL** → **AI Risk Scoring** → **SOAR Playbooks** → **Audit/Explainability**

See `architecture_diagram.png` for a high-level visual.

## Safety/Compliance

- No real data, vendors, configs, keys, or IP disclosed.
- The materials are designed for **public sharing** and **Tech Nation evidence** of thought leadership.

## License

MIT — see `LICENSE.txt`.
