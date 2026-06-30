from __future__ import annotations

from dataclasses import dataclass

import polars as pl
from sklearn.model_selection import train_test_split

from pd_scoring.config import get_settings


@dataclass(frozen=True)
class SplitResult:
    seed: int
    test_size: float
    train_ids: list[int]
    test_ids: list[int]

    @property
    def n_train(self) -> int:
        return len(self.train_ids)

    @property
    def n_test(self) -> int:
        return len(self.test_ids)


def make_split(
    labels: pl.DataFrame,
    *,
    id_col: str = "SK_ID_CURR",
    target_col: str = "TARGET",
    test_size: float = 0.2,
    seed: int | None = None,
) -> SplitResult:
    resolved_seed = seed if seed is not None else get_settings().random_seed
    labeled = labels.filter(pl.col(target_col).is_not_null())
    ids = labeled[id_col].to_list()
    targets = labeled[target_col].to_list()
    train_ids, test_ids = train_test_split(
        ids, test_size=test_size, random_state=resolved_seed, stratify=targets
    )
    return SplitResult(resolved_seed, test_size, sorted(train_ids), sorted(test_ids))
