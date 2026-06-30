# EDA - findings (Home Credit, Phase 1)

- Feature mart: 356255 clients x 123 columns (120 features).
- Class balance: 24825 defaults out of 307511 (8.07%) - strong imbalance (~1:11), account for it in training/metrics.
- DAYS_EMPLOYED==365243 anomaly: 55374 (18.0%) - placeholder for the unemployed; moved to a flag and cleaned to null.
- EXT_SOURCE_1/2/3 - the strongest predictors (max |corr| with the target), but with missing values.

## Top 15 missing values

- `CC_AMT_PAYMENT_CURRENT_MEAN`: 79.8%
- `CC_UTILIZATION_MEAN`: 71.2%
- `CC_UTILIZATION_MAX`: 71.2%
- `CC_COUNT`: 70.9%
- `CC_AMT_BALANCE_MEAN`: 70.9%
- `CC_AMT_BALANCE_MAX`: 70.9%
- `CC_AMT_CREDIT_LIMIT_ACTUAL_MEAN`: 70.9%
- `CC_AMT_CREDIT_LIMIT_ACTUAL_MAX`: 70.9%
- `CC_AMT_DRAWINGS_CURRENT_SUM`: 70.9%
- `CC_AMT_DRAWINGS_CURRENT_MEAN`: 70.9%
- `CC_AMT_PAYMENT_CURRENT_SUM`: 70.9%
- `CC_SK_DPD_MEAN`: 70.9%
- `CC_SK_DPD_MAX`: 70.9%
- `CC_SK_DPD_DEF_MEAN`: 70.9%
- `CC_SK_DPD_DEF_MAX`: 70.9%

## Top 15 correlations with TARGET

- `EXT_SOURCE_3`: -0.179
- `EXT_SOURCE_2`: -0.160
- `EXT_SOURCE_1`: -0.155
- `CC_UTILIZATION_MEAN`: +0.136
- `CC_UTILIZATION_MAX`: +0.097
- `BUREAU_DAYS_CREDIT_MEAN`: +0.090
- `CC_AMT_BALANCE_MEAN`: +0.087
- `CC_CNT_DRAWINGS_CURRENT_MEAN`: +0.083
- `BUREAU_BB_MONTHS_COUNT_MEAN`: -0.080
- `DAYS_BIRTH`: +0.078
- `BUREAU_DAYS_CREDIT_MIN`: +0.075
- `DAYS_EMPLOYED`: +0.075
- `BUREAU_DAYS_CREDIT_UPDATE_MEAN`: +0.069
- `CC_AMT_BALANCE_MAX`: +0.069
- `EMPLOYED_BIRTH_RATIO`: -0.068
