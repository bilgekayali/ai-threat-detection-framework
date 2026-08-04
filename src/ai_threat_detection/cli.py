"""Command-line interface for reproducible threat-triage evaluation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from ai_threat_detection import __version__
from ai_threat_detection.config import EvaluationConfig
from ai_threat_detection.evaluation import evaluate_alerts, sha256_file, write_artifacts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate explainable rule and ML alert-risk scores on synthetic telemetry."
        )
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("synthetic_alerts.csv"),
        help="Input CSV path (default: synthetic_alerts.csv).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/latest"),
        help="Directory for scored alerts and evaluation evidence.",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.25,
        help="Chronological holdout fraction between 0.10 and 0.50.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Model random seed.")
    parser.add_argument(
        "--model-weight",
        type=float,
        default=0.60,
        help="Model contribution to the blended score between 0 and 1.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        source_digest = sha256_file(args.data)
        data = pd.read_csv(args.data)
        config = EvaluationConfig(
            test_size=args.test_size,
            random_seed=args.seed,
            model_weight=args.model_weight,
        )
        artifacts = evaluate_alerts(
            data,
            evaluation_config=config,
            source_sha256=source_digest,
        )
        write_artifacts(artifacts, args.output_dir)
    except (OSError, ValueError) as exc:
        print(f"Evaluation failed: {exc}", file=sys.stderr)
        return 2

    print(f"Evaluated {len(artifacts.scored_alerts)} synthetic alerts.")
    print(f"Evidence written to {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
