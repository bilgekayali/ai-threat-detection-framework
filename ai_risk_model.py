#!/usr/bin/env python3
"""Compatibility entry point for the packaged command-line evaluator."""

from ai_threat_detection.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
