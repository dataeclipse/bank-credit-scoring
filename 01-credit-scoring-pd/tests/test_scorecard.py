"""Тесты scorecard (маркер ml): сильная фича → высокий IV; сборка и predict."""

from __future__ import annotations

import pytest

pytest.importorskip("optbinning")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from pd_scoring.models.dataset import ModelingData  # noqa: E402
from pd_scoring.models.scorecard import fit_scorecard  # noqa: E402


def _signal_data() -> ModelingData:
    rng = np.random.default_rng(0)
    n = 1000
    signal = rng.normal(size=n)
    noise = rng.normal(size=n)
    y = (signal + rng.normal(scale=0.3, size=n) > 0).astype(int)
    frame = pd.DataFrame({"signal": signal, "noise": noise})
    return ModelingData(
        X_train=frame.iloc[:800].reset_index(drop=True),
        y_train=pd.Series(y[:800]),
        X_holdout=frame.iloc[800:].reset_index(drop=True),
        y_holdout=pd.Series(y[800:]),
        feature_names=["signal", "noise"],
        categorical_features=[],
    )


@pytest.mark.ml
def test_scorecard_strong_feature_high_iv() -> None:
    result = fit_scorecard(_signal_data(), seed=42)
    iv = dict(zip(result.iv_table["name"], result.iv_table["iv"], strict=False))
    assert iv["signal"] > iv["noise"]  # сильная фича — выше IV
    assert "signal" in result.selected_features
    assert result.holdout_metrics["roc_auc"] > 0.7  # сигнал ловится


@pytest.mark.ml
def test_scorecard_cv_metrics_present() -> None:
    result = fit_scorecard(_signal_data(), seed=42)
    for metric in ("roc_auc", "pr_auc", "ks", "gini"):
        assert metric in result.cv_metrics
        assert metric in result.holdout_metrics
