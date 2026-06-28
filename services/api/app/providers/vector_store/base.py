from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID


class VectorStoreProvider(Protocol):
    def ensure_collection(self, vector_size: int) -> None: ...

    def delete_vectors_for_version(self, tenant_id: UUID, document_version_id: UUID) -> None: ...

    def upsert_chunk_vectors(
        self,
        points: list[tuple[UUID, list[float], dict[str, Any]]],
    ) -> None: ...

    def search_chunk_vectors(
        self,
        *,
        tenant_id: UUID,
        query_vector: list[float],
        limit: int,
    ) -> list[dict[str, Any]]: ...
