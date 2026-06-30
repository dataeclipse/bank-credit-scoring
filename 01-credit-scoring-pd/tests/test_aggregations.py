from __future__ import annotations

import polars as pl

from pd_scoring.features.aggregations import (
    AggResult,
    aggregate_bureau,
    aggregate_bureau_balance,
    aggregate_credit_card,
    aggregate_installments,
    aggregate_pos,
    aggregate_previous,
)


def _val(frame: pl.DataFrame, sk_id: int, column: str) -> float:
    return frame.filter(pl.col("SK_ID_CURR") == sk_id).select(column).item()


def _assert_client_level(result: AggResult) -> None:
    frame = result.frame
    assert frame["SK_ID_CURR"].n_unique() == frame.height
    assert "TARGET" not in frame.columns


def test_bureau_with_balance() -> None:
    bureau = pl.DataFrame(
        {
            "SK_ID_CURR": [1, 1, 2],
            "SK_ID_BUREAU": [10, 11, 12],
            "CREDIT_ACTIVE": ["Active", "Closed", "Active"],
            "DAYS_CREDIT": [-100, -200, -50],
            "CREDIT_DAY_OVERDUE": [0, 0, 5],
            "AMT_CREDIT_SUM": [1000.0, 2000.0, 500.0],
            "AMT_CREDIT_SUM_DEBT": [100.0, 0.0, 50.0],
            "AMT_CREDIT_SUM_OVERDUE": [0.0, 0.0, 10.0],
            "AMT_CREDIT_MAX_OVERDUE": [0.0, 0.0, 20.0],
            "CNT_CREDIT_PROLONG": [0, 1, 0],
            "DAYS_CREDIT_UPDATE": [-10, -20, -5],
        }
    )
    bureau_balance = pl.DataFrame(
        {
            "SK_ID_BUREAU": [10, 10, 11, 12],
            "MONTHS_BALANCE": [-1, -2, -1, -1],
            "STATUS": ["0", "1", "C", "2"],
        }
    )
    bb_agg = aggregate_bureau_balance(bureau_balance)
    result = aggregate_bureau(bureau, bb_agg)
    _assert_client_level(result)

    assert _val(result.frame, 1, "BUREAU_COUNT") == 2
    assert _val(result.frame, 1, "BUREAU_ACTIVE_COUNT") == 1
    assert _val(result.frame, 1, "BUREAU_CLOSED_COUNT") == 1
    assert _val(result.frame, 1, "BUREAU_AMT_CREDIT_SUM_SUM") == 3000.0

    assert _val(result.frame, 1, "BUREAU_BB_DPD_COUNT_SUM") == 1
    assert _val(result.frame, 2, "BUREAU_BB_DPD_COUNT_SUM") == 1


def test_previous() -> None:
    previous = pl.DataFrame(
        {
            "SK_ID_CURR": [1, 1, 2],
            "SK_ID_PREV": [100, 101, 102],
            "AMT_APPLICATION": [500.0, 1000.0, 200.0],
            "AMT_CREDIT": [400.0, 1000.0, 200.0],
            "AMT_DOWN_PAYMENT": [50.0, 0.0, 10.0],
            "NAME_CONTRACT_STATUS": ["Approved", "Refused", "Approved"],
            "DAYS_DECISION": [-10, -20, -5],
            "CNT_PAYMENT": [12, 0, 6],
        }
    )
    result = aggregate_previous(previous)
    _assert_client_level(result)
    assert _val(result.frame, 1, "PREV_COUNT") == 2
    assert _val(result.frame, 1, "PREV_APPROVED_COUNT") == 1
    assert _val(result.frame, 1, "PREV_REFUSED_COUNT") == 1
    assert _val(result.frame, 1, "PREV_AMT_APPLICATION_SUM") == 1500.0


def test_installments() -> None:
    installments = pl.DataFrame(
        {
            "SK_ID_CURR": [1, 1],
            "AMT_INSTALMENT": [100.0, 100.0],
            "AMT_PAYMENT": [100.0, 80.0],
            "DAYS_INSTALMENT": [-30, -60],
            "DAYS_ENTRY_PAYMENT": [-28, -65],
        }
    )
    result = aggregate_installments(installments)
    _assert_client_level(result)
    assert _val(result.frame, 1, "INST_COUNT") == 2
    assert _val(result.frame, 1, "INST_PAYMENT_DIFF_SUM") == 20.0
    assert _val(result.frame, 1, "INST_DPD_MAX") == 2


def test_pos() -> None:
    pos = pl.DataFrame(
        {
            "SK_ID_CURR": [1, 1],
            "MONTHS_BALANCE": [-1, -2],
            "SK_DPD": [0, 5],
            "SK_DPD_DEF": [0, 3],
            "CNT_INSTALMENT_FUTURE": [10, 8],
        }
    )
    result = aggregate_pos(pos)
    _assert_client_level(result)
    assert _val(result.frame, 1, "POS_COUNT") == 2
    assert _val(result.frame, 1, "POS_SK_DPD_MAX") == 5


def test_credit_card() -> None:
    credit_card = pl.DataFrame(
        {
            "SK_ID_CURR": [1],
            "AMT_BALANCE": [500.0],
            "AMT_CREDIT_LIMIT_ACTUAL": [1000.0],
            "AMT_DRAWINGS_CURRENT": [100.0],
            "AMT_PAYMENT_CURRENT": [200.0],
            "SK_DPD": [0],
            "SK_DPD_DEF": [0],
            "CNT_DRAWINGS_CURRENT": [2],
        }
    )
    result = aggregate_credit_card(credit_card)
    _assert_client_level(result)
    assert _val(result.frame, 1, "CC_COUNT") == 1
    assert _val(result.frame, 1, "CC_UTILIZATION_MEAN") == 0.5
