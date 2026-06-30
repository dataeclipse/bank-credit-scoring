"""Данные для моделирования: витрина фичей + фиксированный split из Фазы 1.

Берём ТОЛЬКО размеченные строки (inner-join со split.parquet). Таргет не пересобираем,
split (seed 42) не трогаем — train/holdout одни и те же для всех моделей.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from pd_scoring.config import get_settings

NON_FEATURES = ("SK_ID_CURR", "TARGET", "is_train", "split")


@dataclass(frozen=True)
class ModelingData:
    """Train/holdout матрицы + списки фич и категориальных колонок."""

    X_train: pd.DataFrame
    y_train: pd.Series
    X_holdout: pd.DataFrame
    y_holdout: pd.Series
    feature_names: list[str]
    categorical_features: list[str]


def load_modeling_data(processed_dir: Path | None = None) -> ModelingData:
    """Загрузить mart + split, вернуть train/holdout (только размеченные клиенты)."""
    settings = get_settings()
    pdir = processed_dir if processed_dir is not None else settings.data_dir / "processed"
    mart = pd.read_parquet(pdir / "mart.parquet")
    split = pd.read_parquet(pdir / "split.parquet")
    df = mart.merge(split, on="SK_ID_CURR", how="inner")

    features = [c for c in mart.columns if c not in NON_FEATURES]
    categorical = [c for c in features if not pd.api.types.is_numeric_dtype(df[c])]

    train = df[df["split"] == "train"].reset_index(drop=True)
    holdout = df[df["split"] == "test"].reset_index(drop=True)
    return ModelingData(
        X_train=train[features],
        y_train=train["TARGET"].astype(int),
        X_holdout=holdout[features],
        y_holdout=holdout["TARGET"].astype(int),
        feature_names=features,
        categorical_features=categorical,
    )
