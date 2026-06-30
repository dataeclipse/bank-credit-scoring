"""Банковские метрики качества PD-моделей (чистые функции; sklearn/numpy).

ROC-AUC, PR-AUC, KS-статистика, Gini. Используются для всех моделей на одном holdout.
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt
from sklearn.metrics import average_precision_score, roc_auc_score, roc_curve


def roc_auc(y_true: npt.ArrayLike, y_score: npt.ArrayLike) -> float:
    """Площадь под ROC-кривой."""
    return float(roc_auc_score(y_true, y_score))


def pr_auc(y_true: npt.ArrayLike, y_score: npt.ArrayLike) -> float:
    """Площадь под precision-recall кривой (average precision)."""
    return float(average_precision_score(y_true, y_score))


def ks_statistic(y_true: npt.ArrayLike, y_score: npt.ArrayLike) -> float:
    """KS-статистика = max(TPR − FPR) по порогам."""
    fpr, tpr, _ = roc_curve(y_true, y_score)
    return float(np.max(tpr - fpr))


def gini(y_true: npt.ArrayLike, y_score: npt.ArrayLike) -> float:
    """Gini = 2·ROC-AUC − 1."""
    return 2.0 * roc_auc(y_true, y_score) - 1.0


def evaluate(y_true: npt.ArrayLike, y_score: npt.ArrayLike) -> dict[str, float]:
    """Все банковские метрики разом."""
    auc = roc_auc(y_true, y_score)
    return {
        "roc_auc": auc,
        "pr_auc": pr_auc(y_true, y_score),
        "ks": ks_statistic(y_true, y_score),
        "gini": 2.0 * auc - 1.0,
    }
