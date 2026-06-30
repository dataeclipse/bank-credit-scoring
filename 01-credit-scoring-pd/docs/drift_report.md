# Drift report (сгенерировано pd-scoring-drift)

Порог алерта PSI > **0.2**. Дрейф PD (PSI): **0.217**.
Алерты: **AMT_CREDIT, EXT_SOURCE_2, EXT_SOURCE_3, PD**.

## PSI по входным фичам (топ-20)
| Фича | PSI | алерт |
|------|-----|-------|
| `EXT_SOURCE_2` | 2.469 | ⚠️ |
| `EXT_SOURCE_3` | 1.664 | ⚠️ |
| `AMT_CREDIT` | 0.427 | ⚠️ |
| `DAYS_EMPLOYED` | 0.064 |  |
| `CNT_CHILDREN` | 0.000 |  |
| `AMT_INCOME_TOTAL` | 0.000 |  |
| `AMT_ANNUITY` | 0.000 |  |
| `AMT_GOODS_PRICE` | 0.000 |  |
| `REGION_POPULATION_RELATIVE` | 0.000 |  |
| `DAYS_BIRTH` | 0.000 |  |
| `DAYS_REGISTRATION` | 0.000 |  |
| `DAYS_ID_PUBLISH` | 0.000 |  |
| `OWN_CAR_AGE` | 0.000 |  |
| `FLAG_EMP_PHONE` | 0.000 |  |
| `FLAG_WORK_PHONE` | 0.000 |  |
| `FLAG_PHONE` | 0.000 |  |
| `FLAG_EMAIL` | 0.000 |  |
| `CNT_FAM_MEMBERS` | 0.000 |  |
| `REGION_RATING_CLIENT` | 0.000 |  |
| `REGION_RATING_CLIENT_W_CITY` | 0.000 |  |

HTML-отчёт Evidently: `img/evidently_drift.html`.
