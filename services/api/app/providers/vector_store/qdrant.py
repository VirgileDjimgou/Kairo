from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.core.config import settings

logger = structlog.get_logger(__name__)


class QdrantVectorStoreProvider:
    """Qdrant adapter for tenant-scoped document chunk vectors."""

    def __init__(self) -> None:
        self._client = QdrantClient(url=settings.qdrant_url, timeout=30)
        self._collection = settings.qdrant_collection

    def ensure_collection(self, vector_size: int) -> None:
        existing = {item.name for item in self._client.get_collections().collections}
        if self._collection in existing:
            info = self._client.get_collection(self._collection)
            current_size = info.config.params.vectors.size  # type: ignore[union-attr]
            if current_size != vector_size:
                raise ValueError(
                    f"Qdrant collection {self._collection} expects size {current_size}, got {vector_size}"
                )
            return

        self._client.create_collection(
            collection_name=self._collection,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        logger.info("qdrant_collection_created", collection=self._collection, vector_size=vector_size)

    def delete_vectors_for_version(self, tenant_id: UUID, document_version_id: UUID) -> None:
        self._client.delete(
            collection_name=self._collection,
            points_selector=Filter(
                must=[
                    FieldCondition(key="tenant_id", match=MatchValue(value=str(tenant_id))),
                    FieldCondition(
                        key="document_version_id",
                        match=MatchValue(value=str(document_version_id)),
                    ),
                ]
            ),
        )

    def upsert_chunk_vectors(
        self,
        points: list[tuple[UUID, list[float], dict[str, Any]]],
    ) -> None:
        if not points:
            return

        qdrant_points = [
            PointStruct(id=str(point_id), vector=vector, payload=payload)
            for point_id, vector, payload in points
        ]
        self._client.upsert(collection_name=self._collection, points=qdrant_points)

    def search_chunk_vectors(
        self,
        *,
        tenant_id: UUID,
        query_vector: list[float],
        limit: int,
    ) -> list[dict[str, Any]]:
        results = self._client.search(
            collection_name=self._collection,
            query_vector=query_vector,
            query_filter=Filter(
                must=[
                    FieldCondition(key="tenant_id", match=MatchValue(value=str(tenant_id))),
                ]
            ),
            limit=limit,
            with_payload=True,
        )
        return [
            {
                "id": str(point.id),
                "score": float(point.score or 0.0),
                "payload": point.payload or {},
            }
            for point in results
        ]
