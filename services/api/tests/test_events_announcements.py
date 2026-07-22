"""Sprint 10 integration tests: events and announcements."""

from __future__ import annotations

import uuid as _uuid

import pytest
from helpers import create_tenant_with_user, create_user_for_tenant, login
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


async def _create_linked_member(
    db: AsyncSession,
    *,
    tenant_id,
    email: str,
    password: str,
    member_code: str,
    display_name: str,
    role_code: str = "member",
) -> dict:
    from app.core.security import hash_password
    from app.modules.identity.models import User
    from app.modules.membership.models import MembershipProfile
    from app.modules.tenancy.models import Role, TenantUser, user_roles

    user = User(
        id=_uuid.uuid4(),
        email=email,
        password_hash=hash_password(password),
        display_name=display_name,
        status="active",
    )
    db.add(user)
    await db.flush()

    role = await db.get(Role, _uuid.uuid4())
    role = Role(
        id=_uuid.uuid4(),
        tenant_id=tenant_id,
        code=role_code,
        name=role_code.title(),
        is_system_role=role_code in {"admin", "member"},
    )
    db.add(role)
    await db.flush()

    tenant_user = TenantUser(
        id=_uuid.uuid4(),
        tenant_id=tenant_id,
        user_id=user.id,
        profile_type=role_code,
        membership_status="active",
    )
    db.add(tenant_user)
    await db.flush()

    await db.execute(
        user_roles.insert().values(
            tenant_user_id=tenant_user.id,
            role_id=role.id,
        )
    )

    profile = MembershipProfile(
        id=_uuid.uuid4(),
        tenant_id=tenant_id,
        user_id=user.id,
        member_code=member_code,
        first_name=display_name.split()[0],
        last_name=display_name.split()[-1],
        display_name=display_name,
        email=email,
        status="active",
    )
    db.add(profile)
    await db.flush()
    return {"user": user, "password": password, "profile": profile, "tenant_user": tenant_user, "role": role}


