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

    # Пути проекта.
    data_dir: Path = Path("data")
    model_dir: Path = Path("artifacts/models")


@lru_cache
def get_settings() -> Settings:
    """Вернуть кэшированный singleton настроек."""
    return Settings()
