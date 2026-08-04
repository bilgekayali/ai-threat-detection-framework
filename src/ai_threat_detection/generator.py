"""Deterministic synthetic telemetry generation for pipeline experiments."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class GeneratorConfig:
    """Controls for a reproducible synthetic alert scenario."""

    rows: int = 2_000
    random_seed: int = 42
    start: str = "2026-01-01T00:00:00Z"

    def __post_init__(self) -> None:
        if self.rows < 100:
            raise ValueError("rows must be at least 100.")
        if pd.isna(pd.to_datetime(self.start, errors="coerce", utc=True)):
            raise ValueError("start must be a valid timestamp.")


def generate_synthetic_alerts(
    config: GeneratorConfig | None = None,
) -> pd.DataFrame:
    """Generate noisy, learnable and entirely synthetic alert telemetry."""

    settings = config or GeneratorConfig()
    rng = np.random.default_rng(settings.random_seed)
    rows = settings.rows

    event_type = rng.choice(
        np.array(["login", "process", "network", "file", "registry"]),
        size=rows,
        p=np.array([0.34, 0.23, 0.20, 0.14, 0.09]),
    )
    anomaly_score = rng.beta(2.0, 4.5, size=rows)
    off_hours = rng.binomial(1, 0.22, size=rows)
    failed_logins = np.clip(
        rng.poisson(0.8 + 3.2 * anomaly_score + 1.5 * off_hours),
        0,
        50,
    )
    geo_distance = np.clip(
        rng.lognormal(4.2 + 0.8 * off_hours, 1.0, size=rows),
        0,
        12_000,
    )
    injection_probability = (
        0.01
        + 0.09 * (event_type == "process")
        + 0.14 * (anomaly_score >= 0.70)
    )
    process_injection = rng.binomial(
        1,
        np.clip(injection_probability, 0, 0.45),
    )

    latent_risk = (
        -3.5
        + 4.2 * anomaly_score
        + 0.65 * off_hours
        + 0.14 * np.minimum(failed_logins, 10)
        + 0.00025 * np.minimum(geo_distance, 5_000)
        + 1.9 * process_injection
        + 0.20 * (event_type == "process")
    )
    probability = 1 / (1 + np.exp(-latent_risk))
    labels = rng.binomial(1, probability)

    return pd.DataFrame(
        {
            "timestamp": pd.date_range(
                start=settings.start,
                periods=rows,
                freq="15min",
                tz="UTC",
            ),
            "user_id": rng.integers(1_000, 1_100, size=rows),
            "asset_id": rng.integers(2_000, 2_200, size=rows),
            "event_type": event_type,
            "anomaly_score": np.round(anomaly_score, 6),
            "off_hours": off_hours,
            "failed_logins_24h": failed_logins,
            "geo_distance_km": np.round(geo_distance, 3),
            "proc_injection_flag": process_injection,
            "label": labels,
        }
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate an entirely synthetic alert dataset."
    )
    parser.add_argument("--rows", type=int, default=2_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--start", default="2026-01-01T00:00:00Z")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/generated_alerts.csv"),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = generate_synthetic_alerts(
            GeneratorConfig(
                rows=args.rows,
                random_seed=args.seed,
                start=args.start,
            )
        )
        args.out.parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(args.out, index=False)
    except (OSError, ValueError) as exc:
        print(f"Generation failed: {exc}")
        return 2

    print(f"Wrote {len(data)} synthetic alerts to {args.out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
