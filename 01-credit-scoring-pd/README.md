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
make install          # uv sync (core + dev); или: uv sync
make lint             # ruff;        или: uv run ruff check . && uv run ruff format --check .
make type             # mypy strict; или: uv run mypy src
make test             # pytest;      или: uv run pytest
make run              # сервис на :8000; затем curl http://localhost:8000/healthz
```
Нет `make` (Windows)? Запускай команды из правой колонки напрямую через `uv run`.
Тяжёлый ML-стек (Фаза 1+): `make install-ml` (`uv sync --extra ml`).

## Results
`TODO` (Фаза 2+): таблица банковских метрик (Gini/KS/ROC-AUC/PR-AUC) для scorecard vs GBDT,
reliability curve, пример reason codes, дашборд дрейфа.

## Model card
См. [docs/model_card.md](docs/model_card.md) — назначение, данные, метрики, калибровка,
объяснимость, fairness, ограничения, требования к мониторингу (НБРК/SR 11-7).

## Roadmap
| Фаза | Содержание |
|---|---|
| 0 ✅ | Скелет: структура, uv/pyproject, ruff/mypy/pytest/pre-commit, CI, `/healthz` |
| 1 | Данные и витрина фичей (Home Credit, агрегации без утечек, EDA, split+seed) |
| 2 | Две модели: WOE-scorecard + GBDT, метрики, MLflow, выбор в прод |
| 3 | Калибровка + SHAP reason codes + fairness (Fairlearn) |
| 4 | Сервис `/score` + Evidently PSI/CSI дрейф + нагрузочный тест |
| 5 | Прод: Docker/compose, CI/CD, полная model card, демо |

## License
[MIT](../LICENSE).
