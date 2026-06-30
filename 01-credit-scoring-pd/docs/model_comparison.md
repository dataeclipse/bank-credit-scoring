# Model comparison (Phase 2)

Holdout: 61503 applications (Phase 1 split, seed 42). Feature base: 120 features for all models.

## Holdout metrics
| Model | ROC-AUC | PR-AUC | KS | Gini |
|---|---|---|---|---|
| scorecard | 0.7696 | 0.2552 | 0.4065 | 0.5392 |
| lightgbm | 0.7895 | 0.2872 | 0.4401 | 0.5789 |
| catboost | 0.7893 | 0.2890 | 0.4400 | 0.5786 |

## Scorecard - honest CV (binning inside folds)
| Model | ROC-AUC | PR-AUC | KS | Gini |
|---|---|---|---|---|
| scorecard (CV mean) | 0.7640 | 0.2427 | 0.3978 | 0.5280 |

## Methodology
- HPO (Optuna, TPE, seed) on a stratified subsample of train; final models - on the full train. CatBoost: `max_ctr_complexity=1` (no categorical combinations).

## Feature-base consistency
- Same input: **120 features**.
- **Scorecard**: WOE + selection by IV>=0.02 -> **76** features (parsimonious by design).
- **LightGBM**: categoricals as `category` dtype, missing values handled natively.
- **CatBoost**: native categoricals (no one-hot) + missing values handled natively.
- Difference: the scorecard takes a subset (IV selection) and WOE; GBDT - all features and raw missing values. The comparison is valid (single holdout, single input), the interpretation differs.
