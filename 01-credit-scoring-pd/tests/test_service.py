"""Smoke-тесты HTTP-сервиса."""

from __future__ import annotations

from fastapi.testclient import TestClient

from pd_scoring import __version__


def test_healthz_ok(client: TestClient) -> None:
    """GET /healthz отвечает 200 и корректным телом."""
    response = client.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == __version__
