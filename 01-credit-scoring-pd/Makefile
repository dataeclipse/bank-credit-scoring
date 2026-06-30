.DEFAULT_GOAL := help
.PHONY: help install install-ml fmt lint type test run ingest download features eda

help:  ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install:  ## Install core + dev + data layer (Phase 1)
	uv sync --extra data

install-ml:  ## Install everything, including the heavy ML stack (Phase 2+)
	uv sync --extra ml

fmt:  ## Format and auto-fix
	uv run ruff format .
	uv run ruff check --fix .

lint:  ## Lint (ruff check + format --check)
	uv run ruff check .
	uv run ruff format --check .

type:  ## Type check (mypy strict)
	uv run mypy src

test:  ## Tests with coverage
	uv run pytest

run:  ## Run the service locally
	uv run uvicorn pd_scoring.service.app:app --reload --port 8000

ingest:  ## Home Credit data manifest (dry-run; to actually download: make download)
	uv run python -m pd_scoring.data.download

download:  ## Download Home Credit data (Kaggle API; ~2.7 GB CSV)
	uv run python -m pd_scoring.data.download --yes

features:  ## Build client-level feature mart (parquet + schema + dictionary + split)
	uv run python -m pd_scoring.features.build_mart

eda:  ## Run the EDA notebook (output with numbers and charts)
	uv run jupyter nbconvert --to notebook --execute --inplace notebooks/01_eda.ipynb
