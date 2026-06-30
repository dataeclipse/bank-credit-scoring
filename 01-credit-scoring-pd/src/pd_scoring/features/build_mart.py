"""Сборка единой client-level витрины фичей Home Credit.

Пайплайн: application (curated + engineered) → join client-level агрегатов всех дочерних
таблиц по SK_ID_CURR → витрина parquet + версионируемая схема + словарь данных + split.
Аномалия DAYS_EMPLOYED==365243 (заглушка пенсионеров) чистится в null с флагом DAYS_EMPLOYED_ANOM.
"""

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

# Curated raw application-фичи: (колонка, описание). Источник истины и для select, и для словаря.
_APP_RAW: tuple[tuple[str, str], ...] = (
    ("NAME_CONTRACT_TYPE", "тип кредита (cash/revolving)"),
    ("CODE_GENDER", "пол клиента"),
    ("FLAG_OWN_CAR", "есть автомобиль"),
    ("FLAG_OWN_REALTY", "есть недвижимость"),
    ("CNT_CHILDREN", "число детей"),
    ("AMT_INCOME_TOTAL", "совокупный доход"),
    ("AMT_CREDIT", "сумма кредита по заявке"),
    ("AMT_ANNUITY", "аннуитетный платёж"),
    ("AMT_GOODS_PRICE", "стоимость товара под кредит"),
    ("NAME_INCOME_TYPE", "тип источника дохода"),
    ("NAME_EDUCATION_TYPE", "уровень образования"),
    ("NAME_FAMILY_STATUS", "семейное положение"),
    ("NAME_HOUSING_TYPE", "тип жилья"),
    ("REGION_POPULATION_RELATIVE", "относительная населённость региона"),
    ("DAYS_BIRTH", "возраст в днях (<0)"),
    ("DAYS_EMPLOYED", "стаж в днях (<0; 365243 — аномалия, чистится)"),
    ("DAYS_REGISTRATION", "давность смены регистрации (дни)"),
    ("DAYS_ID_PUBLISH", "давность смены документа (дни)"),
    ("OWN_CAR_AGE", "возраст автомобиля"),
    ("FLAG_EMP_PHONE", "указан рабочий телефон"),
    ("FLAG_WORK_PHONE", "указан рабочий мобильный"),
    ("FLAG_PHONE", "указан домашний телефон"),
    ("FLAG_EMAIL", "указан email"),
    ("OCCUPATION_TYPE", "профессия"),
    ("CNT_FAM_MEMBERS", "членов семьи"),
    ("REGION_RATING_CLIENT", "рейтинг региона клиента"),
    ("REGION_RATING_CLIENT_W_CITY", "рейтинг региона с учётом города"),
    ("EXT_SOURCE_1", "внешний скоринговый балл 1"),
    ("EXT_SOURCE_2", "внешний скоринговый балл 2"),
    ("EXT_SOURCE_3", "внешний скоринговый балл 3"),
    ("DAYS_LAST_PHONE_CHANGE", "давность смены телефона (дни)"),
    ("AMT_REQ_CREDIT_BUREAU_QRT", "запросов в бюро за квартал"),
    ("AMT_REQ_CREDIT_BUREAU_YEAR", "запросов в бюро за год"),
    ("ORGANIZATION_TYPE", "тип организации-работодателя"),
)

# Engineered application-фичи: (имя, описание).
_APP_ENGINEERED: tuple[tuple[str, str], ...] = (
    ("DAYS_EMPLOYED_ANOM", "флаг аномалии стажа (DAYS_EMPLOYED==365243)"),
    ("CREDIT_INCOME_RATIO", "сумма кредита / доход"),
    ("ANNUITY_INCOME_RATIO", "аннуитет / доход"),
    ("CREDIT_ANNUITY_RATIO", "сумма кредита / аннуитет (прокси срока)"),
    ("GOODS_CREDIT_RATIO", "стоимость товара / сумма кредита"),
    ("EMPLOYED_BIRTH_RATIO", "стаж / возраст"),
    ("INCOME_PER_PERSON", "доход на члена семьи"),
)

_APP_KEEP = [name for name, _ in _APP_RAW]
APPLICATION_DOCS: list[FeatureDoc] = [
    FeatureDoc(name, "application.csv", "", desc) for name, desc in (*_APP_RAW, *_APP_ENGINEERED)
]


def _prepare_application(df: pl.DataFrame, *, is_train: bool) -> pl.DataFrame:
    """Curated application-колонки + чистка аномалии + engineered ratios + флаг is_train."""
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
    """Базовый client-level фрейм из application_train/test (TARGET=null для test)."""
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
    """Собрать витрину: application + все client-level агрегаты, join по SK_ID_CURR."""
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
    """Записать витрину в PostgreSQL (опционально; требует PD_DATABASE_URL)."""
    mart.write_database(
        table_name=table, connection=database_url, if_table_exists="replace", engine="sqlalchemy"
    )


def main(argv: list[str] | None = None) -> int:
    """CLI ``pd-scoring-build-mart``: собрать витрину, записать parquet/схему/словарь/split."""
    parser = argparse.ArgumentParser(description="Build client-level feature mart.")
    parser.add_argument(
        "--raw-dir", default=None, help="каталог с CSV (по умолчанию <data_dir>/raw)"
    )
    parser.add_argument(
        "--out-dir", default=None, help="куда писать mart (по умолчанию <data_dir>/processed)"
    )
    parser.add_argument("--docs-dir", default="docs", help="куда писать схему и словарь")
    parser.add_argument(
        "--postgres", action="store_true", help="дополнительно записать витрину в PostgreSQL"
    )
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
