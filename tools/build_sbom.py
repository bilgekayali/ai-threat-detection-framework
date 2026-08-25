from __future__ import annotations

import argparse
import json
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from ai_threat_detection.version import PACKAGE_VERSION

DIRECT_RUNTIME_DEPENDENCIES = ("numpy", "pandas", "scikit-learn")
ROOT_COMPONENT_REF = f"pkg:pypi/ai-threat-detection-framework@{PACKAGE_VERSION}"


def build_sbom() -> dict:
    components = []
    dependency_refs = []
    for name in DIRECT_RUNTIME_DEPENDENCIES:
        try:
            resolved = version(name)
        except PackageNotFoundError as exc:
            raise SystemExit(f"required runtime dependency is not installed: {name}") from exc
        reference = f"pkg:pypi/{name}@{resolved}"
        dependency_refs.append(reference)
        components.append(
            {
                "type": "library",
                "bom-ref": reference,
                "name": name,
                "version": resolved,
                "purl": reference,
            }
        )
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "component": {
                "type": "application",
                "bom-ref": ROOT_COMPONENT_REF,
                "name": "ai-threat-detection-framework",
                "version": PACKAGE_VERSION,
                "purl": ROOT_COMPONENT_REF,
            }
        },
        "components": components,
        "dependencies": [
            {"ref": ROOT_COMPONENT_REF, "dependsOn": dependency_refs},
            *({"ref": reference, "dependsOn": []} for reference in dependency_refs),
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a deterministic CycloneDX dependency SBOM for the current runtime."
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = build_sbom()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
