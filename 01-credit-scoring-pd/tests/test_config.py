"""Smoke-тесты конфигурации."""

from __future__ import annotations

from pd_scoring.config import Settings, get_settings


def test_settings_defaults() -> None:
    """Дефолты подхватываются без .env (изолируемся от локального .env)."""
    settings = Settings(_env_file=None)
    assert settings.random_seed == 42
    assert settings.env == "local"
    assert settings.log_level == "INFO"


def test_get_settings_is_cached() -> None:
    """get_settings возвращает один и тот же объект (lru_cache)."""
    assert get_settings() is get_settings()