# ── Events ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_admin_can_create_and_list_events(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    ctx = await create_tenant_with_user(db_session, f"evt-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)

    created = await client.post(
        "/api/v1/events/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Annual General Meeting",
            "description": "Yearly members assembly",
            "start_at": "2026-07-15T10:00:00Z",
            "end_at": "2026-07-15T12:00:00Z",
            "location": "Main Hall",
            "visibility_scope": "tenant_public",
            "status": "published",
        },
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["title"] == "Annual General Meeting"
    assert body["status"] == "published"
    event_id = body["id"]

    listing = await client.get(
        "/api/v1/events/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert listing.status_code == 200, listing.text
    assert any(e["id"] == event_id for e in listing.json())


@pytest.mark.asyncio
async def test_admin_can_update_event(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    ctx = await create_tenant_with_user(db_session, f"evt-upd-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)

    created = await client.post(
        "/api/v1/events/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Workshop",
            "start_at": "2026-08-01T09:00:00Z",
            "end_at": "2026-08-01T17:00:00Z",
            "visibility_scope": "tenant_public",
            "status": "draft",
        },
    )
    assert created.status_code == 201, created.text
    event_id = created.json()["id"]

    updated = await client.patch(
        f"/api/v1/events/{event_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Advanced Workshop", "status": "published"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["title"] == "Advanced Workshop"
    assert updated.json()["status"] == "published"


@pytest.mark.asyncio
async def test_admin_can_delete_event(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    ctx = await create_tenant_with_user(db_session, f"evt-del-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)

    created = await client.post(
        "/api/v1/events/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Disposable Event",
            "start_at": "2026-09-01T10:00:00Z",
            "end_at": "2026-09-01T11:00:00Z",
            "visibility_scope": "tenant_public",
        },
    )
    assert created.status_code == 201, created.text
    event_id = created.json()["id"]

    deleted = await client.delete(
        f"/api/v1/events/{event_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert deleted.status_code == 204

    fetched = await client.get(
        f"/api/v1/events/{event_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert fetched.status_code == 404


@pytest.mark.asyncio
async def test_member_can_read_public_events(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    ctx = await create_tenant_with_user(db_session, f"evt-pub-{_uuid.uuid4().hex[:6]}")
    member = await _create_linked_member(
        db_session,
        tenant_id=ctx["tenant"].id,
        email=f"member-evt-{_uuid.uuid4().hex[:6]}@test.org",
        password="MemberPass1!",
        member_code="ME-001",
        display_name="Member Events",
    )

    admin_token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)
    member_token = await login(client, member["user"].email, member["password"], tenant_slug=ctx["tenant"].slug)

    await client.post(
        "/api/v1/events/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Public Meeting",
            "start_at": "2026-10-01T10:00:00Z",
            "end_at": "2026-10-01T12:00:00Z",
            "visibility_scope": "tenant_public",
            "status": "published",
        },
    )

    await client.post(
        "/api/v1/events/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Admin Only",
            "start_at": "2026-10-02T10:00:00Z",
            "end_at": "2026-10-02T12:00:00Z",
            "visibility_scope": "admin_only",
            "status": "published",
        },
    )

    listing = await client.get(
        "/api/v1/events/public",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert listing.status_code == 200
    titles = [e["title"] for e in listing.json()]
    assert "Public Meeting" in titles
    assert "Admin Only" not in titles


@pytest.mark.asyncio
async def test_non_admin_cannot_create_events(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    ctx = await create_tenant_with_user(db_session, f"evt-lock-{_uuid.uuid4().hex[:6]}")
    member = await _create_linked_member(
        db_session,
        tenant_id=ctx["tenant"].id,
        email=f"member-lock-{_uuid.uuid4().hex[:6]}@test.org",
        password="MemberPass2!",
        member_code="ME-002",
        display_name="Member Lock",
    )

    token = await login(client, member["user"].email, member["password"], tenant_slug=ctx["tenant"].slug)
    response = await client.post(
        "/api/v1/events/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Blocked Event",
            "start_at": "2026-11-01T10:00:00Z",
            "end_at": "2026-11-01T11:00:00Z",
            "visibility_scope": "tenant_public",
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_events_are_tenant_isolated(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    alpha = await create_tenant_with_user(db_session, f"evt-alpha-{_uuid.uuid4().hex[:6]}")
    beta = await create_tenant_with_user(db_session, f"evt-beta-{_uuid.uuid4().hex[:6]}")

    token_alpha = await login(client, alpha["user"].email, alpha["password"], tenant_slug=alpha["tenant"].slug)
    token_beta = await login(client, beta["user"].email, beta["password"], tenant_slug=beta["tenant"].slug)

    await client.post(
        "/api/v1/events/",
        headers={"Authorization": f"Bearer {token_alpha}"},
        json={
            "title": "Alpha Event",
            "start_at": "2026-12-01T10:00:00Z",
            "end_at": "2026-12-01T11:00:00Z",
            "visibility_scope": "tenant_public",
            "status": "published",
        },
    )

    beta_events = await client.get(
        "/api/v1/events/",
        headers={"Authorization": f"Bearer {token_beta}"},
    )
    assert beta_events.status_code == 200
    assert len(beta_events.json()) == 0


@pytest.mark.asyncio
async def test_sports_events_are_tenant_isolated(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    alpha = await create_tenant_with_user(db_session, f"sports-alpha-{_uuid.uuid4().hex[:6]}")
    beta = await create_tenant_with_user(db_session, f"sports-beta-{_uuid.uuid4().hex[:6]}")
    alpha_manager = await create_user_for_tenant(
        db_session,
        tenant_id=alpha["tenant"].id,
        email=f"sports-alpha-{_uuid.uuid4().hex[:6]}@test.org",
        password="SportsTenant1!",
        display_name="Sports Alpha",
        role_code="sports_manager",
        profile_type="staff",
    )
    await db_session.commit()

    alpha_token = await login(
        client,
        alpha_manager["user"].email,
        alpha_manager["password"],
        tenant_slug=alpha["tenant"].slug,
    )
    beta_token = await login(
        client,
        beta["user"].email,
        beta["password"],
        tenant_slug=beta["tenant"].slug,
    )

    created = await client.post(
        "/api/v1/sports/events",
        headers={"Authorization": f"Bearer {alpha_token}"},
        json={
            "title": "Alpha Sports Session",
            "start_at": "2026-12-01T10:00:00Z",
            "end_at": "2026-12-01T12:00:00Z",
            "visibility_scope": "members_only",
            "status": "published",
            "metadata_json": {"sport_type": "training"},
        },
    )
    assert created.status_code == 201, created.text
    assert created.json()["metadata_json"]["workspace"] == "sports"

    beta_list = await client.get(
        "/api/v1/sports/events",
        headers={"Authorization": f"Bearer {beta_token}"},
    )
    assert beta_list.status_code == 200, beta_list.text
    assert len(beta_list.json()) == 0


# ── Announcements ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_admin_can_create_and_list_announcements(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    ctx = await create_tenant_with_user(db_session, f"ann-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)

    created = await client.post(
        "/api/v1/announcements/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Holiday Notice",
            "body": "Office will be closed on July 14th.",
            "visibility_scope": "tenant_public",
            "status": "published",
            "published_at": "2026-06-01T00:00:00Z",
        },
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["title"] == "Holiday Notice"
    ann_id = body["id"]

    listing = await client.get(
        "/api/v1/announcements/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert listing.status_code == 200
    assert any(a["id"] == ann_id for a in listing.json())


@pytest.mark.asyncio
async def test_admin_can_update_announcement(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    ctx = await create_tenant_with_user(db_session, f"ann-upd-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)

    created = await client.post(
        "/api/v1/announcements/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Notice",
            "body": "Original body",
            "visibility_scope": "tenant_public",
            "status": "draft",
        },
    )
    assert created.status_code == 201
    ann_id = created.json()["id"]

    updated = await client.patch(
        f"/api/v1/announcements/{ann_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Updated Notice", "body": "Updated body", "status": "published"},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated Notice"
    assert updated.json()["body"] == "Updated body"


@pytest.mark.asyncio
async def test_admin_can_delete_announcement(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    ctx = await create_tenant_with_user(db_session, f"ann-del-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)

    created = await client.post(
        "/api/v1/announcements/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Temp Notice",
            "body": "Will be deleted",
            "visibility_scope": "tenant_public",
        },
    )
    assert created.status_code == 201
    ann_id = created.json()["id"]

    deleted = await client.delete(
        f"/api/v1/announcements/{ann_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert deleted.status_code == 204

    fetched = await client.get(
        f"/api/v1/announcements/{ann_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert fetched.status_code == 404


@pytest.mark.asyncio
async def test_member_can_read_public_announcements(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    ctx = await create_tenant_with_user(db_session, f"ann-pub-{_uuid.uuid4().hex[:6]}")
    member = await _create_linked_member(
        db_session,
        tenant_id=ctx["tenant"].id,
        email=f"member-ann-{_uuid.uuid4().hex[:6]}@test.org",
        password="MemberAnn1!",
        member_code="MA-001",
        display_name="Member Announcements",
    )

    admin_token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)
    member_token = await login(client, member["user"].email, member["password"], tenant_slug=ctx["tenant"].slug)

    await client.post(
        "/api/v1/announcements/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Public Announcement",
            "body": "For everyone",
            "visibility_scope": "tenant_public",
            "status": "published",
            "published_at": "2026-06-01T00:00:00Z",
        },
    )

    await client.post(
        "/api/v1/announcements/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Admin Only Announcement",
            "body": "Secret",
            "visibility_scope": "admin_only",
            "status": "published",
            "published_at": "2026-06-01T00:00:00Z",
        },
    )

    listing = await client.get(
        "/api/v1/announcements/active",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert listing.status_code == 200
    titles = [a["title"] for a in listing.json()]
    assert "Public Announcement" in titles
    assert "Admin Only Announcement" not in titles


@pytest.mark.asyncio
async def test_non_admin_cannot_create_announcements(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    ctx = await create_tenant_with_user(db_session, f"ann-lock-{_uuid.uuid4().hex[:6]}")
    member = await _create_linked_member(
        db_session,
        tenant_id=ctx["tenant"].id,
        email=f"member-ann-lock-{_uuid.uuid4().hex[:6]}@test.org",
        password="MemberLock1!",
        member_code="MA-002",
        display_name="Member Lock",
    )

    token = await login(client, member["user"].email, member["password"], tenant_slug=ctx["tenant"].slug)
    response = await client.post(
        "/api/v1/announcements/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Blocked Announcement",
            "body": "Should not be created",
            "visibility_scope": "tenant_public",
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_announcements_are_tenant_isolated(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    alpha = await create_tenant_with_user(db_session, f"ann-alpha-{_uuid.uuid4().hex[:6]}")
    beta = await create_tenant_with_user(db_session, f"ann-beta-{_uuid.uuid4().hex[:6]}")

    token_alpha = await login(client, alpha["user"].email, alpha["password"], tenant_slug=alpha["tenant"].slug)
    token_beta = await login(client, beta["user"].email, beta["password"], tenant_slug=beta["tenant"].slug)

    await client.post(
        "/api/v1/announcements/",
        headers={"Authorization": f"Bearer {token_alpha}"},
        json={
            "title": "Alpha Announcement",
            "body": "Alpha body",
            "visibility_scope": "tenant_public",
            "status": "published",
            "published_at": "2026-06-01T00:00:00Z",
        },
    )

    beta_list = await client.get(
        "/api/v1/announcements/",
        headers={"Authorization": f"Bearer {token_beta}"},
    )
    assert beta_list.status_code == 200
    assert len(beta_list.json()) == 0


@pytest.mark.asyncio
async def test_active_announcements_filter(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    ctx = await create_tenant_with_user(db_session, f"ann-act-{_uuid.uuid4().hex[:6]}")
    token = await login(client, ctx["user"].email, ctx["password"], tenant_slug=ctx["tenant"].slug)

    await client.post(
        "/api/v1/announcements/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Current Notice",
            "body": "This is active",
            "visibility_scope": "tenant_public",
            "status": "published",
            "published_at": "2026-01-01T00:00:00Z",
        },
    )

    await client.post(
        "/api/v1/announcements/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Expired Notice",
            "body": "This is expired",
            "visibility_scope": "tenant_public",
            "status": "published",
            "published_at": "2025-01-01T00:00:00Z",
            "expires_at": "2025-06-01T00:00:00Z",
        },
    )

    active_list = await client.get(
        "/api/v1/announcements/active",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert active_list.status_code == 200
    titles = [a["title"] for a in active_list.json()]
    assert "Current Notice" in titles
    assert "Expired Notice" not in titles
