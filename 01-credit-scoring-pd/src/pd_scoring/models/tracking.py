"""MLflow: sqlite-бэкенд (нужен для Model Registry), логирование и регистрация кандидатов."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import joblib
import mlflow
import mlflow.catboost
import mlflow.lightgbm
import mlflow.pyfunc

from pd_scoring.config import Settings

DEFAULT_TRACKING_URI = "sqlite:///mlflow.db"


def setup_mlflow(settings: Settings) -> None:
    """Настроить tracking URI (sqlite по умолчанию — иначе registry недоступен) и эксперимент."""
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri or DEFAULT_TRACKING_URI)
    mlflow.set_experiment(settings.mlflow_experiment)


def _flatten(metrics: dict[str, dict[str, float]]) -> dict[str, float]:
    """{'holdout': {...}, 'cv': {...}} → {'holdout_roc_auc': ..., 'cv_gini': ...}."""
    return {
        f"{group}_{name}": value
        for group, block in metrics.items()
        for name, value in block.items()
    }


def _log_model(log_fn: Callable[..., Any], model: Any, registered_name: str | None) -> None:
    """Совместимость API mlflow 2/3: name= (3.x) с откатом на artifact_path= (2.x)."""
    try:
        log_fn(model, name="model", registered_model_name=registered_name)
    except TypeError:
        log_fn(model, artifact_path="model", registered_model_name=registered_name)


class ScorecardModel(mlflow.pyfunc.PythonModel):  # type: ignore[misc,name-defined]
    """pyfunc-обёртка scorecard → вероятность дефолта (для регистрации в registry)."""

    def load_context(self, context: Any) -> None:
        self._model = joblib.load(context.artifacts["scorecard"])

    def predict(self, context: Any, model_input: Any, params: Any = None) -> Any:
        return self._model.predict_proba(model_input)[:, 1]


def log_candidate(
    *,
    run_name: str,
    flavor: str,
    model: Any,
    params: dict[str, Any],
    metrics: dict[str, dict[str, float]],
    artifacts: list[Path],
    scorecard_path: Path | None = None,
    register: bool = True,
) -> None:
    """Залогировать один кандидат (params/metrics/artifacts) и зарегистрировать в registry."""
    registered = f"pd-{run_name}" if register else None
    with mlflow.start_run(run_name=run_name):
        mlflow.log_params(params)
        mlflow.log_metrics(_flatten(metrics))
        for path in artifacts:
            if path.exists():
                mlflow.log_artifact(str(path))
        if flavor == "lightgbm":
            _log_model(mlflow.lightgbm.log_model, model, registered)
        elif flavor == "catboost":
            _log_model(mlflow.catboost.log_model, model, registered)
        elif flavor == "scorecard" and scorecard_path is not None:
            mlflow.pyfunc.log_model(
                name="model",
                python_model=ScorecardModel(),
                artifacts={"scorecard": str(scorecard_path)},
                registered_model_name=registered,
                pip_requirements=["optbinning", "scikit-learn", "pandas"],
            )
