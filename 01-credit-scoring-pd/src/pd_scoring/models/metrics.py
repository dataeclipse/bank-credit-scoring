from __future__ import annotations

from typing import Any

import numpy as np
import numpy.typing as npt
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    roc_auc_score,
    roc_curve,
)


def roc_auc(y_true: npt.ArrayLike, y_score: npt.ArrayLike) -> float:
    return float(roc_auc_score(y_true, y_score))


def pr_auc(y_true: npt.ArrayLike, y_score: npt.ArrayLike) -> float:
    return float(average_precision_score(y_true, y_score))


def ks_statistic(y_true: npt.ArrayLike, y_score: npt.ArrayLike) -> float:
    fpr, tpr, _ = roc_curve(y_true, y_score)
    return float(np.max(tpr - fpr))


def gini(y_true: npt.ArrayLike, y_score: npt.ArrayLike) -> float:
    return 2.0 * roc_auc(y_true, y_score) - 1.0


def evaluate(y_true: npt.ArrayLike, y_score: npt.ArrayLike) -> dict[str, float]:
    auc = roc_auc(y_true, y_score)
    return {
        "roc_auc": auc,
        "pr_auc": pr_auc(y_true, y_score),
        "ks": ks_statistic(y_true, y_score),
        "gini": 2.0 * auc - 1.0,
    }


def brier(y_true: npt.ArrayLike, y_score: npt.ArrayLike) -> float:
    return float(brier_score_loss(y_true, y_score))


def ece(y_true: npt.ArrayLike, y_score: npt.ArrayLike, *, bins: int = 10) -> float:
    y = np.asarray(y_true, dtype=float)
    p = np.asarray(y_score, dtype=float)
    edges = np.linspace(0.0, 1.0, bins + 1)
    bin_idx = np.clip(np.digitize(p, edges[1:-1]), 0, bins - 1)
    total = len(p)
    score = 0.0
    for b in range(bins):
        mask = bin_idx == b
        n = int(mask.sum())
        if n == 0:
            continue
        score += (n / total) * abs(float(y[mask].mean()) - float(p[mask].mean()))
    return score


def reliability_curve(
    y_true: npt.ArrayLike, y_score: npt.ArrayLike, *, bins: int = 10
) -> tuple[Any, Any]:
    frac_pos, mean_pred = calibration_curve(y_true, y_score, n_bins=bins, strategy="uniform")
    return mean_pred, frac_pos
