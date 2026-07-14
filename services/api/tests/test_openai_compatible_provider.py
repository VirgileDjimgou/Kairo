from __future__ import annotations

import pytest

from app.core.config import settings
from app.providers.embeddings.openai_compatible import OpenAICompatibleEmbeddingProvider
from app.providers.llm.openai_compatible import OpenAICompatibleLLMProvider


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict) -> None:
        self.status_code = status_code
        self._payload = payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self) -> dict:
        return self._payload


class _FakeStreamResponse:
    def __init__(self, lines: list[str]) -> None:
        self._lines = lines

    def raise_for_status(self) -> None:
        return None

    async def __aenter__(self) -> _FakeStreamResponse:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def aiter_lines(self):
        for line in self._lines:
            yield line


class _FakeAsyncClient:
    def __init__(self, responses: list[_FakeResponse], stream_lines: list[str] | None = None) -> None:
        self._responses = responses
        self._stream_lines = stream_lines or []
        self.calls: list[tuple[str, dict]] = []

    async def __aenter__(self) -> _FakeAsyncClient:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def post(self, path: str, json: dict) -> _FakeResponse:
        self.calls.append((path, json))
        return self._responses.pop(0)

    def stream(self, method: str, path: str, json: dict):
        self.calls.append((path, json))
        return _FakeStreamResponse(self._stream_lines)


@pytest.mark.asyncio
async def test_openai_compatible_llm_generate(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = _FakeAsyncClient(
        [_FakeResponse(200, {"choices": [{"message": {"content": "Hello from LM Studio"}}]})]
    )
    monkeypatch.setattr("app.providers.llm.openai_compatible.httpx.AsyncClient", lambda *args, **kwargs: fake_client)
    monkeypatch.setattr(settings, "openai_compatible_base_url", "http://127.0.0.1:1234/v1")
    monkeypatch.setattr(settings, "openai_compatible_api_key", "lm-studio")
    monkeypatch.setattr(settings, "openai_compatible_llm_model", "zai-org/glm-4.7-flash")

    provider = OpenAICompatibleLLMProvider()
    answer = await provider.generate(system_prompt="sys", user_prompt="user", max_tokens=64)

    assert answer == "Hello from LM Studio"
    assert fake_client.calls == [
        (
            "/chat/completions",
            {
                "model": "zai-org/glm-4.7-flash",
                "messages": [{"role": "system", "content": "sys"}, {"role": "user", "content": "user"}],
                "stream": False,
                "temperature": 0.3,
                "top_p": 0.9,
                "max_tokens": 64,
            },
        )
    ]


@pytest.mark.asyncio
async def test_openai_compatible_llm_generate_uses_reasoning_content_when_final_content_is_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = _FakeAsyncClient(
        [
            _FakeResponse(
                200,
                {
                    "choices": [
                        {
                            "message": {
                                "content": "",
                                "reasoning_content": "Analysis... Final Output: Bonjour ! Comment puis-je vous aider ?",
                            }
                        }
                    ]
                },
            )
        ]
    )
    monkeypatch.setattr("app.providers.llm.openai_compatible.httpx.AsyncClient", lambda *args, **kwargs: fake_client)
    monkeypatch.setattr(settings, "openai_compatible_base_url", "http://127.0.0.1:1234/v1")
    monkeypatch.setattr(settings, "openai_compatible_api_key", "lm-studio")
    monkeypatch.setattr(settings, "openai_compatible_llm_model", "zai-org/glm-4.7-flash")

    provider = OpenAICompatibleLLMProvider()
    answer = await provider.generate(system_prompt="sys", user_prompt="user", max_tokens=64)

    assert answer == "Bonjour ! Comment puis-je vous aider ?"


@pytest.mark.asyncio
async def test_openai_compatible_embedding_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = _FakeAsyncClient([_FakeResponse(200, {"data": [{"embedding": [0.1, 0.2, 0.3]}]})])
    monkeypatch.setattr(
        "app.providers.embeddings.openai_compatible.httpx.AsyncClient",
        lambda *args, **kwargs: fake_client,
    )
    monkeypatch.setattr(settings, "openai_compatible_base_url", "http://127.0.0.1:1234/v1")
    monkeypatch.setattr(settings, "openai_compatible_api_key", "lm-studio")
    monkeypatch.setattr(settings, "openai_compatible_embedding_model", "text-embedding-nomic-embed-text-v1.5")

    provider = OpenAICompatibleEmbeddingProvider()
    vectors = await provider.embed_texts(["hello"])

    assert vectors == [[0.1, 0.2, 0.3]]
    assert fake_client.calls == [
        (
            "/embeddings",
            {
                "model": "text-embedding-nomic-embed-text-v1.5",
                "input": "hello",
            },
        )
    ]
