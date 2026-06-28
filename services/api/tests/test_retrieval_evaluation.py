"""Sprint 12 tests: retrieval evaluation and answer quality."""

from __future__ import annotations

import uuid as _uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.documents.models import Document, DocumentChunk, DocumentStatus, DocumentVersion
from helpers import create_tenant_with_user, login


def _seed_chunk(
    db: AsyncSession,
    *,
    tenant_id,
    owner_user_id,
    title: str,
    text: str,
    access_scope: str = "tenant_public",
) -> DocumentChunk:
    document_id = _uuid.uuid4()
    version_id = _uuid.uuid4()
    chunk_id = _uuid.uuid4()

    document = Document(
        id=document_id,
        tenant_id=tenant_id,
        title=title,
        source_type="upload",
        language="en",
        access_scope=access_scope,
        owner_user_id=owner_user_id,
        status=DocumentStatus.ready.value,
        current_version_id=version_id,
    )
    version = DocumentVersion(
        id=version_id,
        tenant_id=tenant_id,
        document_id=document_id,
        version_number=1,
        file_name=f"{title}.txt",
        mime_type="text/plain",
        file_size_bytes=len(text.encode()),
        storage_bucket="documents",
        storage_key=f"{document_id}/{version_id}",
        checksum="abc123",
    )
    chunk = DocumentChunk(
        id=chunk_id,
        tenant_id=tenant_id,
        document_id=document_id,
        document_version_id=version_id,
        chunk_index=0,
        text=text,
        language="en",
        token_count=len(text.split()),
    )
    db.add(document)
    db.add(version)
    db.add(chunk)
    return chunk


@pytest.mark.asyncio
async def test_answer_returns_citations_when_sources_found(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_vector_store,
) -> None:
    """When authorized chunks match, the answer must include citations."""
    data = await create_tenant_with_user(db_session, f"qual-{_uuid.uuid4().hex[:6]}")
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    chunk = _seed_chunk(
        db_session,
        tenant_id=data["tenant"].id,
        owner_user_id=data["user"].id,
        title="Membership Fee",
        text="The annual membership fee is 120 EUR, due on January 1st each year.",
    )
    await db_session.flush()
    fake_vector_store.upsert_chunk_vectors([
        (
            chunk.id,
            [0.3] * 8,
            {
                "tenant_id": str(data["tenant"].id),
                "document_id": str(chunk.document_id),
                "document_version_id": str(chunk.document_version_id),
                "chunk_id": str(chunk.id),
                "access_scope": "tenant_public",
                "owner_user_id": str(data["user"].id),
                "allowed_role_ids": [],
                "language": "en",
                "source_type": "upload",
                "created_at": "2026-06-28T00:00:00Z",
            },
        )
    ])

    response = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "How much is the membership fee?"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["refused"] is False
    assert len(body["citations"]) >= 1
    assert body["confidence"] > 0.0
    assert str(chunk.id) in str(body["citations"][0]["chunk_id"])


@pytest.mark.asyncio
async def test_answer_citations_contain_excerpts(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_vector_store,
) -> None:
    """Citation excerpts must contain actual text from the source chunk."""
    data = await create_tenant_with_user(db_session, f"cite-{_uuid.uuid4().hex[:6]}")
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    original_text = "The board meeting is scheduled for the third Thursday of every month at 6 PM."
    chunk = _seed_chunk(
        db_session,
        tenant_id=data["tenant"].id,
        owner_user_id=data["user"].id,
        title="Board Meeting",
        text=original_text,
    )
    await db_session.flush()
    fake_vector_store.upsert_chunk_vectors([
        (
            chunk.id,
            [0.4] * 8,
            {
                "tenant_id": str(data["tenant"].id),
                "document_id": str(chunk.document_id),
                "document_version_id": str(chunk.document_version_id),
                "chunk_id": str(chunk.id),
                "access_scope": "tenant_public",
                "owner_user_id": str(data["user"].id),
                "allowed_role_ids": [],
                "language": "en",
                "source_type": "upload",
                "created_at": "2026-06-28T00:00:00Z",
            },
        )
    ])

    response = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "When is the board meeting?"},
    )
    assert response.status_code == 200
    body = response.json()
    excerpt = body["citations"][0]["excerpt"]
    assert "board meeting" in excerpt.lower()
    assert "Thursday" in excerpt
    assert body["citations"][0]["document_title"] == "Board Meeting"


@pytest.mark.asyncio
async def test_top_k_limits_citations(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_vector_store,
) -> None:
    """The number of citations must not exceed the requested top_k."""
    data = await create_tenant_with_user(db_session, f"topk-{_uuid.uuid4().hex[:6]}")
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    chunks: list[DocumentChunk] = []
    for i in range(6):
        chunk = _seed_chunk(
            db_session,
            tenant_id=data["tenant"].id,
            owner_user_id=data["user"].id,
            title=f"Doc {i}",
            text=f"This is document number {i} with some unique content.",
        )
        chunks.append(chunk)
    await db_session.flush()
    fake_vector_store.upsert_chunk_vectors([
        (
            chunk.id,
            [0.1 + i * 0.01] * 8,
            {
                "tenant_id": str(data["tenant"].id),
                "document_id": str(chunk.document_id),
                "document_version_id": str(chunk.document_version_id),
                "chunk_id": str(chunk.id),
                "access_scope": "tenant_public",
                "owner_user_id": str(data["user"].id),
                "allowed_role_ids": [],
                "language": "en",
                "source_type": "upload",
                "created_at": "2026-06-28T00:00:00Z",
            },
        )
        for i, chunk in enumerate(chunks)
    ])

    response = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "Tell me about documents.", "top_k": 3},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["citations"]) <= 3
    assert body["refused"] is False


@pytest.mark.asyncio
async def test_confidence_is_non_zero_when_sources_found(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_vector_store,
) -> None:
    """Confidence must be > 0 when authorized sources are retrieved."""
    data = await create_tenant_with_user(db_session, f"conf-{_uuid.uuid4().hex[:6]}")
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    chunk = _seed_chunk(
        db_session,
        tenant_id=data["tenant"].id,
        owner_user_id=data["user"].id,
        title="Payment Policy",
        text="Late payments incur a 10 EUR penalty.",
    )
    await db_session.flush()
    fake_vector_store.upsert_chunk_vectors([
        (
            chunk.id,
            [0.5] * 8,
            {
                "tenant_id": str(data["tenant"].id),
                "document_id": str(chunk.document_id),
                "document_version_id": str(chunk.document_version_id),
                "chunk_id": str(chunk.id),
                "access_scope": "tenant_public",
                "owner_user_id": str(data["user"].id),
                "allowed_role_ids": [],
                "language": "en",
                "source_type": "upload",
                "created_at": "2026-06-28T00:00:00Z",
            },
        ),
    ])

    response = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "What is the late payment penalty?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["refused"] is False
    assert body["confidence"] > 0.0
    assert len(body["citations"]) >= 1
