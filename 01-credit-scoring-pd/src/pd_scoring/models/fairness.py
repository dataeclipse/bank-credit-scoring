"""Fairness-анализ прод-модели через Fairlearn по прокси-группам.

Решение: PD ≥ порог → предсказан дефолт (заявка отклоняется). Порог по умолчанию — KS-точка
(Youden's J) на holdout. Благоприятный исход = одобрение (PD < порог).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from fairlearn.metrics import (
    MetricFrame,
    demographic_parity_difference,
    equalized_odds_difference,
    false_positive_rate,
    selection_rate,
    true_positive_rate,
)
from sklearn.metrics import roc_curve


def youden_threshold(y_true: Any, y_score: Any) -> float:
    """Порог, максимизирующий TPR − FPR (KS-точка)."""
    fpr, tpr, thresholds = roc_curve(y_true, y_score)
    return float(thresholds[int(np.argmax(tpr - fpr))])


def age_bands(days_birth: pd.Series) -> pd.Series:
    """Возрастные бэнды из DAYS_BIRTH (отрицательные дни)."""
    age = (-days_birth / 365).round()
    return pd.cut(
        age, bins=[0, 30, 40, 50, 60, 200], labels=["<30", "30-40", "40-50", "50-60", "60+"]
    )


@dataclass(frozen=True)
class GroupFairness:
    """Fairness по одной прокси-группе."""

    by_group: pd.DataFrame
    approval_rate: dict[str, float]
    demographic_parity_diff: float
    equalized_odds_diff: float
    disparate_impact: float


# Невалидные/служебные значения групп — исключаем (не настоящие демографические подгруппы).
DROP_TOKENS = {"xna", "unknown", "nan", "none", ""}


def fairness_report(
    y_true: Any,
    y_score: Any,
    sensitive: dict[str, pd.Series],
    *,
    threshold: float | None = None,
    min_count: int = 50,
) -> tuple[float, dict[str, GroupFairness]]:
    """Fairness-метрики по каждой прокси-группе (мелкие/служебные подгруппы отбрасываем).

    Возвращает (порог, отчёт).
    """
    thr = threshold if threshold is not None else youden_threshold(y_true, y_score)
    y_pred_default = (np.asarray(y_score) >= thr).astype(int)  # 1 = предсказан дефолт (отказ)
    y_true_arr = np.asarray(y_true)

    report: dict[str, GroupFairness] = {}
    for name, groups in sensitive.items():
        labels = pd.Series(groups).astype(str).reset_index(drop=True)
        counts = labels[~labels.str.lower().isin(DROP_TOKENS)].value_counts()
        keep = set(counts[counts >= min_count].index)
        mask = labels.isin(keep).to_numpy()
        frame = MetricFrame(
            metrics={
                "selection_rate": selection_rate,
                "tpr": true_positive_rate,
                "fpr": false_positive_rate,
            },
            y_true=y_true_arr[mask],
            y_pred=y_pred_default[mask],
            sensitive_features=labels[mask],
        )
        by_group = frame.by_group
        approval = {str(g): 1.0 - float(rate) for g, rate in by_group["selection_rate"].items()}
        max_appr, min_appr = max(approval.values()), min(approval.values())
        report[name] = GroupFairness(
            by_group=by_group,
            approval_rate=approval,
            demographic_parity_diff=float(
                demographic_parity_difference(
                    y_true_arr[mask], y_pred_default[mask], sensitive_features=labels[mask]
                )
            ),
            equalized_odds_diff=float(
                equalized_odds_difference(
                    y_true_arr[mask], y_pred_default[mask], sensitive_features=labels[mask]
                )
            ),
            disparate_impact=(min_appr / max_appr if max_appr > 0 else float("nan")),
        )
    return thr, report
