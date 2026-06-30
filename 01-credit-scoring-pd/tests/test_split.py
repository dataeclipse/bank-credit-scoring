from __future__ import annotations

import polars as pl

from pd_scoring.data.split import make_split


def _labeled(n: int, n_unlabeled: int = 0) -> pl.DataFrame:
    ids: list[int] = list(range(1, n + 1))
    target: list[int | None] = [i % 2 for i in range(n)]
    if n_unlabeled:
        ids += list(range(n + 1, n + 1 + n_unlabeled))
        target += [None] * n_unlabeled
    return pl.DataFrame({"SK_ID_CURR": ids, "TARGET": target})


def test_split_deterministic() -> None:
    df = _labeled(100)
    first = make_split(df, seed=42)
    second = make_split(df, seed=42)
    assert first.train_ids == second.train_ids
    assert first.test_ids == second.test_ids


def test_split_disjoint_and_complete() -> None:
    df = _labeled(100)
    result = make_split(df, seed=42, test_size=0.2)
    train, test = set(result.train_ids), set(result.test_ids)
    assert train.isdisjoint(test)
    assert train | test == set(range(1, 101))
    assert result.n_test == 20


def test_split_excludes_unlabeled() -> None:
    df = _labeled(100, n_unlabeled=10)
    result = make_split(df, seed=42)
    all_ids = set(result.train_ids) | set(result.test_ids)
    assert all_ids == set(range(1, 101))


def test_split_stratified() -> None:
    df = _labeled(100)
    result = make_split(df, seed=42, test_size=0.2)
    train_df = df.filter(pl.col("SK_ID_CURR").is_in(result.train_ids))
    rate = train_df.select(pl.col("TARGET").mean()).item()
    assert abs(rate - 0.5) < 0.05


def test_split_different_seed() -> None:
    df = _labeled(100)
    assert make_split(df, seed=1).train_ids != make_split(df, seed=2).train_ids
