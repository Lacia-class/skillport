import pytest

from skillport.shared.config import Config


def test_openai_requires_key(monkeypatch):
    """provider=openai without key should fail fast."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError):
        Config(embedding_provider="openai")


def test_openai_compatible_requires_base_url(monkeypatch):
    """provider=openai_compatible without base url should fail fast."""
    monkeypatch.delenv("SKILLPORT_EMBEDDING_BASE_URL", raising=False)
    with pytest.raises(ValueError):
        Config(
            embedding_provider="openai_compatible",
            embedding_model="test-model",
            embedding_api_key="sk-test-key",
        )
