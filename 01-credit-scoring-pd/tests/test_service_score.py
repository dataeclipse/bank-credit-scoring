from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from pd_scoring.service.app import app, get_service
from pd_scoring.service.schemas import ReasonCodeOut, ScoreOut

_VALID = {
    "AMT_INCOME_TOTAL": 150000,
    "AMT_CREDIT": 600000,
    "DAYS_BIRTH": -12000,
    "CODE_GENDER": "M",
    "EXT_SOURCE_2": 0.5,
}


class _StubService:
    model_version = "test"

    def score(self, app_dict: dict[str, Any]) -> ScoreOut:
        return ScoreOut(
            pd=0.12,
            score=640,
            segment="medium",
            reason_codes=[
                ReasonCodeOut(
                    feature="EXT_SOURCE_2",
                    contribution=-0.1,
                    direction="decreases",
                    description="external score (source 2) = 0.5 - decreases risk",
                )
            ],
            model_version="test",
        )


@pytest.fixture
def client() -> Iterator[TestClient]:
    app.dependency_overrides[get_service] = _StubService
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_score_valid(client: TestClient) -> None:
    response = client.post("/score", json=_VALID)
    assert response.status_code == 200
    body = response.json()
    assert 0.0 <= body["pd"] <= 1.0
    assert body["segment"] in ("low", "medium", "high")
    assert len(body["reason_codes"]) >= 1
    assert body["reason_codes"][0]["direction"] in ("increases", "decreases")
    assert body["model_version"] == "test"


def test_score_rejects_positive_days_birth(client: TestClient) -> None:
    bad = {**_VALID, "DAYS_BIRTH": 12000}
    assert client.post("/score", json=bad).status_code == 422


def test_score_rejects_bad_gender(client: TestClient) -> None:
    bad = {**_VALID, "CODE_GENDER": "X"}
    assert client.post("/score", json=bad).status_code == 422


def test_score_rejects_ext_source_out_of_range(client: TestClient) -> None:
    bad = {**_VALID, "EXT_SOURCE_2": 1.5}
    assert client.post("/score", json=bad).status_code == 422


def test_score_rejects_unknown_field(client: TestClient) -> None:
    bad = {**_VALID, "UNKNOWN_FIELD": 1}
    assert client.post("/score", json=bad).status_code == 422


def test_healthz(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert "version" in response.json()
