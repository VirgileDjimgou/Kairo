from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from helpers import create_tenant_with_user, create_user_for_tenant, login
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.announcements.models import Announcement
from app.modules.disciplinary.models import DisciplinaryRecord
from app.modules.documents.models import Document
from app.modules.events.models import Event


async def _add_document(db: AsyncSession, tenant_id: uuid.UUID, title: str, access_scope: str, owner_id=None) -> None:
    db.add(
        Document(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            title=title,
            access_scope=access_scope,
            owner_user_id=owner_id,
        )
    )
    await db.flush()


async def _add_event(db: AsyncSession, tenant_id: uuid.UUID, title: str, visibility: str) -> None:
    db.add(
        Event(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            title=title,
            description="search fixture",
            location="Somewhere",
            start_at=datetime(2026, 12, 1, 10, 0, tzinfo=UTC),
            end_at=datetime(2026, 12, 1, 12, 0, tzinfo=UTC),
            visibility_scope=visibility,
            status="published",
        )
    )
    await db.flush()


async def _add_announcement(db: AsyncSession, tenant_id: uuid.UUID, title: str, visibility: str) -> None:
    db.add(
        Announcement(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            title=title,
            body="search fixture body",
            visibility_scope=visibility,
            published_at=datetime(2026, 11, 1, tzinfo=UTC),
        )
    )
    await db.flush()


async def _add_discipline(db: AsyncSession, tenant_id: uuid.UUID, profile_id, title: str) -> None:
    db.add(
        DisciplinaryRecord(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            membership_profile_id=profile_id,
            policy_record_id=None,
            title=title,
            description=f"{title} description",
            amount=Decimal("10.00"),
            currency="EUR",
            status="open",
            metadata_json="{}",
        )
    )
    await db.flush()


async def _search(client: AsyncClient, token: str, query: str):
    response = await client.get(
        "/api/v1/search",
        params={"q": query},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    return response.json()["results"]


@pytest.mark.asyncio
async def test_member_search_never_returns_inaccessible_titles(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    context = await create_tenant_with_user(db_session, f"srch-a-{uuid.uuid4().hex[:6]}", role_code="admin")
    member = await create_user_for_tenant(
        db_session,
        tenant_id=context["tenant"].id,
        email="search-member@example.org",
        password="MemberPass1!",
        display_name="Search Member",
        role_code="member",
        member_code="SRCH-001",
    )
    token = await login(client, member["user"].email, member["password"], context["tenant"].slug)

    await _add_document(db_session, context["tenant"].id, "Confidential board minutes", "admin_only")
    await _add_event(db_session, context["tenant"].id, "Confidential cup", "admin_only")
    await _add_event(db_session, context["tenant"].id, "Open confidential cup", "members_only")
    await _add_announcement(db_session, context["tenant"].id, "Confidential news", "admin_only")
    await _add_discipline(db_session, context["tenant"].id, member["profile"].id, "Confidential case")
    await db_session.commit()

    results = await _search(client, token, "Confidential")
    titles = [row["title"] for row in results]

    assert "Open confidential cup" in titles
    for forbidden in (
        "Confidential board minutes",
        "Confidential cup",
        "Confidential news",
        "Confidential case",
    ):
        assert forbidden not in titles


@pytest.mark.asyncio
async def test_cross_module_search_ranks_and_labels_results(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    context = await create_tenant_with_user(db_session, f"srch-b-{uuid.uuid4().hex[:6]}", role_code="treasurer")
    token = await login(client, context["user"].email, context["password"], context["tenant"].slug)

    member = await create_user_for_tenant(
        db_session,
        tenant_id=context["tenant"].id,
        email="alice@example.org",
        password="MemberPass1!",
        display_name="Alice",
        role_code="member",
        member_code="SRCH-002",
    )
    await _add_event(db_session, context["tenant"].id, "Alice tournament", "members_only")
    await _add_announcement(db_session, context["tenant"].id, "Alice news", "members_only")
    await _add_discipline(db_session, context["tenant"].id, member["profile"].id, "Alice case")
    await db_session.commit()

    results = await _search(client, token, "Alice")
    titles = [row["title"] for row in results]

    # Exact match ranks above prefix matches.
    assert titles[0] == "Alice"
    assert "Alice tournament" in titles
    assert "Alice news" in titles
    # Treasurer has no discipline read access: the record title never appears.
    assert "Alice case" not in titles

    by_type = {row["type"] for row in results}
    assert {"members", "events", "announcements"} <= by_type
    for row in results:
        assert row["type_key"].startswith("search.types.")
        assert row["target_path"].startswith("/")


@pytest.mark.asyncio
async def test_search_is_tenant_scoped(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    first = await create_tenant_with_user(db_session, f"srch-c1-{uuid.uuid4().hex[:6]}", role_code="admin")
    second = await create_tenant_with_user(db_session, f"srch-c2-{uuid.uuid4().hex[:6]}", role_code="admin")

    await _add_event(db_session, first["tenant"].id, "Secret cup", "members_only")
    await db_session.commit()

    token_b = await login(client, second["user"].email, second["password"], second["tenant"].slug)
    results = await _search(client, token_b, "Secret")
    assert results == []


@pytest.mark.asyncio
async def test_search_respects_role_boundaries(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    context = await create_tenant_with_user(db_session, f"srch-d-{uuid.uuid4().hex[:6]}", role_code="admin")
    censor = await create_user_for_tenant(
        db_session,
        tenant_id=context["tenant"].id,
        email="search-censor@example.org",
        password="CensorPass1!",
        display_name="Search Censor",
        role_code="censor",
    )
    auditor = await create_user_for_tenant(
        db_session,
        tenant_id=context["tenant"].id,
        email="search-auditor@example.org",
        password="AuditorPass1!",
        display_name="Search Auditor",
        role_code="auditor",
    )
    member = await create_user_for_tenant(
        db_session,
        tenant_id=context["tenant"].id,
        email="search-member2@example.org",
        password="MemberPass1!",
        display_name="Search Member2",
        role_code="member",
        member_code="SRCH-003",
    )
    await _add_discipline(db_session, context["tenant"].id, member["profile"].id, "Confidential case")
    await _add_document(db_session, context["tenant"].id, "Confidential minutes", "admin_only")
    await db_session.commit()

    censor_token = await login(client, censor["user"].email, censor["password"], context["tenant"].slug)
    auditor_token = await login(client, auditor["user"].email, auditor["password"], context["tenant"].slug)
    admin_token = await login(client, context["user"].email, context["password"], context["tenant"].slug)

    censor_titles = [row["title"] for row in await _search(client, censor_token, "Confidential")]
    assert "Confidential case" in censor_titles
    assert "Confidential minutes" not in censor_titles

    auditor_titles = [row["title"] for row in await _search(client, auditor_token, "Confidential")]
    assert "Confidential case" not in auditor_titles
    assert "Confidential minutes" not in auditor_titles

    admin_titles = [row["title"] for row in await _search(client, admin_token, "Confidential")]
    assert "Confidential case" in admin_titles
    assert "Confidential minutes" in admin_titles


@pytest.mark.asyncio
async def test_empty_query_returns_no_results(client: AsyncClient, db_session: AsyncSession) -> None:
    context = await create_tenant_with_user(db_session, f"srch-e-{uuid.uuid4().hex[:6]}", role_code="admin")
    token = await login(client, context["user"].email, context["password"], context["tenant"].slug)
    results = await _search(client, token, "   ")
    assert results == []
