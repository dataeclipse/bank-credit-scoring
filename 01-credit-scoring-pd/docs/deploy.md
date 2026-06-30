# Deploy - Fly.io / VPS (brief)

The image is self-contained: the model is baked into `deploy/model/` (joblib), the runtime is a lean serve stack
(no mlflow/shap). Secrets - only via env, not in the image.

## Preparation
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
`PD_MODEL_URI=/app/deploy/model/model.joblib` is already set in the image. A HEALTHCHECK on `/healthz` is built in.
For the full setup - `docker compose -f infra/compose.yaml up -d` (api + postgres).

## Fly.io
```bash
fly launch --no-deploy            # generates fly.toml; internal_port = 8000
fly secrets set PD_DATABASE_URL="postgresql+psycopg://..."   # secrets outside the image
fly deploy --dockerfile infra/docker/Dockerfile
```
In `fly.toml`: `[http_service] internal_port = 8000`, health-check `GET /healthz`. Postgres - `fly postgres
create` + attach (passes `DATABASE_URL`; map it to `PD_DATABASE_URL`).

## Notes
- The model is in the image -> a new model = rebuilding the image (`make export-model` + build). Alternative:
  mount `deploy/model/` as a volume and avoid rebuilding.
- Scaling: per-request ~85 ms, the sync endpoint - horizontally (`--workers N` / replicas behind an LB).
- Drift monitoring - a separate scheduled job (`pd-scoring-drift`), not in the service hot path.
