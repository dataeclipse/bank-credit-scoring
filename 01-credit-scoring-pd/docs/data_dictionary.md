# Data dictionary — витрина фичей PD-скоринга

Schema version: **1** · features: **120** · hash: `ac4281b5adbc`

| # | Фича | Тип | Источник | Описание |
|---|------|-----|----------|----------|
| 1 | `NAME_CONTRACT_TYPE` | String | application.csv | тип кредита (cash/revolving) |
| 2 | `CODE_GENDER` | String | application.csv | пол клиента |
| 3 | `FLAG_OWN_CAR` | String | application.csv | есть автомобиль |
| 4 | `FLAG_OWN_REALTY` | String | application.csv | есть недвижимость |
| 5 | `CNT_CHILDREN` | Int64 | application.csv | число детей |
| 6 | `AMT_INCOME_TOTAL` | Float64 | application.csv | совокупный доход |
| 7 | `AMT_CREDIT` | Float64 | application.csv | сумма кредита по заявке |
| 8 | `AMT_ANNUITY` | Float64 | application.csv | аннуитетный платёж |
| 9 | `AMT_GOODS_PRICE` | Float64 | application.csv | стоимость товара под кредит |
| 10 | `NAME_INCOME_TYPE` | String | application.csv | тип источника дохода |
| 11 | `NAME_EDUCATION_TYPE` | String | application.csv | уровень образования |
| 12 | `NAME_FAMILY_STATUS` | String | application.csv | семейное положение |
| 13 | `NAME_HOUSING_TYPE` | String | application.csv | тип жилья |
| 14 | `REGION_POPULATION_RELATIVE` | Float64 | application.csv | относительная населённость региона |
| 15 | `DAYS_BIRTH` | Int64 | application.csv | возраст в днях (<0) |
| 16 | `DAYS_EMPLOYED` | Int64 | application.csv | стаж в днях (<0; 365243 — аномалия, чистится) |
| 17 | `DAYS_REGISTRATION` | Float64 | application.csv | давность смены регистрации (дни) |
| 18 | `DAYS_ID_PUBLISH` | Int64 | application.csv | давность смены документа (дни) |
| 19 | `OWN_CAR_AGE` | Float64 | application.csv | возраст автомобиля |
| 20 | `FLAG_EMP_PHONE` | Int64 | application.csv | указан рабочий телефон |
| 21 | `FLAG_WORK_PHONE` | Int64 | application.csv | указан рабочий мобильный |
| 22 | `FLAG_PHONE` | Int64 | application.csv | указан домашний телефон |
| 23 | `FLAG_EMAIL` | Int64 | application.csv | указан email |
| 24 | `OCCUPATION_TYPE` | String | application.csv | профессия |
| 25 | `CNT_FAM_MEMBERS` | Float64 | application.csv | членов семьи |
| 26 | `REGION_RATING_CLIENT` | Int64 | application.csv | рейтинг региона клиента |
| 27 | `REGION_RATING_CLIENT_W_CITY` | Int64 | application.csv | рейтинг региона с учётом города |
| 28 | `EXT_SOURCE_1` | Float64 | application.csv | внешний скоринговый балл 1 |
| 29 | `EXT_SOURCE_2` | Float64 | application.csv | внешний скоринговый балл 2 |
| 30 | `EXT_SOURCE_3` | Float64 | application.csv | внешний скоринговый балл 3 |
| 31 | `DAYS_LAST_PHONE_CHANGE` | Float64 | application.csv | давность смены телефона (дни) |
| 32 | `AMT_REQ_CREDIT_BUREAU_QRT` | Float64 | application.csv | запросов в бюро за квартал |
| 33 | `AMT_REQ_CREDIT_BUREAU_YEAR` | Float64 | application.csv | запросов в бюро за год |
| 34 | `ORGANIZATION_TYPE` | String | application.csv | тип организации-работодателя |
| 35 | `DAYS_EMPLOYED_ANOM` | Int8 | application.csv | флаг аномалии стажа (DAYS_EMPLOYED==365243) |
| 36 | `CREDIT_INCOME_RATIO` | Float64 | application.csv | сумма кредита / доход |
| 37 | `ANNUITY_INCOME_RATIO` | Float64 | application.csv | аннуитет / доход |
| 38 | `CREDIT_ANNUITY_RATIO` | Float64 | application.csv | сумма кредита / аннуитет (прокси срока) |
| 39 | `GOODS_CREDIT_RATIO` | Float64 | application.csv | стоимость товара / сумма кредита |
| 40 | `EMPLOYED_BIRTH_RATIO` | Float64 | application.csv | стаж / возраст |
| 41 | `INCOME_PER_PERSON` | Float64 | application.csv | доход на члена семьи |
| 42 | `BUREAU_COUNT` | UInt32 | bureau.csv | число записей (BUREAU) на клиента |
| 43 | `BUREAU_DAYS_CREDIT_MEAN` | Float64 | bureau.csv | среднее DAYS_CREDIT: давность кредитов в бюро (дни, <0 — прошлое) |
| 44 | `BUREAU_DAYS_CREDIT_MIN` | Int64 | bureau.csv | минимум DAYS_CREDIT: давность кредитов в бюро (дни, <0 — прошлое) |
| 45 | `BUREAU_DAYS_CREDIT_MAX` | Int64 | bureau.csv | максимум DAYS_CREDIT: давность кредитов в бюро (дни, <0 — прошлое) |
| 46 | `BUREAU_CREDIT_DAY_OVERDUE_MEAN` | Float64 | bureau.csv | среднее CREDIT_DAY_OVERDUE: дней просрочки на отчётную дату |
| 47 | `BUREAU_CREDIT_DAY_OVERDUE_MAX` | Int64 | bureau.csv | максимум CREDIT_DAY_OVERDUE: дней просрочки на отчётную дату |
| 48 | `BUREAU_AMT_CREDIT_SUM_SUM` | Float64 | bureau.csv | сумма AMT_CREDIT_SUM: сумма кредита по записи бюро |
| 49 | `BUREAU_AMT_CREDIT_SUM_MEAN` | Float64 | bureau.csv | среднее AMT_CREDIT_SUM: сумма кредита по записи бюро |
| 50 | `BUREAU_AMT_CREDIT_SUM_MAX` | Float64 | bureau.csv | максимум AMT_CREDIT_SUM: сумма кредита по записи бюро |
| 51 | `BUREAU_AMT_CREDIT_SUM_DEBT_SUM` | Float64 | bureau.csv | сумма AMT_CREDIT_SUM_DEBT: текущий долг по кредиту бюро |
| 52 | `BUREAU_AMT_CREDIT_SUM_DEBT_MEAN` | Float64 | bureau.csv | среднее AMT_CREDIT_SUM_DEBT: текущий долг по кредиту бюро |
| 53 | `BUREAU_AMT_CREDIT_SUM_OVERDUE_SUM` | Float64 | bureau.csv | сумма AMT_CREDIT_SUM_OVERDUE: просроченная сумма |
| 54 | `BUREAU_AMT_CREDIT_MAX_OVERDUE_MEAN` | Float64 | bureau.csv | среднее AMT_CREDIT_MAX_OVERDUE: макс. историческая просрочка |
| 55 | `BUREAU_AMT_CREDIT_MAX_OVERDUE_MAX` | Float64 | bureau.csv | максимум AMT_CREDIT_MAX_OVERDUE: макс. историческая просрочка |
| 56 | `BUREAU_CNT_CREDIT_PROLONG_SUM` | Int64 | bureau.csv | сумма CNT_CREDIT_PROLONG: число пролонгаций кредита |
| 57 | `BUREAU_DAYS_CREDIT_UPDATE_MEAN` | Float64 | bureau.csv | среднее DAYS_CREDIT_UPDATE: давность обновления записи бюро |
| 58 | `BUREAU_BB_MONTHS_COUNT_MEAN` | Float64 | bureau.csv | среднее BB_MONTHS_COUNT: число месяцев истории в bureau_balance |
| 59 | `BUREAU_BB_MONTHS_COUNT_SUM` | UInt32 | bureau.csv | сумма BB_MONTHS_COUNT: число месяцев истории в bureau_balance |
| 60 | `BUREAU_BB_DPD_COUNT_SUM` | Int64 | bureau.csv | сумма BB_DPD_COUNT: число месяцев с просрочкой (статусы 1–5) |
| 61 | `BUREAU_BB_DPD_COUNT_MEAN` | Float64 | bureau.csv | среднее BB_DPD_COUNT: число месяцев с просрочкой (статусы 1–5) |
| 62 | `BUREAU_ACTIVE_COUNT` | Int64 | bureau.csv | число активных кредитов в бюро |
| 63 | `BUREAU_CLOSED_COUNT` | Int64 | bureau.csv | число закрытых кредитов в бюро |
| 64 | `PREV_COUNT` | UInt32 | previous_application.csv | число записей (PREV) на клиента |
| 65 | `PREV_AMT_APPLICATION_MEAN` | Float64 | previous_application.csv | среднее AMT_APPLICATION: запрошенная сумма по прошлой заявке |
| 66 | `PREV_AMT_APPLICATION_SUM` | Float64 | previous_application.csv | сумма AMT_APPLICATION: запрошенная сумма по прошлой заявке |
| 67 | `PREV_AMT_APPLICATION_MAX` | Float64 | previous_application.csv | максимум AMT_APPLICATION: запрошенная сумма по прошлой заявке |
| 68 | `PREV_AMT_CREDIT_MEAN` | Float64 | previous_application.csv | среднее AMT_CREDIT: одобренная сумма по прошлой заявке |
| 69 | `PREV_AMT_CREDIT_SUM` | Float64 | previous_application.csv | сумма AMT_CREDIT: одобренная сумма по прошлой заявке |
| 70 | `PREV_AMT_CREDIT_MAX` | Float64 | previous_application.csv | максимум AMT_CREDIT: одобренная сумма по прошлой заявке |
| 71 | `PREV_AMT_DOWN_PAYMENT_MEAN` | Float64 | previous_application.csv | среднее AMT_DOWN_PAYMENT: первоначальный взнос |
| 72 | `PREV_DAYS_DECISION_MEAN` | Float64 | previous_application.csv | среднее DAYS_DECISION: давность решения по прошлой заявке |
| 73 | `PREV_DAYS_DECISION_MIN` | Int64 | previous_application.csv | минимум DAYS_DECISION: давность решения по прошлой заявке |
| 74 | `PREV_DAYS_DECISION_MAX` | Int64 | previous_application.csv | максимум DAYS_DECISION: давность решения по прошлой заявке |
| 75 | `PREV_CNT_PAYMENT_MEAN` | Float64 | previous_application.csv | среднее CNT_PAYMENT: срок кредита в платежах |
| 76 | `PREV_CNT_PAYMENT_SUM` | Float64 | previous_application.csv | сумма CNT_PAYMENT: срок кредита в платежах |
| 77 | `PREV_APP_CREDIT_RATIO_MEAN` | Float64 | previous_application.csv | среднее APP_CREDIT_RATIO: запрошено/одобрено (derived) |
| 78 | `PREV_APP_CREDIT_RATIO_MAX` | Float64 | previous_application.csv | максимум APP_CREDIT_RATIO: запрошено/одобрено (derived) |
| 79 | `PREV_APPROVED_COUNT` | Int64 | previous_application.csv | число одобренных заявок |
| 80 | `PREV_REFUSED_COUNT` | Int64 | previous_application.csv | число отклонённых заявок |
| 81 | `INST_COUNT` | UInt32 | installments_payments.csv | число записей (INST) на клиента |
| 82 | `INST_PAYMENT_DIFF_MEAN` | Float64 | installments_payments.csv | среднее PAYMENT_DIFF: недоплата = план − факт (derived) |
| 83 | `INST_PAYMENT_DIFF_SUM` | Float64 | installments_payments.csv | сумма PAYMENT_DIFF: недоплата = план − факт (derived) |
| 84 | `INST_PAYMENT_DIFF_MAX` | Float64 | installments_payments.csv | максимум PAYMENT_DIFF: недоплата = план − факт (derived) |
| 85 | `INST_PAYMENT_RATIO_MEAN` | Float64 | installments_payments.csv | среднее PAYMENT_RATIO: факт/план платежа (derived) |
| 86 | `INST_PAYMENT_RATIO_MIN` | Float64 | installments_payments.csv | минимум PAYMENT_RATIO: факт/план платежа (derived) |
| 87 | `INST_DPD_MEAN` | Float64 | installments_payments.csv | среднее DPD: дней просрочки платежа (derived) |
| 88 | `INST_DPD_MAX` | Float64 | installments_payments.csv | максимум DPD: дней просрочки платежа (derived) |
| 89 | `INST_DPD_SUM` | Float64 | installments_payments.csv | сумма DPD: дней просрочки платежа (derived) |
| 90 | `INST_DBD_MEAN` | Float64 | installments_payments.csv | среднее DBD: дней до срока платежа (derived) |
| 91 | `INST_AMT_PAYMENT_SUM` | Float64 | installments_payments.csv | сумма AMT_PAYMENT: фактический платёж |
| 92 | `INST_AMT_PAYMENT_MEAN` | Float64 | installments_payments.csv | среднее AMT_PAYMENT: фактический платёж |
| 93 | `INST_AMT_INSTALMENT_SUM` | Float64 | installments_payments.csv | сумма AMT_INSTALMENT: плановый платёж |
| 94 | `INST_AMT_INSTALMENT_MEAN` | Float64 | installments_payments.csv | среднее AMT_INSTALMENT: плановый платёж |
| 95 | `POS_COUNT` | UInt32 | POS_CASH_balance.csv | число записей (POS) на клиента |
| 96 | `POS_MONTHS_BALANCE_MEAN` | Float64 | POS_CASH_balance.csv | среднее MONTHS_BALANCE: глубина истории POS (мес., <0 — прошлое) |
| 97 | `POS_MONTHS_BALANCE_MIN` | Int64 | POS_CASH_balance.csv | минимум MONTHS_BALANCE: глубина истории POS (мес., <0 — прошлое) |
| 98 | `POS_SK_DPD_MEAN` | Float64 | POS_CASH_balance.csv | среднее SK_DPD: дней просрочки POS |
| 99 | `POS_SK_DPD_MAX` | Int64 | POS_CASH_balance.csv | максимум SK_DPD: дней просрочки POS |
| 100 | `POS_SK_DPD_DEF_MEAN` | Float64 | POS_CASH_balance.csv | среднее SK_DPD_DEF: дней просрочки POS (с учётом толеранса) |
| 101 | `POS_SK_DPD_DEF_MAX` | Int64 | POS_CASH_balance.csv | максимум SK_DPD_DEF: дней просрочки POS (с учётом толеранса) |
| 102 | `POS_CNT_INSTALMENT_FUTURE_MEAN` | Float64 | POS_CASH_balance.csv | среднее CNT_INSTALMENT_FUTURE: оставшиеся платежи POS |
| 103 | `POS_CNT_INSTALMENT_FUTURE_MIN` | Float64 | POS_CASH_balance.csv | минимум CNT_INSTALMENT_FUTURE: оставшиеся платежи POS |
| 104 | `CC_COUNT` | UInt32 | credit_card_balance.csv | число записей (CC) на клиента |
| 105 | `CC_AMT_BALANCE_MEAN` | Float64 | credit_card_balance.csv | среднее AMT_BALANCE: баланс по карте |
| 106 | `CC_AMT_BALANCE_MAX` | Float64 | credit_card_balance.csv | максимум AMT_BALANCE: баланс по карте |
| 107 | `CC_AMT_CREDIT_LIMIT_ACTUAL_MEAN` | Float64 | credit_card_balance.csv | среднее AMT_CREDIT_LIMIT_ACTUAL: кредитный лимит карты |
| 108 | `CC_AMT_CREDIT_LIMIT_ACTUAL_MAX` | Int64 | credit_card_balance.csv | максимум AMT_CREDIT_LIMIT_ACTUAL: кредитный лимит карты |
| 109 | `CC_UTILIZATION_MEAN` | Float64 | credit_card_balance.csv | среднее UTILIZATION: утилизация = баланс/лимит (derived) |
| 110 | `CC_UTILIZATION_MAX` | Float64 | credit_card_balance.csv | максимум UTILIZATION: утилизация = баланс/лимит (derived) |
| 111 | `CC_AMT_DRAWINGS_CURRENT_SUM` | Float64 | credit_card_balance.csv | сумма AMT_DRAWINGS_CURRENT: снятия по карте |
| 112 | `CC_AMT_DRAWINGS_CURRENT_MEAN` | Float64 | credit_card_balance.csv | среднее AMT_DRAWINGS_CURRENT: снятия по карте |
| 113 | `CC_AMT_PAYMENT_CURRENT_SUM` | Float64 | credit_card_balance.csv | сумма AMT_PAYMENT_CURRENT: платежи по карте |
| 114 | `CC_AMT_PAYMENT_CURRENT_MEAN` | Float64 | credit_card_balance.csv | среднее AMT_PAYMENT_CURRENT: платежи по карте |
| 115 | `CC_SK_DPD_MEAN` | Float64 | credit_card_balance.csv | среднее SK_DPD: дней просрочки по карте |
| 116 | `CC_SK_DPD_MAX` | Int64 | credit_card_balance.csv | максимум SK_DPD: дней просрочки по карте |
| 117 | `CC_SK_DPD_DEF_MEAN` | Float64 | credit_card_balance.csv | среднее SK_DPD_DEF: дней просрочки по карте (толеранс) |
| 118 | `CC_SK_DPD_DEF_MAX` | Int64 | credit_card_balance.csv | максимум SK_DPD_DEF: дней просрочки по карте (толеранс) |
| 119 | `CC_CNT_DRAWINGS_CURRENT_SUM` | Int64 | credit_card_balance.csv | сумма CNT_DRAWINGS_CURRENT: число снятий по карте |
| 120 | `CC_CNT_DRAWINGS_CURRENT_MEAN` | Float64 | credit_card_balance.csv | среднее CNT_DRAWINGS_CURRENT: число снятий по карте |
