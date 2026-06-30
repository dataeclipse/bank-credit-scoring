from __future__ import annotations

import polars as pl
import polars.selectors as cs


def target_rate(df: pl.DataFrame, target: str = "TARGET") -> dict[str, float]:
    labeled = df.filter(pl.col(target).is_not_null())
    n = labeled.height
    positives = int(labeled.select(pl.col(target).sum()).item()) if n else 0
    return {
        "n": float(n),
        "positives": float(positives),
        "rate": positives / n if n else 0.0,
    }


def missingness(df: pl.DataFrame) -> pl.DataFrame:
    n = df.height
    null_counts = df.null_count()
    records = [
        {
            "column": col,
            "null_count": int(null_counts[col].item()),
            "null_frac": (int(null_counts[col].item()) / n if n else 0.0),
        }
        for col in df.columns
    ]
    return pl.DataFrame(records).sort("null_frac", descending=True)


def numeric_summary(df: pl.DataFrame, columns: list[str]) -> pl.DataFrame:
    return df.select(columns).describe()


def top_correlations(
    df: pl.DataFrame, target: str = "TARGET", k: int = 15
) -> list[tuple[str, float]]:
    labeled = df.filter(pl.col(target).is_not_null())
    numeric_cols = [c for c in labeled.select(cs.numeric()).columns if c != target]
    correlations: list[tuple[str, float]] = []
    for col in numeric_cols:
        value = labeled.select(pl.corr(pl.col(col), pl.col(target))).item()
        if value is not None:
            correlations.append((col, float(value)))
    correlations.sort(key=lambda pair: abs(pair[1]), reverse=True)
    return correlations[:k]


def days_employed_anomaly(
    df: pl.DataFrame, column: str = "DAYS_EMPLOYED", anomaly: int = 365243
) -> dict[str, float]:
    if column not in df.columns:
        return {"anomaly_count": 0.0, "anomaly_frac": 0.0}
    n = df.height
    count = int(df.select((pl.col(column) == anomaly).sum()).item())
    return {"anomaly_count": float(count), "anomaly_frac": (count / n if n else 0.0)}
