# syntax=docker/dockerfile:1
# Multi-stage, non-root, lean serve-стек (без mlflow/shap/numba/catboost).
# Контекст сборки — каталог проекта (01-credit-scoring-pd). Модель запекается в deploy/ (joblib).

# ---------- builder ----------
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Кэшируемый слой зависимостей (только serve-рантайм, без dev/ml/explain).
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --extra serve --no-dev --no-install-project

# Исходники + установка самого пакета.
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --extra serve --no-dev

# ---------- runtime ----------
FROM python:3.12-slim AS runtime

RUN useradd --create-home --uid 1000 appuser

WORKDIR /app
COPY --from=builder --chown=appuser:appuser /app /app

# Артефакты serving: схема фич (в git) + запечённая модель (deploy/ может быть пустой → degraded).
COPY --chown=appuser:appuser docs/feature_schema.json ./docs/feature_schema.json
COPY --chown=appuser:appuser deploy ./deploy

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PD_ENV=docker \
    PD_MODEL_URI=/app/deploy/model/model.joblib

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=3s --start-period=25s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/healthz').status==200 else 1)"

CMD ["uvicorn", "pd_scoring.service.app:app", "--host", "0.0.0.0", "--port", "8000"]
