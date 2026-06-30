.DEFAULT_GOAL := help
.PHONY: help install install-ml fmt lint type test run ingest

help:  ## Показать доступные таргеты
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install:  ## Установить core + dev (без тяжёлого ML-стека)
	uv sync

install-ml:  ## Установить всё, включая ML-стек (Фаза 1+)
	uv sync --extra ml

fmt:  ## Форматировать и автофиксить
	uv run ruff format .
	uv run ruff check --fix .

lint:  ## Линт (ruff check + format --check)
	uv run ruff check .
	uv run ruff format --check .

type:  ## Проверка типов (mypy strict)
	uv run mypy src

test:  ## Тесты с покрытием
	uv run pytest

run:  ## Запустить сервис локально
	uv run uvicorn pd_scoring.service.app:app --reload --port 8000

ingest:  ## Загрузка данных Home Credit (Фаза 1 — пока заглушка)
	uv run python -m pd_scoring.data.ingest
