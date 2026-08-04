from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def synthetic_frame() -> pd.DataFrame:
    rows = 120
    index = np.arange(rows)
    anomaly = ((index * 7) % 100) / 100
    off_hours = (index % 5 == 0).astype(int)
    failed_logins = index % 9
    geo_distance = (index * 137) % 6_000
    injection = (index % 13 == 0).astype(int)
    signal = (
        0.55 * anomaly
        + 0.10 * off_hours
        + 0.15 * (failed_logins / 8)
        + 0.10 * (geo_distance / 6_000)
        + 0.25 * injection
    )
    labels = (signal >= 0.48).astype(int)

    return pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-01-01",
                periods=rows,
                freq="15min",
                tz="UTC",
            ),
            "user_id": 1_000 + (index % 20),
            "asset_id": 2_000 + (index % 25),
            "event_type": np.resize(
                np.array(["login", "process", "network", "file", "registry"]),
                rows,
            ),
            "anomaly_score": anomaly,
            "off_hours": off_hours,
            "failed_logins_24h": failed_logins,
            "geo_distance_km": geo_distance,
            "proc_injection_flag": injection,
            "label": labels,
        }
    )
