"""ScoringService: одна заявка → PD, балл, риск-сегмент, топ-3 reason codes.

Строит полную строку из 120 фич модели (переданные поля + engineered ratios, остальное null),
предсказывает PD (опц. калибровка), масштабирует в балл, сегментирует, объясняет через SHAP.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from pd_scoring.config import Settings
from pd_scoring.models.explain import reason_codes_from_shap
from pd_scoring.scoring import assign_segment, pd_to_score
from pd_scoring.service.schemas import ReasonCodeOut, ScoreOut

DAYS_EMPLOYED_ANOMALY = 365243


def _safe_div(numerator: Any, denominator: Any) -> float | None:
    if numerator is None or denominator is None or denominator == 0:
        return None
    return float(numerator) / float(denominator)


class ScoringService:
    """Инкапсулирует прод-модель, опц. калибратор и метаданные фич (порядок, категориальные)."""

    def __init__(
        self,
        model: Any,
        calibrator: Any,
        feature_order: list[str],
        categorical: list[str],
        descriptions: dict[str, str],
        settings: Settings,
        model_version: str,
    ) -> None:
        self.model = model
        self.calibrator = calibrator
        self.feature_order = feature_order
        self._categorical = set(categorical)
        self.descriptions = descriptions
        self.settings = settings
        self.model_version = model_version

    def _engineered(self, app: dict[str, Any], days_employed: Any) -> dict[str, Any]:
        return {
            "DAYS_EMPLOYED_ANOM": 1 if app.get("DAYS_EMPLOYED") == DAYS_EMPLOYED_ANOMALY else 0,
            "CREDIT_INCOME_RATIO": _safe_div(app.get("AMT_CREDIT"), app.get("AMT_INCOME_TOTAL")),
            "ANNUITY_INCOME_RATIO": _safe_div(app.get("AMT_ANNUITY"), app.get("AMT_INCOME_TOTAL")),
            "CREDIT_ANNUITY_RATIO": _safe_div(app.get("AMT_CREDIT"), app.get("AMT_ANNUITY")),
            "GOODS_CREDIT_RATIO": _safe_div(app.get("AMT_GOODS_PRICE"), app.get("AMT_CREDIT")),
            "EMPLOYED_BIRTH_RATIO": _safe_div(days_employed, app.get("DAYS_BIRTH")),
            "INCOME_PER_PERSON": _safe_div(app.get("AMT_INCOME_TOTAL"), app.get("CNT_FAM_MEMBERS")),
        }

    def build_feature_row(self, app: dict[str, Any]) -> pd.DataFrame:
        """Полная 120-фич строка в порядке модели; категориальные → category, остальное → float."""
        values: dict[str, Any] = dict.fromkeys(self.feature_order)
        for key, value in app.items():
            if key in values:
                values[key] = value
        # Аномалия стажа: 365243 → null + флаг (как в витрине Фазы 1).
        days_employed = (
            None if app.get("DAYS_EMPLOYED") == DAYS_EMPLOYED_ANOMALY else app.get("DAYS_EMPLOYED")
        )
        if "DAYS_EMPLOYED" in values:
            values["DAYS_EMPLOYED"] = days_employed
        for key, value in self._engineered(app, days_employed).items():
            if key in values:
                values[key] = value

        frame = pd.DataFrame([values], columns=self.feature_order)
        for column in self.feature_order:
            if column in self._categorical:
                frame[column] = frame[column].astype("category")
            else:
                frame[column] = pd.to_numeric(frame[column], errors="coerce")
        return frame

    def score(self, app: dict[str, Any]) -> ScoreOut:
        """Скоринг одной заявки."""
        frame = self.build_feature_row(app)
        pd_value = float(self.model.predict_proba(frame)[:, 1][0])
        if self.calibrator is not None:
            pd_value = float(self.calibrator.predict(np.array([pd_value]))[0])

        settings = self.settings
        score = pd_to_score(
            pd_value,
            base_score=settings.score_base,
            pdo=settings.score_pdo,
            base_odds=settings.score_base_odds,
        )
        segment = assign_segment(pd_value, low=settings.segment_low, high=settings.segment_high)
        # Нативный LightGBM TreeSHAP (pred_contrib) — на порядок быстрее shap.TreeExplainer;
        # последняя колонка — base value, отбрасываем.
        contributions = np.asarray(self.model.booster_.predict(frame, pred_contrib=True))[0][:-1]
        codes = reason_codes_from_shap(
            self.feature_order, contributions, self.descriptions, top_n=3
        )
        return ScoreOut(
            pd=pd_value,
            score=score,
            segment=segment.value,
            reason_codes=[
                ReasonCodeOut(
                    feature=c.feature, contribution=c.contribution, description=c.description
                )
                for c in codes
            ],
            model_version=self.model_version,
        )
