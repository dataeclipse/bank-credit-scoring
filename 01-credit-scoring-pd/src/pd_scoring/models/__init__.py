from __future__ import annotations

from typing import Protocol


class PdModel(Protocol):
    def predict_proba(self, features: dict[str, float]) -> float: ...
