# Explainability: SHAP reason codes (Phase 3)

TreeExplainer over the production LightGBM. Global importance - mean(|SHAP|); reason codes -
top factors "for/against" per application (SHAP sign = direction of effect on risk).

## Global importance (top 15)
| # | Feature | mean(\|SHAP\|) |
|---|------|---------------|
| 1 | `EXT_SOURCE_2` | 0.2961 |
| 2 | `EXT_SOURCE_3` | 0.2652 |
| 3 | `EXT_SOURCE_1` | 0.1539 |
| 4 | `POS_CNT_INSTALMENT_FUTURE_MEAN` | 0.1116 |
| 5 | `INST_DPD_MEAN` | 0.0988 |
| 6 | `CREDIT_ANNUITY_RATIO` | 0.0965 |
| 7 | `GOODS_CREDIT_RATIO` | 0.0960 |
| 8 | `CODE_GENDER` | 0.0931 |
| 9 | `ORGANIZATION_TYPE` | 0.0838 |
| 10 | `DAYS_EMPLOYED` | 0.0811 |
| 11 | `DAYS_BIRTH` | 0.0794 |
| 12 | `AMT_ANNUITY` | 0.0773 |
| 13 | `BUREAU_AMT_CREDIT_SUM_DEBT_MEAN` | 0.0766 |
| 14 | `INST_AMT_PAYMENT_SUM` | 0.0753 |
| 15 | `OWN_CAR_AGE` | 0.0734 |

![bar](img/shap_bar.png)

![beeswarm](img/shap_beeswarm.png)

## Reason code examples

**High risk (rejection candidate)** (PD = 1.000):

- `EXT_SOURCE_3` - external scoring score 3 - increases risk (SHAP +1.163)
- `EXT_SOURCE_2` - external scoring score 2 - increases risk (SHAP +1.091)
- `BUREAU_AMT_CREDIT_SUM_OVERDUE_SUM` - sum of AMT_CREDIT_SUM_OVERDUE: overdue amount - increases risk (SHAP +0.687)
- `BUREAU_ACTIVE_COUNT` - number of active credits in the bureau - increases risk (SHAP +0.214)
- `BUREAU_AMT_CREDIT_SUM_DEBT_MEAN` - mean of AMT_CREDIT_SUM_DEBT: current debt on bureau credit - increases risk (SHAP +0.153)
- `EXT_SOURCE_1` - external scoring score 1 - increases risk (SHAP +0.145)

**Low risk (approval candidate)** (PD = 0.000):

- `EXT_SOURCE_3` - external scoring score 3 - reduces risk (SHAP −0.382)
- `EXT_SOURCE_2` - external scoring score 2 - reduces risk (SHAP −0.372)
- `PREV_REFUSED_COUNT` - number of refused applications - increases risk (SHAP +0.187)
- `INST_PAYMENT_DIFF_SUM` - sum of PAYMENT_DIFF: underpayment = plan − actual (derived) - reduces risk (SHAP −0.164)
- `INST_AMT_PAYMENT_SUM` - sum of AMT_PAYMENT: actual payment - reduces risk (SHAP −0.144)
- `POS_CNT_INSTALMENT_FUTURE_MEAN` - mean of CNT_INSTALMENT_FUTURE: remaining POS payments - reduces risk (SHAP −0.116)
