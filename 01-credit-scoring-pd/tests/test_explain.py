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
    assert first == second
    assert first[0][0] == "strong"


@pytest.mark.explain
def test_reason_codes_balanced_and_directioned() -> None:
    columns = ["a", "b", "c", "d"]
    values = [0.5, 0.3, -0.4, -0.1]
    codes = reason_codes_from_shap(columns, values, {}, top_n=2)
    increasing = [c for c in codes if c.direction == "increases"]
    decreasing = [c for c in codes if c.direction == "decreases"]
    assert len(increasing) == 2 and len(decreasing) == 2
    assert increasing[0].feature == "a"
    assert decreasing[0].feature == "c"
    assert all(c.direction in ("increases", "decreases") for c in codes)


@pytest.mark.explain
def test_reason_codes_ext_source_humanized_with_value() -> None:
    codes = reason_codes_from_shap(
        ["EXT_SOURCE_3"],
        [0.8],
        {"EXT_SOURCE_3": "external score 3"},
        top_n=1,
        feature_values={"EXT_SOURCE_3": 0.15},
    )
    code = codes[0]
    assert "source 3" in code.description
    assert "0.15" in code.description
    assert code.direction == "increases"


@pytest.mark.explain
def test_reason_codes_real_model_has_direction() -> None:
    model, frame = _model_and_features()
    codes = reason_codes(model, frame.iloc[[0]], {"strong": "strong", "weak": "weak"}, top_n=2)
    assert codes
    assert all(c.direction in ("increases", "decreases") for c in codes)
