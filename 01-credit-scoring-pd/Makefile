.DEFAULT_GOAL := help
.PHONY: help install install-ml fmt lint type test run ingest download features eda

help:  ## Показать доступные таргеты
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install:  ## Установить core + dev + слой данных (Фаза 1)
	uv sync --extra data

install-ml:  ## Установить всё, включая тяжёлый ML-стек (Фаза 2+)
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

ingest:  ## Манифест данных Home Credit (dry-run; реально качать: make download)
	uv run python -m pd_scoring.data.download

download:  ## Скачать данные Home Credit (Kaggle API; ~2.7 GB CSV)
	uv run python -m pd_scoring.data.download --yes

features:  ## Собрать client-level витрину фичей (parquet + схема + словарь + split)
	uv run python -m pd_scoring.features.build_mart

eda:  ## Выполнить EDA-ноутбук (вывод с числами и графиками)
	uv run jupyter nbconvert --to notebook --execute --inplace notebooks/01_eda.ipynb
