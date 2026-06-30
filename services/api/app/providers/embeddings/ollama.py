from __future__ import annotations

import httpx

from app.core.config import settings


class OllamaEmbeddingProvider:
    """Local embedding provider backed by Ollama."""

    def __init__(self) -> None:
        self._vector_size = settings.embedding_dimensions

    @property
    def vector_size(self) -> int:
        return self._vector_size

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        vectors: list[list[float]] = []
        async with httpx.AsyncClient(
            base_url=settings.ollama_base_url,
            timeout=settings.embedding_request_timeout_seconds,
        ) as client:
            for text in texts:
                vector = await self._embed_with_current_or_legacy_api(client, text)
                if not vector:
                    raise ValueError("Ollama returned an empty embedding vector")
                if len(vector) != self._vector_size:
                    self._vector_size = len(vector)
                vectors.append(vector)
        return vectors

    async def _embed_with_current_or_legacy_api(
        self,
        client: httpx.AsyncClient,
        text: str,
    ) -> list[float]:
        current_response = await client.post(
            "/api/embed",
            json={"model": settings.ollama_embedding_model, "input": text},
        )
        if current_response.status_code == 404:
            legacy_response = await client.post(
                "/api/embeddings",
                json={"model": settings.ollama_embedding_model, "prompt": text},
            )
            legacy_response.raise_for_status()
            payload = legacy_response.json()
            return payload.get("embedding", [])

        current_response.raise_for_status()
        payload = current_response.json()
        embeddings = payload.get("embeddings")
        if isinstance(embeddings, list) and embeddings:
            first_embedding = embeddings[0]
            if isinstance(first_embedding, list):
                return first_embedding

        return payload.get("embedding", [])
