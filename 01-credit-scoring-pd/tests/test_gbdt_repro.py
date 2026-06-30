"""Тесты воспроизводимости GBDT (маркер ml): один seed → идентичные holdout-метрики."""

from __future__ import annotations

import pytest

pytest.importorskip("lightgbm")
pytest.importorskip("catboost")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from pd_scoring.models.dataset import ModelingData  # noqa: E402
from pd_scoring.models.gbdt import train_catboost, train_lightgbm  # noqa: E402


def _synthetic() -> ModelingData:
    rng = np.random.default_rng(0)
    n = 600
    num = rng.normal(size=n)
    cat = rng.choice(["a", "b", "c"], size=n)
    y = (num + (cat == "a") * 0.8 + rng.normal(scale=0.4, size=n) > 0).astype(int)
    frame = pd.DataFrame({"num": num, "cat": pd.Series(cat)})
    return ModelingData(
        X_train=frame.iloc[:480].reset_index(drop=True),
        y_train=pd.Series(y[:480]),
        X_holdout=frame.iloc[480:].reset_index(drop=True),
        y_holdout=pd.Series(y[480:]),
        feature_names=["num", "cat"],
        categorical_features=["cat"],
    )


@pytest.mark.ml
def test_lightgbm_reproducible() -> None:
    data = _synthetic()
    params = {"num_leaves": 15, "learning_rate": 0.1}
    m1 = train_lightgbm(data, params, seed=42)
    m2 = train_lightgbm(data, params, seed=42)
    assert m1.holdout_metrics["roc_auc"] == m2.holdout_metrics["roc_auc"]


@pytest.mark.ml
def test_catboost_reproducible() -> None:
    data = _synthetic()
    params = {"depth": 4, "learning_rate": 0.1}
    m1 = train_catboost(data, params, seed=42)
    m2 = train_catboost(data, params, seed=42)
    assert m1.holdout_metrics["roc_auc"] == m2.holdout_metrics["roc_auc"]
