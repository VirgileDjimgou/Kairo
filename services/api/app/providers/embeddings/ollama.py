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
                response = await client.post(
                    "/api/embeddings",
                    json={"model": settings.ollama_embedding_model, "prompt": text},
                )
                response.raise_for_status()
                payload = response.json()
                vector = payload.get("embedding")
                if not vector:
                    raise ValueError("Ollama returned an empty embedding vector")
                if len(vector) != self._vector_size:
                    self._vector_size = len(vector)
                vectors.append(vector)
        return vectors
