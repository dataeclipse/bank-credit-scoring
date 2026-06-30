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
    head = "| Model | ROC-AUC | PR-AUC | KS | Gini |\n|---|---|---|---|---|"
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
        "# Model comparison (Phase 2)",
        "",
        f"Holdout: {n_holdout} applications (Phase 1 split, seed 42). "
        f"Feature base: {n_features} features for all models.",
        "",
        "## Metrics on holdout",
        _metrics_table(results),
        "",
        "## Scorecard - honest CV (binning inside folds)",
        _metrics_table({"scorecard (CV mean)": sc.cv_metrics}),
        "",
        "## Methodology",
        "- HPO (Optuna, TPE, seed) on a stratified train subsample; final models - "
        "on the full train. CatBoost: `max_ctr_complexity=1` (no categorical combinations).",
        "",
        "## Feature base consistency",
        f"- Input is identical: **{n_features} features**.",
        f"- **Scorecard**: WOE + selection by IV≥0.02 → **{len(sc.selected_features)}** features "
        "(parsimonious by design).",
        "- **LightGBM**: categoricals as `category` dtype, missing values handled natively.",
        "- **CatBoost**: native categoricals (no one-hot) + missing values handled natively.",
        "- Difference: scorecard takes a subset (IV selection) and WOE; GBDT - all features and "
        "raw missing values. The comparison is fair (one holdout, same input), "
        "interpretation differs.",
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
            f"**In prod: {best_name}** (Gini {best['gini']:.3f}, KS {best['ks']:.3f}) - above "
            f"scorecard (Gini {scorecard['gini']:.3f}) by Δ Gini {gap:.3f}. Scorecard - an "
            "interpretable challenger and regulatory explainability (points/reason codes)."
        )
    else:
        verdict = (
            f"**In prod: scorecard** - the gap to the best GBDT by Gini is small ({gap:.3f}), and "
            "interpretability and regulatory defensibility outweigh it."
        )
    lines = [
        "# Production model selection (Phase 2)",
        "",
        "## Ranking by Gini (holdout)",
        _metrics_table(dict(ranked)),
        "",
        "## Decision",
        verdict,
        "",
        '## Trade-off "quality ↔ interpretability"',
        "- **GBDT (LightGBM/CatBoost)**: higher Gini/KS, capture nonlinearities and interactions; "
        "handle missing values and cat natively. Downside - a black box (SHAP in Phase 3).",
        "- **Scorecard (WOE + logistic)**: transparent points, monotonic bins, IV selection; easy "
        "to validate and explain to a regulator. Downside - usually lower quality.",
        f"- The final scorecard uses {len(sc.selected_features)} features versus the full base "
        "of GBDT.",
        "",
        "_Probability calibration, SHAP reason codes and fairness - Phase 3._",
    ]
    (docs_dir / "model_selection.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_scorecard_docs(docs_dir: Path, sc: ScorecardResult) -> None:
    selected_iv = sc.iv_table[sc.iv_table["selected"]]
    lines = [
        "# Scorecard - features, IV and points (Phase 2)",
        "",
        f"Selected **{len(sc.selected_features)}** features by IV≥0.02. Full points table - "
        "`scorecard_points.csv`.",
        "",
        "## Selected features by IV",
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
    parser = argparse.ArgumentParser(description="Train scorecard + GBDT, compare, log to MLflow.")
    parser.add_argument("--trials", type=int, default=30, help="Optuna trials per model")
    parser.add_argument("--no-tune", action="store_true", help="no Optuna (default parameters)")
    parser.add_argument("--tune-sample", type=int, default=40000, help="subsample size for HPO")
    parser.add_argument("--gpu", action="store_true", help="CatBoost on GPU (task_type=GPU)")
    parser.add_argument(
        "--sample", type=int, default=None, help="subsample train for a smoke check"
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

    cat_task = "GPU" if args.gpu else "CPU"
    cat_params = (
        DEFAULT_CATBOOST
        if args.no_tune
        else tune_catboost(tune_data, seed=seed, n_trials=args.trials, task_type=cat_task)
    )
    catboost = train_catboost(data, cat_params, seed=seed, task_type=cat_task)
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
