"""Тесты SHAP-объяснимости (маркер explain): детерминизм + структура reason codes."""

from __future__ import annotations

import pytest

pytest.importorskip("shap")
pytest.importorskip("lightgbm")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from lightgbm import LGBMClassifier  # noqa: E402

from pd_scoring.models.explain import (  # noqa: E402
    global_importance,
    reason_codes,
    reason_codes_from_shap,
)


def _model_and_features() -> tuple[LGBMClassifier, pd.DataFrame]:
    rng = np.random.default_rng(0)
    n = 400
    strong = rng.normal(size=n)
    weak = rng.normal(size=n)
    y = (2 * strong + rng.normal(scale=0.3, size=n) > 0).astype(int)
    frame = pd.DataFrame({"strong": strong, "weak": weak})
    model = LGBMClassifier(n_estimators=50, num_leaves=8, random_state=42, verbose=-1)
    model.fit(frame, y)
    return model, frame


@pytest.mark.explain
def test_shap_deterministic_and_ranked() -> None:
    model, frame = _model_and_features()
    first = global_importance(model, frame)
    second = global_importance(model, frame)
    assert first == second  # TreeSHAP детерминирован
    assert first[0][0] == "strong"  # сильная фича важнее


@pytest.mark.explain
def test_reason_codes_balanced_and_directioned() -> None:
    # Контролируемые SHAP-значения: 2 за (+), 2 против (−).
    columns = ["a", "b", "c", "d"]
    values = [0.5, 0.3, -0.4, -0.1]
    codes = reason_codes_from_shap(columns, values, {}, top_n=2)
    increasing = [c for c in codes if c.direction == "increases"]
    decreasing = [c for c in codes if c.direction == "decreases"]
    assert len(increasing) == 2 and len(decreasing) == 2  # оба направления
    assert increasing[0].feature == "a"  # самый сильный «за» первым
    assert decreasing[0].feature == "c"  # самый сильный «против» первым
    assert all(c.direction in ("increases", "decreases") for c in codes)


@pytest.mark.explain
def test_reason_codes_ext_source_humanized_with_value() -> None:
    codes = reason_codes_from_shap(
        ["EXT_SOURCE_3"],
        [0.8],
        {"EXT_SOURCE_3": "внешний скоринговый балл 3"},
        top_n=1,
        feature_values={"EXT_SOURCE_3": 0.15},
    )
    code = codes[0]
    assert "источник 3" in code.description  # цифра — номер источника
    assert "0.15" in code.description  # значение фичи показано
    assert code.direction == "increases"


@pytest.mark.explain
def test_reason_codes_real_model_has_direction() -> None:
    model, frame = _model_and_features()
    codes = reason_codes(model, frame.iloc[[0]], {"strong": "сильный", "weak": "слабый"}, top_n=2)
    assert codes
    assert all(c.direction in ("increases", "decreases") for c in codes)
