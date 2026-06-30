# data/

The directory is **in `.gitignore`** - datasets are not committed (we keep only this README).

Phase 1 places **Home Credit Default Risk** (Kaggle) here:
`application_train.csv`, `application_test.csv`, `bureau.csv`, `bureau_balance.csv`,
`previous_application.csv`, `installments_payments.csv`, `credit_card_balance.csv`,
`POS_CASH_balance.csv`.

## Download

```bash
# 1. Set up Kaggle credentials (one of):
#    - environment variables KAGGLE_USERNAME / KAGGLE_KEY
#    - file ~/.kaggle/kaggle.json  (also in .gitignore - NEVER commit it)
# 2. Run ingest:
uv run python -m pd_scoring.data.ingest   # Phase 1: still a stub
```
