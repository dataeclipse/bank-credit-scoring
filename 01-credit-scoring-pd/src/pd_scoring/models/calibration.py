from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from pd_scoring.models.dataset import ModelingData
from pd_scoring.models.gbdt import to_lightgbm_frame, train_lightgbm
from pd_scoring.models.metrics import brier, ece, reliability_curve


@dataclass(frozen=True)
class CalibrationResult:
    model: Any
    method: str
    calibrator: Any
    metrics_table: dict[str, dict[str, float]]
    reliability: dict[str, tuple[Any, Any]]
    holdout_proba_raw: Any
    holdout_proba_calibrated: Any


def split_fit_calib(data: ModelingData, *, seed: int, calib_size: float = 0.2) -> Any:
    return train_test_split(
        data.X_train,
        data.y_train,
        test_size=calib_size,
        stratify=data.y_train,
        random_state=seed,
    )


def _apply(calibrator: Any, proba: Any) -> Any:
    if isinstance(calibrator, IsotonicRegression):
        return calibrator.predict(proba)
    return calibrator.predict_proba(np.asarray(proba).reshape(-1, 1))[:, 1]


def calibrate(
    data: ModelingData, params: dict[str, Any], *, seed: int, calib_size: float = 0.2
) -> CalibrationResult:
    x_fit, x_calib, y_fit, y_calib = split_fit_calib(data, seed=seed, calib_size=calib_size)
    fit_data = ModelingData(
        X_train=x_fit.reset_index(drop=True),
        y_train=y_fit.reset_index(drop=True),
        X_holdout=data.X_holdout,
        y_holdout=data.y_holdout,
        feature_names=data.feature_names,
        categorical_features=data.categorical_features,
    )
    gbdt = train_lightgbm(fit_data, params, seed=seed)
    model = gbdt.model

    p_calib = model.predict_proba(to_lightgbm_frame(x_calib, data.categorical_features))[:, 1]
    p_holdout_raw = gbdt.holdout_proba
    y_calib_arr = np.asarray(y_calib)

    isotonic = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
    isotonic.fit(p_calib, y_calib_arr)
    sigmoid = LogisticRegression()
    sigmoid.fit(p_calib.reshape(-1, 1), y_calib_arr)

    candidates = {"isotonic": isotonic, "sigmoid": sigmoid}
    y_holdout = data.y_holdout
    table: dict[str, dict[str, float]] = {
        "raw": {"brier": brier(y_holdout, p_holdout_raw), "ece": ece(y_holdout, p_holdout_raw)}
    }
    proba_by_method: dict[str, Any] = {"raw": p_holdout_raw}
    for name, calibrator in candidates.items():
        proba = _apply(calibrator, p_holdout_raw)
        proba_by_method[name] = proba
        table[name] = {"brier": brier(y_holdout, proba), "ece": ece(y_holdout, proba)}

    best = min(candidates, key=lambda m: table[m]["brier"])
    return CalibrationResult(
        model=model,
        method=best,
        calibrator=candidates[best],
        metrics_table=table,
        reliability={
            "raw": reliability_curve(y_holdout, p_holdout_raw),
            best: reliability_curve(y_holdout, proba_by_method[best]),
        },
        holdout_proba_raw=p_holdout_raw,
        holdout_proba_calibrated=proba_by_method[best],
    )
