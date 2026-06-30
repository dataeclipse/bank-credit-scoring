from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

import polars as pl

STAT_EXPR: dict[str, Callable[[str], pl.Expr]] = {
    "mean": lambda c: pl.col(c).mean(),
    "sum": lambda c: pl.col(c).sum(),
    "max": lambda c: pl.col(c).max(),
    "min": lambda c: pl.col(c).min(),
    "std": lambda c: pl.col(c).std(),
}
STAT_RU: dict[str, str] = {
    "mean": "среднее",
    "sum": "сумма",
    "max": "максимум",
    "min": "минимум",
    "std": "ст.откл.",
}


@dataclass(frozen=True)
class NumAgg:
    column: str
    stats: tuple[str, ...]
    desc: str


@dataclass(frozen=True)
class FlagCount:
    name: str
    column: str
    value: str
    desc: str


@dataclass(frozen=True)
class TableSpec:
    prefix: str
    source: str
    key: str
    numeric: tuple[NumAgg, ...]
    flags: tuple[FlagCount, ...] = field(default_factory=tuple)


BUREAU_SPEC = TableSpec(
    prefix="BUREAU",
    source="bureau.csv",
    key="SK_ID_CURR",
    numeric=(
        NumAgg(
            "DAYS_CREDIT", ("mean", "min", "max"), "давность кредитов в бюро (дни, <0 - прошлое)"
        ),
        NumAgg("CREDIT_DAY_OVERDUE", ("mean", "max"), "дней просрочки на отчётную дату"),
        NumAgg("AMT_CREDIT_SUM", ("sum", "mean", "max"), "сумма кредита по записи бюро"),
        NumAgg("AMT_CREDIT_SUM_DEBT", ("sum", "mean"), "текущий долг по кредиту бюро"),
        NumAgg("AMT_CREDIT_SUM_OVERDUE", ("sum",), "просроченная сумма"),
        NumAgg("AMT_CREDIT_MAX_OVERDUE", ("mean", "max"), "макс. историческая просрочка"),
        NumAgg("CNT_CREDIT_PROLONG", ("sum",), "число пролонгаций кредита"),
        NumAgg("DAYS_CREDIT_UPDATE", ("mean",), "давность обновления записи бюро"),
        NumAgg("BB_MONTHS_COUNT", ("mean", "sum"), "число месяцев истории в bureau_balance"),
        NumAgg("BB_DPD_COUNT", ("sum", "mean"), "число месяцев с просрочкой (статусы 1-5)"),
    ),
    flags=(
        FlagCount(
            "BUREAU_ACTIVE_COUNT", "CREDIT_ACTIVE", "Active", "число активных кредитов в бюро"
        ),
        FlagCount(
            "BUREAU_CLOSED_COUNT", "CREDIT_ACTIVE", "Closed", "число закрытых кредитов в бюро"
        ),
    ),
)

PREVIOUS_SPEC = TableSpec(
    prefix="PREV",
    source="previous_application.csv",
    key="SK_ID_CURR",
    numeric=(
        NumAgg("AMT_APPLICATION", ("mean", "sum", "max"), "запрошенная сумма по прошлой заявке"),
        NumAgg("AMT_CREDIT", ("mean", "sum", "max"), "одобренная сумма по прошлой заявке"),
        NumAgg("AMT_DOWN_PAYMENT", ("mean",), "первоначальный взнос"),
        NumAgg("DAYS_DECISION", ("mean", "min", "max"), "давность решения по прошлой заявке"),
        NumAgg("CNT_PAYMENT", ("mean", "sum"), "срок кредита в платежах"),
        NumAgg("APP_CREDIT_RATIO", ("mean", "max"), "запрошено/одобрено (derived)"),
    ),
    flags=(
        FlagCount(
            "PREV_APPROVED_COUNT", "NAME_CONTRACT_STATUS", "Approved", "число одобренных заявок"
        ),
        FlagCount(
            "PREV_REFUSED_COUNT", "NAME_CONTRACT_STATUS", "Refused", "число отклонённых заявок"
        ),
    ),
)

INSTALLMENTS_SPEC = TableSpec(
    prefix="INST",
    source="installments_payments.csv",
    key="SK_ID_CURR",
    numeric=(
        NumAgg("PAYMENT_DIFF", ("mean", "sum", "max"), "недоплата = план − факт (derived)"),
        NumAgg("PAYMENT_RATIO", ("mean", "min"), "факт/план платежа (derived)"),
        NumAgg("DPD", ("mean", "max", "sum"), "дней просрочки платежа (derived)"),
        NumAgg("DBD", ("mean",), "дней до срока платежа (derived)"),
        NumAgg("AMT_PAYMENT", ("sum", "mean"), "фактический платёж"),
        NumAgg("AMT_INSTALMENT", ("sum", "mean"), "плановый платёж"),
    ),
)

POS_SPEC = TableSpec(
    prefix="POS",
    source="POS_CASH_balance.csv",
    key="SK_ID_CURR",
    numeric=(
        NumAgg("MONTHS_BALANCE", ("mean", "min"), "глубина истории POS (мес., <0 - прошлое)"),
        NumAgg("SK_DPD", ("mean", "max"), "дней просрочки POS"),
        NumAgg("SK_DPD_DEF", ("mean", "max"), "дней просрочки POS (с учётом толеранса)"),
        NumAgg("CNT_INSTALMENT_FUTURE", ("mean", "min"), "оставшиеся платежи POS"),
    ),
)

CREDIT_CARD_SPEC = TableSpec(
    prefix="CC",
    source="credit_card_balance.csv",
    key="SK_ID_CURR",
    numeric=(
        NumAgg("AMT_BALANCE", ("mean", "max"), "баланс по карте"),
        NumAgg("AMT_CREDIT_LIMIT_ACTUAL", ("mean", "max"), "кредитный лимит карты"),
        NumAgg("UTILIZATION", ("mean", "max"), "утилизация = баланс/лимит (derived)"),
        NumAgg("AMT_DRAWINGS_CURRENT", ("sum", "mean"), "снятия по карте"),
        NumAgg("AMT_PAYMENT_CURRENT", ("sum", "mean"), "платежи по карте"),
        NumAgg("SK_DPD", ("mean", "max"), "дней просрочки по карте"),
        NumAgg("SK_DPD_DEF", ("mean", "max"), "дней просрочки по карте (толеранс)"),
        NumAgg("CNT_DRAWINGS_CURRENT", ("sum", "mean"), "число снятий по карте"),
    ),
)
