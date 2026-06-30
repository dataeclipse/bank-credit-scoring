from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pd_scoring.config import Settings
from pd_scoring.service.scoring_service import ScoringService


def _schema(path: Path) -> tuple[dict[str, str], list[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    descriptions = {f["name"]: f["description"] for f in payload["features"]}
    categorical = [f["name"] for f in payload["features"] if f["dtype"] == "String"]
    return descriptions, categorical


def _load_model(settings: Settings) -> tuple[Any, str]:
    if settings.model_uri:
        import joblib

        return joblib.load(settings.model_uri), settings.model_version_label

    import mlflow
    from mlflow import MlflowClient

    uri = settings.mlflow_tracking_uri or "sqlite:///mlflow.db"
    mlflow.set_tracking_uri(uri)
    model = mlflow.lightgbm.load_model(f"models:/{settings.model_name}@{settings.model_alias}")
    version = (
        MlflowClient(tracking_uri=uri)
        .get_model_version_by_alias(settings.model_name, settings.model_alias)
        .version
    )
    return model, str(version)


def load_scoring_service(
    settings: Settings, *, schema_path: Path = Path("docs/feature_schema.json")
) -> ScoringService:
    model, version = _load_model(settings)

    calibrator = None
    if settings.use_calibrator:
        import joblib

        path = settings.model_dir / "calibrator_isotonic.joblib"
        if path.exists():
            calibrator = joblib.load(path)

    descriptions, categorical = _schema(schema_path)
    return ScoringService(
        model=model,
        calibrator=calibrator,
        feature_order=list(model.feature_name_),
        categorical=categorical,
        descriptions=descriptions,
        settings=settings,
        model_version=version,
    )
