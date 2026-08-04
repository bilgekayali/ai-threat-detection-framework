import pandas as pd
import pytest

from ai_threat_detection.generator import (
    GeneratorConfig,
    generate_synthetic_alerts,
    main,
)
from ai_threat_detection.validation import validate_alerts


def test_generator_is_reproducible_and_valid():
    config = GeneratorConfig(rows=200, random_seed=17)

    first = generate_synthetic_alerts(config)
    second = generate_synthetic_alerts(config)

    assert first.equals(second)
    assert len(validate_alerts(first)) == 200
    assert first["label"].nunique() == 2


def test_generator_cli_writes_a_valid_dataset(tmp_path):
    output = tmp_path / "generated.csv"

    result = main(["--rows", "200", "--seed", "9", "--out", str(output)])

    assert result == 0
    assert len(validate_alerts(pd.read_csv(output))) == 200


def test_generator_rejects_invalid_configuration(tmp_path):
    with pytest.raises(ValueError, match="at least 100"):
        GeneratorConfig(rows=99)
    with pytest.raises(ValueError, match="valid timestamp"):
        GeneratorConfig(start="invalid")

    result = main(["--rows", "10", "--out", str(tmp_path / "invalid.csv")])

    assert result == 2
