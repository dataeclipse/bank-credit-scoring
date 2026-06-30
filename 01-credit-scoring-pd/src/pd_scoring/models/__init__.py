"""Модели PD: WOE-scorecard и градиентный бустинг (GBDT). Реализация — Фаза 2.

Интерфейсы — заглушки. Тяжёлые ML-зависимости (lightgbm/optbinning/…) подключаются
в Фазе 2 вместе с extra ``ml``, поэтому здесь импортов ML-библиотек нет.
"""

from __future__ import annotations

from typing import Protocol


class PdModel(Protocol):
    """Контракт модели вероятности дефолта."""

    def predict_proba(self, features: dict[str, float]) -> float:
        """Вернуть PD (вероятность дефолта) по словарю фич заявки."""
        ...
