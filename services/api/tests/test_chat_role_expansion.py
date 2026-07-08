"""Sprint 57 tests: role-aware chat expansion for office roles."""

from __future__ import annotations

import json
import uuid as _uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.announcements.models import Announcement
from app.modules.disciplinary.models import DisciplinaryRecord
from app.modules.documents.models import Document, DocumentChunk, DocumentStatus, DocumentVersion
from app.modules.events.models import Event, EventStatus, EventVisibility
from app.modules.membership.models import MembershipProfile
from app.modules.policies.models import PolicyRecord, PolicyStatus
from helpers import create_tenant_with_user, create_user_for_tenant, login


def _seed_document(
    db: AsyncSession,
    *,
    tenant_id,
    owner_user_id,
    title: str,
    text: str,
) -> None:
    document_id = _uuid.uuid4()
    version_id = _uuid.uuid4()
    chunk_id = _uuid.uuid4()

    document = Document(
        id=document_id,
        tenant_id=tenant_id,
        title=title,
        source_type="upload",
        language="en",
        access_scope="tenant_public",
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


def _seed_membership_profile(
    db: AsyncSession,
    *,
    tenant_id,
    user_id,
    member_code: str,
    display_name: str,
) -> None:
    db.add(
        MembershipProfile(
            id=_uuid.uuid4(),
            tenant_id=tenant_id,
            user_id=user_id,
            member_code=member_code,
            first_name=display_name.split()[0],
            last_name=display_name.split()[-1],
            display_name=display_name,
            email=f"{member_code.lower()}@test.org",
            status="active",
        )
    )


def _seed_policy(
    db: AsyncSession,
    *,
    tenant_id,
    title: str,
    category: str,
    status: str = PolicyStatus.published.value,
) -> None:
    db.add(
        PolicyRecord(
            id=_uuid.uuid4(),
            tenant_id=tenant_id,
            title=title,
            category=category,
            description=f"{title} description",
            status=status,
            metadata_json="{}",
        )
    )


def _seed_announcement(
    db: AsyncSession,
    *,
    tenant_id,
    title: str,
    published_at: datetime | None = None,
    visibility_scope: str = "members_only",
) -> None:
    db.add(
        Announcement(
            id=_uuid.uuid4(),
            tenant_id=tenant_id,
            title=title,
            body=f"{title} body",
            visibility_scope=visibility_scope,
            published_at=published_at or datetime.now(timezone.utc),
            metadata_json="{}",
        )
    )


def _seed_event(
    db: AsyncSession,
    *,
    tenant_id,
    title: str,
    start_at: datetime,
    location: str | None = None,
    sport_type: str = "training",
) -> None:
    db.add(
        Event(
            id=_uuid.uuid4(),
            tenant_id=tenant_id,
            title=title,
            description=f"{title} description",
            start_at=start_at,
            end_at=start_at,
            location=location,
            visibility_scope=EventVisibility.members_only.value,
            status=EventStatus.published.value,
            metadata_json=json.dumps({"workspace": "sports", "sport_type": sport_type}),
        )
    )


def _seed_disciplinary_record(
    db: AsyncSession,
    *,
    tenant_id,
    membership_profile_id,
    title: str,
    status: str,
) -> None:
    db.add(
        DisciplinaryRecord(
            id=_uuid.uuid4(),
            tenant_id=tenant_id,
            membership_profile_id=membership_profile_id,
            policy_record_id=None,
            title=title,
            description=f"{title} description",
            amount=Decimal("10.00"),
            currency="EUR",
            status=status,
            metadata_json="{}",
        )
    )


@pytest.mark.asyncio
async def test_governance_summary_is_available_to_president(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_llm,
) -> None:
    data = await create_tenant_with_user(
        db_session,
        f"gov-{_uuid.uuid4().hex[:6]}",
        role_code="president",
        profile_type="staff",
    )
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    _seed_membership_profile(
        db_session,
        tenant_id=data["tenant"].id,
        user_id=data["user"].id,
        member_code="PRS-001",
        display_name="President User",
    )
    secondary = await create_user_for_tenant(
        db_session,
        tenant_id=data["tenant"].id,
        email="member-overview@test.org",
        password="Member123!",
        display_name="Member Overview",
        role_code="member",
        profile_type="member",
        member_code="MEM-101",
    )
    _seed_document(
        db_session,
        tenant_id=data["tenant"].id,
        owner_user_id=data["user"].id,
        title="Governance Charter",
        text="The charter defines the executive framework.",
    )
    _seed_policy(
        db_session,
        tenant_id=data["tenant"].id,
        title="Attendance Policy",
        category="governance",
    )
    _seed_announcement(
        db_session,
        tenant_id=data["tenant"].id,
        title="General Assembly Notice",
    )
    _seed_event(
        db_session,
        tenant_id=data["tenant"].id,
        title="Annual Assembly",
        start_at=datetime(2030, 8, 1, 12, 0, tzinfo=timezone.utc),
        location="Main Hall",
    )
    await db_session.flush()

    response = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "Give me a governance summary."},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["refused"] is False
    assert "structured:governance_summary" in body["source_types"]
    assert len(fake_llm.calls) == 1
    user_prompt = fake_llm.calls[0]["user_prompt"]
    assert "Tenant governance summary" in user_prompt
    assert "Members in tenant: 2" in user_prompt
    assert "Documents available: 1" in user_prompt
    assert "Published policies: 1" in user_prompt
    assert "Active announcements: 1" in user_prompt
    assert "Upcoming events: 1" in user_prompt


