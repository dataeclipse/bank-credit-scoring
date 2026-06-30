from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import shap  # noqa: E402

from pd_scoring.config import get_settings  # noqa: E402
from pd_scoring.logging_config import configure_logging, get_logger  # noqa: E402
from pd_scoring.models.calibration import CalibrationResult, calibrate  # noqa: E402
from pd_scoring.models.dataset import ModelingData, load_modeling_data  # noqa: E402
from pd_scoring.models.explain import (  # noqa: E402
    global_importance,
    load_feature_descriptions,
    reason_codes,
)
from pd_scoring.models.fairness import GroupFairness, age_bands, fairness_report  # noqa: E402
from pd_scoring.models.gbdt import to_lightgbm_frame  # noqa: E402
from pd_scoring.scoring import ReasonCode  # noqa: E402
from pd_scoring.seeds import set_seeds  # noqa: E402


def _metric_pair_table(table: dict[str, dict[str, float]]) -> str:
    head = "| Variant | Brier ↓ | ECE ↓ |\n|---|---|---|"
    rows = [f"| {name} | {m['brier']:.4f} | {m['ece']:.4f} |" for name, m in table.items()]
    return "\n".join([head, *rows])


def _reliability_figure(cal: CalibrationResult, path: Path) -> None:
    plt.figure(figsize=(5, 5))
    plt.plot([0, 1], [0, 1], "--", color="gray", label="ideal")
    for name, (mean_pred, frac_pos) in cal.reliability.items():
        plt.plot(mean_pred, frac_pos, marker="o", label=name)
    plt.xlabel("Mean predicted PD")
    plt.ylabel("Observed default frequency")
    plt.title("Reliability curve (holdout)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=110)
    plt.close()


def _shap_figures(
    model: Any, features: Any, importance: list[tuple[str, float]], img_dir: Path
) -> None:
    top = importance[:15]
    plt.figure(figsize=(7, 5))
    plt.barh(
        [name for name, _ in reversed(top)], [val for _, val in reversed(top)], color="#4c78a8"
    )
    plt.xlabel("mean(|SHAP|)")
    plt.title("Global feature importance (top-15)")
    plt.tight_layout()
    plt.savefig(img_dir / "shap_bar.png", dpi=110)
    plt.close()

    shap_values = shap.TreeExplainer(model).shap_values(features)
    if isinstance(shap_values, list):
        shap_values = shap_values[1]
    plt.figure()
    shap.summary_plot(shap_values, features, show=False, max_display=15)
    plt.tight_layout()
    plt.savefig(img_dir / "shap_beeswarm.png", dpi=110, bbox_inches="tight")
    plt.close()


def _codes_md(title: str, pd_value: float, codes: list[ReasonCode]) -> list[str]:
    lines = [f"**{title}** (PD = {pd_value:.3f}):", ""]
    for code in codes:
        sign = "+" if code.contribution > 0 else "−"
        lines.append(
            f"- `{code.feature}` - {code.description} (SHAP {sign}{abs(code.contribution):.3f})"
        )
    lines.append("")
    return lines


def _write_calibration_md(docs: Path, cal: CalibrationResult) -> None:
    table = cal.metrics_table
    best_overall = min(table, key=lambda k: table[k]["brier"])
    raw_ece = table["raw"]["ece"]
    if best_overall == "raw":
        verdict = [
            f"The model is **already well calibrated** (raw ECE {raw_ece:.4f} < 0.01): "
            "isotonic/Platt",
            f"do not reduce Brier/ECE. In prod - raw PD; the `{cal.method}` calibrator is kept as",
            "a safeguard (for example, in case of drift - Phase 4).",
        ]
    else:
        verdict = [
            f"**Best method: {best_overall}** - reduces Brier/ECE versus raw. The calibrated PD",
            "is closer to the observed default frequency (see reliability curve).",
        ]
    lines = [
        "# Probability calibration (Phase 3)",
        "",
        "Prod model: LightGBM. The calibrator is trained on a separate calib set (from train), "
        "evaluation is on",
        "holdout. No leakage: the holdout is seen neither by the model nor the calibrator.",
        "",
        "## Brier / ECE on holdout (before and after)",
        _metric_pair_table(table),
        "",
        *verdict,
        "",
        "![reliability](img/reliability.png)",
    ]
    (docs / "calibration.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_explainability_md(
    docs: Path,
    importance: list[tuple[str, float]],
    examples: list[tuple[str, float, list[ReasonCode]]],
) -> None:
    lines = [
        "# Explainability: SHAP reason codes (Phase 3)",
        "",
        "TreeExplainer on the prod LightGBM. Global importance - mean(|SHAP|); reason codes -",
        'top "for/against" factors per application (SHAP sign = direction of the risk effect).',
        "",
        "## Global importance (top-15)",
        "| # | Feature | mean(\\|SHAP\\|) |",
        "|---|------|---------------|",
    ]
    for i, (name, value) in enumerate(importance[:15], start=1):
        lines.append(f"| {i} | `{name}` | {value:.4f} |")
    lines += ["", "![bar](img/shap_bar.png)", "", "![beeswarm](img/shap_beeswarm.png)", ""]
    lines += ["## Reason code examples", ""]
    for title, pd_value, codes in examples:
        lines += _codes_md(title, pd_value, codes)
    (docs / "explainability.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_fairness_md(docs: Path, threshold: float, report: dict[str, GroupFairness]) -> None:
    lines = [
        "# Fairness (Phase 3)",
        "",
        f"Decision: PD ≥ {threshold:.3f} → default (rejection). Threshold - KS point (Youden's J).",
        "Favorable outcome = approval (PD < threshold). Fairlearn metrics over proxy groups.",
        "",
    ]
    for name, group in report.items():
        lines += [
            f"## Group: {name}",
            "",
            "| Subgroup | selection_rate (rejection) | TPR | FPR | approval |",
            "|---|---|---|---|---|",
        ]
        approval = group.approval_rate
        for sub, row in group.by_group.iterrows():
            key = str(sub)
            lines.append(
                f"| {key} | {row['selection_rate']:.3f} | {row['tpr']:.3f} | "
                f"{row['fpr']:.3f} | {approval.get(key, float('nan')):.3f} |"
            )
        lines += [
            "",
            f"- Demographic parity diff: **{group.demographic_parity_diff:.3f}**",
            f"- Equalized odds diff: **{group.equalized_odds_diff:.3f}**",
            f"- Disparate impact (4/5 rule, approval): **{group.disparate_impact:.3f}** "
            "(threshold 0.8: below - bias indicator)",
            "",
        ]
    lines += [
        "## How this is handled in a bank",
        "- **Diagnostic, not a verdict**: the Home Credit proxy groups are anonymous; the "
        "result is a bias risk indicator.",
        "- **Mitigation options** (not applied here): reweighting/resampling by group,",
        "  ThresholdOptimizer (Fairlearn) for equal TPR/FPR, per-group calibration.",
        "- **Regulatory**: fix proxies, feature justification, parity monitoring (Phase 4).",
    ]
    (docs / "fairness.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _reason_examples(
    cal: CalibrationResult, data: ModelingData, descriptions: dict[str, str], top_n: int
) -> list[tuple[str, float, list[ReasonCode]]]:
    frame = to_lightgbm_frame(data.X_holdout, data.categorical_features)
    proba = cal.holdout_proba_calibrated
    hi = int(proba.argmax())
    lo = int(proba.argmin())
    return [
        (
            "High risk (rejection candidate)",
            float(proba[hi]),
            reason_codes(cal.model, frame.iloc[[hi]], descriptions, top_n=top_n),
        ),
        (
            "Low risk (approval candidate)",
            float(proba[lo]),
            reason_codes(cal.model, frame.iloc[[lo]], descriptions, top_n=top_n),
        ),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 3: calibration + SHAP + fairness.")
    parser.add_argument("--docs-dir", default="docs")
    parser.add_argument("--params", default="docs/prod_lgbm_params.json")
    parser.add_argument("--shap-sample", type=int, default=3000)
    parser.add_argument("--top-n", type=int, default=6)
    args = parser.parse_args(argv)

    configure_logging()
    log = get_logger("evaluate")
    settings = get_settings()
    seed = settings.random_seed
    set_seeds(seed)

    docs = Path(args.docs_dir)
    img_dir = docs / "img"
    img_dir.mkdir(parents=True, exist_ok=True)
    params = json.loads(Path(args.params).read_text(encoding="utf-8"))

    data = load_modeling_data()
    cal = calibrate(data, params, seed=seed)
    log.info(
        "calibration_done",
        method=cal.method,
        **{f"{k}_brier": round(v["brier"], 4) for k, v in cal.metrics_table.items()},
    )

    _reliability_figure(cal, img_dir / "reliability.png")
    _write_calibration_md(docs, cal)

    holdout_lgb = to_lightgbm_frame(data.X_holdout, data.categorical_features)
    sample = holdout_lgb.sample(n=min(args.shap_sample, len(holdout_lgb)), random_state=seed)
    importance = global_importance(cal.model, sample)
    _shap_figures(cal.model, sample, importance, img_dir)
    descriptions = load_feature_descriptions(docs / "feature_schema.json")
    examples = _reason_examples(cal, data, descriptions, args.top_n)
    _write_explainability_md(docs, importance, examples)
    log.info("shap_done", top_feature=importance[0][0])

    sensitive = {
        "CODE_GENDER": data.X_holdout["CODE_GENDER"].fillna("XNA").astype(str),
        "AGE_BAND": age_bands(data.X_holdout["DAYS_BIRTH"]).astype("object").fillna("unknown"),
    }
    threshold, report = fairness_report(data.y_holdout, cal.holdout_proba_calibrated, sensitive)
    _write_fairness_md(docs, threshold, report)
    log.info("fairness_done", threshold=round(threshold, 4), groups=list(report))

    settings.model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(cal.calibrator, settings.model_dir / f"calibrator_{cal.method}.joblib")
    log.info("phase3_done", docs=str(docs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
