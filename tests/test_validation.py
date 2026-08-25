import pytest

from ai_threat_detection.validation import DataValidationError, validate_alerts


def test_validation_sorts_alerts_chronologically(synthetic_frame):
    shuffled = synthetic_frame.sample(frac=1, random_state=7)

    validated = validate_alerts(shuffled)

    assert validated["timestamp"].is_monotonic_increasing
    assert len(validated) == len(synthetic_frame)


def test_validation_rejects_missing_columns(synthetic_frame):
    invalid = synthetic_frame.drop(columns=["label"])

    with pytest.raises(DataValidationError, match="Missing required columns: label"):
        validate_alerts(invalid)


def test_validation_rejects_out_of_range_values(synthetic_frame):
    invalid = synthetic_frame.copy()
    invalid.loc[0, "anomaly_score"] = 1.2

    with pytest.raises(DataValidationError, match="between 0 and 1"):
        validate_alerts(invalid)


def test_validation_rejects_empty_data(synthetic_frame):
    with pytest.raises(DataValidationError, match="empty"):
        validate_alerts(synthetic_frame.iloc[:0])


def test_validation_rejects_unsupported_event_type(synthetic_frame):
    invalid = synthetic_frame.copy()
    invalid.loc[0, "event_type"] = "cloud_control_plane"

    with pytest.raises(DataValidationError, match="unsupported values"):
        validate_alerts(invalid)


@pytest.mark.parametrize(
    ("column", "value", "message"),
    [
        ("timestamp", "not-a-date", "timestamp"),
        ("user_id", -1, "non-negative integers"),
        ("event_type", " ", "blank"),
        ("off_hours", 2, "only 0 or 1"),
        ("failed_logins_24h", -1, "cannot be negative"),
        ("geo_distance_km", -1, "cannot be negative"),
    ],
)
def test_validation_rejects_invalid_field_values(
    synthetic_frame,
    column,
    value,
    message,
):
    invalid = synthetic_frame.copy()
    if column == "timestamp":
        invalid[column] = invalid[column].astype("object")
    invalid.loc[0, column] = value

    with pytest.raises(DataValidationError, match=message):
        validate_alerts(invalid)


def test_validation_rejects_non_numeric_values(synthetic_frame):
    invalid = synthetic_frame.copy()
    invalid["asset_id"] = invalid["asset_id"].astype("object")
    invalid.loc[0, "asset_id"] = "unknown"

    with pytest.raises(DataValidationError, match="non-numeric"):
        validate_alerts(invalid)
