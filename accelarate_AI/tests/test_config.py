import pytest

from core.config import Settings, get_settings, ensure_data_dirs, ALL_DATA_DIRS


def test_settings_reads_env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-test")
    monkeypatch.setenv("LLM_MAX_TOKENS", "123")

    settings = get_settings()

    assert settings.anthropic_api_key == "fake-key"
    assert settings.anthropic_model == "claude-test"
    assert settings.llm_max_tokens == 123


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_MODEL", raising=False)
    monkeypatch.delenv("LLM_MAX_TOKENS", raising=False)

    settings = get_settings()

    assert settings.anthropic_model == "claude-sonnet-4-5"
    assert settings.llm_max_tokens == 4096


def test_validate_raises_when_api_key_missing():
    settings = Settings(llm_provider="anthropic", anthropic_api_key=None)

    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        settings.validate()


def test_validate_passes_when_api_key_present():
    settings = Settings(llm_provider="anthropic", anthropic_api_key="fake-key")
    settings.validate()  # should not raise


def test_ensure_data_dirs_creates_all(tmp_path, monkeypatch):
    import core.config as config_module

    fake_dirs = tuple(tmp_path / d.name for d in ALL_DATA_DIRS)
    monkeypatch.setattr(config_module, "ALL_DATA_DIRS", fake_dirs)

    ensure_data_dirs()

    assert all(d.exists() for d in fake_dirs)
