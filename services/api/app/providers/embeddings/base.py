from __future__ import annotations

from typing import Protocol


class EmbeddingProvider(Protocol):
    @property
    def vector_size(self) -> int: ...

    async def embed_texts(self, texts: list[str]) -> list[list[float]]: ...
