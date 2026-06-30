"""Тесты банковских метрик (data-слой, без ml-стека)."""

from __future__ import annotations

import numpy as np

from pd_scoring.models.metrics import evaluate, gini, ks_statistic, pr_auc, roc_auc


def test_perfect_separation() -> None:
    y = np.array([0, 0, 0, 1, 1, 1])
    p = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])
    assert roc_auc(y, p) == 1.0
    assert gini(y, p) == 1.0
    assert ks_statistic(y, p) > 0.999
    metrics = evaluate(y, p)
    assert metrics["roc_auc"] == 1.0
    assert metrics["gini"] == 1.0


def test_random_scores_near_half() -> None:
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, size=2000)
    p = rng.random(2000)
    assert abs(roc_auc(y, p) - 0.5) < 0.06
    assert abs(gini(y, p)) < 0.12


def test_pr_auc_in_unit_interval() -> None:
    y = np.array([0, 1, 0, 1])
    p = np.array([0.2, 0.8, 0.3, 0.7])
    assert 0.0 <= pr_auc(y, p) <= 1.0
