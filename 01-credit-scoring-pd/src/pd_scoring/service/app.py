"""FastAPI-приложение сервиса скоринга.

В Фазе 0 реализован только healthcheck ``/healthz``. Боевой эндпоинт ``/score``
(заявка → PD, балл, риск-сегмент, топ-3 reason codes) появится в Фазе 4.
"""

from __future__ import annotations

from fastapi import FastAPI

from pd_scoring import __version__

app = FastAPI(title="PD Scoring Service", version=__version__)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Liveness-проба сервиса."""
    return {"status": "ok", "version": __version__}


# TODO(Phase 4): POST /score — pydantic-валидация заявки → PD, балл, сегмент, reason codes.
# TODO(Phase 4): GET /metrics — Prometheus-метрики и дрейф PD.
