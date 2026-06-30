"""SHAP-объяснимость прод-LightGBM: глобальная важность + локальные reason codes.

Reason codes — человекочитаемые топ-факторы «за/против» по конкретной заявке: знак SHAP
показывает направление (повышает/снижает риск), описание берётся из словаря фич.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import shap

from pd_scoring.scoring import ReasonCode


def load_feature_descriptions(schema_path: Path) -> dict[str, str]:
    """Маппинг имя_фичи → человекочитаемое описание из feature_schema.json."""
    payload = json.loads(schema_path.read_text(encoding="utf-8"))
    return {feature["name"]: feature["description"] for feature in payload["features"]}


def _extract(values: Any) -> Any:
    """Привести вывод TreeExplainer к матрице (n_samples, n_features) для класса 1."""
    if isinstance(values, list):  # старый API: список по классам
        values = values[1]
    values = np.asarray(values)
    if values.ndim == 3:  # (n, features, classes)
        values = values[:, :, -1]
    return values


def shap_values(model: Any, features: pd.DataFrame) -> Any:
    """SHAP-значения класса 1 (создаёт TreeExplainer; для офлайн-анализа)."""
    return _extract(shap.TreeExplainer(model).shap_values(features))


def shap_values_with(explainer: Any, features: pd.DataFrame) -> Any:
    """SHAP-значения через уже созданный explainer (для serving — без пересоздания)."""
    return _extract(explainer.shap_values(features))


def global_importance(model: Any, features: pd.DataFrame) -> list[tuple[str, float]]:
    """Глобальная важность фич = mean(|SHAP|), убыванию."""
    mean_abs = np.abs(shap_values(model, features)).mean(axis=0)
    pairs = zip(list(features.columns), mean_abs, strict=False)
    return sorted(((str(c), float(v)) for c, v in pairs), key=lambda t: t[1], reverse=True)


def reason_codes_from_shap(
    columns: list[str], values: Any, descriptions: dict[str, str], *, top_n: int = 5
) -> list[ReasonCode]:
    """Собрать reason codes из SHAP-значений одной заявки (без вызова explainer)."""
    ranked = sorted(zip(columns, values, strict=False), key=lambda t: abs(t[1]), reverse=True)[
        :top_n
    ]
    codes: list[ReasonCode] = []
    for feature, contribution in ranked:
        feature = str(feature)
        direction = "повышает риск" if contribution > 0 else "снижает риск"
        codes.append(
            ReasonCode(
                feature=feature,
                contribution=float(contribution),
                description=f"{descriptions.get(feature, feature)} — {direction}",
            )
        )
    return codes


def reason_codes(
    model: Any, application: pd.DataFrame, descriptions: dict[str, str], *, top_n: int = 5
) -> list[ReasonCode]:
    """Топ-N reason codes по одной заявке (1-строчный DataFrame; офлайн-путь)."""
    values = shap_values(model, application)[0]
    return reason_codes_from_shap(list(application.columns), values, descriptions, top_n=top_n)
