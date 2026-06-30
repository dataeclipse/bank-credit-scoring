"""Locust-нагрузочный тест POST /score.

Запуск: uv run --extra loadtest locust -f loadtest/locustfile.py --headless \
  -u 20 -r 5 -t 30s --host http://localhost:8000
"""

from __future__ import annotations

import random
from typing import Any

from locust import HttpUser, between, task

_GENDERS = ["M", "F"]
_EDUCATION = ["Secondary / secondary special", "Higher education", "Incomplete higher"]


def _payload() -> dict[str, Any]:
    income = random.choice([90000, 120000, 150000, 200000, 270000])
    credit = income * random.uniform(2.0, 6.0)
    return {
        "AMT_INCOME_TOTAL": income,
        "AMT_CREDIT": round(credit, 1),
        "AMT_ANNUITY": round(credit / random.uniform(10, 40), 1),
        "AMT_GOODS_PRICE": round(credit * random.uniform(0.8, 1.0), 1),
        "DAYS_BIRTH": -random.randint(7500, 24000),
        "DAYS_EMPLOYED": -random.randint(100, 8000),
        "CODE_GENDER": random.choice(_GENDERS),
        "CNT_CHILDREN": random.randint(0, 3),
        "CNT_FAM_MEMBERS": float(random.randint(1, 5)),
        "EXT_SOURCE_1": round(random.random(), 3),
        "EXT_SOURCE_2": round(random.random(), 3),
        "EXT_SOURCE_3": round(random.random(), 3),
        "NAME_EDUCATION_TYPE": random.choice(_EDUCATION),
        "REGION_RATING_CLIENT": random.randint(1, 3),
    }


class ScoreUser(HttpUser):
    """Пользователь, дёргающий /score случайными валидными заявками."""

    wait_time = between(0.0, 0.05)

    @task
    def score(self) -> None:
        self.client.post("/score", json=_payload())
