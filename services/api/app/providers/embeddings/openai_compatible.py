from __future__ import annotations

import httpx

from app.core.config import settings


class OpenAICompatibleEmbeddingProvider:
    """Embedding provider for OpenAI-compatible local servers such as LM Studio."""

    def __init__(self) -> None:
        self._vector_size = settings.embedding_dimensions

    @property
    def vector_size(self) -> int:
        return self._vector_size

    def _headers(self) -> dict[str, str]:
        api_key = settings.openai_compatible_api_key.strip()
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        vectors: list[list[float]] = []
        async with httpx.AsyncClient(
            base_url=settings.openai_compatible_base_url,
            timeout=settings.embedding_request_timeout_seconds,
            headers=self._headers(),
        ) as client:
            for text in texts:
                response = await client.post(
                    "/embeddings",
                    json={
                        "model": settings.openai_compatible_embedding_model,
                        "input": text,
                    },
                )
                response.raise_for_status()
                payload = response.json()
                vector = self._extract_embedding(payload)
                if not vector:
                    raise ValueError("OpenAI-compatible server returned an empty embedding vector")
                if len(vector) != self._vector_size:
                    self._vector_size = len(vector)
                vectors.append(vector)
        return vectors

    def _extract_embedding(self, payload: dict) -> list[float]:
        data = payload.get("data")
        if isinstance(data, list) and data:
            first = data[0]
            if isinstance(first, dict):
                embedding = first.get("embedding")
                if isinstance(embedding, list):
                    return [float(value) for value in embedding]
        embedding = payload.get("embedding")
        if isinstance(embedding, list):
            return [float(value) for value in embedding]
        return []
