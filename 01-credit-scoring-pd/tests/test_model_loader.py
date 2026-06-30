"""Тест локальной загрузки модели (ml): joblib-ветка model_loader без MLflow."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("lightgbm")

import joblib  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from lightgbm import LGBMClassifier  # noqa: E402

from pd_scoring.config import Settings  # noqa: E402
from pd_scoring.service.model_loader import load_scoring_service  # noqa: E402


@pytest.mark.ml
def test_load_from_local_joblib(tmp_path: Path) -> None:
    rng = np.random.default_rng(0)
    n = 300
    frame = pd.DataFrame({"EXT_SOURCE_2": rng.random(n), "AMT_CREDIT": rng.normal(5e5, 1e5, n)})
    y = (frame["EXT_SOURCE_2"] < 0.5).astype(int)
    model = LGBMClassifier(n_estimators=20, num_leaves=7, random_state=42, verbose=-1).fit(frame, y)

    model_path = tmp_path / "model.joblib"
    joblib.dump(model, model_path)
    schema_path = tmp_path / "feature_schema.json"
    schema_path.write_text(
        json.dumps(
            {
                "features": [
                    {"name": "EXT_SOURCE_2", "dtype": "Float64", "description": "скор 2"},
                    {"name": "AMT_CREDIT", "dtype": "Float64", "description": "кредит"},
                ]
            }
        ),
        encoding="utf-8",
    )

    settings = Settings(model_uri=str(model_path), model_version_label="test", _env_file=None)
    service = load_scoring_service(settings, schema_path=schema_path)

    assert service.model_version == "test"  # локальная ветка, без mlflow
    out = service.score({"EXT_SOURCE_2": 0.1, "AMT_CREDIT": 600000})
    assert 0.0 <= out.pd <= 1.0
    assert out.segment in ("low", "medium", "high")
    assert out.reason_codes
