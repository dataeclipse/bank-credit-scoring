# Deploy - Fly.io / VPS (кратко)

Образ самодостаточный: модель запечена в `deploy/model/` (joblib), рантайм - lean serve-стек
(без mlflow/shap). Секреты - только через env, не в образ.

## Подготовка
```bash
make export-model        # pd-lightgbm@champion → deploy/model/model.joblib
docker build -f infra/docker/Dockerfile -t pd-scoring-api:1.0.0 .
```

## VPS (docker)
```bash
docker run -d -p 8000:8000 --restart unless-stopped \
  -e PD_LOG_LEVEL=INFO \
  -e PD_DATABASE_URL="postgresql+psycopg://user:pass@db:5432/scoring" \
  pd-scoring-api:1.0.0
```
`PD_MODEL_URI=/app/deploy/model/model.joblib` уже задан в образе. HEALTHCHECK на `/healthz` встроен.
Для полного контура - `docker compose -f infra/compose.yaml up -d` (api + postgres).

## Fly.io
```bash
fly launch --no-deploy            # сгенерит fly.toml; internal_port = 8000
fly secrets set PD_DATABASE_URL="postgresql+psycopg://..."   # секреты вне образа
fly deploy --dockerfile infra/docker/Dockerfile
```
В `fly.toml`: `[http_service] internal_port = 8000`, health-check `GET /healthz`. Postgres - `fly postgres
create` + attach (прокинет `DATABASE_URL`; смапь в `PD_DATABASE_URL`).

## Заметки
- Модель в образе → новая модель = пересборка образа (`make export-model` + build). Альтернатива:
  монтировать `deploy/model/` томом и не пересобирать.
- Масштаб: per-request ~85 мс, sync-эндпоинт - горизонтально (`--workers N` / реплики за LB).
- Мониторинг дрейфа - отдельной джобой по расписанию (`pd-scoring-drift`), не в hot-path сервиса.
