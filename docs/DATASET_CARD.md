# Dataset Card

## Dataset

`synthetic_alerts.csv` is the retained 2025 reference snapshot used to exercise the
evaluation pipeline. It contains synthetic timestamps, identifiers, event families,
observable signals and generated binary research labels. It contains no customer,
employee, bank, security-product or production-system data.

The exact file digest and row count are frozen in
`release/release-contract.json`. A reproducible alternative dataset can be produced
with `ai-threat-generate` using an explicit row count, seed and start time.

## Schema

Each normalized row follows `schemas/alert-input.schema.json`. The v1 event families
are `file`, `login`, `network`, `process` and `registry`. Identifiers must be
non-negative integers; binary fields must contain 0 or 1; anomaly scores are bounded
from 0 to 1; and timestamps are normalized to UTC.

The `label` is a generated research label. It is not an analyst-adjudicated incident
outcome and must not be interpreted as ground truth about a real person, device or
security event.

## Generation

The generator samples event types and supporting signals from documented probability
distributions. A noisy latent-risk function produces labels so the example is learnable
without becoming perfectly separable. Given the same supported runtime, parameters and
dependency environment, generation is deterministic.

## Allowed use

The dataset may be used to test validation, scoring, evidence generation, model
evaluation and governance workflows. It must not be represented as a benchmark of
operational detection quality or combined with real identifiers in a public fork.

## Known limitations

- Synthetic distributions do not reproduce an operational SOC.
- The event taxonomy is deliberately small.
- There is no analyst disagreement, delayed adjudication or label correction history.
- There are no production-source quality, missingness or drift characteristics.
- Results from this snapshot and a newly generated scenario are not directly
  comparable unless generation parameters and runtime versions are controlled.
