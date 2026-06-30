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
    "mean": "mean",
    "sum": "sum",
    "max": "max",
    "min": "min",
    "std": "std",
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
        NumAgg("DAYS_CREDIT", ("mean", "min", "max"), "age of bureau credits (days, <0 - past)"),
        NumAgg("CREDIT_DAY_OVERDUE", ("mean", "max"), "days past due as of the reporting date"),
        NumAgg("AMT_CREDIT_SUM", ("sum", "mean", "max"), "credit amount per bureau record"),
        NumAgg("AMT_CREDIT_SUM_DEBT", ("sum", "mean"), "current debt on the bureau credit"),
        NumAgg("AMT_CREDIT_SUM_OVERDUE", ("sum",), "overdue amount"),
        NumAgg("AMT_CREDIT_MAX_OVERDUE", ("mean", "max"), "max historical overdue"),
        NumAgg("CNT_CREDIT_PROLONG", ("sum",), "number of credit prolongations"),
        NumAgg("DAYS_CREDIT_UPDATE", ("mean",), "age of the bureau record update"),
        NumAgg("BB_MONTHS_COUNT", ("mean", "sum"), "number of months of history in bureau_balance"),
        NumAgg("BB_DPD_COUNT", ("sum", "mean"), "number of months with overdue (statuses 1-5)"),
    ),
    flags=(
        FlagCount(
            "BUREAU_ACTIVE_COUNT", "CREDIT_ACTIVE", "Active", "number of active bureau credits"
        ),
        FlagCount(
            "BUREAU_CLOSED_COUNT", "CREDIT_ACTIVE", "Closed", "number of closed bureau credits"
        ),
    ),
)

PREVIOUS_SPEC = TableSpec(
    prefix="PREV",
    source="previous_application.csv",
    key="SK_ID_CURR",
    numeric=(
        NumAgg(
            "AMT_APPLICATION", ("mean", "sum", "max"), "requested amount on the prior application"
        ),
        NumAgg("AMT_CREDIT", ("mean", "sum", "max"), "approved amount on the prior application"),
        NumAgg("AMT_DOWN_PAYMENT", ("mean",), "down payment"),
        NumAgg(
            "DAYS_DECISION", ("mean", "min", "max"), "age of the decision on the prior application"
        ),
        NumAgg("CNT_PAYMENT", ("mean", "sum"), "credit term in payments"),
        NumAgg("APP_CREDIT_RATIO", ("mean", "max"), "requested/approved (derived)"),
    ),
    flags=(
        FlagCount(
            "PREV_APPROVED_COUNT",
            "NAME_CONTRACT_STATUS",
            "Approved",
            "number of approved applications",
        ),
        FlagCount(
            "PREV_REFUSED_COUNT",
            "NAME_CONTRACT_STATUS",
            "Refused",
            "number of refused applications",
        ),
    ),
)

INSTALLMENTS_SPEC = TableSpec(
    prefix="INST",
    source="installments_payments.csv",
    key="SK_ID_CURR",
    numeric=(
        NumAgg("PAYMENT_DIFF", ("mean", "sum", "max"), "underpayment = planned - actual (derived)"),
        NumAgg("PAYMENT_RATIO", ("mean", "min"), "actual/planned payment (derived)"),
        NumAgg("DPD", ("mean", "max", "sum"), "days past due on the payment (derived)"),
        NumAgg("DBD", ("mean",), "days before the payment due date (derived)"),
        NumAgg("AMT_PAYMENT", ("sum", "mean"), "actual payment"),
        NumAgg("AMT_INSTALMENT", ("sum", "mean"), "planned payment"),
    ),
)

POS_SPEC = TableSpec(
    prefix="POS",
    source="POS_CASH_balance.csv",
    key="SK_ID_CURR",
    numeric=(
        NumAgg("MONTHS_BALANCE", ("mean", "min"), "POS history depth (months, <0 - past)"),
        NumAgg("SK_DPD", ("mean", "max"), "POS days past due"),
        NumAgg("SK_DPD_DEF", ("mean", "max"), "POS days past due (with tolerance)"),
        NumAgg("CNT_INSTALMENT_FUTURE", ("mean", "min"), "remaining POS payments"),
    ),
)

CREDIT_CARD_SPEC = TableSpec(
    prefix="CC",
    source="credit_card_balance.csv",
    key="SK_ID_CURR",
    numeric=(
        NumAgg("AMT_BALANCE", ("mean", "max"), "card balance"),
        NumAgg("AMT_CREDIT_LIMIT_ACTUAL", ("mean", "max"), "card credit limit"),
        NumAgg("UTILIZATION", ("mean", "max"), "utilization = balance/limit (derived)"),
        NumAgg("AMT_DRAWINGS_CURRENT", ("sum", "mean"), "card drawings"),
        NumAgg("AMT_PAYMENT_CURRENT", ("sum", "mean"), "card payments"),
        NumAgg("SK_DPD", ("mean", "max"), "card days past due"),
        NumAgg("SK_DPD_DEF", ("mean", "max"), "card days past due (tolerance)"),
        NumAgg("CNT_DRAWINGS_CURRENT", ("sum", "mean"), "number of card drawings"),
    ),
)
