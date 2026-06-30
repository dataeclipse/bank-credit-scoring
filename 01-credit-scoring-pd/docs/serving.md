# Serving — PD scoring API (Фаза 4)

FastAPI-сервис. Модель грузится из MLflow registry по алиасу `models:/pd-lightgbm@champion`
на старте (lifespan). Запуск: `make run` (или `uv run uvicorn pd_scoring.service.app:app`).

## Эндпоинты
| Метод | Путь | Назначение |
|---|---|---|
| POST | `/score` | заявка → PD, балл, риск-сегмент, топ-3 reason codes |
| GET | `/healthz` | готовность + версия загруженной модели |
| GET | `/metrics` | метрики Prometheus (запросы, латентность, распределение PD) |

## Контракт /score
Вход — **поля заявки** (application-level). Валидация диапазонов (pydantic): `EXT_SOURCE_*∈[0,1]`,
`AMT_*>0`, `DAYS_BIRTH<0`, `CODE_GENDER∈{M,F,XNA}`, неизвестные поля запрещены (`extra=forbid`).
Обязательные: `AMT_INCOME_TOTAL`, `AMT_CREDIT`, `DAYS_BIRTH`, `CODE_GENDER`.

> **Ограничение**: одна заявка не содержит агрегатов кредитной истории (bureau/previous/…).
> Сервис строит полную строку из 120 фич модели: переданные поля + engineered ratios, остальное —
> `null` (LightGBM обрабатывает нативно). Это «быстрый путь по данным заявки»; полный скоринг с
> историей бюро — батч/фичестор (вне Фазы 4).

### Пример запроса
```bash
curl -s -X POST http://localhost:8000/score -H 'Content-Type: application/json' -d '{
  "AMT_INCOME_TOTAL": 135000, "AMT_CREDIT": 600000, "AMT_ANNUITY": 27000,
  "DAYS_BIRTH": -14000, "DAYS_EMPLOYED": -1200, "CODE_GENDER": "M",
  "EXT_SOURCE_1": 0.12, "EXT_SOURCE_2": 0.18, "EXT_SOURCE_3": 0.15
}'
```

### Пример ответа
```json
{
  "pd": 0.436,
  "score": 336,
  "segment": "high",
  "reason_codes": [
    {"feature": "EXT_SOURCE_3", "contribution": 0.833, "description": "внешний скоринговый балл 3 — повышает риск"},
    {"feature": "EXT_SOURCE_2", "contribution": 0.566, "description": "внешний скоринговый балл 2 — повышает риск"},
    {"feature": "EXT_SOURCE_1", "contribution": 0.523, "description": "внешний скоринговый балл 1 — повышает риск"}
  ],
  "model_version": "3"
}
```
Невалидный вход (например `DAYS_BIRTH > 0`, `EXT_SOURCE_2 > 1`, неизвестное поле) → **422**.

## Балл и риск-сегмент
Балл — PDO/odds-шкала (config `score_base=600`, `score_pdo=50`, `score_base_odds=50`): выше балл = ниже риск.
Сегмент по PD: `< 0.05` → **low**, `< 0.15` → **medium**, иначе **high** (пороги в config).

## Reason codes
LightGBM native TreeSHAP (`pred_contrib`) — топ-3 фактора по |вкладу|; знак = направление влияния
на риск; описание — из `feature_schema.json`.

## Латентность
См. [load_test.md](load_test.md): одиночный запрос p50 ≈ 83 мс, p95 ≈ 86 мс.
