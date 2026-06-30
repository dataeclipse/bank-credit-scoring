# Credit Scoring (PD) as a Service

Сервис оценки **вероятности дефолта (PD)** по кредитной заявке: REST-эндпоинт принимает
заявку → возвращает PD, скоринговый балл, риск-сегмент и **топ-причины решения** (SHAP reason
codes). Помимо модели — WOE/scorecard рядом с градиентным бустингом, **калибровка вероятностей**,
**fairness-анализ**, **мониторинг дрейфа (PSI/CSI)** и **model card** в духе банковской
валидации (НБРК / SR 11-7).

> **Статус: Фаза 0 (скелет).** Готов production-каркас (структура, тулинг, CI, `/healthz`).
> Модели и бизнес-логика — в фазах 1–5 (см. [Roadmap](#roadmap)).

## Problem
Команды кредитных рисков банка оценивают PD по заявке, чтобы принять решение о выдаче. Нужна не
просто точная модель, а **защищаемая**: интерпретируемая (scorecard + reason codes), с корректной
вероятностью (калибровка), проверенная на справедливость (fairness) и с мониторингом стабильности
во времени (PSI/CSI) — ровно то, что спрашивают на валидации модели.

## Data
**Home Credit Default Risk** (Kaggle) — анонимизированные данные: заявки, кредитная история бюро,
предыдущие кредиты, платежи, баланс по картам. `data/` — в `.gitignore` (датасеты не коммитим);
загрузка — `make ingest` (Фаза 1). Креды Kaggle — через `KAGGLE_USERNAME`/`KAGGLE_KEY` или
`~/.kaggle/kaggle.json` (никогда не коммить).

## Architecture
```mermaid
flowchart TD
    A[Заявка + бюро + история] --> B[feature pipeline → витрина фичей]
    B --> C[WOE/IV + scorecard]
    B --> D[GBDT (LightGBM/CatBoost)]
    C --> E[Сравнение / выбор]
    D --> E
    E --> F[Калибровка → PD]
    F --> G[SHAP reason codes + риск-сегмент]
    G --> H[FastAPI /score]
    H --> I[MLflow registry]
    H --> J[Evidently: PSI/CSI, дрейф PD → алерты]
```

## How to run
Требуется [uv](https://docs.astral.sh/uv/). Из каталога `01-credit-scoring-pd/`:
```bash
make install          # uv sync --extra data (core + dev + слой данных)
make lint             # ruff;        или: uv run ruff check . && uv run ruff format --check .
make type             # mypy strict; или: uv run mypy src
make test             # pytest;      или: uv run pytest
make run              # сервис на :8000; затем curl http://localhost:8000/healthz
```
Данные и витрина фичей (Фаза 1; нужны Kaggle-креды в `.env` + принятые правила соревнования):
```bash
make ingest           # манифест данных (dry-run, показывает размеры)
make download         # скачать Home Credit (~2.5 GB, Kaggle API; data/ в .gitignore)
make features         # собрать client-level витрину → data/processed/mart.parquet + схема
make eda              # выполнить notebooks/01_eda.ipynb → docs/eda.md
```
Нет `make` (Windows)? Запускай команды напрямую через `uv run`.
Тяжёлый ML-стек (Фаза 2+): `make install-ml` (`uv sync --extra ml`).

## Results
**Фаза 1 — витрина фичей** (Home Credit, воспроизводимо из `make download && make features`):
- Витрина: **356 255** заявок × **120 фич** (curated application + engineered ratios + client-level
  агрегаты bureau/previous/installments/POS/credit_card). Словарь: [docs/data_dictionary.md](docs/data_dictionary.md),
  схема: [docs/feature_schema.json](docs/feature_schema.json).
- Баланс классов: **8.07%** дефолтов (24 825 / 307 511) — сильный дисбаланс (~1:11).
- Сильнейшие предикторы: **EXT_SOURCE_3/2/1** (corr с TARGET −0.18 / −0.16 / −0.16),
  утилизация кредитки и просрочки бюро. Аномалия `DAYS_EMPLOYED==365243` (18%) вынесена во флаг.
- Полный разбор: [docs/eda.md](docs/eda.md) + [notebooks/01_eda.ipynb](notebooks/01_eda.ipynb).

**Фаза 2+** `TODO`: банковские метрики (Gini/KS/ROC-AUC/PR-AUC) scorecard vs GBDT, reliability
curve, reason codes, дашборд дрейфа.

## Model card
См. [docs/model_card.md](docs/model_card.md) — назначение, данные, метрики, калибровка,
объяснимость, fairness, ограничения, требования к мониторингу (НБРК/SR 11-7).

## Roadmap
| Фаза | Содержание |
|---|---|
| 0 ✅ | Скелет: структура, uv/pyproject, ruff/mypy/pytest/pre-commit, CI, `/healthz` |
| 1 ✅ | Данные и витрина фичей (Home Credit, агрегации без утечек, EDA, split+seed) |
| 2 | Две модели: WOE-scorecard + GBDT, метрики, MLflow, выбор в прод |
| 3 | Калибровка + SHAP reason codes + fairness (Fairlearn) |
| 4 | Сервис `/score` + Evidently PSI/CSI дрейф + нагрузочный тест |
| 5 | Прод: Docker/compose, CI/CD, полная model card, демо |

## License
[MIT](../LICENSE).
