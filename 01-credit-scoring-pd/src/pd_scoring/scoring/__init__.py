"""Скоринг: PD → балл → риск-сегмент → reason codes.

Типы результата определены здесь; расчёт балла и сегментация реализуются в Фазах 2 и 4.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RiskSegment(StrEnum):
    """Риск-сегмент заявки."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class ReasonCode:
    """Причина решения — вклад фактора (SHAP)."""

    feature: str
    contribution: float
    description: str


@dataclass(frozen=True)
class ScoringResult:
    """Результат скоринга кредитной заявки."""

    pd: float
    score: int
    segment: RiskSegment
    reason_codes: list[ReasonCode]


def pd_to_score(pd: float, *, base_score: int = 600, pdo: int = 50) -> int:
    """Преобразовать PD в скоринговый балл (scorecard scaling). Реализация — Фаза 2."""
    raise NotImplementedError("Phase 2: scorecard score scaling")


def assign_segment(pd: float) -> RiskSegment:
    """Назначить риск-сегмент по PD. Реализация — Фаза 4."""
    raise NotImplementedError("Phase 4: risk segmentation")
