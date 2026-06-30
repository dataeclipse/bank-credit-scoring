from __future__ import annotations

import os
import random

DEFAULT_SEED = 42


def set_seeds(seed: int = DEFAULT_SEED) -> None:
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import numpy as np
    except ImportError:
        return
    np.random.seed(seed)
