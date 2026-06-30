"""CLI-запуск сервиса (console-script ``pd-scoring-serve``)."""

from __future__ import annotations

import uvicorn

from pd_scoring.config import get_settings


def serve() -> None:
    """Запустить FastAPI-сервис через uvicorn."""
    settings = get_settings()
    uvicorn.run(
        "pd_scoring.service.app:app",
        host="0.0.0.0",  # контейнерный сервис слушает все интерфейсы
        port=8000,
        log_level=settings.log_level.lower(),
    )
