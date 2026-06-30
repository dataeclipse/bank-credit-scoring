# Serving - PD scoring API (Phase 4)

FastAPI service. The model is loaded from the MLflow registry by the alias `models:/pd-lightgbm@champion`
at startup (lifespan). Run: `make run` (or `uv run uvicorn pd_scoring.service.app:app`).

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| POST | `/score` | application → PD, score, risk segment, top-3 reason codes |
| GET | `/healthz` | readiness + version of the loaded model |
| GET | `/metrics` | Prometheus metrics (requests, latency, PD distribution) |

## /score contract
Input - **application fields** (application-level). Range validation (pydantic): `EXT_SOURCE_*∈[0,1]`,
`AMT_*>0`, `DAYS_BIRTH<0`, `CODE_GENDER∈{M,F,XNA}`, unknown fields are not allowed (`extra=forbid`).
Required: `AMT_INCOME_TOTAL`, `AMT_CREDIT`, `DAYS_BIRTH`, `CODE_GENDER`.

> **Limitation**: a single application does not contain credit history aggregates (bureau/previous/…).
> The service builds the full row of the model's 120 features: passed fields + engineered ratios, the rest -
> `null` (LightGBM handles this natively). This is the "fast path over application data"; full scoring with
> bureau history - batch/feature store (outside Phase 4).

### Example request
```bash
curl -s -X POST http://localhost:8000/score -H 'Content-Type: application/json' -d '{
  "AMT_INCOME_TOTAL": 135000, "AMT_CREDIT": 600000, "AMT_ANNUITY": 27000,
  "DAYS_BIRTH": -14000, "DAYS_EMPLOYED": -1200, "CODE_GENDER": "M",
  "EXT_SOURCE_1": 0.12, "EXT_SOURCE_2": 0.18, "EXT_SOURCE_3": 0.15
}'
```

### Example response A - high risk (low EXT_SOURCE)
```json
{
  "pd": 0.532, "score": 309, "segment": "high",
  "reason_codes": [
    {"feature": "EXT_SOURCE_3", "contribution": 0.958, "direction": "increases",
     "description": "external scoring score (source 3) = 0.1 - increases risk"},
    {"feature": "EXT_SOURCE_2", "contribution": 0.683, "direction": "increases",
     "description": "external scoring score (source 2) = 0.12 - increases risk"},
    {"feature": "EXT_SOURCE_1", "contribution": 0.599, "direction": "increases",
     "description": "external scoring score (source 1) = 0.08 - increases risk"},
    {"feature": "DAYS_BIRTH", "contribution": -0.179, "direction": "decreases",
     "description": "age in days (<0) = -8500 - reduces risk"},
    {"feature": "NAME_CONTRACT_TYPE", "contribution": -0.113, "direction": "decreases",
     "description": "credit type (cash/revolving) - reduces risk"},
    {"feature": "REGION_RATING_CLIENT_W_CITY", "contribution": -0.071, "direction": "decreases",
     "description": "region rating accounting for city - reduces risk"}
  ],
  "model_version": "3"
}
```

### Example response B - low risk (high EXT_SOURCE)
```json
{
  "pd": 0.016, "score": 615, "segment": "low",
  "reason_codes": [
    {"feature": "DAYS_REGISTRATION", "contribution": 0.241, "direction": "increases",
     "description": "time since registration change (days) - increases risk"},
    {"feature": "CREDIT_ANNUITY_RATIO", "contribution": 0.137, "direction": "increases",
     "description": "credit amount / annuity (term proxy) = 20.5 - increases risk"},
    {"feature": "EXT_SOURCE_2", "contribution": -0.497, "direction": "decreases",
     "description": "external scoring score (source 2) = 0.72 - reduces risk"},
    {"feature": "EXT_SOURCE_1", "contribution": -0.328, "direction": "decreases",
     "description": "external scoring score (source 1) = 0.75 - reduces risk"},
    {"feature": "EXT_SOURCE_3", "contribution": -0.241, "direction": "decreases",
     "description": "external scoring score (source 3) = 0.68 - reduces risk"}
  ],
  "model_version": "3"
}
```
Invalid input (for example `DAYS_BIRTH > 0`, `EXT_SOURCE_2 > 1`, an unknown field) → **422**.

## Score and risk segment
The score is a PDO/odds scale (config `score_base=600`, `score_pdo=50`, `score_base_odds=50`): higher score = lower risk.
Segment by PD: `< 0.05` → **low**, `< 0.15` → **medium**, otherwise **high** (thresholds in config).

## Reason codes
LightGBM native TreeSHAP (`pred_contrib`). Returned **in a balanced way**: top-3 factors "for" risk
(`direction: increases`) + top-3 "against" (`decreases`) - both sides of the decision are visible. The `direction` field
is machine-readable; the description is human-readable (for `EXT_SOURCE_N` the digit = source number, plus
the feature value). Source of names - `feature_schema.json`.

## Latency
See [load_test.md](load_test.md): single request p50 ≈ 83 ms, p95 ≈ 86 ms.
