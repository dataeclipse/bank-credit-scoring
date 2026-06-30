from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

_EPS = 1e-6

Direction = Literal["increases", "decreases"]


class RiskSegment(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class ReasonCode:
    feature: str
    contribution: float
    description: str
    direction: Direction


@dataclass(frozen=True)
class ScoringResult:
    pd: float
    score: int
    segment: RiskSegment
    reason_codes: list[ReasonCode]


def pd_to_score(pd: float, *, base_score: int = 600, pdo: int = 50, base_odds: float = 50.0) -> int:
    pd = min(max(pd, _EPS), 1.0 - _EPS)
    factor = pdo / math.log(2.0)
    offset = base_score - factor * math.log(base_odds)
    return int(round(offset + factor * math.log((1.0 - pd) / pd)))


def assign_segment(pd: float, *, low: float = 0.05, high: float = 0.15) -> RiskSegment:
    if pd < low:
        return RiskSegment.LOW
    if pd < high:
        return RiskSegment.MEDIUM
    return RiskSegment.HIGH
