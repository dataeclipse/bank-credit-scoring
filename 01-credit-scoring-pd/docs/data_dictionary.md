# Data dictionary - PD scoring feature mart

Schema version: **1** · features: **120** · hash: `ac4281b5adbc`

| # | Feature | Type | Source | Description |
|---|------|-----|----------|----------|
| 1 | `NAME_CONTRACT_TYPE` | String | application.csv | loan type (cash/revolving) |
| 2 | `CODE_GENDER` | String | application.csv | client gender |
| 3 | `FLAG_OWN_CAR` | String | application.csv | owns a car |
| 4 | `FLAG_OWN_REALTY` | String | application.csv | owns real estate |
| 5 | `CNT_CHILDREN` | Int64 | application.csv | number of children |
| 6 | `AMT_INCOME_TOTAL` | Float64 | application.csv | total income |
| 7 | `AMT_CREDIT` | Float64 | application.csv | loan amount on the application |
| 8 | `AMT_ANNUITY` | Float64 | application.csv | annuity payment |
| 9 | `AMT_GOODS_PRICE` | Float64 | application.csv | price of the goods financed by the loan |
| 10 | `NAME_INCOME_TYPE` | String | application.csv | income source type |
| 11 | `NAME_EDUCATION_TYPE` | String | application.csv | education level |
| 12 | `NAME_FAMILY_STATUS` | String | application.csv | family status |
| 13 | `NAME_HOUSING_TYPE` | String | application.csv | housing type |
| 14 | `REGION_POPULATION_RELATIVE` | Float64 | application.csv | relative region population |
| 15 | `DAYS_BIRTH` | Int64 | application.csv | age in days (<0) |
| 16 | `DAYS_EMPLOYED` | Int64 | application.csv | tenure in days (<0; 365243 - anomaly, cleaned) |
| 17 | `DAYS_REGISTRATION` | Float64 | application.csv | time since registration change (days) |
| 18 | `DAYS_ID_PUBLISH` | Int64 | application.csv | time since document change (days) |
| 19 | `OWN_CAR_AGE` | Float64 | application.csv | car age |
| 20 | `FLAG_EMP_PHONE` | Int64 | application.csv | work phone provided |
| 21 | `FLAG_WORK_PHONE` | Int64 | application.csv | work mobile provided |
| 22 | `FLAG_PHONE` | Int64 | application.csv | home phone provided |
| 23 | `FLAG_EMAIL` | Int64 | application.csv | email provided |
| 24 | `OCCUPATION_TYPE` | String | application.csv | occupation |
| 25 | `CNT_FAM_MEMBERS` | Float64 | application.csv | family members |
| 26 | `REGION_RATING_CLIENT` | Int64 | application.csv | client region rating |
| 27 | `REGION_RATING_CLIENT_W_CITY` | Int64 | application.csv | region rating accounting for the city |
| 28 | `EXT_SOURCE_1` | Float64 | application.csv | external scoring value 1 |
| 29 | `EXT_SOURCE_2` | Float64 | application.csv | external scoring value 2 |
| 30 | `EXT_SOURCE_3` | Float64 | application.csv | external scoring value 3 |
| 31 | `DAYS_LAST_PHONE_CHANGE` | Float64 | application.csv | time since phone change (days) |
| 32 | `AMT_REQ_CREDIT_BUREAU_QRT` | Float64 | application.csv | bureau inquiries per quarter |
| 33 | `AMT_REQ_CREDIT_BUREAU_YEAR` | Float64 | application.csv | bureau inquiries per year |
| 34 | `ORGANIZATION_TYPE` | String | application.csv | employer organization type |
| 35 | `DAYS_EMPLOYED_ANOM` | Int8 | application.csv | tenure anomaly flag (DAYS_EMPLOYED==365243) |
| 36 | `CREDIT_INCOME_RATIO` | Float64 | application.csv | loan amount / income |
| 37 | `ANNUITY_INCOME_RATIO` | Float64 | application.csv | annuity / income |
| 38 | `CREDIT_ANNUITY_RATIO` | Float64 | application.csv | loan amount / annuity (term proxy) |
| 39 | `GOODS_CREDIT_RATIO` | Float64 | application.csv | goods price / loan amount |
| 40 | `EMPLOYED_BIRTH_RATIO` | Float64 | application.csv | tenure / age |
| 41 | `INCOME_PER_PERSON` | Float64 | application.csv | income per family member |
| 42 | `BUREAU_COUNT` | UInt32 | bureau.csv | number of records (BUREAU) per client |
| 43 | `BUREAU_DAYS_CREDIT_MEAN` | Float64 | bureau.csv | mean DAYS_CREDIT: age of bureau loans (days, <0 - past) |
| 44 | `BUREAU_DAYS_CREDIT_MIN` | Int64 | bureau.csv | min DAYS_CREDIT: age of bureau loans (days, <0 - past) |
| 45 | `BUREAU_DAYS_CREDIT_MAX` | Int64 | bureau.csv | max DAYS_CREDIT: age of bureau loans (days, <0 - past) |
| 46 | `BUREAU_CREDIT_DAY_OVERDUE_MEAN` | Float64 | bureau.csv | mean CREDIT_DAY_OVERDUE: days overdue as of the reporting date |
| 47 | `BUREAU_CREDIT_DAY_OVERDUE_MAX` | Int64 | bureau.csv | max CREDIT_DAY_OVERDUE: days overdue as of the reporting date |
| 48 | `BUREAU_AMT_CREDIT_SUM_SUM` | Float64 | bureau.csv | sum of AMT_CREDIT_SUM: loan amount per bureau record |
| 49 | `BUREAU_AMT_CREDIT_SUM_MEAN` | Float64 | bureau.csv | mean AMT_CREDIT_SUM: loan amount per bureau record |
| 50 | `BUREAU_AMT_CREDIT_SUM_MAX` | Float64 | bureau.csv | max AMT_CREDIT_SUM: loan amount per bureau record |
| 51 | `BUREAU_AMT_CREDIT_SUM_DEBT_SUM` | Float64 | bureau.csv | sum of AMT_CREDIT_SUM_DEBT: current debt on the bureau loan |
| 52 | `BUREAU_AMT_CREDIT_SUM_DEBT_MEAN` | Float64 | bureau.csv | mean AMT_CREDIT_SUM_DEBT: current debt on the bureau loan |
| 53 | `BUREAU_AMT_CREDIT_SUM_OVERDUE_SUM` | Float64 | bureau.csv | sum of AMT_CREDIT_SUM_OVERDUE: overdue amount |
| 54 | `BUREAU_AMT_CREDIT_MAX_OVERDUE_MEAN` | Float64 | bureau.csv | mean AMT_CREDIT_MAX_OVERDUE: max historical overdue |
| 55 | `BUREAU_AMT_CREDIT_MAX_OVERDUE_MAX` | Float64 | bureau.csv | max AMT_CREDIT_MAX_OVERDUE: max historical overdue |
| 56 | `BUREAU_CNT_CREDIT_PROLONG_SUM` | Int64 | bureau.csv | sum of CNT_CREDIT_PROLONG: number of loan prolongations |
| 57 | `BUREAU_DAYS_CREDIT_UPDATE_MEAN` | Float64 | bureau.csv | mean DAYS_CREDIT_UPDATE: time since bureau record update |
| 58 | `BUREAU_BB_MONTHS_COUNT_MEAN` | Float64 | bureau.csv | mean BB_MONTHS_COUNT: number of months of history in bureau_balance |
| 59 | `BUREAU_BB_MONTHS_COUNT_SUM` | UInt32 | bureau.csv | sum of BB_MONTHS_COUNT: number of months of history in bureau_balance |
| 60 | `BUREAU_BB_DPD_COUNT_SUM` | Int64 | bureau.csv | sum of BB_DPD_COUNT: number of months overdue (statuses 1-5) |
| 61 | `BUREAU_BB_DPD_COUNT_MEAN` | Float64 | bureau.csv | mean BB_DPD_COUNT: number of months overdue (statuses 1-5) |
| 62 | `BUREAU_ACTIVE_COUNT` | Int64 | bureau.csv | number of active bureau loans |
| 63 | `BUREAU_CLOSED_COUNT` | Int64 | bureau.csv | number of closed bureau loans |
| 64 | `PREV_COUNT` | UInt32 | previous_application.csv | number of records (PREV) per client |
| 65 | `PREV_AMT_APPLICATION_MEAN` | Float64 | previous_application.csv | mean AMT_APPLICATION: amount requested on the prior application |
| 66 | `PREV_AMT_APPLICATION_SUM` | Float64 | previous_application.csv | sum of AMT_APPLICATION: amount requested on the prior application |
| 67 | `PREV_AMT_APPLICATION_MAX` | Float64 | previous_application.csv | max AMT_APPLICATION: amount requested on the prior application |
| 68 | `PREV_AMT_CREDIT_MEAN` | Float64 | previous_application.csv | mean AMT_CREDIT: amount approved on the prior application |
| 69 | `PREV_AMT_CREDIT_SUM` | Float64 | previous_application.csv | sum of AMT_CREDIT: amount approved on the prior application |
| 70 | `PREV_AMT_CREDIT_MAX` | Float64 | previous_application.csv | max AMT_CREDIT: amount approved on the prior application |
| 71 | `PREV_AMT_DOWN_PAYMENT_MEAN` | Float64 | previous_application.csv | mean AMT_DOWN_PAYMENT: down payment |
| 72 | `PREV_DAYS_DECISION_MEAN` | Float64 | previous_application.csv | mean DAYS_DECISION: time since decision on the prior application |
| 73 | `PREV_DAYS_DECISION_MIN` | Int64 | previous_application.csv | min DAYS_DECISION: time since decision on the prior application |
| 74 | `PREV_DAYS_DECISION_MAX` | Int64 | previous_application.csv | max DAYS_DECISION: time since decision on the prior application |
| 75 | `PREV_CNT_PAYMENT_MEAN` | Float64 | previous_application.csv | mean CNT_PAYMENT: loan term in payments |
| 76 | `PREV_CNT_PAYMENT_SUM` | Float64 | previous_application.csv | sum of CNT_PAYMENT: loan term in payments |
| 77 | `PREV_APP_CREDIT_RATIO_MEAN` | Float64 | previous_application.csv | mean APP_CREDIT_RATIO: requested/approved (derived) |
| 78 | `PREV_APP_CREDIT_RATIO_MAX` | Float64 | previous_application.csv | max APP_CREDIT_RATIO: requested/approved (derived) |
| 79 | `PREV_APPROVED_COUNT` | Int64 | previous_application.csv | number of approved applications |
| 80 | `PREV_REFUSED_COUNT` | Int64 | previous_application.csv | number of refused applications |
| 81 | `INST_COUNT` | UInt32 | installments_payments.csv | number of records (INST) per client |
| 82 | `INST_PAYMENT_DIFF_MEAN` | Float64 | installments_payments.csv | mean PAYMENT_DIFF: shortfall = planned - actual (derived) |
| 83 | `INST_PAYMENT_DIFF_SUM` | Float64 | installments_payments.csv | sum of PAYMENT_DIFF: shortfall = planned - actual (derived) |
| 84 | `INST_PAYMENT_DIFF_MAX` | Float64 | installments_payments.csv | max PAYMENT_DIFF: shortfall = planned - actual (derived) |
| 85 | `INST_PAYMENT_RATIO_MEAN` | Float64 | installments_payments.csv | mean PAYMENT_RATIO: actual/planned payment (derived) |
| 86 | `INST_PAYMENT_RATIO_MIN` | Float64 | installments_payments.csv | min PAYMENT_RATIO: actual/planned payment (derived) |
| 87 | `INST_DPD_MEAN` | Float64 | installments_payments.csv | mean DPD: days overdue on a payment (derived) |
| 88 | `INST_DPD_MAX` | Float64 | installments_payments.csv | max DPD: days overdue on a payment (derived) |
| 89 | `INST_DPD_SUM` | Float64 | installments_payments.csv | sum of DPD: days overdue on a payment (derived) |
| 90 | `INST_DBD_MEAN` | Float64 | installments_payments.csv | mean DBD: days before the payment due date (derived) |
| 91 | `INST_AMT_PAYMENT_SUM` | Float64 | installments_payments.csv | sum of AMT_PAYMENT: actual payment |
| 92 | `INST_AMT_PAYMENT_MEAN` | Float64 | installments_payments.csv | mean AMT_PAYMENT: actual payment |
| 93 | `INST_AMT_INSTALMENT_SUM` | Float64 | installments_payments.csv | sum of AMT_INSTALMENT: scheduled payment |
| 94 | `INST_AMT_INSTALMENT_MEAN` | Float64 | installments_payments.csv | mean AMT_INSTALMENT: scheduled payment |
| 95 | `POS_COUNT` | UInt32 | POS_CASH_balance.csv | number of records (POS) per client |
| 96 | `POS_MONTHS_BALANCE_MEAN` | Float64 | POS_CASH_balance.csv | mean MONTHS_BALANCE: depth of POS history (months, <0 - past) |
| 97 | `POS_MONTHS_BALANCE_MIN` | Int64 | POS_CASH_balance.csv | min MONTHS_BALANCE: depth of POS history (months, <0 - past) |
| 98 | `POS_SK_DPD_MEAN` | Float64 | POS_CASH_balance.csv | mean SK_DPD: POS days overdue |
| 99 | `POS_SK_DPD_MAX` | Int64 | POS_CASH_balance.csv | max SK_DPD: POS days overdue |
| 100 | `POS_SK_DPD_DEF_MEAN` | Float64 | POS_CASH_balance.csv | mean SK_DPD_DEF: POS days overdue (with tolerance) |
| 101 | `POS_SK_DPD_DEF_MAX` | Int64 | POS_CASH_balance.csv | max SK_DPD_DEF: POS days overdue (with tolerance) |
| 102 | `POS_CNT_INSTALMENT_FUTURE_MEAN` | Float64 | POS_CASH_balance.csv | mean CNT_INSTALMENT_FUTURE: remaining POS payments |
| 103 | `POS_CNT_INSTALMENT_FUTURE_MIN` | Float64 | POS_CASH_balance.csv | min CNT_INSTALMENT_FUTURE: remaining POS payments |
| 104 | `CC_COUNT` | UInt32 | credit_card_balance.csv | number of records (CC) per client |
| 105 | `CC_AMT_BALANCE_MEAN` | Float64 | credit_card_balance.csv | mean AMT_BALANCE: card balance |
| 106 | `CC_AMT_BALANCE_MAX` | Float64 | credit_card_balance.csv | max AMT_BALANCE: card balance |
| 107 | `CC_AMT_CREDIT_LIMIT_ACTUAL_MEAN` | Float64 | credit_card_balance.csv | mean AMT_CREDIT_LIMIT_ACTUAL: card credit limit |
| 108 | `CC_AMT_CREDIT_LIMIT_ACTUAL_MAX` | Int64 | credit_card_balance.csv | max AMT_CREDIT_LIMIT_ACTUAL: card credit limit |
| 109 | `CC_UTILIZATION_MEAN` | Float64 | credit_card_balance.csv | mean UTILIZATION: utilization = balance/limit (derived) |
| 110 | `CC_UTILIZATION_MAX` | Float64 | credit_card_balance.csv | max UTILIZATION: utilization = balance/limit (derived) |
| 111 | `CC_AMT_DRAWINGS_CURRENT_SUM` | Float64 | credit_card_balance.csv | sum of AMT_DRAWINGS_CURRENT: card drawings |
| 112 | `CC_AMT_DRAWINGS_CURRENT_MEAN` | Float64 | credit_card_balance.csv | mean AMT_DRAWINGS_CURRENT: card drawings |
| 113 | `CC_AMT_PAYMENT_CURRENT_SUM` | Float64 | credit_card_balance.csv | sum of AMT_PAYMENT_CURRENT: card payments |
| 114 | `CC_AMT_PAYMENT_CURRENT_MEAN` | Float64 | credit_card_balance.csv | mean AMT_PAYMENT_CURRENT: card payments |
| 115 | `CC_SK_DPD_MEAN` | Float64 | credit_card_balance.csv | mean SK_DPD: card days overdue |
| 116 | `CC_SK_DPD_MAX` | Int64 | credit_card_balance.csv | max SK_DPD: card days overdue |
| 117 | `CC_SK_DPD_DEF_MEAN` | Float64 | credit_card_balance.csv | mean SK_DPD_DEF: card days overdue (tolerance) |
| 118 | `CC_SK_DPD_DEF_MAX` | Int64 | credit_card_balance.csv | max SK_DPD_DEF: card days overdue (tolerance) |
| 119 | `CC_CNT_DRAWINGS_CURRENT_SUM` | Int64 | credit_card_balance.csv | sum of CNT_DRAWINGS_CURRENT: number of card drawings |
| 120 | `CC_CNT_DRAWINGS_CURRENT_MEAN` | Float64 | credit_card_balance.csv | mean CNT_DRAWINGS_CURRENT: number of card drawings |
