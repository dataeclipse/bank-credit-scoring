"""Тесты калибровки (маркер ml): нет утечки, ECE не ухудшается."""

from __future__ import annotations

import pytest

pytest.importorskip("lightgbm")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from pd_scoring.models.calibration import calibrate, split_fit_calib  # noqa: E402
from pd_scoring.models.dataset import ModelingData  # noqa: E402


def _data() -> ModelingData:
    rng = np.random.default_rng(0)
    n = 2000
    signal = rng.normal(size=n)
    cat = rng.choice(["a", "b"], size=n)
    y = (signal + rng.normal(scale=0.5, size=n) > 0).astype(int)
    frame = pd.DataFrame({"signal": signal, "cat": pd.Series(cat)})
    return ModelingData(
        X_train=frame.iloc[:1500].reset_index(drop=True),
        y_train=pd.Series(y[:1500]),
        X_holdout=frame.iloc[1500:].reset_index(drop=True),
        y_holdout=pd.Series(y[1500:]),
        feature_names=["signal", "cat"],
        categorical_features=["cat"],
    )


@pytest.mark.ml
def test_calibration_no_leakage() -> None:
    data = _data()
    x_fit, x_calib, _, _ = split_fit_calib(data, seed=42, calib_size=0.2)
    assert set(x_fit.index).isdisjoint(set(x_calib.index))  # fit и calib не пересекаются
    assert len(x_fit) + len(x_calib) == len(data.X_train)  # вместе = train (holdout отдельный)


@pytest.mark.ml
def test_calibration_does_not_worsen_ece() -> None:
    data = _data()
    result = calibrate(data, {"num_leaves": 15, "learning_rate": 0.1}, seed=42)
    raw_ece = result.metrics_table["raw"]["ece"]
    best_ece = result.metrics_table[result.method]["ece"]
    assert best_ece <= raw_ece + 1e-6
    assert result.method in ("isotonic", "sigmoid")
