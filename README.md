# Bank ML Portfolio

Banking ML/DS projects, each built from raw data through to a running service.

## Featured: Credit Scoring (PD) as a Service · v1.0.0

[![CI](https://github.com/dataeclipse/bank-credit-scoring/actions/workflows/ci.yml/badge.svg)](https://github.com/dataeclipse/bank-credit-scoring/actions/workflows/ci.yml)

A REST service that estimates probability of default on a loan application. It pairs a WOE
scorecard with LightGBM (Gini 0.579), calibrates the probabilities (ECE 0.003), returns SHAP
reason codes, checks fairness, and monitors input drift (PSI/CSI). It ships in Docker and is
tested in GitHub Actions. The model card follows NBRK / SR 11-7 expectations.

See **[01-credit-scoring-pd/](01-credit-scoring-pd/)** for the full README, model card, metrics,
and the `/score` API.

## Stack
Python 3.12 · uv · LightGBM / CatBoost · scikit-learn · optbinning (WOE) · SHAP · Fairlearn ·
Evidently · FastAPI · MLflow · PostgreSQL · Docker · GitHub Actions.

## Status
Project 1 (credit scoring) is released as v1.0.0. Further banking ML projects are in progress.

## License
[MIT](LICENSE)
