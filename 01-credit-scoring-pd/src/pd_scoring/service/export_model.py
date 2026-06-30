from __future__ import annotations

import argparse
from pathlib import Path

import joblib

from pd_scoring.config import get_settings
from pd_scoring.logging_config import configure_logging, get_logger


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export champion model from MLflow registry to joblib."
    )
    parser.add_argument("--out", default="deploy/model", help="каталог для model.joblib")
    args = parser.parse_args(argv)

    configure_logging()
    log = get_logger("export_model")
    settings = get_settings()

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

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    model_path = out_dir / "model.joblib"
    joblib.dump(model, model_path)

    calibrator_src = settings.model_dir / "calibrator_isotonic.joblib"
    if calibrator_src.exists():
        joblib.dump(joblib.load(calibrator_src), out_dir / "calibrator_isotonic.joblib")

    log.info(
        "model_exported", path=str(model_path), version=str(version), features=model.n_features_in_
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
