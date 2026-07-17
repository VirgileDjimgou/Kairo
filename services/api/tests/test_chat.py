"""Sprint 6 acceptance tests: secure RAG chat."""

from __future__ import annotations

import uuid as _uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from helpers import create_tenant_with_user, create_user_for_tenant, login
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.contributions.models import ContributionRecord
from app.modules.documents.models import Document, DocumentChunk, DocumentStatus, DocumentVersion
from app.modules.membership.models import MembershipProfile


def _seed_document_and_chunk(
    db: AsyncSession,
    *,
    tenant_id,
    owner_user_id,
    title: str,
    text: str,
    access_scope: str = "tenant_public",
    language: str = "en",
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
        language=language,
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
        language=language,
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
        due_date=datetime(2026, 1, 31, tzinfo=UTC),
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

    conversation = await client.get(
        f"/api/v1/chat/conversations/{body['conversation_id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert conversation.status_code == 200, conversation.text
    conversation_body = conversation.json()
    assert conversation_body["messages"][1]["citations_json"]
    assert conversation_body["messages"][1]["citations_json"][0]["document_title"] == "Finance Policy"


@pytest.mark.asyncio
async def test_chat_query_works_after_explicit_conversation_creation(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_vector_store,
) -> None:
    data = await create_tenant_with_user(db_session, f"chat-create-{_uuid.uuid4().hex[:6]}")
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    chunk = _seed_document_and_chunk(
        db_session,
        tenant_id=data["tenant"].id,
        owner_user_id=data["user"].id,
        title="Governance Charter",
        text="The internal regulation is detailed in the charter and conduct code.",
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

    created = await client.post(
        "/api/v1/chat/conversations",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Nouvelle conversation"},
    )
    assert created.status_code == 201, created.text
    conversation_id = created.json()["id"]

    response = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "conversation_id": conversation_id,
            "question": "Which documents mention the internal regulation?",
            "response_language": "en",
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["conversation_id"] == conversation_id
    assert body["answer"]
    assert body["citations"]


@pytest.mark.asyncio
async def test_chat_list_conversations_after_creation(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    data = await create_tenant_with_user(db_session, f"chat-list-{_uuid.uuid4().hex[:6]}")
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    created = await client.post(
        "/api/v1/chat/conversations",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Nouvelle conversation"},
    )
    assert created.status_code == 201, created.text

    listed = await client.get(
        "/api/v1/chat/conversations",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert listed.status_code == 200, listed.text
    conversations = listed.json()
    assert len(conversations) == 1
    assert conversations[0]["title"] == "Nouvelle conversation"
    assert conversations[0]["message_count"] == 0


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
        json={"question": "What is the secret policy?", "response_language": "en"},
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
        json={"question": "What is my balance?", "response_language": "de"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["refused"] is False
    assert "structured:member_balance" in body["source_types"]
    assert len(fake_llm.calls) == 1
    user_prompt = fake_llm.calls[0]["user_prompt"]
    assert "Personal contribution balance" in user_prompt
    assert "Outstanding balance: 75.00 EUR" in user_prompt
    assert "Response language: de" in user_prompt
    assert "Role profile: member" in user_prompt
    assert "Use this structure when a full answer is appropriate" in user_prompt


@pytest.mark.asyncio
async def test_chat_query_includes_structured_personal_balance_context_for_french_question(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_llm,
) -> None:
    data = await create_tenant_with_user(
        db_session,
        f"self-balance-fr-{_uuid.uuid4().hex[:6]}",
        role_code="member",
        profile_type="member",
    )
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)
    profile = _seed_membership_profile(
        db_session,
        tenant_id=data["tenant"].id,
        user_id=data["user"].id,
        member_code="MEM-101",
        display_name="Aline Ndzi",
    )
    _seed_contribution_record(
        db_session,
        tenant_id=data["tenant"].id,
        membership_profile_id=profile.id,
        year=2026,
        expected_amount="125.00",
        paid_amount="50.00",
    )
    await db_session.flush()

    response = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "Quel est mon solde ?", "response_language": "fr"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["refused"] is False
    assert "structured:member_balance" in body["source_types"]
    assert len(fake_llm.calls) == 1
    user_prompt = fake_llm.calls[0]["user_prompt"]
    assert "Outstanding balance: 75.00 EUR" in user_prompt
    assert "Response language: fr" in user_prompt


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
async def test_chat_query_allows_principal_admin_to_access_privileged_document_scopes(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_vector_store,
    fake_llm,
) -> None:
    admin_ctx = await create_tenant_with_user(db_session, f"principal-doc-{_uuid.uuid4().hex[:6]}")
    principal_ctx = await create_user_for_tenant(
        db_session,
        tenant_id=admin_ctx["tenant"].id,
        email=f"principal-doc-{_uuid.uuid4().hex[:6]}@test.org",
        password="Principal123!",
        display_name="Pauline Ebanda",
        role_code="principal_admin",
        profile_type="admin",
    )
    token = await login(
        client,
        principal_ctx["user"].email,
        principal_ctx["password"],
        tenant_slug=admin_ctx["tenant"].slug,
    )

    private_chunk = _seed_document_and_chunk(
        db_session,
        tenant_id=admin_ctx["tenant"].id,
        owner_user_id=admin_ctx["user"].id,
        title="Private Treasurer Notes",
        text="Private operator notes remain available to the principal admin inside the tenant.",
        access_scope="user_private",
    )
    admin_only_chunk = _seed_document_and_chunk(
        db_session,
        tenant_id=admin_ctx["tenant"].id,
        owner_user_id=admin_ctx["user"].id,
        title="Admin Runbook",
        text="Administrative runbook for sensitive tenant operations.",
        access_scope="admin_only",
    )
    await db_session.flush()
    fake_vector_store.upsert_chunk_vectors(
        [
            (
                private_chunk.id,
                [0.31] * 8,
                {
                    "tenant_id": str(admin_ctx["tenant"].id),
                    "document_id": str(private_chunk.document_id),
                    "document_version_id": str(private_chunk.document_version_id),
                    "chunk_id": str(private_chunk.id),
                    "access_scope": "user_private",
                    "owner_user_id": str(admin_ctx["user"].id),
                    "allowed_role_ids": [],
                    "language": "fr",
                    "source_type": "upload",
                    "created_at": "2026-07-15T00:00:00Z",
                },
            ),
            (
                admin_only_chunk.id,
                [0.32] * 8,
                {
                    "tenant_id": str(admin_ctx["tenant"].id),
                    "document_id": str(admin_only_chunk.document_id),
                    "document_version_id": str(admin_only_chunk.document_version_id),
                    "chunk_id": str(admin_only_chunk.id),
                    "access_scope": "admin_only",
                    "owner_user_id": str(admin_ctx["user"].id),
                    "allowed_role_ids": [],
                    "language": "fr",
                    "source_type": "upload",
                    "created_at": "2026-07-15T00:00:00Z",
                },
            ),
        ]
    )

    response = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "question": "Montre-moi les notes privees et le runbook administratif.",
            "response_language": "fr",
        },
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["refused"] is False
    assert len(body["citations"]) == 2
    assert len(fake_llm.calls) == 1


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
        json={
            "question": "Quelle est la cotisation de Boris Schneider ?",
            "response_language": "fr",
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["refused"] is True
    assert "autre membre" in body["refusal_reason"].lower()
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
    assert "Role profile: auditor" in user_prompt
    assert "numbers first" in user_prompt or "numbers and items" in user_prompt


@pytest.mark.asyncio
async def test_chat_stream_emits_citations_and_source_types(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_vector_store,
    fake_llm,
) -> None:
    data = await create_tenant_with_user(db_session, f"stream-{_uuid.uuid4().hex[:6]}")
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    chunk = _seed_document_and_chunk(
        db_session,
        tenant_id=data["tenant"].id,
        owner_user_id=data["user"].id,
        title="Streaming Policy",
        text="Streaming answers should preserve citations.",
    )
    await db_session.flush()
    fake_vector_store.upsert_chunk_vectors(
        [
            (
                chunk.id,
                [0.25] * 8,
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

    async with client.stream(
        "POST",
        "/api/v1/chat/query-stream",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "What does the streaming policy say?"},
    ) as response:
        status = response.status_code
        body = await response.aread()
        assert status == 200, body

    text = body.decode()
    assert '"type": "done"' in text
    assert '"citations"' in text
    assert '"source_types"' in text
    assert len(fake_llm.calls) == 1
    assert "Answer in the requested response language only." in fake_llm.calls[0]["user_prompt"]


@pytest.mark.asyncio
async def test_chat_stream_refuses_without_authorized_sources(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_llm,
) -> None:
    data = await create_tenant_with_user(db_session, f"stream-nohit-{_uuid.uuid4().hex[:6]}")
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    async with client.stream(
        "POST",
        "/api/v1/chat/query-stream",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "What is the secret policy?", "response_language": "en"},
    ) as response:
        status = response.status_code
        body = await response.aread()
        assert status == 200, body

    text = body.decode()
    assert '"type": "error"' in text
    assert "authorized documents or structured data available to you" in text
    assert len(fake_llm.calls) == 0


@pytest.mark.asyncio
async def test_chat_query_prefers_documents_in_user_language(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_llm,
    fake_vector_store,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.core.dependencies import get_reranker_provider
    from app.main import app

    app.dependency_overrides[get_reranker_provider] = lambda: None
    try:
        data = await create_tenant_with_user(db_session, f"lang-{_uuid.uuid4().hex[:6]}")
        token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

        owner_user_id = data["user"].id

        fr_chunk = _seed_document_and_chunk(
            db_session,
            tenant_id=data["tenant"].id,
            owner_user_id=owner_user_id,
            title="Règlement intérieur",
            text="Les cotisations doivent être payées avant le 10 de chaque mois.",
            access_scope="tenant_public",
            language="fr",
        )
        en_chunk = _seed_document_and_chunk(
            db_session,
            tenant_id=data["tenant"].id,
            owner_user_id=owner_user_id,
            title="Bylaws",
            text="Contributions must be paid before the 10th day of each month.",
            access_scope="tenant_public",
        )
        await db_session.flush()
        captured_search_kwargs: dict[str, object] = {}

        def _fake_search_chunk_vectors(**kwargs):
            captured_search_kwargs.update(kwargs)
            return [
                {
                    "id": str(en_chunk.id),
                    "score": 0.93,
                    "payload": {
                        "tenant_id": str(data["tenant"].id),
                        "document_id": str(en_chunk.document_id),
                        "document_version_id": str(en_chunk.document_version_id),
                        "chunk_id": str(en_chunk.id),
                        "access_scope": "tenant_public",
                        "owner_user_id": str(owner_user_id),
                        "allowed_role_ids": [],
                        "language": "en",
                        "source_type": "upload",
                        "created_at": "2026-06-28T00:00:00Z",
                    },
                },
                {
                    "id": str(fr_chunk.id),
                    "score": 0.93,
                    "payload": {
                        "tenant_id": str(data["tenant"].id),
                        "document_id": str(fr_chunk.document_id),
                        "document_version_id": str(fr_chunk.document_version_id),
                        "chunk_id": str(fr_chunk.id),
                        "access_scope": "tenant_public",
                        "owner_user_id": str(owner_user_id),
                        "allowed_role_ids": [],
                        "language": "fr",
                        "source_type": "upload",
                        "created_at": "2026-06-28T00:00:00Z",
                    },
                },
            ]

        monkeypatch.setattr(fake_vector_store, "search_chunk_vectors", _fake_search_chunk_vectors)

        response = await client.post(
            "/api/v1/chat/query",
            headers={"Authorization": f"Bearer {token}"},
            json={"question": "Quels documents parlent des règlements ?", "response_language": "fr"},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["citations"][0]["document_title"] == "Règlement intérieur"
        assert fake_llm.calls[0]["system_prompt"].startswith("You are a grounded assistant")
        assert "query_text" in captured_search_kwargs
        assert "français" in str(captured_search_kwargs["query_text"]).lower()
        assert "document" in str(captured_search_kwargs["query_text"]).lower()
    finally:
        app.dependency_overrides.pop(get_reranker_provider, None)


@pytest.mark.asyncio
async def test_chat_query_prefers_keyword_matching_documents_when_dense_scores_are_close(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_llm,
    fake_vector_store,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.core.dependencies import get_reranker_provider
    from app.main import app

    app.dependency_overrides[get_reranker_provider] = lambda: None
    try:
        data = await create_tenant_with_user(db_session, f"keyword-rank-{_uuid.uuid4().hex[:6]}")
        token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)
        owner_user_id = data["user"].id

        keyword_chunk = _seed_document_and_chunk(
            db_session,
            tenant_id=data["tenant"].id,
            owner_user_id=owner_user_id,
            title="Reglement interieur",
            text="Le reglement interieur explique les regles de fonctionnement interne.",
            access_scope="tenant_public",
            language="fr",
        )
        generic_chunk = _seed_document_and_chunk(
            db_session,
            tenant_id=data["tenant"].id,
            owner_user_id=owner_user_id,
            title="Guide general",
            text="Guide general pour les membres de l'association.",
            access_scope="tenant_public",
            language="fr",
        )
        await db_session.flush()

        def _fake_search_chunk_vectors(**kwargs):
            return [
                {
                    "id": str(generic_chunk.id),
                    "score": 0.84,
                    "payload": {
                        "tenant_id": str(data["tenant"].id),
                        "document_id": str(generic_chunk.document_id),
                        "document_version_id": str(generic_chunk.document_version_id),
                        "chunk_id": str(generic_chunk.id),
                        "access_scope": "tenant_public",
                        "owner_user_id": str(owner_user_id),
                        "allowed_role_ids": [],
                        "language": "fr",
                        "source_type": "upload",
                        "created_at": "2026-07-16T00:00:00Z",
                    },
                    "retrieval_mode": "dense",
                },
                {
                    "id": str(keyword_chunk.id),
                    "score": 0.78,
                    "payload": {
                        "tenant_id": str(data["tenant"].id),
                        "document_id": str(keyword_chunk.document_id),
                        "document_version_id": str(keyword_chunk.document_version_id),
                        "chunk_id": str(keyword_chunk.id),
                        "access_scope": "tenant_public",
                        "owner_user_id": str(owner_user_id),
                        "allowed_role_ids": [],
                        "language": "fr",
                        "source_type": "upload",
                        "created_at": "2026-07-16T00:00:00Z",
                    },
                    "retrieval_mode": "dense",
                },
            ]

        monkeypatch.setattr(fake_vector_store, "search_chunk_vectors", _fake_search_chunk_vectors)

        response = await client.post(
            "/api/v1/chat/query",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "question": "Quels documents parlent du reglement interieur ?",
                "response_language": "fr",
            },
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["citations"][0]["document_title"] == "Reglement interieur"
        assert len(fake_llm.calls) == 1
    finally:
        app.dependency_overrides.pop(get_reranker_provider, None)


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

    refused_query = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "What is another member's balance?", "response_language": "en"},
    )
    assert refused_query.status_code == 200, refused_query.text

    admin_token = token
    logs = await client.get(
        "/api/v1/admin/chat-queries",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"search": "trace", "refused": False},
    )
    assert logs.status_code == 200, logs.text
    body = logs.json()
    assert len(body) == 1
    assert body[0]["question_preview"] == "What does the trace log record?"
    assert body[0]["answer_preview"]
    assert body[0]["citation_count"] == 1
    assert "document" in body[0]["source_types"]

    refused_logs = await client.get(
        "/api/v1/admin/chat-queries",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"search": "another member", "refused": True},
    )
    assert refused_logs.status_code == 200, refused_logs.text
    refused_body = refused_logs.json()
    assert len(refused_body) == 1
    assert refused_body[0]["refused"] is True
    assert "another member" in refused_body[0]["refusal_reason_preview"].lower()


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
