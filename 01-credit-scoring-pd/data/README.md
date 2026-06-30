# data/

Каталог **в `.gitignore`** - датасеты не коммитятся (держим только этот README).

Сюда Фаза 1 кладёт **Home Credit Default Risk** (Kaggle):
`application_train.csv`, `application_test.csv`, `bureau.csv`, `bureau_balance.csv`,
`previous_application.csv`, `installments_payments.csv`, `credit_card_balance.csv`,
`POS_CASH_balance.csv`.

## Загрузка

```bash
# 1. Настрой Kaggle-креды (одно из):
#    - переменные KAGGLE_USERNAME / KAGGLE_KEY
#    - файл ~/.kaggle/kaggle.json  (тоже в .gitignore - НИКОГДА не коммить)
# 2. Запусти ingest:
uv run python -m pd_scoring.data.ingest   # Фаза 1: пока заглушка
```
