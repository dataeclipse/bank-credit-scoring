from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from pd_scoring.scoring import Direction, ReasonCode

_EXT_SOURCE_RE = re.compile(r"^EXT_SOURCE_(\d)$")


def _humanize(feature: str, description: str) -> str:
    match = _EXT_SOURCE_RE.match(feature)
    if match:
        return f"external score (source {match.group(1)})"
    return description


def _format_value(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)):
        numeric = float(value)
        if math.isnan(numeric):
            return None
        return f"{numeric:.0f}" if abs(numeric) >= 100 else f"{numeric:.3g}"
    return str(value)


def load_feature_descriptions(schema_path: Path) -> dict[str, str]:
    payload = json.loads(schema_path.read_text(encoding="utf-8"))
    return {feature["name"]: feature["description"] for feature in payload["features"]}


def _extract(values: Any) -> Any:
    if isinstance(values, list):
        values = values[1]
    values = np.asarray(values)
    if values.ndim == 3:
        values = values[:, :, -1]
    return values


def shap_values(model: Any, features: pd.DataFrame) -> Any:
    import shap

    return _extract(shap.TreeExplainer(model).shap_values(features))


def shap_values_with(explainer: Any, features: pd.DataFrame) -> Any:
    return _extract(explainer.shap_values(features))


def global_importance(model: Any, features: pd.DataFrame) -> list[tuple[str, float]]:
    mean_abs = np.abs(shap_values(model, features)).mean(axis=0)
    pairs = zip(list(features.columns), mean_abs, strict=False)
    return sorted(((str(c), float(v)) for c, v in pairs), key=lambda t: t[1], reverse=True)


def _make_code(
    feature: str,
    contribution: float,
    descriptions: dict[str, str],
    feature_values: dict[str, Any] | None,
) -> ReasonCode:
    direction: Direction = "increases" if contribution > 0 else "decreases"
    effect = "increases risk" if contribution > 0 else "decreases risk"
    human = _humanize(feature, descriptions.get(feature, feature))
    value_str = ""
    if feature_values is not None:
        formatted = _format_value(feature_values.get(feature))
        if formatted is not None:
            value_str = f" = {formatted}"
    return ReasonCode(
        feature=feature,
        contribution=float(contribution),
        direction=direction,
        description=f"{human}{value_str} - {effect}",
    )


def reason_codes_from_shap(
    columns: list[str],
    values: Any,
    descriptions: dict[str, str],
    *,
    top_n: int = 3,
    feature_values: dict[str, Any] | None = None,
) -> list[ReasonCode]:
    pairs = [(str(c), float(v)) for c, v in zip(columns, values, strict=False)]
    increasing = sorted((p for p in pairs if p[1] > 0), key=lambda t: t[1], reverse=True)[:top_n]
    decreasing = sorted((p for p in pairs if p[1] < 0), key=lambda t: t[1])[:top_n]
    return [
        _make_code(feature, contribution, descriptions, feature_values)
        for feature, contribution in [*increasing, *decreasing]
    ]


def reason_codes(
    model: Any, application: pd.DataFrame, descriptions: dict[str, str], *, top_n: int = 3
) -> list[ReasonCode]:
    values = shap_values(model, application)[0]
    feature_values = application.iloc[0].to_dict()
    return reason_codes_from_shap(
        list(application.columns), values, descriptions, top_n=top_n, feature_values=feature_values
    )
