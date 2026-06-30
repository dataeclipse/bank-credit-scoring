"""Детерминированный train/test split витрины (stratified по TARGET)."""

from __future__ import annotations

from dataclasses import dataclass

import polars as pl
from sklearn.model_selection import train_test_split

from pd_scoring.config import get_settings


@dataclass(frozen=True)
class SplitResult:
    """Результат разбиения: сид, доля теста и отсортированные списки SK_ID_CURR."""

    seed: int
    test_size: float
    train_ids: list[int]
    test_ids: list[int]

    @property
    def n_train(self) -> int:
        """Размер train."""
        return len(self.train_ids)

    @property
    def n_test(self) -> int:
        """Размер test."""
        return len(self.test_ids)


def make_split(
    labels: pl.DataFrame,
    *,
    id_col: str = "SK_ID_CURR",
    target_col: str = "TARGET",
    test_size: float = 0.2,
    seed: int | None = None,
) -> SplitResult:
    """Stratified hold-out по ``target_col``. Берём только размеченные строки (train-часть).

    Детерминизм: при фиксированном ``seed`` (по умолчанию из ``Settings.random_seed``)
    разбиение воспроизводимо. Утечки нет: строки без TARGET (application_test) исключаются,
    train и test не пересекаются.

    Time-aware вариант: при наличии даты заявки сортировать по ней и резать по временно́му
    порогу (train — раньше, test — позже), чтобы не подсматривать будущее. В Home Credit явной
    календарной даты нет (всё в относительных DAYS_*), поэтому используем stratified hold-out.
    """
    resolved_seed = seed if seed is not None else get_settings().random_seed
    labeled = labels.filter(pl.col(target_col).is_not_null())
    ids = labeled[id_col].to_list()
    targets = labeled[target_col].to_list()
    train_ids, test_ids = train_test_split(
        ids, test_size=test_size, random_state=resolved_seed, stratify=targets
    )
    return SplitResult(resolved_seed, test_size, sorted(train_ids), sorted(test_ids))
