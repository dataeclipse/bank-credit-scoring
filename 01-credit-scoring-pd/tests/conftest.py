"""Общие фикстуры pytest."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from pd_scoring.service.app import app


@pytest.fixture
def client() -> TestClient:
    """HTTP-клиент для FastAPI-приложения."""
    return TestClient(app)