@pytest.mark.asyncio
async def test_secretary_publication_context_includes_policy_and_announcement_counts(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_llm,
) -> None:
    data = await create_tenant_with_user(
        db_session,
        f"sec-{_uuid.uuid4().hex[:6]}",
        role_code="secretary_general",
        profile_type="staff",
    )
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    _seed_policy(
        db_session,
        tenant_id=data["tenant"].id,
        title="Publication Policy",
        category="communications",
        status=PolicyStatus.draft.value,
    )
    _seed_policy(
        db_session,
        tenant_id=data["tenant"].id,
        title="Formal Notice Policy",
        category="communications",
    )
    _seed_announcement(
        db_session,
        tenant_id=data["tenant"].id,
        title="Member Notice",
    )
    await db_session.flush()

    response = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "Show the official publication context."},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["refused"] is False
    assert "structured:publication_context" in body["source_types"]
    assert len(fake_llm.calls) == 1
    user_prompt = fake_llm.calls[0]["user_prompt"]
    assert "Official publication context" in user_prompt
    assert "Policies in workspace: 2" in user_prompt
    assert "Published policies: 1" in user_prompt
    assert "Draft policies: 1" in user_prompt
    assert "Active announcements: 1" in user_prompt


@pytest.mark.asyncio
async def test_censor_can_request_disciplinary_summary_without_member_names(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_llm,
) -> None:
    data = await create_tenant_with_user(
        db_session,
        f"cen-{_uuid.uuid4().hex[:6]}",
        role_code="censor",
        profile_type="staff",
    )
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    profile = MembershipProfile(
        id=_uuid.uuid4(),
        tenant_id=data["tenant"].id,
        user_id=data["user"].id,
        member_code="CEN-001",
        first_name="Censor",
        last_name="User",
        display_name="Censor User",
        email="censor@example.org",
        status="active",
    )
    db_session.add(profile)
    _seed_disciplinary_record(
        db_session,
        tenant_id=data["tenant"].id,
        membership_profile_id=profile.id,
        title="Late submission",
        status="open",
    )
    _seed_disciplinary_record(
        db_session,
        tenant_id=data["tenant"].id,
        membership_profile_id=profile.id,
        title="Policy reminder",
        status="under_review",
    )
    await db_session.flush()

    response = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "Give me a disciplinary summary."},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["refused"] is False
    assert "structured:disciplinary_summary" in body["source_types"]
    assert len(fake_llm.calls) == 1
    user_prompt = fake_llm.calls[0]["user_prompt"]
    assert "Disciplinary summary" in user_prompt
    assert "Disciplinary cases: 2" in user_prompt
    assert "Open cases: 1" in user_prompt
    assert "Under review: 1" in user_prompt
    assert "Resolved: 0" in user_prompt
    assert "Waived: 0" in user_prompt
    assert "Member:" not in user_prompt


@pytest.mark.asyncio
async def test_sports_manager_can_request_sports_schedule(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_llm,
) -> None:
    data = await create_tenant_with_user(
        db_session,
        f"sport-{_uuid.uuid4().hex[:6]}",
        role_code="sports_manager",
        profile_type="staff",
    )
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    _seed_event(
        db_session,
        tenant_id=data["tenant"].id,
        title="Morning Training",
        start_at=datetime(2030, 8, 5, 18, 0, tzinfo=timezone.utc),
        location="Field A",
    )
    _seed_event(
        db_session,
        tenant_id=data["tenant"].id,
        title="Weekend Match",
        start_at=datetime(2030, 8, 12, 16, 0, tzinfo=timezone.utc),
        location="Arena",
    )
    await db_session.flush()

    response = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "Show the sports schedule."},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["refused"] is False
    assert "structured:sports_schedule" in body["source_types"]
    assert len(fake_llm.calls) == 1
    user_prompt = fake_llm.calls[0]["user_prompt"]
    assert "Sports schedule" in user_prompt
    assert "Sports events in tenant: 2" in user_prompt
    assert "Upcoming sports events: 2" in user_prompt
    assert "Morning Training" in user_prompt
    assert "Weekend Match" in user_prompt


@pytest.mark.asyncio
async def test_member_cannot_request_governance_summary_before_llm(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_llm,
) -> None:
    data = await create_tenant_with_user(
        db_session,
        f"mem-{_uuid.uuid4().hex[:6]}",
        role_code="member",
        profile_type="member",
    )
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    response = await client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "Give me a governance summary."},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["refused"] is True
    assert "résumé de gouvernance" in body["refusal_reason"].lower() or "gouvernance" in body["refusal_reason"].lower()
    assert len(fake_llm.calls) == 0
