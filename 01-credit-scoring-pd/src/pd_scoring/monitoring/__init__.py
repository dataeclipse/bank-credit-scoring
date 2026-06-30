"""Мониторинг дрейфа: PSI/CSI по входным фичам и дрейф PD. Реализация — Фаза 4."""

from __future__ import annotations

from collections.abc import Sequence


def population_stability_index(
    expected: Sequence[float], actual: Sequence[float], *, bins: int = 10
) -> float:
    """Рассчитать PSI между эталонным и текущим распределениями. Реализация — Фаза 4."""
    raise NotImplementedError("Phase 4: PSI/CSI drift monitoring")
