from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised by the Python 3.10 CI job
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "release" / "release-contract.json"
REPOSITORY_POLICY_PATH = ROOT / "release" / "repository-governance.json"
SCHEMA_DIR = ROOT / "schemas"
WORKFLOW_DIR = ROOT / ".github" / "workflows"
REFERENCE_DATASET = ROOT / "synthetic_alerts.csv"
_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_USES = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)", re.MULTILINE)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"{path}: expected JSON object")
    return payload


def _public_api_fingerprint() -> dict[str, object]:
    if str(ROOT / "src") not in sys.path:
        sys.path.insert(0, str(ROOT / "src"))
    import ai_threat_detection

    symbols = list(ai_threat_detection.__all__)
    if len(symbols) != len(set(symbols)):
        raise SystemExit("ai_threat_detection.__all__ contains duplicate public symbols")
    missing = [name for name in symbols if not hasattr(ai_threat_detection, name)]
    if missing:
        raise SystemExit("public API exports missing attributes: " + ", ".join(missing))
    ordered = sorted(symbols)
    return {"symbol_count": len(ordered), "sha256": _sha256(ordered)}


def _schema_set_fingerprint() -> dict[str, object]:
    entries = [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in sorted(SCHEMA_DIR.glob("*.schema.json"))
    ]
    if not entries:
        raise SystemExit("public schema set is empty")
    return {"file_count": len(entries), "sha256": _sha256(entries)}


def _reference_dataset_fingerprint() -> dict[str, object]:
    with REFERENCE_DATASET.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        row_count = sum(1 for _ in reader)
    return {
        "path": REFERENCE_DATASET.relative_to(ROOT).as_posix(),
        "row_count": row_count,
        "sha256": hashlib.sha256(REFERENCE_DATASET.read_bytes()).hexdigest(),
    }


def compute_fingerprints() -> dict[str, dict[str, object]]:
    return {
        "public_api": _public_api_fingerprint(),
        "schema_set": _schema_set_fingerprint(),
        "reference_dataset": _reference_dataset_fingerprint(),
    }


def _verify_action_pins() -> None:
    failures: list[str] = []
    for path in sorted(WORKFLOW_DIR.glob("*.y*ml")):
        source = path.read_text(encoding="utf-8")
        for spec in _USES.findall(source):
            if spec.startswith("./"):
                continue
            if "@" not in spec:
                failures.append(f"{path.relative_to(ROOT)}: action without ref: {spec}")
                continue
            ref = spec.rsplit("@", 1)[1]
            if not _SHA40.fullmatch(ref):
                failures.append(
                    f"{path.relative_to(ROOT)}: action ref is not an exact commit SHA: {spec}"
                )
    if failures:
        raise SystemExit("\n".join(failures))


def _verify_release_metadata(manifest: dict) -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]
    current = manifest.get("current_release_version")
    if current != "1.0.0" or manifest.get("release_stage") != "stable-reference":
        raise SystemExit("release contract must describe the v1.0.0 stable reference")
    if project.get("version") != current:
        raise SystemExit("pyproject version does not match current_release_version")
    if "Development Status :: 5 - Production/Stable" not in project.get(
        "classifiers", []
    ):
        raise SystemExit("stable reference requires the Production/Stable package classifier")

    if str(ROOT / "src") not in sys.path:
        sys.path.insert(0, str(ROOT / "src"))
    import ai_threat_detection

    if ai_threat_detection.__version__ != current:
        raise SystemExit("runtime package version does not match the release contract")
    scripts = project.get("scripts", {})
    if sorted(scripts) != manifest.get("stable_cli_commands"):
        raise SystemExit("stable CLI command set does not match pyproject scripts")

    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    if not re.search(rf"^version:\s*{re.escape(current)}\s*$", citation, re.MULTILINE):
        raise SystemExit("CITATION.cff version does not match the release contract")


def _verify_repository_policy(manifest: dict) -> None:
    policy = _load_json(REPOSITORY_POLICY_PATH)
    if policy.get("default_branch") != "main":
        raise SystemExit("repository governance policy must target main")
    if policy.get("enforcement_verified") is not False:
        raise SystemExit("repository policy must not claim unverified live enforcement")
    if manifest.get("repository_governance_enforcement_verified") is not False:
        raise SystemExit("release contract must preserve unverified enforcement state")
    required = policy.get("required_workflow_names")
    expected = ["CI", "CodeQL", "Stable Release Gate"]
    if required != expected:
        raise SystemExit("repository policy must declare the exact v1 workflow set")


def _verify_documentation() -> None:
    required = [
        ROOT / "CHANGELOG.md",
        ROOT / "COMPATIBILITY.md",
        ROOT / "docs" / "DATASET_CARD.md",
        ROOT / "docs" / "MODEL_CARD.md",
        ROOT / "docs" / "RELEASE_PROCESS.md",
        ROOT / "docs" / "THREAT_MODEL.md",
    ]
    missing = [path.relative_to(ROOT).as_posix() for path in required if not path.is_file()]
    empty = [
        path.relative_to(ROOT).as_posix()
        for path in required
        if path.is_file() and not path.read_text(encoding="utf-8").strip()
    ]
    if missing or empty:
        raise SystemExit(
            "release documentation is incomplete: " + ", ".join(sorted(missing + empty))
        )


def verify() -> dict[str, dict[str, object]]:
    manifest = _load_json(MANIFEST_PATH)
    computed = compute_fingerprints()
    for key, actual in computed.items():
        expected = manifest.get(key)
        if expected != actual:
            raise SystemExit(
                f"{key} freeze mismatch: expected {json.dumps(expected, sort_keys=True)}, "
                f"computed {json.dumps(actual, sort_keys=True)}"
            )

    if manifest.get("schema_version") != "ai-threat-detection.release-contract.v1":
        raise SystemExit("unsupported release-contract schema version")
    if manifest.get("requires_human_release_decision") is not True:
        raise SystemExit("tagging and publication must remain explicit human decisions")
    if manifest.get("source_promotion_only") is not True:
        raise SystemExit("v1 hardening must remain a source-only promotion")
    non_claims = manifest.get("non_claims")
    if (
        not isinstance(non_claims, dict)
        or not non_claims
        or any(value is not False for value in non_claims.values())
    ):
        raise SystemExit("release-contract non-claims must be explicit false booleans")

    _verify_release_metadata(manifest)
    _verify_repository_policy(manifest)
    _verify_documentation()
    _verify_action_pins()
    return computed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit or verify the AI threat-detection v1 release contract."
    )
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    computed = compute_fingerprints()
    if args.emit:
        print(json.dumps(computed, indent=2, sort_keys=True))
        if not args.verify:
            return 0
    verify()
    print(json.dumps(computed, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
