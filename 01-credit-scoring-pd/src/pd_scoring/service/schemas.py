"""Pydantic-схемы /score: валидируемый вход (application-поля) и выход."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ApplicationIn(BaseModel):
    """Поля кредитной заявки. Агрегаты бюро/истории НЕ требуются — заполняются null."""

    model_config = ConfigDict(extra="forbid")

    AMT_INCOME_TOTAL: float = Field(gt=0, description="совокупный доход")
    AMT_CREDIT: float = Field(gt=0, description="сумма кредита по заявке")
    DAYS_BIRTH: int = Field(lt=0, description="возраст в днях (<0)")
    CODE_GENDER: Literal["M", "F", "XNA"] = Field(description="пол")

    AMT_ANNUITY: float | None = Field(default=None, gt=0)
    AMT_GOODS_PRICE: float | None = Field(default=None, gt=0)
    EXT_SOURCE_1: float | None = Field(default=None, ge=0, le=1)
    EXT_SOURCE_2: float | None = Field(default=None, ge=0, le=1)
    EXT_SOURCE_3: float | None = Field(default=None, ge=0, le=1)
    DAYS_EMPLOYED: int | None = None
    CNT_CHILDREN: int | None = Field(default=None, ge=0)
    CNT_FAM_MEMBERS: float | None = Field(default=None, ge=1)
    NAME_CONTRACT_TYPE: str | None = None
    NAME_EDUCATION_TYPE: str | None = None
    NAME_FAMILY_STATUS: str | None = None
    NAME_INCOME_TYPE: str | None = None
    NAME_HOUSING_TYPE: str | None = None
    OCCUPATION_TYPE: str | None = None
    ORGANIZATION_TYPE: str | None = None
    FLAG_OWN_CAR: Literal["Y", "N"] | None = None
    FLAG_OWN_REALTY: Literal["Y", "N"] | None = None
    REGION_RATING_CLIENT: int | None = Field(default=None, ge=1, le=3)


class ReasonCodeOut(BaseModel):
    """Reason code в ответе: фича, вклад SHAP, направление и человекочитаемое описание."""

    feature: str
    contribution: float
    direction: Literal["increases", "decreases"]
    description: str


class ScoreOut(BaseModel):
    """Ответ /score: PD, балл, риск-сегмент, топ-3 reason codes, версия модели."""

    model_config = ConfigDict(protected_namespaces=())

    pd: float = Field(description="вероятность дефолта (0..1)")
    score: int = Field(description="скоринговый балл")
    segment: Literal["low", "medium", "high"]
    reason_codes: list[ReasonCodeOut]
    model_version: str
