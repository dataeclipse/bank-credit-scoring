# Fairness (Phase 3)

Decision: PD ≥ 0.106 → default (rejection). The threshold is the KS point (Youden's J).
Favorable outcome = approval (PD < threshold). Fairlearn metrics over proxy groups.

## Group: CODE_GENDER

| Subgroup | selection_rate (rejection) | TPR | FPR | approval |
|---|---|---|---|---|
| F | 0.244 | 0.637 | 0.215 | 0.756 |
| M | 0.383 | 0.763 | 0.340 | 0.617 |

- Demographic parity diff: **0.139**
- Equalized odds diff: **0.126**
- Disparate impact (4/5 rule, approval): **0.816** (threshold 0.8: below it - bias indicator)

## Group: AGE_BAND

| Subgroup | selection_rate (rejection) | TPR | FPR | approval |
|---|---|---|---|---|
| 30-40 | 0.350 | 0.755 | 0.308 | 0.650 |
| 40-50 | 0.263 | 0.664 | 0.230 | 0.737 |
| 50-60 | 0.200 | 0.577 | 0.175 | 0.800 |
| 60+ | 0.146 | 0.426 | 0.132 | 0.854 |
| <30 | 0.465 | 0.796 | 0.423 | 0.535 |

- Demographic parity diff: **0.319**
- Equalized odds diff: **0.371**
- Disparate impact (4/5 rule, approval): **0.627** (threshold 0.8: below it - bias indicator)

## How this is handled in a bank
- **Diagnostic, not a verdict**: Home Credit proxy groups are anonymous; the result is a
  bias risk indicator.
- **Mitigation options** (not applied here): reweighting/resampling by group,
  ThresholdOptimizer (Fairlearn) for equal TPR/FPR, calibration by group.
- **Regulatory**: fix the proxies, justify the features, monitor parity (Phase 4).
