"""Версионируемая схема витрины фичей + словарь данных.

Схема строится из реальных dtype собранной витрины и описаний фич (``FeatureDoc``),
поэтому артефакт всегда соответствует фактическим колонкам mart.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import polars as pl

# Версия схемы витрины. Поднимать при изменении набора/семантики фич.
SCHEMA_VERSION = 1

# Служебные колонки витрины — не являются фичами.
NON_FEATURE_COLUMNS = ("SK_ID_CURR", "TARGET", "is_train")


@dataclass(frozen=True)
class FeatureDoc:
    """Документация одной фичи: имя, источник, тип, человеческое описание."""

    name: str
    source: str
    dtype: str
    description: str


def feature_columns(mart: pl.DataFrame) -> list[str]:
    """Колонки-фичи витрины (без ключа/таргета/служебных)."""
    return [c for c in mart.columns if c not in NON_FEATURE_COLUMNS]


def build_feature_schema(mart: pl.DataFrame, docs: list[FeatureDoc]) -> dict[str, Any]:
    """Собрать payload схемы: версия, хэш набора фич, список фич с типами и описаниями."""
    doc_by_name = {d.name: d for d in docs}
    features: list[dict[str, str]] = []
    for name in feature_columns(mart):
        doc = doc_by_name.get(name)
        features.append(
            {
                "name": name,
                "dtype": str(mart.schema[name]),
                "source": doc.source if doc else "application",
                "description": doc.description if doc else "",
            }
        )
    names_blob = ",".join(sorted(f["name"] for f in features))
    return {
        "schema_version": SCHEMA_VERSION,
        "n_features": len(features),
        "features_hash": hashlib.sha256(names_blob.encode()).hexdigest()[:12],
        "features": features,
    }


def write_feature_schema(payload: dict[str, Any], path: Path) -> None:
    """Записать схему витрины в JSON (UTF-8, с отступами)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_data_dictionary(payload: dict[str, Any], path: Path) -> None:
    """Записать человекочитаемый словарь данных (Markdown-таблица)."""
    lines = [
        "# Data dictionary — витрина фичей PD-скоринга",
        "",
        f"Schema version: **{payload['schema_version']}** · "
        f"features: **{payload['n_features']}** · hash: `{payload['features_hash']}`",
        "",
        "| # | Фича | Тип | Источник | Описание |",
        "|---|------|-----|----------|----------|",
    ]
    for i, feat in enumerate(payload["features"], start=1):
        lines.append(
            f"| {i} | `{feat['name']}` | {feat['dtype']} "
            f"| {feat['source']} | {feat['description']} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
