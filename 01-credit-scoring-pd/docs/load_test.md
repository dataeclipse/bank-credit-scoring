# Load test — латентность /score (Фаза 4)

Сервис: 1 uvicorn-воркер, CPU, прод-LightGBM (120 фич) + native TreeSHAP reason codes.

## Одиночный запрос (без contention, 100 послед. запросов)
| Метрика | Значение |
|---|---|
| p50 | **83 мс** |
| p95 | **86 мс** |
| p99 | **86 мс** |
| mean | 85 мс |

Это честная латентность обработки заявки (build row → predict_proba → pred_contrib → reason codes).

## Под нагрузкой (locust, 20 пользователей, 15с, 1 воркер)
- Пропускная способность ≈ **17 req/s**, 0% ошибок.
- p50 ≈ 1100 мс — **насыщение одного воркера** (sync CPU-bound эндпоинт сериализуется под GIL),
  а не рост стоимости запроса.

## Запуск
```bash
make run                     # поднять сервис на :8000
uv sync --extra loadtest
uv run locust -f loadtest/locustfile.py --headless -u 20 -r 10 -t 15s --host http://localhost:8000
```
(Windows: запускать с `PYTHONUTF8=1` — locust читает pyproject.toml.)

## Вывод
Per-request латентность ~85 мс приемлема. Пропускная способность масштабируется горизонтально:
`uvicorn --workers N` или реплики за балансировщиком (Фаза 5, Docker/compose).
