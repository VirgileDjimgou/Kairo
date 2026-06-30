from __future__ import annotations

import pytest

from app.core.config import settings
from app.providers.embeddings.ollama import OllamaEmbeddingProvider


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict) -> None:
        self.status_code = status_code
        self._payload = payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self) -> dict:
        return self._payload


class _FakeAsyncClient:
    def __init__(self, responses: list[_FakeResponse]) -> None:
        self._responses = responses
        self.calls: list[tuple[str, dict]] = []

    async def __aenter__(self) -> _FakeAsyncClient:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def post(self, path: str, json: dict) -> _FakeResponse:
        self.calls.append((path, json))
        return self._responses.pop(0)


@pytest.mark.asyncio
async def test_embed_texts_uses_current_ollama_embed_api(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = _FakeAsyncClient([_FakeResponse(200, {"embeddings": [[0.1, 0.2, 0.3]]})])
    monkeypatch.setattr(
        "app.providers.embeddings.ollama.httpx.AsyncClient",
        lambda *args, **kwargs: fake_client,
    )

    provider = OllamaEmbeddingProvider()
    vectors = await provider.embed_texts(["hello"])

    assert vectors == [[0.1, 0.2, 0.3]]
    assert fake_client.calls == [
        ("/api/embed", {"model": settings.ollama_embedding_model, "input": "hello"})
    ]


@pytest.mark.asyncio
async def test_embed_texts_falls_back_to_legacy_ollama_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = _FakeAsyncClient(
        [
            _FakeResponse(404, {"error": "not found"}),
            _FakeResponse(200, {"embedding": [0.4, 0.5]}),
        ]
    )
    monkeypatch.setattr(
        "app.providers.embeddings.ollama.httpx.AsyncClient",
        lambda *args, **kwargs: fake_client,
    )

    provider = OllamaEmbeddingProvider()
    vectors = await provider.embed_texts(["legacy"])

    assert vectors == [[0.4, 0.5]]
    assert fake_client.calls == [
        ("/api/embed", {"model": settings.ollama_embedding_model, "input": "legacy"}),
        ("/api/embeddings", {"model": settings.ollama_embedding_model, "prompt": "legacy"}),
    ]
