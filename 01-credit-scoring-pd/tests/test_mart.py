from __future__ import annotations

import polars as pl

from pd_scoring.features.build_mart import (
    DAYS_EMPLOYED_ANOMALY,
    build_application_features,
)
from pd_scoring.features.schema import build_feature_schema, feature_columns


def _make_app(ids: list[int], *, train: bool, anomaly_first: bool = False) -> pl.DataFrame:
    n = len(ids)
    employed = [-1000] * n
    if anomaly_first and n:
        employed[0] = DAYS_EMPLOYED_ANOMALY
    data: dict[str, list[object]] = {
        "SK_ID_CURR": list(ids),
        "AMT_CREDIT": [1000.0] * n,
        "AMT_INCOME_TOTAL": [5000.0] * n,
        "AMT_ANNUITY": [100.0] * n,
        "AMT_GOODS_PRICE": [900.0] * n,
        "DAYS_EMPLOYED": employed,
        "DAYS_BIRTH": [-10000] * n,
        "CNT_FAM_MEMBERS": [2.0] * n,
        "EXT_SOURCE_2": [0.5] * n,
        "CODE_GENDER": ["M"] * n,
    }
    if train:
        data["TARGET"] = [i % 2 for i in range(n)]
    return pl.DataFrame(data)


def test_application_features_basic() -> None:
    train = _make_app([1, 2, 3, 4], train=True, anomaly_first=True)
    test = _make_app([5, 6], train=False)
    base, docs = build_application_features(train, test)

    assert base["SK_ID_CURR"].n_unique() == base.height == 6

    for col in ("CREDIT_INCOME_RATIO", "ANNUITY_INCOME_RATIO", "DAYS_EMPLOYED_ANOM"):
        assert col in base.columns

    assert base.filter(pl.col("is_train").not_())["TARGET"].null_count() == 2
    assert docs


def test_days_employed_anomaly_cleaned() -> None:
    train = _make_app([1, 2], train=True, anomaly_first=True)
    test = _make_app([3], train=False)
    base, _ = build_application_features(train, test)
    row = base.filter(pl.col("SK_ID_CURR") == 1)
    assert row.select("DAYS_EMPLOYED_ANOM").item() == 1
    assert row.select("DAYS_EMPLOYED").item() is None


def test_schema_matches_columns() -> None:
    train = _make_app([1, 2, 3, 4], train=True)
    test = _make_app([5, 6], train=False)
    base, docs = build_application_features(train, test)

    schema = build_feature_schema(base, docs)
    cols = set(feature_columns(base))

    assert schema["n_features"] == len(cols)
    assert {f["name"] for f in schema["features"]} == cols

    for non_feature in ("SK_ID_CURR", "TARGET", "is_train"):
        assert non_feature not in cols

    assert all(f["description"] for f in schema["features"])
