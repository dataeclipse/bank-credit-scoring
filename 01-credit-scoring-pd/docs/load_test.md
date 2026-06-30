# Load test - /score latency (Phase 4)

Service: 1 uvicorn worker, CPU, prod LightGBM (120 features) + native TreeSHAP reason codes.

## Single request (no contention, 100 sequential requests)
| Metric | Value |
|---|---|
| p50 | **83 ms** |
| p95 | **86 ms** |
| p99 | **86 ms** |
| mean | 85 ms |

This is the real processing latency of an application (build row -> predict_proba -> pred_contrib -> reason codes).

## Latency budget (breakdown of p99 ~ 86 ms)
In-process measurement of `score()` components (300 iterations, no HTTP):

| Stage | ms | share |
|---|---|---|
| `pred_contrib` (reason codes, TreeSHAP) | 38.8 | **45%** |
| `build_feature_row` (assembling the 120-feature DataFrame) | 28.7 | **33%** |
| `predict_proba` (PD inference) | 11.9 | 14% |
| response serialization (pydantic) | ~0.01 | ~0% |
| **score() total** | **86.6** | 100% |

The HTTP wrapper (FastAPI/uvicorn) adds a negligible amount: p50 over HTTP (83 ms) ~ in-process score().
**The main contributors are reason codes (45%) and row assembly (33%)**, not the inference itself.

## Speedup options (recorded, not implemented)
- **Reason codes on demand** - a request flag / separate `/explain` endpoint: without explanation
  `score()` ~ 48 ms (-39 ms), compute the explanation only when needed.
- **build_row optimization** - assemble the input directly into a `numpy` array in the required order instead of
  a `DataFrame` + per-column `to_numeric` (potentially -20 ms).
- **Precomputation for common segments** / cache keyed by the hash of a normalized application.
- **Batch scoring** for offline batches (amortizing overhead per request).
- **Horizontal scaling** under load: `uvicorn --workers N` / replicas (see below).

## Under load (locust, 20 users, 15s, 1 worker)
- Throughput ~ **17 req/s**, 0% errors.
- p50 ~ 1100 ms - **saturation of a single worker** (the sync CPU-bound endpoint is serialized under the GIL),
  not an increase in per-request cost.

## Run
```bash
make run                     # start the service on :8000
uv sync --extra loadtest
uv run locust -f loadtest/locustfile.py --headless -u 20 -r 10 -t 15s --host http://localhost:8000
```
(Windows: run with `PYTHONUTF8=1` - locust reads pyproject.toml.)

## Conclusion
Per-request latency of ~85 ms is acceptable. Throughput scales horizontally:
`uvicorn --workers N` or replicas behind a load balancer (Phase 5, Docker/compose).
