from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import polars as pl


SCHEMA_VERSION = 1


NON_FEATURE_COLUMNS = ("SK_ID_CURR", "TARGET", "is_train")


@dataclass(frozen=True)
class FeatureDoc:
    name: str
    source: str
    dtype: str
    description: str


def feature_columns(mart: pl.DataFrame) -> list[str]:
    return [c for c in mart.columns if c not in NON_FEATURE_COLUMNS]


def build_feature_schema(mart: pl.DataFrame, docs: list[FeatureDoc]) -> dict[str, Any]:
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_data_dictionary(payload: dict[str, Any], path: Path) -> None:
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
