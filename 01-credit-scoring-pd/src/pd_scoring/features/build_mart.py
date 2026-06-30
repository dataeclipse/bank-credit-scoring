from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import polars as pl

from pd_scoring.config import get_settings
from pd_scoring.data.loaders import load_table
from pd_scoring.data.split import make_split
from pd_scoring.features.aggregations import (
    aggregate_bureau,
    aggregate_bureau_balance,
    aggregate_credit_card,
    aggregate_installments,
    aggregate_pos,
    aggregate_previous,
    safe_div,
)
from pd_scoring.features.schema import (
    FeatureDoc,
    build_feature_schema,
    write_data_dictionary,
    write_feature_schema,
)
from pd_scoring.logging_config import configure_logging, get_logger
from pd_scoring.seeds import set_seeds

DAYS_EMPLOYED_ANOMALY = 365243


_APP_RAW: tuple[tuple[str, str], ...] = (
    ("NAME_CONTRACT_TYPE", "credit type (cash/revolving)"),
    ("CODE_GENDER", "client gender"),
    ("FLAG_OWN_CAR", "owns a car"),
    ("FLAG_OWN_REALTY", "owns real estate"),
    ("CNT_CHILDREN", "number of children"),
    ("AMT_INCOME_TOTAL", "total income"),
    ("AMT_CREDIT", "credit amount on the application"),
    ("AMT_ANNUITY", "annuity payment"),
    ("AMT_GOODS_PRICE", "price of the goods financed by the credit"),
    ("NAME_INCOME_TYPE", "income source type"),
    ("NAME_EDUCATION_TYPE", "education level"),
    ("NAME_FAMILY_STATUS", "family status"),
    ("NAME_HOUSING_TYPE", "housing type"),
    ("REGION_POPULATION_RELATIVE", "relative population of the region"),
    ("DAYS_BIRTH", "age in days (<0)"),
    ("DAYS_EMPLOYED", "employment length in days (<0; 365243 - anomaly, cleaned)"),
    ("DAYS_REGISTRATION", "time since registration change (days)"),
    ("DAYS_ID_PUBLISH", "time since ID document change (days)"),
    ("OWN_CAR_AGE", "car age"),
    ("FLAG_EMP_PHONE", "work phone provided"),
    ("FLAG_WORK_PHONE", "work mobile provided"),
    ("FLAG_PHONE", "home phone provided"),
    ("FLAG_EMAIL", "email provided"),
    ("OCCUPATION_TYPE", "occupation"),
    ("CNT_FAM_MEMBERS", "family members"),
    ("REGION_RATING_CLIENT", "client region rating"),
    ("REGION_RATING_CLIENT_W_CITY", "region rating including city"),
    ("EXT_SOURCE_1", "external scoring score 1"),
    ("EXT_SOURCE_2", "external scoring score 2"),
    ("EXT_SOURCE_3", "external scoring score 3"),
    ("DAYS_LAST_PHONE_CHANGE", "time since phone change (days)"),
    ("AMT_REQ_CREDIT_BUREAU_QRT", "bureau inquiries in the last quarter"),
    ("AMT_REQ_CREDIT_BUREAU_YEAR", "bureau inquiries in the last year"),
    ("ORGANIZATION_TYPE", "employer organization type"),
)


_APP_ENGINEERED: tuple[tuple[str, str], ...] = (
    ("DAYS_EMPLOYED_ANOM", "employment anomaly flag (DAYS_EMPLOYED==365243)"),
    ("CREDIT_INCOME_RATIO", "credit amount / income"),
    ("ANNUITY_INCOME_RATIO", "annuity / income"),
    ("CREDIT_ANNUITY_RATIO", "credit amount / annuity (term proxy)"),
    ("GOODS_CREDIT_RATIO", "goods price / credit amount"),
    ("EMPLOYED_BIRTH_RATIO", "employment length / age"),
    ("INCOME_PER_PERSON", "income per family member"),
)

_APP_KEEP = [name for name, _ in _APP_RAW]
APPLICATION_DOCS: list[FeatureDoc] = [
    FeatureDoc(name, "application.csv", "", desc) for name, desc in (*_APP_RAW, *_APP_ENGINEERED)
]


