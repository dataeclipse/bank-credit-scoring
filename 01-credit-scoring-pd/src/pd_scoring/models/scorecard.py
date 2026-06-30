"""WOE-scorecard через optbinning.

Главное про утечки: в CV биннинг (WOE/IV) обучается СТРОГО внутри каждого train-фолда и
применяется к val-фолду — оценка scorecard честная, не оптимистичная. Финальная модель
обучает биннинг на полном train и фиксированно применяет его к holdout.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from optbinning import BinningProcess, Scorecard
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

from pd_scoring.models.dataset import ModelingData
from pd_scoring.models.metrics import evaluate

IV_MIN = 0.02  # классический порог отбора: IV < 0.02 — бесполезная фича


def _build_scorecard(feature_names: list[str], categorical: list[str], seed: int) -> Any:
    """Собрать необученный Scorecard (биннинг + логистическая регрессия + PDO-шкала)."""
    binning_process = BinningProcess(
        variable_names=list(feature_names),
        categorical_variables=list(categorical),
        selection_criteria={"iv": {"min": IV_MIN}},
        n_jobs=-1,
    )
    estimator = LogisticRegression(max_iter=1000, random_state=seed)
    return Scorecard(
        binning_process=binning_process,
        estimator=estimator,
        scaling_method="pdo_odds",
        scaling_method_params={"pdo": 50, "odds": 20, "scorecard_points": 600},
    )


def _default_proba(model: Any, features: pd.DataFrame) -> Any:
    """Вероятность дефолта (класс 1) от scorecard."""
    return model.predict_proba(features)[:, 1]


def cross_val_scorecard(data: ModelingData, *, seed: int, n_splits: int = 5) -> dict[str, float]:
    """CV-оценка scorecard с биннингом, обученным ВНУТРИ каждого фолда (без оптимизма)."""
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    x, y = data.X_train, data.y_train
    per_fold: list[dict[str, float]] = []
    for train_idx, val_idx in cv.split(x, y):
        model = _build_scorecard(data.feature_names, data.categorical_features, seed)
        model.fit(x.iloc[train_idx], y.iloc[train_idx])
        proba = _default_proba(model, x.iloc[val_idx])
        per_fold.append(evaluate(y.iloc[val_idx], proba))
    return {metric: float(np.mean([fold[metric] for fold in per_fold])) for metric in per_fold[0]}


@dataclass(frozen=True)
class ScorecardResult:
    """Финальный scorecard + метрики (CV и holdout) + артефакты (IV, points)."""

    model: Any
    cv_metrics: dict[str, float]
    holdout_metrics: dict[str, float]
    iv_table: pd.DataFrame
    points_table: pd.DataFrame
    selected_features: list[str]


def fit_scorecard(data: ModelingData, *, seed: int) -> ScorecardResult:
    """Честная CV-оценка + финальный scorecard (биннинг на полном train → holdout)."""
    cv_metrics = cross_val_scorecard(data, seed=seed)

    model = _build_scorecard(data.feature_names, data.categorical_features, seed)
    model.fit(data.X_train, data.y_train)
    holdout_metrics = evaluate(data.y_holdout, _default_proba(model, data.X_holdout))

    fitted_bp = getattr(model, "binning_process_", model.binning_process)
    summary = fitted_bp.summary()
    iv_table = summary[["name", "dtype", "iv", "selected"]].sort_values("iv", ascending=False)
    selected_features = summary.loc[summary["selected"], "name"].tolist()
    points_table = model.table(style="summary")
    return ScorecardResult(
        model=model,
        cv_metrics=cv_metrics,
        holdout_metrics=holdout_metrics,
        iv_table=iv_table,
        points_table=points_table,
        selected_features=selected_features,
    )
