from __future__ import annotations

import polars as pl

from pd_scoring.eda import days_employed_anomaly, missingness, target_rate


def test_target_rate() -> None:
    df = pl.DataFrame({"TARGET": [0, 1, 1, None]})
    rate = target_rate(df)
    assert rate["n"] == 3.0
    assert rate["positives"] == 2.0
    assert abs(rate["rate"] - 2 / 3) < 1e-9


def test_missingness() -> None:
    df = pl.DataFrame({"a": [1, None, None], "b": [1, 2, 3]})
    miss = missingness(df)
    a_row = miss.filter(pl.col("column") == "a")
    assert a_row.select("null_count").item() == 2
    assert abs(a_row.select("null_frac").item() - 2 / 3) < 1e-9
    assert miss["column"][0] == "a"


def test_days_employed_anomaly() -> None:
    df = pl.DataFrame({"DAYS_EMPLOYED": [-1000, 365243, 365243, -500]})
    anomaly = days_employed_anomaly(df)
    assert anomaly["anomaly_count"] == 2.0
    assert abs(anomaly["anomaly_frac"] - 0.5) < 1e-9
