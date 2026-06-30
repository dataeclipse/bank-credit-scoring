"""Подбор гиперпараметров GBDT через Optuna (TPE, фиксированный seed, K-fold CV, early stopping).

Тюнинг гоняет CV строго на train (holdout не виден); early stopping — на val самого фолда,
поэтому утечки нет. Финальная оценка моделей — на общем holdout (см. train.py).
"""

from __future__ import annotations

from typing import Any

import numpy as np
import optuna
import pandas as pd
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier, early_stopping, log_evaluation
from sklearn.model_selection import StratifiedKFold

from pd_scoring.models.dataset import ModelingData
from pd_scoring.models.gbdt import EARLY_STOP, to_catboost_frame, to_lightgbm_frame
from pd_scoring.models.metrics import roc_auc

DEFAULT_TRIALS = 30
TUNING_FOLDS = 3  # для HPO достаточно 3 фолдов; финальная оценка — на holdout
TUNING_ITERS = 600  # cap деревьев для HPO; финальные модели учатся до 3000 с early stopping


def _cv(seed: int) -> Any:
    return StratifiedKFold(n_splits=TUNING_FOLDS, shuffle=True, random_state=seed)


def _mean_cv_auc_lightgbm(
    params: dict[str, Any], x: pd.DataFrame, y: pd.Series, seed: int
) -> float:
    aucs: list[float] = []
    for tr, va in _cv(seed).split(x, y):
        model = LGBMClassifier(
            **params, n_estimators=TUNING_ITERS, random_state=seed, n_jobs=-1, verbose=-1
        )
        model.fit(
            x.iloc[tr],
            y.iloc[tr],
            eval_set=[(x.iloc[va], y.iloc[va])],
            eval_metric="auc",
            callbacks=[early_stopping(EARLY_STOP, verbose=False), log_evaluation(0)],
        )
        aucs.append(roc_auc(y.iloc[va], model.predict_proba(x.iloc[va])[:, 1]))
    return float(np.mean(aucs))


def _mean_cv_auc_catboost(
    params: dict[str, Any], x: pd.DataFrame, y: pd.Series, categorical: list[str], seed: int
) -> float:
    aucs: list[float] = []
    for tr, va in _cv(seed).split(x, y):
        model = CatBoostClassifier(
            **params,
            iterations=TUNING_ITERS,
            random_seed=seed,
            eval_metric="AUC",
            cat_features=categorical,
            max_ctr_complexity=1,  # без комбинаций категориальных — кратно быстрее
            verbose=0,
            allow_writing_files=False,
        )
        model.fit(
            x.iloc[tr],
            y.iloc[tr],
            eval_set=(x.iloc[va], y.iloc[va]),
            early_stopping_rounds=EARLY_STOP,
        )
        aucs.append(roc_auc(y.iloc[va], model.predict_proba(x.iloc[va])[:, 1]))
    return float(np.mean(aucs))


def tune_lightgbm(
    data: ModelingData, *, seed: int, n_trials: int = DEFAULT_TRIALS
) -> dict[str, Any]:
    """TPE-поиск гиперпараметров LightGBM по mean CV ROC-AUC."""
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    x, y = to_lightgbm_frame(data.X_train, data.categorical_features), data.y_train

    def objective(trial: Any) -> float:
        params = {
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
            "num_leaves": trial.suggest_int("num_leaves", 16, 96),
            "min_child_samples": trial.suggest_int("min_child_samples", 20, 200),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "subsample_freq": 1,
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
        }
        return _mean_cv_auc_lightgbm(params, x, y, seed)

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=seed))
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    return dict(study.best_params)


def tune_catboost(
    data: ModelingData, *, seed: int, n_trials: int = DEFAULT_TRIALS
) -> dict[str, Any]:
    """TPE-поиск гиперпараметров CatBoost по mean CV ROC-AUC."""
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    x, y = to_catboost_frame(data.X_train, data.categorical_features), data.y_train

    def objective(trial: Any) -> float:
        params = {
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
            "depth": trial.suggest_int("depth", 4, 6),
            "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1.0, 20.0, log=True),
            "random_strength": trial.suggest_float("random_strength", 1e-3, 10.0, log=True),
        }
        return _mean_cv_auc_catboost(params, x, y, data.categorical_features, seed)

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=seed))
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    return dict(study.best_params)
