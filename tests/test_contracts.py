import hashlib
import json
import subprocess
import sys
from pathlib import Path

import jsonschema
import pandas as pd

from ai_threat_detection.evaluation import evaluate_alerts, write_artifacts

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"


def _schema(name):
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def test_public_schemas_are_valid_draft_2020_12():
    paths = sorted(SCHEMAS.glob("*.schema.json"))

    assert len(paths) == 5
    for path in paths:
        jsonschema.Draft202012Validator.check_schema(
            json.loads(path.read_text(encoding="utf-8"))
        )


def test_generated_evidence_matches_public_schemas(tmp_path, synthetic_frame):
    input_records = synthetic_frame.copy()
    input_records["timestamp"] = input_records["timestamp"].map(lambda value: value.isoformat())
    for record in input_records.to_dict(orient="records"):
        jsonschema.validate(record, _schema("alert-input.schema.json"))

    source = tmp_path / "alerts.csv"
    synthetic_frame.to_csv(source, index=False)
    artifacts = evaluate_alerts(
        synthetic_frame,
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    )
    output = tmp_path / "evidence"
    write_artifacts(artifacts, output)

    report = json.loads((output / "evaluation_report.json").read_text(encoding="utf-8"))
    manifest = json.loads((output / "evidence_manifest.json").read_text(encoding="utf-8"))
    jsonschema.validate(report, _schema("evaluation-report.schema.json"))
    jsonschema.validate(manifest, _schema("evidence-manifest.schema.json"))

    scored = pd.read_csv(output / "scored_alerts.csv")
    for record in scored.to_dict(orient="records"):
        jsonschema.validate(record, _schema("scored-alert.schema.json"))

    importance = pd.read_csv(output / "feature_importance.csv")
    for record in importance.to_dict(orient="records"):
        jsonschema.validate(record, _schema("feature-importance.schema.json"))

    for item in manifest["artifacts"]:
        path = output / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]


def test_release_contract_verifies_exact_repository_state():
    result = subprocess.run(
        [sys.executable, "tools/release_contract.py", "--verify"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
