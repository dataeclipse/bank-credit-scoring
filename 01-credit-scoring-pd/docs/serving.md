# Serving - PD scoring API (Фаза 4)

FastAPI-сервис. Модель грузится из MLflow registry по алиасу `models:/pd-lightgbm@champion`
на старте (lifespan). Запуск: `make run` (или `uv run uvicorn pd_scoring.service.app:app`).

## Эндпоинты
| Метод | Путь | Назначение |
|---|---|---|
| POST | `/score` | заявка → PD, балл, риск-сегмент, топ-3 reason codes |
| GET | `/healthz` | готовность + версия загруженной модели |
| GET | `/metrics` | метрики Prometheus (запросы, латентность, распределение PD) |

## Контракт /score
Вход - **поля заявки** (application-level). Валидация диапазонов (pydantic): `EXT_SOURCE_*∈[0,1]`,
`AMT_*>0`, `DAYS_BIRTH<0`, `CODE_GENDER∈{M,F,XNA}`, неизвестные поля запрещены (`extra=forbid`).
Обязательные: `AMT_INCOME_TOTAL`, `AMT_CREDIT`, `DAYS_BIRTH`, `CODE_GENDER`.

> **Ограничение**: одна заявка не содержит агрегатов кредитной истории (bureau/previous/…).
> Сервис строит полную строку из 120 фич модели: переданные поля + engineered ratios, остальное -
> `null` (LightGBM обрабатывает нативно). Это «быстрый путь по данным заявки»; полный скоринг с
> историей бюро - батч/фичестор (вне Фазы 4).

### Пример запроса
```bash
curl -s -X POST http://localhost:8000/score -H 'Content-Type: application/json' -d '{
  "AMT_INCOME_TOTAL": 135000, "AMT_CREDIT": 600000, "AMT_ANNUITY": 27000,
  "DAYS_BIRTH": -14000, "DAYS_EMPLOYED": -1200, "CODE_GENDER": "M",
  "EXT_SOURCE_1": 0.12, "EXT_SOURCE_2": 0.18, "EXT_SOURCE_3": 0.15
}'
```

### Пример ответа A - высокий риск (низкие EXT_SOURCE)
```json
{
  "pd": 0.532, "score": 309, "segment": "high",
  "reason_codes": [
    {"feature": "EXT_SOURCE_3", "contribution": 0.958, "direction": "increases",
     "description": "внешний скоринговый балл (источник 3) = 0.1 - повышает риск"},
    {"feature": "EXT_SOURCE_2", "contribution": 0.683, "direction": "increases",
     "description": "внешний скоринговый балл (источник 2) = 0.12 - повышает риск"},
    {"feature": "EXT_SOURCE_1", "contribution": 0.599, "direction": "increases",
     "description": "внешний скоринговый балл (источник 1) = 0.08 - повышает риск"},
    {"feature": "DAYS_BIRTH", "contribution": -0.179, "direction": "decreases",
     "description": "возраст в днях (<0) = -8500 - снижает риск"},
    {"feature": "NAME_CONTRACT_TYPE", "contribution": -0.113, "direction": "decreases",
     "description": "тип кредита (cash/revolving) - снижает риск"},
    {"feature": "REGION_RATING_CLIENT_W_CITY", "contribution": -0.071, "direction": "decreases",
     "description": "рейтинг региона с учётом города - снижает риск"}
  ],
  "model_version": "3"
}
```

### Пример ответа B - низкий риск (высокие EXT_SOURCE)
```json
{
  "pd": 0.016, "score": 615, "segment": "low",
  "reason_codes": [
    {"feature": "DAYS_REGISTRATION", "contribution": 0.241, "direction": "increases",
     "description": "давность смены регистрации (дни) - повышает риск"},
    {"feature": "CREDIT_ANNUITY_RATIO", "contribution": 0.137, "direction": "increases",
     "description": "сумма кредита / аннуитет (прокси срока) = 20.5 - повышает риск"},
    {"feature": "EXT_SOURCE_2", "contribution": -0.497, "direction": "decreases",
     "description": "внешний скоринговый балл (источник 2) = 0.72 - снижает риск"},
    {"feature": "EXT_SOURCE_1", "contribution": -0.328, "direction": "decreases",
     "description": "внешний скоринговый балл (источник 1) = 0.75 - снижает риск"},
    {"feature": "EXT_SOURCE_3", "contribution": -0.241, "direction": "decreases",
     "description": "внешний скоринговый балл (источник 3) = 0.68 - снижает риск"}
  ],
  "model_version": "3"
}
```
Невалидный вход (например `DAYS_BIRTH > 0`, `EXT_SOURCE_2 > 1`, неизвестное поле) → **422**.

## Балл и риск-сегмент
Балл - PDO/odds-шкала (config `score_base=600`, `score_pdo=50`, `score_base_odds=50`): выше балл = ниже риск.
Сегмент по PD: `< 0.05` → **low**, `< 0.15` → **medium**, иначе **high** (пороги в config).

## Reason codes
LightGBM native TreeSHAP (`pred_contrib`). Возвращаем **сбалансированно**: топ-3 фактора «за» риск
(`direction: increases`) + топ-3 «против» (`decreases`) - видно обе стороны решения. Поле `direction`
машинно-читаемое; описание - человекочитаемое (для `EXT_SOURCE_N` цифра = номер источника, плюс
значение фичи). Источник имён - `feature_schema.json`.

## Латентность
См. [load_test.md](load_test.md): одиночный запрос p50 ≈ 83 мс, p95 ≈ 86 мс.
