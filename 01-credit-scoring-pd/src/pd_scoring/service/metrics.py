"""Prometheus-метрики сервиса скоринга."""

from __future__ import annotations

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

SCORE_REQUESTS = Counter("pd_score_requests_total", "Запросы /score", ["status"])
SCORE_LATENCY = Histogram(
    "pd_score_latency_seconds",
    "Латентность /score",
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
)
PD_HISTOGRAM = Histogram(
    "pd_predicted_probability",
    "Распределение предсказанного PD",
    buckets=(0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0),
)


def metrics_payload() -> tuple[bytes, str]:
    """Сериализованные метрики Prometheus + content-type."""
    return generate_latest(), CONTENT_TYPE_LATEST
