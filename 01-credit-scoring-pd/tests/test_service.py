"""Smoke-тесты HTTP-сервиса."""

from __future__ import annotations

from fastapi.testclient import TestClient

from pd_scoring import __version__


def test_healthz_ok(client: TestClient) -> None:
    """GET /healthz отвечает 200; без загруженной модели — статус degraded."""
    response = client.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in ("ok", "degraded")  # degraded, пока модель не загружена
    assert body["version"] == __version__
    assert "model_loaded" in body
