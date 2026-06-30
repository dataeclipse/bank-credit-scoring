# Model selection for production (Phase 2)

## Ranking by Gini (holdout)
| Model | ROC-AUC | PR-AUC | KS | Gini |
|---|---|---|---|---|
| lightgbm | 0.7895 | 0.2872 | 0.4401 | 0.5789 |
| catboost | 0.7893 | 0.2890 | 0.4400 | 0.5786 |
| scorecard | 0.7696 | 0.2552 | 0.4065 | 0.5392 |

## Decision
**To production: lightgbm** (Gini 0.579, KS 0.440) - higher than the scorecard (Gini 0.539) by Delta Gini 0.040. The scorecard - an interpretable challenger and regulatory explainability (points/reason codes).

## Trade-off "quality vs interpretability"
- **GBDT (LightGBM/CatBoost)**: higher Gini/KS, capture nonlinearities and interactions; work natively with missing values and categoricals. Downside - a black box (SHAP in Phase 3).
- **Scorecard (WOE + logistic)**: transparent points, monotone bins, IV selection; easy to validate and explain to a regulator. Downside - usually lower in quality.
- The final scorecard uses 76 features versus the full base for GBDT.

_Probability calibration, SHAP reason codes and fairness - Phase 3._
