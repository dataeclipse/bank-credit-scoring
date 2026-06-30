from __future__ import annotations

import uvicorn

from pd_scoring.config import get_settings


def serve() -> None:
    settings = get_settings()
    uvicorn.run(
        "pd_scoring.service.app:app",
        host="0.0.0.0",
        port=8000,
        log_level=settings.log_level.lower(),
    )
