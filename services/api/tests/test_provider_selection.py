from __future__ import annotations

import pytest

from app.core.config import settings
from app.core.dependencies import get_embedding_provider, get_llm_provider
from app.providers.embeddings.ollama import OllamaEmbeddingProvider
from app.providers.embeddings.openai_compatible import OpenAICompatibleEmbeddingProvider
from app.providers.llm.ollama import OllamaLLMProvider
from app.providers.llm.openai_compatible import OpenAICompatibleLLMProvider


@pytest.fixture(autouse=True)
def clear_provider_caches() -> None:
    get_llm_provider.cache_clear()
    get_embedding_provider.cache_clear()
    yield
    get_llm_provider.cache_clear()
    get_embedding_provider.cache_clear()


def test_provider_selection_defaults_to_ollama(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_provider_kind", "ollama")
    monkeypatch.setattr(settings, "embedding_provider_kind", "ollama")

    assert isinstance(get_llm_provider(), OllamaLLMProvider)
    assert isinstance(get_embedding_provider(), OllamaEmbeddingProvider)


def test_provider_selection_can_switch_to_openai_compatible(monkeypatch) -> None:
    monkeypatch.setattr(settings, "llm_provider_kind", "openai_compatible")
    monkeypatch.setattr(settings, "embedding_provider_kind", "openai_compatible")

    assert isinstance(get_llm_provider(), OpenAICompatibleLLMProvider)
    assert isinstance(get_embedding_provider(), OpenAICompatibleEmbeddingProvider)
