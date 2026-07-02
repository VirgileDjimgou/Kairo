"""Sprint 6 acceptance tests: secure RAG chat."""

from __future__ import annotations

import uuid as _uuid
from decimal import Decimal
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.contributions.models import ContributionRecord
from app.modules.documents.models import Document, DocumentChunk, DocumentStatus, DocumentVersion
from app.modules.membership.models import MembershipProfile
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


def _seed_membership_profile(
    db: AsyncSession,
    *,
    tenant_id,
    user_id,
    member_code: str,
    display_name: str,
) -> MembershipProfile:
    profile = MembershipProfile(
        id=_uuid.uuid4(),
        tenant_id=tenant_id,
        user_id=user_id,
        member_code=member_code,
        first_name=display_name.split()[0],
        last_name=display_name.split()[-1],
        display_name=display_name,
        email=f"{member_code}@test.org",
        status="active",
    )
    db.add(profile)
    return profile


def _seed_contribution_record(
    db: AsyncSession,
    *,
    tenant_id,
    membership_profile_id,
    year: int,
    expected_amount: str,
    paid_amount: str,
) -> ContributionRecord:
    record = ContributionRecord(
        id=_uuid.uuid4(),
        tenant_id=tenant_id,
        membership_profile_id=membership_profile_id,
        year=year,
        expected_amount=Decimal(expected_amount),
        paid_amount=Decimal(paid_amount),
        balance=Decimal(expected_amount) - Decimal(paid_amount),
        currency="EUR",
        status="partial" if Decimal(paid_amount) < Decimal(expected_amount) else "paid",
        due_date=datetime(2026, 1, 31, tzinfo=timezone.utc),
    )
    db.add(record)
    return record


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
    assert "document" in body["source_types"]


@pytest.mark.asyncio
async def test_chat_query_refuses_without_authorized_sources(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_llm,
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
    assert len(fake_llm.calls) == 0


@pytest.mark.asyncio
async def test_chat_query_includes_structured_personal_balance_context(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_llm,
) -> None:
    data = await create_tenant_with_user(
        db_session,
        f"self-balance-{_uuid.uuid4().hex[:6]}",
        role_code="member",
        profile_type="member",
    )
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)
    profile = _seed_membership_profile(
        db_session,
        tenant_id=data["tenant"].id,
        user_id=data["user"].id,
        member_code="MEM-100",
        display_name="Alice Member",
    )
    _seed_contribution_record(
        db_session,
        tenant_id=data["tenant"].id,
        membership_profile_id=profile.id,
        year=2026,
        expected_amount="120.00",
        paid_amount="45.00",
    )
    await db_session.flush()

    response = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "What is my balance?"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["refused"] is False
    assert "structured:member_balance" in body["source_types"]
    assert len(fake_llm.calls) == 1
    user_prompt = fake_llm.calls[0]["user_prompt"]
    assert "Personal contribution balance" in user_prompt
    assert "Outstanding balance: 75.00 EUR" in user_prompt


@pytest.mark.asyncio
async def test_chat_query_blocks_private_document_from_other_user(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_vector_store,
    fake_llm,
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
    assert len(fake_llm.calls) == 0


@pytest.mark.asyncio
async def test_chat_query_refuses_other_member_finance_requests_before_llm(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_llm,
) -> None:
    data = await create_tenant_with_user(
        db_session,
        f"other-balance-{_uuid.uuid4().hex[:6]}",
        role_code="member",
        profile_type="member",
    )
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    response = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "What is another member's balance?"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["refused"] is True
    assert "another member" in body["refusal_reason"].lower()
    assert len(fake_llm.calls) == 0


@pytest.mark.asyncio
async def test_chat_query_includes_tenant_finance_summary_for_auditor(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_llm,
) -> None:
    data = await create_tenant_with_user(
        db_session,
        f"finance-summary-{_uuid.uuid4().hex[:6]}",
        role_code="auditor",
        profile_type="staff",
    )
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    profile = _seed_membership_profile(
        db_session,
        tenant_id=data["tenant"].id,
        user_id=data["user"].id,
        member_code="AUD-001",
        display_name="Auditor User",
    )
    _seed_contribution_record(
        db_session,
        tenant_id=data["tenant"].id,
        membership_profile_id=profile.id,
        year=2026,
        expected_amount="120.00",
        paid_amount="45.00",
    )
    _seed_contribution_record(
        db_session,
        tenant_id=data["tenant"].id,
        membership_profile_id=profile.id,
        year=2025,
        expected_amount="100.00",
        paid_amount="100.00",
    )
    await db_session.flush()

    response = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "Give me the contribution summary for the tenant."},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["refused"] is False
    assert "structured:finance_summary" in body["source_types"]
    assert len(fake_llm.calls) == 1
    user_prompt = fake_llm.calls[0]["user_prompt"]
    assert "Tenant contribution summary" in user_prompt
    assert "Total expected: 220.00 EUR" in user_prompt
    assert "Outstanding balance: 75.00 EUR" in user_prompt


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
    assert "document" in body[0]["source_types_json"]


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
