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
    SparseVectorParams,
    VectorParams,
)

from app.core.config import settings

logger = structlog.get_logger(__name__)


class QdrantVectorStoreProvider:
    """Qdrant adapter for tenant-scoped dense retrieval over document chunks."""

    def __init__(self) -> None:
        self._client = QdrantClient(url=settings.qdrant_url, timeout=30)
        self._collection = settings.qdrant_collection

    def ensure_collection(self, vector_size: int) -> None:
        existing = {item.name for item in self._client.get_collections().collections}
        if self._collection in existing:
            info = self._client.get_collection(self._collection)
            vectors = info.config.params.vectors
            assert isinstance(vectors, VectorParams)
            current_size = vectors.size
            if current_size != vector_size:
                raise ValueError(
                    "Qdrant collection "
                    f"{self._collection} expects size {current_size}, got {vector_size}"
                )
            return

        self._client.create_collection(
            collection_name=self._collection,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            sparse_vectors_config={"bm25": SparseVectorParams()},
        )
        logger.info(
            "qdrant_collection_created",
            collection=self._collection,
            vector_size=vector_size,
        )

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
        query_text: str | None = None,
        limit: int,
        score_threshold: float = 0.0,
        hybrid: bool = False,
    ) -> list[dict[str, Any]]:
        query_filter = Filter(
            must=[
                FieldCondition(key="tenant_id", match=MatchValue(value=str(tenant_id))),
            ]
        )

        if hybrid:
            logger.info(
                "qdrant_dense_retrieval_mode",
                collection=self._collection,
                hybrid_requested=True,
                reason="dense_vectors_only",
            )
        response = self._client.query_points(
            collection_name=self._collection,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
            score_threshold=score_threshold if score_threshold > 0 else None,
        )

        results = getattr(response, "points", response)
        return [
            {
                "id": str(point.id),  # type: ignore[union-attr]
                "score": float(point.score or 0.0),  # type: ignore[union-attr]
                "payload": point.payload or {},  # type: ignore[union-attr]
                "retrieval_mode": "dense",
            }
            for point in results
        ]

    def collection_exists(self) -> bool:
        existing = {item.name for item in self._client.get_collections().collections}
        return self._collection in existing
