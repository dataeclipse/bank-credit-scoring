"""Оркестратор Фазы 2: scorecard + LightGBM + CatBoost → метрики на одном holdout → MLflow → docs.

Сравнение честное: все модели на одной фиче-базе, оценка на общем holdout (Фаза 1 split).
Scorecard: WOE + IV-отбор. GBDT: нативные cat/NaN. Различия — в docs/model_comparison.md.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import joblib

from pd_scoring.config import get_settings
from pd_scoring.logging_config import configure_logging, get_logger
from pd_scoring.models.dataset import ModelingData, load_modeling_data
from pd_scoring.models.gbdt import GbdtResult, train_catboost, train_lightgbm
from pd_scoring.models.scorecard import ScorecardResult, fit_scorecard
from pd_scoring.models.tracking import log_candidate, setup_mlflow
from pd_scoring.models.tuning import tune_catboost, tune_lightgbm
from pd_scoring.seeds import set_seeds

DEFAULT_LGBM = {
    "learning_rate": 0.05,
    "num_leaves": 64,
    "min_child_samples": 50,
    "subsample": 0.8,
    "subsample_freq": 1,
    "colsample_bytree": 0.8,
    "reg_lambda": 1.0,
}
DEFAULT_CATBOOST = {"learning_rate": 0.05, "depth": 6, "l2_leaf_reg": 3.0}


def _fmt(value: Any) -> str:
    return f"{value:.4f}" if isinstance(value, float) else str(value)


def _df_to_md(frame: Any, columns: list[str], max_rows: int | None = None) -> str:
    rows = frame[columns].head(max_rows) if max_rows else frame[columns]
    head = "| " + " | ".join(columns) + " |"
    sep = "|" + "|".join(["---"] * len(columns)) + "|"
    body = ["| " + " | ".join(_fmt(r[c]) for c in columns) + " |" for _, r in rows.iterrows()]
    return "\n".join([head, sep, *body])


def _metrics_table(results: dict[str, dict[str, float]]) -> str:
    head = "| Модель | ROC-AUC | PR-AUC | KS | Gini |\n|---|---|---|---|---|"
    rows = [
        f"| {name} | {m['roc_auc']:.4f} | {m['pr_auc']:.4f} | {m['ks']:.4f} | {m['gini']:.4f} |"
        for name, m in results.items()
    ]
    return "\n".join([head, *rows])


def _write_comparison(
    docs_dir: Path,
    results: dict[str, dict[str, float]],
    sc: ScorecardResult,
    n_features: int,
    n_holdout: int,
) -> None:
    lines = [
        "# Сравнение моделей (Фаза 2)",
        "",
        f"Holdout: {n_holdout} заявок (Фаза 1 split, seed 42). "
        f"Фиче-база: {n_features} фич для всех моделей.",
        "",
        "## Метрики на holdout",
        _metrics_table(results),
        "",
        "## Scorecard — честная CV (биннинг внутри фолдов)",
        _metrics_table({"scorecard (CV mean)": sc.cv_metrics}),
        "",
        "## Методология",
        "- HPO (Optuna, TPE, seed) на стратифицированной подвыборке train; финальные модели — "
        "на полном train. CatBoost: `max_ctr_complexity=1` (без комбинаций категориальных).",
        "",
        "## Консистентность фиче-базы",
        f"- Вход одинаковый: **{n_features} фич**.",
        f"- **Scorecard**: WOE + отбор по IV≥0.02 → **{len(sc.selected_features)}** фич "
        "(парсимоничен по дизайну).",
        "- **LightGBM**: категориальные как `category` dtype, пропуски нативно.",
        "- **CatBoost**: нативные категориальные (без one-hot) + пропуски нативно.",
        "- Расхождение: scorecard берёт подмножество (IV-отбор) и WOE; GBDT — все фичи и "
        "сырые пропуски. Сравнение корректно (один holdout, вход), интерпретация разная.",
    ]
    (docs_dir / "model_comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_selection(
    docs_dir: Path, results: dict[str, dict[str, float]], sc: ScorecardResult
) -> None:
    ranked = sorted(results.items(), key=lambda kv: kv[1]["gini"], reverse=True)
    best_name, best = ranked[0]
    scorecard = results["scorecard"]
    gap = best["gini"] - scorecard["gini"]
    if best_name != "scorecard" and gap > 0.03:
        verdict = (
            f"**В прод: {best_name}** (Gini {best['gini']:.3f}, KS {best['ks']:.3f}) — выше "
            f"scorecard (Gini {scorecard['gini']:.3f}) на Δ Gini {gap:.3f}. Scorecard — "
            "интерпретируемый challenger и регуляторная объяснимость (баллы/reason codes)."
        )
    else:
        verdict = (
            f"**В прод: scorecard** — отставание от лучшего GBDT по Gini невелико ({gap:.3f}), а "
            "интерпретируемость и регуляторная защищаемость перевешивают."
        )
    lines = [
        "# Выбор модели в прод (Фаза 2)",
        "",
        "## Ранжирование по Gini (holdout)",
        _metrics_table(dict(ranked)),
        "",
        "## Решение",
        verdict,
        "",
        "## Trade-off «качество ↔ интерпретируемость»",
        "- **GBDT (LightGBM/CatBoost)**: выше Gini/KS, ловят нелинейности и взаимодействия; "
        "нативно работают с пропусками и cat. Минус — чёрный ящик (SHAP в Фазе 3).",
        "- **Scorecard (WOE + логистика)**: прозрачные баллы, монотонные бины, IV-отбор; легко "
        "валидируется и объясняется регулятору. Минус — обычно ниже по качеству.",
        f"- Финальный scorecard использует {len(sc.selected_features)} фич против полной базы "
        "у GBDT.",
        "",
        "_Калибровка вероятностей, SHAP reason codes и fairness — Фаза 3._",
    ]
    (docs_dir / "model_selection.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_scorecard_docs(docs_dir: Path, sc: ScorecardResult) -> None:
    selected_iv = sc.iv_table[sc.iv_table["selected"]]
    lines = [
        "# Scorecard — фичи, IV и баллы (Фаза 2)",
        "",
        f"Отобрано **{len(sc.selected_features)}** фич по IV≥0.02. Полная таблица баллов — "
        "`scorecard_points.csv`.",
        "",
        "## Отобранные фичи по IV",
        _df_to_md(selected_iv, ["name", "dtype", "iv"]),
    ]
    (docs_dir / "scorecard.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    sc.points_table.to_csv(docs_dir / "scorecard_points.csv", index=False)


def _run_scorecard(
    data: ModelingData, seed: int, docs_dir: Path, models_dir: Path
) -> ScorecardResult:
    sc = fit_scorecard(data, seed=seed)
    models_dir.mkdir(parents=True, exist_ok=True)
    sc_path = models_dir / "scorecard.joblib"
    joblib.dump(sc.model, sc_path)
    _write_scorecard_docs(docs_dir, sc)
    log_candidate(
        run_name="scorecard",
        flavor="scorecard",
        model=sc.model,
        params={"iv_min": 0.02, "n_selected": len(sc.selected_features)},
        metrics={"holdout": sc.holdout_metrics, "cv": sc.cv_metrics},
        artifacts=[docs_dir / "scorecard.md", docs_dir / "scorecard_points.csv"],
        scorecard_path=sc_path,
    )
    return sc


def _run_gbdt(
    name: str,
    flavor: str,
    result: GbdtResult,
    params: dict[str, Any],
) -> None:
    log_candidate(
        run_name=name,
        flavor=flavor,
        model=result.model,
        params={**params, "best_iteration": result.best_iteration},
        metrics={"holdout": result.holdout_metrics},
        artifacts=[],
    )


def _subsample(data: ModelingData, n: int, seed: int) -> ModelingData:
    """Стратифицированный subsample train/holdout для быстрой сквозной проверки пайплайна."""
    from sklearn.model_selection import train_test_split

    def take(x: Any, y: Any, k: int) -> Any:
        if len(y) <= k:
            return x.reset_index(drop=True), y.reset_index(drop=True)
        x_s, _, y_s, _ = train_test_split(x, y, train_size=k, stratify=y, random_state=seed)
        return x_s.reset_index(drop=True), y_s.reset_index(drop=True)

    x_train, y_train = take(data.X_train, data.y_train, n)
    x_holdout, y_holdout = take(data.X_holdout, data.y_holdout, max(n // 4, 500))
    return ModelingData(
        x_train, y_train, x_holdout, y_holdout, data.feature_names, data.categorical_features
    )


def main(argv: list[str] | None = None) -> int:
    """CLI ``pd-scoring-train``: обучить 3 модели, сравнить на holdout, залогировать в MLflow."""
    parser = argparse.ArgumentParser(description="Train scorecard + GBDT, compare, log to MLflow.")
    parser.add_argument("--trials", type=int, default=30, help="Optuna trials на модель")
    parser.add_argument("--no-tune", action="store_true", help="без Optuna (дефолтные параметры)")
    parser.add_argument("--tune-sample", type=int, default=40000, help="размер подвыборки для HPO")
    parser.add_argument(
        "--sample", type=int, default=None, help="subsample train для smoke-проверки"
    )
    parser.add_argument("--docs-dir", default="docs")
    args = parser.parse_args(argv)

    configure_logging()
    log = get_logger("train")
    settings = get_settings()
    seed = settings.random_seed
    set_seeds(seed)
    setup_mlflow(settings)

    docs_dir = Path(args.docs_dir)
    docs_dir.mkdir(parents=True, exist_ok=True)
    models_dir = settings.model_dir

    data = load_modeling_data()
    if args.sample:
        data = _subsample(data, args.sample, seed)
    log.info(
        "data_loaded",
        train=len(data.y_train),
        holdout=len(data.y_holdout),
        features=len(data.feature_names),
    )

    results: dict[str, dict[str, float]] = {}

    # Гиперпараметры подбираем на стратифицированном подвыборке (быстро), финал — на полном train.
    tune_data = data
    if not args.no_tune and len(data.y_train) > args.tune_sample:
        tune_data = _subsample(data, args.tune_sample, seed)
        log.info("tuning_subsample", rows=len(tune_data.y_train))

    sc = _run_scorecard(data, seed, docs_dir, models_dir)
    results["scorecard"] = sc.holdout_metrics
    log.info(
        "scorecard_done", **{f"holdout_{k}": round(v, 4) for k, v in sc.holdout_metrics.items()}
    )

    lgbm_params = (
        DEFAULT_LGBM if args.no_tune else tune_lightgbm(tune_data, seed=seed, n_trials=args.trials)
    )
    lgbm = train_lightgbm(data, lgbm_params, seed=seed)
    _run_gbdt("lightgbm", "lightgbm", lgbm, lgbm_params)
    results["lightgbm"] = lgbm.holdout_metrics
    log.info(
        "lightgbm_done", **{f"holdout_{k}": round(v, 4) for k, v in lgbm.holdout_metrics.items()}
    )

    cat_params = (
        DEFAULT_CATBOOST
        if args.no_tune
        else tune_catboost(tune_data, seed=seed, n_trials=args.trials)
    )
    catboost = train_catboost(data, cat_params, seed=seed)
    _run_gbdt("catboost", "catboost", catboost, cat_params)
    results["catboost"] = catboost.holdout_metrics
    log.info(
        "catboost_done",
        **{f"holdout_{k}": round(v, 4) for k, v in catboost.holdout_metrics.items()},
    )

    _write_comparison(docs_dir, results, sc, len(data.feature_names), len(data.y_holdout))
    _write_selection(docs_dir, results, sc)
    log.info("phase2_done", models=list(results), docs=str(docs_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
