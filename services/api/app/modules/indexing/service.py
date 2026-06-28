from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import structlog

from app.core.config import settings
from app.modules.documents.models import Document, DocumentChunk

logger = structlog.get_logger(__name__)


class IndexingService:
    def __init__(self, embedding_provider=None, vector_store_provider=None) -> None:
        self._embedding = embedding_provider
        self._vector_store = vector_store_provider

    def _resolve_providers(self):
        if self._embedding is None:
            from app.core.dependencies import get_embedding_provider

            self._embedding = get_embedding_provider()
        if self._vector_store is None:
            from app.core.dependencies import get_vector_store_provider

            self._vector_store = get_vector_store_provider()
        return self._embedding, self._vector_store

    async def index_chunks(
        self,
        *,
        document: Document,
        document_version_id: UUID,
        chunks: list[DocumentChunk],
    ) -> int:
        if not chunks:
            return 0

        if not settings.indexing_auto_enabled:
            return 0

        embedding_provider, vector_store_provider = self._resolve_providers()
        texts = [chunk.text for chunk in chunks]
        vectors = await embedding_provider.embed_texts(texts)
        vector_store_provider.ensure_collection(embedding_provider.vector_size)

        vector_store_provider.delete_vectors_for_version(document.tenant_id, document_version_id)

        points: list[tuple[UUID, list[float], dict[str, Any]]] = []
        for chunk, vector in zip(chunks, vectors, strict=True):
            payload = build_chunk_payload(document=document, chunk=chunk)
            points.append((chunk.id, vector, payload))

        vector_store_provider.upsert_chunk_vectors(points)

        logger.info(
            "chunks_indexed",
            tenant_id=str(document.tenant_id),
            document_id=str(document.id),
            document_version_id=str(document_version_id),
            chunk_count=len(points),
        )
        return len(points)


def build_chunk_payload(*, document: Document, chunk: DocumentChunk) -> dict[str, Any]:
    allowed_role_ids: list[str] = []
    if getattr(document, "allowed_role_ids_json", None):
        import json

        try:
            parsed = json.loads(document.allowed_role_ids_json or "[]")
            if isinstance(parsed, list):
                allowed_role_ids = [str(role) for role in parsed]
        except json.JSONDecodeError:
            allowed_role_ids = []

    return {
        "tenant_id": str(document.tenant_id),
        "document_id": str(document.id),
        "document_version_id": str(chunk.document_version_id),
        "chunk_id": str(chunk.id),
        "access_scope": document.access_scope,
        "owner_user_id": str(document.owner_user_id) if document.owner_user_id else None,
        "allowed_role_ids": allowed_role_ids,
        "language": document.language,
        "source_type": document.source_type,
        "created_at": datetime.now(UTC).isoformat(),
    }
