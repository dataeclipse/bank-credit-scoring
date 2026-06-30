from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier, early_stopping, log_evaluation
from sklearn.model_selection import train_test_split

from pd_scoring.models.dataset import ModelingData
from pd_scoring.models.metrics import evaluate

CAT_NA = "__NA__"
EARLY_STOP = 100


def to_lightgbm_frame(x: pd.DataFrame, categorical: list[str]) -> pd.DataFrame:
    return x.assign(**{c: x[c].astype("category") for c in categorical})


def to_catboost_frame(x: pd.DataFrame, categorical: list[str]) -> pd.DataFrame:
    return x.assign(**{c: x[c].astype("object").fillna(CAT_NA).astype(str) for c in categorical})


def _early_val(x: pd.DataFrame, y: pd.Series, seed: int) -> Any:
    return train_test_split(x, y, test_size=0.15, stratify=y, random_state=seed)


@dataclass(frozen=True)
class GbdtResult:
    model: Any
    holdout_proba: Any
    holdout_metrics: dict[str, float]
    best_iteration: int


def train_lightgbm(data: ModelingData, params: dict[str, Any], *, seed: int) -> GbdtResult:
    x = to_lightgbm_frame(data.X_train, data.categorical_features)
    x_holdout = to_lightgbm_frame(data.X_holdout, data.categorical_features)
    x_tr, x_val, y_tr, y_val = _early_val(x, data.y_train, seed)
    model = LGBMClassifier(**params, n_estimators=3000, random_state=seed, n_jobs=-1, verbose=-1)
    model.fit(
        x_tr,
        y_tr,
        eval_set=[(x_val, y_val)],
        eval_metric="auc",
        callbacks=[early_stopping(EARLY_STOP, verbose=False), log_evaluation(0)],
    )
    proba = model.predict_proba(x_holdout)[:, 1]
    best = int(model.best_iteration_ or 0)
    return GbdtResult(model, proba, evaluate(data.y_holdout, proba), best)


def train_catboost(
    data: ModelingData, params: dict[str, Any], *, seed: int, task_type: str = "CPU"
) -> GbdtResult:
    x = to_catboost_frame(data.X_train, data.categorical_features)
    x_holdout = to_catboost_frame(data.X_holdout, data.categorical_features)
    x_tr, x_val, y_tr, y_val = _early_val(x, data.y_train, seed)
    model = CatBoostClassifier(
        **params,
        iterations=3000,
        random_seed=seed,
        eval_metric="AUC",
        cat_features=data.categorical_features,
        max_ctr_complexity=1,
        task_type=task_type,
        verbose=0,
        allow_writing_files=False,
    )
    model.fit(x_tr, y_tr, eval_set=(x_val, y_val), early_stopping_rounds=EARLY_STOP)
    proba = model.predict_proba(x_holdout)[:, 1]
    best = int(model.get_best_iteration() or 0)
    return GbdtResult(model, proba, evaluate(data.y_holdout, proba), best)
