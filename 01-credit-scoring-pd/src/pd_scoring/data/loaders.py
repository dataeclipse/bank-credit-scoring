from __future__ import annotations

from pathlib import Path

import polars as pl


def load_table(raw_dir: Path, name: str, *, cache_dir: Path | None = None) -> pl.DataFrame:
    csv_path = raw_dir / f"{name}.csv"
    cache = cache_dir if cache_dir is not None else raw_dir.parent / "interim"
    parquet_path = cache / f"{name}.parquet"
    if parquet_path.exists():
        return pl.read_parquet(parquet_path)
    if not csv_path.exists():
        msg = f"{csv_path} not found. Download the data first: pd-scoring-ingest --yes"
        raise FileNotFoundError(msg)
    frame = pl.read_csv(csv_path, infer_schema_length=20000, null_values=["", "XNA"])
    cache.mkdir(parents=True, exist_ok=True)
    frame.write_parquet(parquet_path)
    return frame
