"""Тесты fairness-метрик (маркер explain): известная диспропорция → ожидаемые значения."""

from __future__ import annotations

import pytest

pytest.importorskip("fairlearn")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from pd_scoring.models.fairness import fairness_report, youden_threshold  # noqa: E402


@pytest.mark.explain
def test_fairness_full_disparity() -> None:
    n = 200
    group = pd.Series(["A"] * n + ["B"] * n)
    score = np.concatenate([np.full(n, 0.1), np.full(n, 0.9)])  # A одобряют, B отказывают
    y_true = np.concatenate([np.zeros(n), np.ones(n)]).astype(int)
    _, report = fairness_report(y_true, score, {"grp": group}, threshold=0.5)
    group_fairness = report["grp"]
    assert group_fairness.disparate_impact == 0.0  # approval A=1, B=0 → ratio 0
    assert group_fairness.demographic_parity_diff == 1.0


@pytest.mark.explain
def test_youden_threshold_in_unit_interval() -> None:
    y_true = np.array([0, 0, 1, 1])
    score = np.array([0.1, 0.4, 0.6, 0.9])
    threshold = youden_threshold(y_true, score)
    assert 0.0 <= threshold <= 1.0
