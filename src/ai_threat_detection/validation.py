"""Schema and range validation for alert telemetry."""

from collections.abc import Iterable

import pandas as pd

TIMESTAMP_COLUMN = "timestamp"
IDENTIFIER_COLUMNS = ("user_id", "asset_id")
NUMERIC_FEATURES = (
    "anomaly_score",
    "off_hours",
    "failed_logins_24h",
    "geo_distance_km",
    "proc_injection_flag",
)
CATEGORICAL_FEATURES = ("event_type",)
ALLOWED_EVENT_TYPES = frozenset({"file", "login", "network", "process", "registry"})
LABEL_COLUMN = "label"
FEATURE_COLUMNS = (*NUMERIC_FEATURES, *CATEGORICAL_FEATURES)
REQUIRED_COLUMNS = (
    TIMESTAMP_COLUMN,
    *IDENTIFIER_COLUMNS,
    *CATEGORICAL_FEATURES,
    *NUMERIC_FEATURES,
    LABEL_COLUMN,
)


class DataValidationError(ValueError):
    """Raised when an input dataset cannot be evaluated safely."""


def _missing_columns(columns: Iterable[str]) -> list[str]:
    available = set(columns)
    return [column for column in REQUIRED_COLUMNS if column not in available]


def validate_alerts(data: pd.DataFrame) -> pd.DataFrame:
    """Return a validated, chronologically sorted copy of alert data."""

    missing = _missing_columns(data.columns)
    if missing:
        raise DataValidationError(f"Missing required columns: {', '.join(missing)}")
    if data.empty:
        raise DataValidationError("The alert dataset is empty.")

    frame = data.loc[:, REQUIRED_COLUMNS].copy()
    frame[TIMESTAMP_COLUMN] = pd.to_datetime(
        frame[TIMESTAMP_COLUMN],
        errors="coerce",
        format="mixed",
        utc=True,
    )
    if frame[TIMESTAMP_COLUMN].isna().any():
        raise DataValidationError("timestamp contains missing or invalid ISO-8601 values.")

    numeric_columns = (*IDENTIFIER_COLUMNS, *NUMERIC_FEATURES, LABEL_COLUMN)
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        if frame[column].isna().any():
            raise DataValidationError(f"{column} contains missing or non-numeric values.")

    for column in IDENTIFIER_COLUMNS:
        if (frame[column] < 0).any() or (frame[column] % 1 != 0).any():
            raise DataValidationError(f"{column} must contain non-negative integers.")
        frame[column] = frame[column].astype("int64")

    frame["event_type"] = frame["event_type"].astype("string").str.strip()
    if frame["event_type"].isna().any() or (frame["event_type"] == "").any():
        raise DataValidationError("event_type contains missing or blank values.")
    unknown_event_types = sorted(set(frame["event_type"]) - ALLOWED_EVENT_TYPES)
    if unknown_event_types:
        raise DataValidationError(
            "event_type contains unsupported values: " + ", ".join(unknown_event_types)
        )

    if not frame["anomaly_score"].between(0, 1).all():
        raise DataValidationError("anomaly_score must be between 0 and 1.")
    for column in ("off_hours", "proc_injection_flag", LABEL_COLUMN):
        if not frame[column].isin((0, 1)).all():
            raise DataValidationError(f"{column} must contain only 0 or 1.")
        frame[column] = frame[column].astype("int8")
    if (frame["failed_logins_24h"] < 0).any():
        raise DataValidationError("failed_logins_24h cannot be negative.")
    if (frame["geo_distance_km"] < 0).any():
        raise DataValidationError("geo_distance_km cannot be negative.")

    return frame.sort_values(TIMESTAMP_COLUMN, kind="stable").reset_index(drop=True)
