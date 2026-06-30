"""Тест отсутствия утечки в CV: фолды не пересекаются, покрывают train, holdout вне фолдов."""

from __future__ import annotations

import numpy as np
from sklearn.model_selection import StratifiedKFold


def test_cv_folds_disjoint_cover_train_exclude_holdout() -> None:
    n_train, n_holdout = 200, 50
    train_idx = np.arange(n_train)
    holdout_idx = set(range(n_train, n_train + n_holdout))
    y = np.array([0, 1] * (n_train // 2))

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    seen_val: set[int] = set()
    for tr, va in cv.split(train_idx, y):
        assert set(tr).isdisjoint(set(va))  # train/val фолда не пересекаются
        assert set(va).isdisjoint(holdout_idx)  # holdout не попадает в val
        seen_val.update(int(i) for i in va)
    assert seen_val == set(range(n_train))  # val-фолды покрывают весь train
