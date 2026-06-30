"""Client-level агрегации дочерних таблиц Home Credit (без утечек будущего).

Все агрегации построчны по ``SK_ID_CURR`` (group_by) — между клиентами нет перетекания
информации. TARGET в агрегациях не участвует. Движок ``apply_spec`` устойчив к отсутствующим
колонкам (пропускает их вместе с описанием), что упрощает тестирование на синтетике.
"""

from __future__ import annotations

from dataclasses import dataclass

import polars as pl

from pd_scoring.features.schema import FeatureDoc
from pd_scoring.features.specs import (
    BUREAU_SPEC,
    CREDIT_CARD_SPEC,
    INSTALLMENTS_SPEC,
    POS_SPEC,
    PREVIOUS_SPEC,
    STAT_EXPR,
    STAT_RU,
    TableSpec,
)


@dataclass(frozen=True)
class AggResult:
    """Результат агрегации: client-level фрейм + документация его фич."""

    frame: pl.DataFrame
    docs: list[FeatureDoc]


def safe_div(num: pl.Expr, den: pl.Expr) -> pl.Expr:
    """Деление с защитой от нуля (0 в знаменателе → null)."""
    return pl.when(den != 0).then(num / den).otherwise(None)


def apply_spec(df: pl.DataFrame, spec: TableSpec) -> AggResult:
    """Применить спецификацию: свернуть таблицу до ``spec.key`` и описать фичи."""
    exprs: list[pl.Expr] = [pl.len().alias(f"{spec.prefix}_COUNT")]
    docs: list[FeatureDoc] = [
        FeatureDoc(
            f"{spec.prefix}_COUNT",
            spec.source,
            "UInt32",
            f"число записей ({spec.prefix}) на клиента",
        )
    ]
    cols = set(df.columns)
    for na in spec.numeric:
        if na.column not in cols:
            continue
        for stat in na.stats:
            name = f"{spec.prefix}_{na.column}_{stat.upper()}"
            exprs.append(STAT_EXPR[stat](na.column).alias(name))
            docs.append(
                FeatureDoc(name, spec.source, "Float64", f"{STAT_RU[stat]} {na.column}: {na.desc}")
            )
    for fc in spec.flags:
        if fc.column not in cols:
            continue
        exprs.append((pl.col(fc.column) == fc.value).sum().cast(pl.Int64).alias(fc.name))
        docs.append(FeatureDoc(fc.name, spec.source, "Int64", fc.desc))
    return AggResult(df.group_by(spec.key).agg(exprs), docs)


def aggregate_bureau_balance(bureau_balance: pl.DataFrame) -> pl.DataFrame:
    """Свернуть bureau_balance до уровня кредита (SK_ID_BUREAU).

    DPD-месяцы — статусы '1'..'5' (1=1–30 дней просрочки, ..., 5=>120). 'C'=закрыт, 'X'=нет данных.
    """
    return (
        bureau_balance.with_columns(pl.col("STATUS").is_in(["1", "2", "3", "4", "5"]).alias("_dpd"))
        .group_by("SK_ID_BUREAU")
        .agg(
            pl.len().alias("BB_MONTHS_COUNT"),
            pl.col("MONTHS_BALANCE").min().alias("BB_MONTHS_BALANCE_MIN"),
            pl.col("_dpd").sum().cast(pl.Int64).alias("BB_DPD_COUNT"),
        )
    )


def aggregate_bureau(
    bureau: pl.DataFrame, bureau_balance_agg: pl.DataFrame | None = None
) -> AggResult:
    """Кредитное бюро → client-level. Подмешивает агрегаты bureau_balance, если переданы."""
    df = bureau
    if bureau_balance_agg is not None:
        df = df.join(bureau_balance_agg, on="SK_ID_BUREAU", how="left")
    return apply_spec(df, BUREAU_SPEC)


def aggregate_previous(previous: pl.DataFrame) -> AggResult:
    """Прошлые заявки → client-level (с derived-фичей запрошено/одобрено)."""
    df = previous.with_columns(
        safe_div(pl.col("AMT_APPLICATION"), pl.col("AMT_CREDIT")).alias("APP_CREDIT_RATIO")
    )
    return apply_spec(df, PREVIOUS_SPEC)


def aggregate_installments(installments: pl.DataFrame) -> AggResult:
    """Платежи по рассрочкам → client-level (недоплата, ratio, DPD/DBD)."""
    df = installments.with_columns(
        (pl.col("AMT_INSTALMENT") - pl.col("AMT_PAYMENT")).alias("PAYMENT_DIFF"),
        safe_div(pl.col("AMT_PAYMENT"), pl.col("AMT_INSTALMENT")).alias("PAYMENT_RATIO"),
        (pl.col("DAYS_ENTRY_PAYMENT") - pl.col("DAYS_INSTALMENT")).clip(lower_bound=0).alias("DPD"),
        (pl.col("DAYS_INSTALMENT") - pl.col("DAYS_ENTRY_PAYMENT")).clip(lower_bound=0).alias("DBD"),
    )
    return apply_spec(df, INSTALLMENTS_SPEC)


def aggregate_pos(pos: pl.DataFrame) -> AggResult:
    """POS/CASH баланс → client-level."""
    return apply_spec(pos, POS_SPEC)


def aggregate_credit_card(credit_card: pl.DataFrame) -> AggResult:
    """Баланс по кредитным картам → client-level (с утилизацией)."""
    df = credit_card.with_columns(
        safe_div(pl.col("AMT_BALANCE"), pl.col("AMT_CREDIT_LIMIT_ACTUAL")).alias("UTILIZATION")
    )
    return apply_spec(df, CREDIT_CARD_SPEC)