def _prepare_application(df: pl.DataFrame, *, is_train: bool) -> pl.DataFrame:
    keep = ["SK_ID_CURR", *[c for c in _APP_KEEP if c in df.columns]]
    out = df.select(keep)
    out = out.with_columns(
        (pl.col("DAYS_EMPLOYED") == DAYS_EMPLOYED_ANOMALY).cast(pl.Int8).alias("DAYS_EMPLOYED_ANOM")
    )
    out = out.with_columns(
        pl.when(pl.col("DAYS_EMPLOYED") == DAYS_EMPLOYED_ANOMALY)
        .then(None)
        .otherwise(pl.col("DAYS_EMPLOYED"))
        .alias("DAYS_EMPLOYED")
    )
    out = out.with_columns(
        safe_div(pl.col("AMT_CREDIT"), pl.col("AMT_INCOME_TOTAL")).alias("CREDIT_INCOME_RATIO"),
        safe_div(pl.col("AMT_ANNUITY"), pl.col("AMT_INCOME_TOTAL")).alias("ANNUITY_INCOME_RATIO"),
        safe_div(pl.col("AMT_CREDIT"), pl.col("AMT_ANNUITY")).alias("CREDIT_ANNUITY_RATIO"),
        safe_div(pl.col("AMT_GOODS_PRICE"), pl.col("AMT_CREDIT")).alias("GOODS_CREDIT_RATIO"),
        safe_div(pl.col("DAYS_EMPLOYED"), pl.col("DAYS_BIRTH")).alias("EMPLOYED_BIRTH_RATIO"),
        safe_div(pl.col("AMT_INCOME_TOTAL"), pl.col("CNT_FAM_MEMBERS")).alias("INCOME_PER_PERSON"),
    )
    return out.with_columns(is_train=pl.lit(is_train))


def build_application_features(
    app_train: pl.DataFrame, app_test: pl.DataFrame
) -> tuple[pl.DataFrame, list[FeatureDoc]]:
    train = _prepare_application(app_train, is_train=True).join(
        app_train.select("SK_ID_CURR", pl.col("TARGET").cast(pl.Int8)),
        on="SK_ID_CURR",
        how="left",
    )
    test = _prepare_application(app_test, is_train=False).with_columns(
        pl.lit(None, dtype=pl.Int8).alias("TARGET")
    )
    base = pl.concat([train, test], how="diagonal")
    return base, list(APPLICATION_DOCS)


def build_mart(raw_dir: Path) -> tuple[pl.DataFrame, list[FeatureDoc]]:
    set_seeds(get_settings().random_seed)
    mart, docs = build_application_features(
        load_table(raw_dir, "application_train"),
        load_table(raw_dir, "application_test"),
    )
    results = [
        aggregate_bureau(
            load_table(raw_dir, "bureau"),
            aggregate_bureau_balance(load_table(raw_dir, "bureau_balance")),
        ),
        aggregate_previous(load_table(raw_dir, "previous_application")),
        aggregate_installments(load_table(raw_dir, "installments_payments")),
        aggregate_pos(load_table(raw_dir, "POS_CASH_balance")),
        aggregate_credit_card(load_table(raw_dir, "credit_card_balance")),
    ]
    for result in results:
        mart = mart.join(result.frame, on="SK_ID_CURR", how="left")
        docs.extend(result.docs)
    return mart, docs


def write_mart_to_postgres(
    mart: pl.DataFrame, database_url: str, table: str = "feature_mart"
) -> None:
    mart.write_database(
        table_name=table, connection=database_url, if_table_exists="replace", engine="sqlalchemy"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build client-level feature mart.")
    parser.add_argument(
        "--raw-dir", default=None, help="directory with CSV files (default <data_dir>/raw)"
    )
    parser.add_argument(
        "--out-dir", default=None, help="where to write the mart (default <data_dir>/processed)"
    )
    parser.add_argument(
        "--docs-dir", default="docs", help="where to write the schema and dictionary"
    )
    parser.add_argument("--postgres", action="store_true", help="also write the mart to PostgreSQL")
    args = parser.parse_args(argv)

    configure_logging()
    log = get_logger("build_mart")
    settings = get_settings()
    raw_dir = Path(args.raw_dir) if args.raw_dir else settings.data_dir / "raw"
    out_dir = Path(args.out_dir) if args.out_dir else settings.data_dir / "processed"
    docs_dir = Path(args.docs_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    mart, docs = build_mart(raw_dir)
    mart.write_parquet(out_dir / "mart.parquet")

    schema = build_feature_schema(mart, docs)
    write_feature_schema(schema, docs_dir / "feature_schema.json")
    write_data_dictionary(schema, docs_dir / "data_dictionary.md")

    split = make_split(mart.select("SK_ID_CURR", "TARGET"))
    split_frame = pl.DataFrame(
        {
            "SK_ID_CURR": [*split.train_ids, *split.test_ids],
            "split": ["train"] * split.n_train + ["test"] * split.n_test,
        }
    )
    split_frame.write_parquet(out_dir / "split.parquet")
    split_meta: dict[str, Any] = {
        "seed": split.seed,
        "test_size": split.test_size,
        "n_train": split.n_train,
        "n_test": split.n_test,
    }
    (out_dir / "split_meta.json").write_text(
        json.dumps(split_meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if args.postgres and settings.database_url:
        write_mart_to_postgres(mart, settings.database_url)
        log.info("mart_written_to_postgres", table="feature_mart")

    log.info(
        "mart_built",
        rows=mart.height,
        features=schema["n_features"],
        schema_hash=schema["features_hash"],
        out=str(out_dir / "mart.parquet"),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
