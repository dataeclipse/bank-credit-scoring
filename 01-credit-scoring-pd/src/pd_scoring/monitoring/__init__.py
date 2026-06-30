"""Мониторинг дрейфа: PSI/CSI по входным фичам и дрейф распределения PD."""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

_EPS = 1e-6


def population_stability_index(
    expected: npt.ArrayLike, actual: npt.ArrayLike, *, bins: int = 10
) -> float:
    """PSI между эталонным (expected) и текущим (actual) распределениями.

    Бины — квантильные по expected. PSI = Σ (a% − e%)·ln(a%/e%). Эмпирически:
    <0.1 — нет сдвига, 0.1–0.2 — умеренный, >0.2 — значимый дрейф.
    CSI (по входной фиче) считается этой же формулой.
    """
    exp = np.asarray(expected, dtype=float)
    exp = exp[~np.isnan(exp)]
    act = np.asarray(actual, dtype=float)
    act = act[~np.isnan(act)]
    if exp.size == 0 or act.size == 0:
        return 0.0

    edges = np.unique(np.quantile(exp, np.linspace(0.0, 1.0, bins + 1)))
    if edges.size < 3:  # почти константа — дрейф не оцениваем
        return 0.0
    edges[0], edges[-1] = -np.inf, np.inf

    exp_pct = np.clip(np.histogram(exp, bins=edges)[0] / exp.size, _EPS, None)
    act_pct = np.clip(np.histogram(act, bins=edges)[0] / act.size, _EPS, None)
    return float(np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct)))


# Короткий алиас.
psi = population_stability_index
