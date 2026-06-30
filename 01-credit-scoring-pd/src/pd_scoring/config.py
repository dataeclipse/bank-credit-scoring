"""Конфигурация приложения через pydantic-settings.

Значения читаются из окружения и файла ``.env`` (префикс ``PD_``).
Секреты держим ТОЛЬКО в ``.env`` / переменных окружения, в коде не хардкодим.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки сервиса скоринга."""

    model_config = SettingsConfigDict(
        env_prefix="PD_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = "local"
    log_level: str = "INFO"
    random_seed: int = 42

    # Внешние ресурсы — значения только из .env, в репозиторий не попадают.
    database_url: str | None = None
    mlflow_tracking_uri: str | None = None
    mlflow_experiment: str = "pd-scoring-phase2"

    # Прод-модель: model_uri (локальный joblib — контейнер) ИЛИ MLflow registry по алиасу (dev).
    model_uri: str | None = None
    model_version_label: str = "baked"
    model_name: str = "pd-lightgbm"
    model_alias: str = "champion"
    use_calibrator: bool = False

    # Шкала скорингового балла (PDO/odds) и пороги риск-сегмента по PD.
    score_base: int = 600
    score_pdo: int = 50
    score_base_odds: float = 50.0
    segment_low: float = 0.05
    segment_high: float = 0.15

    # Мониторинг дрейфа.
    psi_threshold: float = 0.2

    # Пути проекта.
    data_dir: Path = Path("data")
    model_dir: Path = Path("artifacts/models")


@lru_cache
def get_settings() -> Settings:
    """Вернуть кэшированный singleton настроек."""
    return Settings()
