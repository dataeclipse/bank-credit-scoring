# Model Card - PD Scoring (credit scoring)

> Final model card in the style of banking validation (NBRK / Fed **SR 11-7** / Basel).
> Versioned together with the model.

| Field | Value |
|---|---|
| Model | PD scoring (probability of default on a credit application) |
| Prod model | **LightGBM**, MLflow registry `pd-lightgbm` **v3** (alias `@champion`) |
| Code version | pd-scoring **1.0.0** |
| Date | 2026-06-30 |
| Owner / validator | dataeclipse (DS) / independent validation required before prod |
| Status | Release v1.0.0 (demo/portfolio; not a live credit decision) |

## 1. Purpose & Scope
PD estimation on a credit application to **support** the lending decision (decision support), not an automatic rejection.
- **In-scope:** consumer lending to individuals, scoring at the application stage from questionnaire data + (in the full
  setup) credit-history aggregates; risk ranking and segmentation, reason codes for justification.
- **Out-of-scope:** automatic rejection without a human in the loop; legal entities/mortgages/other products; use
  as the sole basis for a decision; transfer to a different population without revalidation.

## 2. Data
- Source: **Home Credit Default Risk** (Kaggle) - anonymized consumer-lending data
  (close to the Kazakhstan market). Target variable `TARGET` (1 = default).
- Feature mart: **356,255** clients × **120 features** (curated application + engineered ratios + client-level
  aggregates of bureau/bureau_balance/previous/installments/POS/credit_card), aggregations **without future leakage**.
- Class balance: **8.07%** defaults (strong imbalance ~1:11) - accounted for in the metrics (PR-AUC/KS/Gini).
- Known characteristics: missing values (EXT_SOURCE, card aggregates ~71%), the anomaly `DAYS_EMPLOYED=365243`
  (18%, moved to a flag). Details: [eda.md](eda.md), dictionary - [data_dictionary.md](data_dictionary.md).
- **Data limitations**: anonymous proxies (external validity is limited); only approved applications
  (survivorship - see §8); the dataset is not Kazakhstan-specific.

## 3. Methodology
- **Split**: stratified hold-out by TARGET, seed 42 (train 246,008 / holdout 61,503). HPO (Optuna)
  on a train subsample, final models - on the full train.
- **Scorecard**: WOE/IV binning (`optbinning`, binning inside CV folds - no optimism) + logistic
  regression -> scores; feature selection by IV>=0.02 (76 of 120).
- **GBDT**: LightGBM and CatBoost (native categoricals/missing values), early stopping, fixed seeds.
- **Selected for prod - LightGBM** (Gini 0.579 ~ CatBoost, above the scorecard by Δ Gini 0.04); the scorecard is kept
  as an interpretable challenger. Score - PDO/odds scale (base 600, PDO 50). Rationale:
  [model_selection.md](model_selection.md).

## 4. Quality metrics
Holdout of 61,503 applications (Phase 1 stratified split, seed 42). HPO - Optuna on a train subsample,
final - on the full train. Selected for prod: **LightGBM** (scorecard - interpretable challenger).

| Metric | Scorecard | LightGBM | CatBoost |
|---|---|---|---|
| ROC-AUC | 0.770 | **0.790** | 0.789 |
| Gini | 0.539 | **0.579** | 0.579 |
| KS | 0.407 | **0.440** | 0.440 |
| PR-AUC | 0.255 | 0.287 | 0.289 |

Scorecard CV (binning inside folds, no optimism): Gini 0.528. Details:
[model_comparison.md](model_comparison.md), [model_selection.md](model_selection.md).

## 5. Calibration
The calibrator was trained on a separate calib set (from train), evaluated on holdout - without leakage.
**LightGBM is already well calibrated**: raw Brier **0.0657**, ECE **0.0028** (< 0.01). Isotonic/Platt
do not improve it (isotonic ECE 0.0042, sigmoid 0.0148) -> in prod raw PD can be served; the isotonic calibrator
is kept as a safeguard. Details and reliability curve: [calibration.md](calibration.md).

## 6. Explainability
SHAP **TreeExplainer** on the prod LightGBM. Globally most important features: **EXT_SOURCE_2/3/1**, bureau
delinquencies and debt, payment history. Local **reason codes** - top "for/against" factors per application (SHAP sign =
direction of influence on risk), feature mapping -> human-readable. Examples + beeswarm: [explainability.md](explainability.md).

## 7. Fairness
Proxy groups (anonymous): **CODE_GENDER**, age bands. Decision threshold - the KS point.
- **Gender**: disparate impact (approval) **0.816** (~ the 4/5 boundary), equalized odds diff 0.126 - acceptable.
- **Age**: disparate impact **0.627** (< 0.8) - the young (<30) are approved noticeably less often; equalized odds diff 0.371.
Mitigation was not applied (diagnostics); options - reweighting, ThresholdOptimizer, group calibration.
Details: [fairness.md](fairness.md).

## 8. Limitations and risks
- **Black box** (GBDT) - addressed by SHAP reason codes; the scorecard as an interpretable challenger.
- **Age bias** (DI 0.627) - monitor and justify; young borrowers are in the rejection risk zone.
- Proxy groups are **anonymous** (Home Credit) - external validity is limited.
- **Reject inference** was not done - the model was trained on approved applications (survivorship bias). An option for the future.
- Calibration depends on the stability of the input distribution - see drift monitoring (Phase 4).

## 9. Monitoring requirements
- **PSI/CSI** on input features and **PD drift** (Evidently + custom PSI). Alert threshold **PSI > 0.2**
  (empirically: <0.1 no shift, 0.1-0.2 moderate, >0.2 significant). Tool: `pd-scoring-drift`.
- **Frequency**: drift - on every batch/daily; model revalidation - at least once every
  6-12 months or when the drift alert fires / Gini drops on a fresh slice.
- Scorecard stability metrics (PSI of the score), review/approve share, fraud/default rate over time.
- Quality degradation (Gini/KS on labeled fresh data) -> trigger for revalidation/retraining.
- Details and demonstration of drift detection: [monitoring.md](monitoring.md).

## 10. Governance / versioning
- **Registry**: MLflow Model Registry; the prod version by the alias `pd-lightgbm@champion` (v3, Gini 0.5789).
  The mart schema is versioned (`feature_schema.json`, hash `ac4281b5`).
- **Reproducibility**: fixed seeds, `uv.lock`, training artifacts in MLflow; the container bakes in
  the model (`pd-scoring-export-model` -> joblib) for a self-contained deploy.
- **Process**: before live use - independent model validation (back-testing, stability,
  fairness review), risk committee approval, an audit trail of versions and decisions. Current status - demo/portfolio.
- **The model version changes** on retraining/feature change -> a new version in the registry + an update to this card.
