# Bank ML Portfolio

Production-grade ML/DS проекты под банковские задачи, собранные end-to-end:
данные → модель → калиброванный, объяснимый, мониторируемый сервис → Docker + CI.

## Featured — Credit Scoring (PD) as a Service · v1.0.0

[![CI](https://github.com/dataeclipse/bank-credit-scoring/actions/workflows/ci.yml/badge.svg)](https://github.com/dataeclipse/bank-credit-scoring/actions/workflows/ci.yml)

Вероятность дефолта по кредитной заявке как REST-сервис: WOE-scorecard рядом с LightGBM
(Gini **0.579**), калибровка вероятностей (ECE **0.003**), SHAP reason codes, fairness-анализ,
мониторинг дрейфа (PSI/CSI), Docker + GitHub Actions. Model card в духе НБРК / SR 11-7.

→ **[01-credit-scoring-pd/](01-credit-scoring-pd/)** — полный README, model card, метрики, `/score`.

## Stack
Python 3.12 · uv · LightGBM / CatBoost · scikit-learn · optbinning (WOE) · SHAP · Fairlearn ·
Evidently · FastAPI · MLflow · PostgreSQL · Docker · GitHub Actions.

## Status
Проект 1 (кредитный скоринг) — зарелижен (**v1.0.0**). Дальнейшие банковские ML-проекты
в работе.

## License
[MIT](LICENSE)
