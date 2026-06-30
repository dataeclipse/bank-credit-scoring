"""Воспроизводимость: фиксация случайных сидов.

В Фазе 0 фиксируем только stdlib ``random`` и ``PYTHONHASHSEED``. Сиды numpy и
ML-фреймворков добавятся в Фазе 1 вместе с extra ``ml``.
"""

from __future__ import annotations

import os
import random

DEFAULT_SEED = 42


def set_seeds(seed: int = DEFAULT_SEED) -> None:
    """Зафиксировать сиды для воспроизводимости (stdlib + numpy, если установлен)."""
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import numpy as np
    except ImportError:
        return
    np.random.seed(seed)
