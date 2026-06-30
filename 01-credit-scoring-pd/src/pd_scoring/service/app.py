"""FastAPI-сервис скоринга: POST /score, GET /healthz, GET /metrics.

Модель грузится из MLflow registry на старте (lifespan) в app.state. Тяжёлый стек (mlflow/
lightgbm/shap) подтягивается только при загрузке модели — API-скелет на core-зависимостях.
"""

from __future__ import annotations

import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import Depends, FastAPI, HTTPException, Request, Response

from pd_scoring import __version__
from pd_scoring.config import get_settings
from pd_scoring.logging_config import get_logger
from pd_scoring.service.metrics import (
    PD_HISTOGRAM,
    SCORE_LATENCY,
    SCORE_REQUESTS,
    metrics_payload,
)
from pd_scoring.service.schemas import ApplicationIn, ScoreOut

if TYPE_CHECKING:
    from pd_scoring.service.scoring_service import ScoringService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Загрузить прод-модель из registry на старте (best-effort)."""
    log = get_logger("service")
    try:
        from pd_scoring.service.model_loader import load_scoring_service

        app.state.service = load_scoring_service(get_settings())
        log.info("model_loaded", version=app.state.service.model_version)
    except Exception as exc:
        app.state.service = None
        log.error("model_load_failed", error=str(exc))
    yield


app = FastAPI(title="PD Scoring Service", version=__version__, lifespan=lifespan)


def get_service(request: Request) -> ScoringService:
    """Достать загруженный ScoringService или вернуть 503."""
    service: ScoringService | None = getattr(request.app.state, "service", None)
    if service is None:
        raise HTTPException(status_code=503, detail="model not loaded")
    return service


@app.post("/score", response_model=ScoreOut)
def score(application: ApplicationIn, service: ScoringService = Depends(get_service)) -> ScoreOut:
    """Скоринг заявки: PD, балл, риск-сегмент, топ-3 reason codes."""
    start = time.perf_counter()
    try:
        result = service.score(application.model_dump())
        SCORE_REQUESTS.labels(status="ok").inc()
        PD_HISTOGRAM.observe(result.pd)
        return result
    except Exception:
        SCORE_REQUESTS.labels(status="error").inc()
        raise
    finally:
        SCORE_LATENCY.observe(time.perf_counter() - start)


@app.get("/healthz")
def healthz(request: Request) -> dict[str, object]:
    """Готовность сервиса + версия загруженной модели."""
    service = getattr(request.app.state, "service", None)
    return {
        "status": "ok" if service is not None else "degraded",
        "model_loaded": service is not None,
        "model_version": service.model_version if service is not None else None,
        "version": __version__,
    }


@app.get("/metrics")
def metrics() -> Response:
    """Prometheus-метрики."""
    payload, content_type = metrics_payload()
    return Response(content=payload, media_type=content_type)
