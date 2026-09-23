"""Tests for configuration loading."""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from core.config import Settings, get_settings


def test_settings_defaults():
    """Test that Settings loads with sensible defaults."""
    settings = Settings()
    assert settings.APP_NAME == 'ALIAS'
    assert settings.APP_VERSION == '0.1.0'
    assert settings.HOST == '127.0.0.1'
    assert settings.PORT == 8000
    assert 'sqlite' in settings.DATABASE_URL


def test_get_settings_returns_settings():
    """Test that get_settings returns a Settings instance."""
    settings = get_settings()
    assert isinstance(settings, Settings)
    assert settings.APP_NAME == 'ALIAS'
