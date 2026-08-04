import json

from ai_threat_detection.cli import main


def test_cli_writes_all_artifacts(tmp_path, synthetic_frame):
    source = tmp_path / "alerts.csv"
    output = tmp_path / "evidence"
    synthetic_frame.to_csv(source, index=False)

    result = main(["--data", str(source), "--output-dir", str(output)])

    assert result == 0
    assert (output / "scored_alerts.csv").is_file()
    assert (output / "feature_importance.csv").is_file()
    report = json.loads((output / "evaluation_report.json").read_text())
    assert report["dataset"]["rows"] == 120


def test_cli_returns_error_for_missing_source(tmp_path):
    result = main(["--data", str(tmp_path / "missing.csv")])

    assert result == 2
