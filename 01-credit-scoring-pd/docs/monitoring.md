# Monitoring - input and PD drift (Phase 4)

We monitor model stability over time: the distributions of input features and the PD distribution
must not drift away from the reference (training sample / feature mart).

## Metrics
- **PSI / CSI** for each input feature - `population_stability_index` (quantile bins over the reference).
  PSI = sum (a% - e%)*ln(a%/e%). Empirical thresholds: **<0.1** no shift, **0.1-0.2** moderate,
  **>0.2** significant drift.
- **PD drift** - PSI between the PD distribution on the reference and on the current batch.

## Alert threshold
`PD_PSI` or the PSI of any feature **> 0.2** (config `psi_threshold`) -> alert.

## Run
```bash
make ingest && make features          # the feature mart (reference) is required
uv run python -m pd_scoring.monitoring.drift --demo-drift     # synthetic shift (demo)
uv run python -m pd_scoring.monitoring.drift --current batch.parquet   # real batch
```
Generates `docs/drift_report.md` (PSI table + alerts) and optionally `docs/img/evidently_drift.html`
(Evidently Data Drift Preset).

## Demonstration of drift detection
`--demo-drift` shifts the distributions of `EXT_SOURCE_2/3` (-0.15), `AMT_CREDIT` (x1.4),
`DAYS_EMPLOYED` (x1.3). Result - the alert fires:

| Feature | PSI | alert |
|------|-----|-------|
| `EXT_SOURCE_2` | 2.47 | ⚠️ |
| `EXT_SOURCE_3` | 1.66 | ⚠️ |
| `AMT_CREDIT` | 0.43 | ⚠️ |
| PD drift | 0.22 | ⚠️ |

-> when the input distribution is replaced, monitoring detects the drift and raises an alert.

## Into production (Phase 5)
Planned: scheduled runs of the drift job, export of PSI to Prometheus/Grafana, periodic
revalidation, and thresholds based on the business stability of the scorecard.
