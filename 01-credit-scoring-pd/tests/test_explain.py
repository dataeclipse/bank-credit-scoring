"""Тесты SHAP-объяснимости (маркер explain): детерминизм + структура reason codes."""

from __future__ import annotations

import pytest

pytest.importorskip("shap")
pytest.importorskip("lightgbm")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from lightgbm import LGBMClassifier  # noqa: E402

from pd_scoring.models.explain import global_importance, reason_codes  # noqa: E402


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
def test_reason_codes_structure() -> None:
    model, frame = _model_and_features()
    descriptions = {"strong": "сильный фактор", "weak": "слабый фактор"}
    codes = reason_codes(model, frame.iloc[[0]], descriptions, top_n=2)
    assert len(codes) == 2
    assert all(isinstance(code.contribution, float) for code in codes)
    assert any(word in codes[0].description for word in ("повышает риск", "снижает риск"))
