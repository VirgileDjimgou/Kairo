"""Sprint 6 acceptance tests: secure RAG chat."""

from __future__ import annotations

import uuid as _uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.documents.models import Document, DocumentChunk, DocumentStatus, DocumentVersion
from helpers import create_tenant_with_user, login


def _seed_document_and_chunk(
    db: AsyncSession,
    *,
    tenant_id,
    owner_user_id,
    title: str,
    text: str,
    access_scope: str = "tenant_public",
    allowed_role_ids_json: str | None = None,
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
        allowed_role_ids_json=allowed_role_ids_json,
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
async def test_chat_query_returns_answer_with_citations(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_vector_store,
) -> None:
    data = await create_tenant_with_user(db_session, f"chat-{_uuid.uuid4().hex[:6]}")
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    chunk = _seed_document_and_chunk(
        db_session,
        tenant_id=data["tenant"].id,
        owner_user_id=data["user"].id,
        title="Finance Policy",
        text="The membership fee is due on the first day of each month.",
    )
    await db_session.flush()
    fake_vector_store.upsert_chunk_vectors(
        [
            (
                chunk.id,
                [0.2] * 8,
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
        ]
    )

    response = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "When is the membership fee due?"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["refused"] is False
    assert body["answer"]
    assert body["citations"]
    assert body["citations"][0]["chunk_id"] == str(chunk.id)


@pytest.mark.asyncio
async def test_chat_query_refuses_without_authorized_sources(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    data = await create_tenant_with_user(db_session, f"nohit-{_uuid.uuid4().hex[:6]}")
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    response = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "What is the secret policy?"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["refused"] is True
    assert body["citations"] == []
    assert "could not find a reliable answer" in body["answer"].lower()


@pytest.mark.asyncio
async def test_chat_query_blocks_private_document_from_other_user(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_vector_store,
) -> None:
    owner = await create_tenant_with_user(db_session, f"owner-{_uuid.uuid4().hex[:6]}")
    viewer = await create_tenant_with_user(
        db_session,
        f"viewer-{_uuid.uuid4().hex[:6]}",
        role_code="member",
        profile_type="member",
    )

    token = await login(client, viewer["user"].email, viewer["password"], tenant_slug=viewer["tenant"].slug)

    chunk = _seed_document_and_chunk(
        db_session,
        tenant_id=viewer["tenant"].id,
        owner_user_id=owner["user"].id,
        title="Private Note",
        text="This is private to the owner.",
        access_scope="user_private",
    )
    await db_session.flush()
    fake_vector_store.upsert_chunk_vectors(
        [
            (
                chunk.id,
                [0.3] * 8,
                {
                    "tenant_id": str(viewer["tenant"].id),
                    "document_id": str(chunk.document_id),
                    "document_version_id": str(chunk.document_version_id),
                    "chunk_id": str(chunk.id),
                    "access_scope": "user_private",
                    "owner_user_id": str(owner["user"].id),
                    "allowed_role_ids": [],
                    "language": "en",
                    "source_type": "upload",
                    "created_at": "2026-06-28T00:00:00Z",
                },
            )
        ]
    )

    response = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "What is in the private note?"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["refused"] is True
    assert body["citations"] == []


@pytest.mark.asyncio
async def test_chat_query_is_logged_for_admin_traceability(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_vector_store,
) -> None:
    data = await create_tenant_with_user(db_session, f"log-{_uuid.uuid4().hex[:6]}")
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    chunk = _seed_document_and_chunk(
        db_session,
        tenant_id=data["tenant"].id,
        owner_user_id=data["user"].id,
        title="Trace Policy",
        text="The trace log records each answer.",
    )
    await db_session.flush()
    fake_vector_store.upsert_chunk_vectors(
        [
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
        ]
    )

    query = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "What does the trace log record?"},
    )
    assert query.status_code == 200, query.text

    admin_token = token
    logs = await client.get(
        "/api/v1/admin/chat-queries",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert logs.status_code == 200, logs.text
    body = logs.json()
    assert len(body) == 1
    assert body[0]["question"] == "What does the trace log record?"


@pytest.mark.asyncio
async def test_non_admin_cannot_access_chat_audit(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    tenant = await create_tenant_with_user(
        db_session,
        f"member-audit-{_uuid.uuid4().hex[:6]}",
        role_code="member",
        profile_type="member",
    )
    token = await login(client, tenant["user"].email, tenant["password"], tenant_slug=tenant["tenant"].slug)

    response = await client.get(
        "/api/v1/admin/chat-queries",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
