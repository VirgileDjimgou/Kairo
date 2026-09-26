from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from helpers import create_tenant_with_user, create_user_for_tenant, login
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.contributions.models import (
    CashHandoverStatus,
    ContributionReceiptDeclaration,
    ContributionReceiptStatus,
    ContributionRecord,
)
from app.modules.notifications.user_models import UserNotification
from app.modules.tenancy.models import Tenant


async def _add_receipt(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    *,
    status: str = ContributionReceiptStatus.submitted.value,
    handover_status: str | None = None,
    handover_due_at: datetime | None = None,
) -> ContributionReceiptDeclaration:
    receipt = ContributionReceiptDeclaration(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        membership_profile_id=None,
        income_type="donation",
        source_name="Test Source",
        declarant_user_id=user_id,
        declarant_role_code="treasurer",
        amount=Decimal("25.00"),
        currency="EUR",
        received_at=datetime.now(UTC),
        status=status,
        cash_handover_status=handover_status,
        handover_due_at=handover_due_at,
    )
    db.add(receipt)
    await db.flush()
    return receipt


async def _add_outstanding_contribution(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    profile_id: uuid.UUID,
) -> ContributionRecord:
    record = ContributionRecord(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        membership_profile_id=profile_id,
        year=2026,
        expected_amount=Decimal("100.00"),
        paid_amount=Decimal("0.00"),
        balance=Decimal("100.00"),
        currency="EUR",
        status="pending",
    )
    db.add(record)
    await db.flush()
    return record


async def _add_unread_notification(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID) -> None:
    notification = UserNotification(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        recipient_user_id=user_id,
        event_type="announcements.published",
        category="announcements",
        priority="normal",
        target_path="/announcements",
        deduplication_key=f"attention-{uuid.uuid4().hex}",
    )
    db.add(notification)
    await db.flush()


@pytest.mark.asyncio
async def test_treasurer_attention_is_finance_scoped_and_prioritized(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    context = await create_tenant_with_user(db_session, f"att-treas-{uuid.uuid4().hex[:6]}", role_code="treasurer")
    token = await login(client, context["user"].email, context["password"], context["tenant"].slug)

    await _add_receipt(
        db_session,
        context["tenant"].id,
        context["user"].id,
        status=ContributionReceiptStatus.validated.value,
        handover_status=CashHandoverStatus.pending_handover.value,
        handover_due_at=datetime.now(UTC) - timedelta(days=1),
    )
    await _add_receipt(db_session, context["tenant"].id, context["user"].id)
    member = await create_user_for_tenant(
        db_session,
        tenant_id=context["tenant"].id,
        email="attention-member@example.org",
        password="MemberPass1!",
        display_name="Attention Member",
        role_code="member",
        member_code="ATT-001",
    )
    await _add_outstanding_contribution(db_session, context["tenant"].id, member["profile"].id)
    await db_session.commit()

    response = await client.get("/api/v1/attention", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    items = response.json()["items"]
    by_id = {item["id"]: item for item in items}

    assert by_id["attention.overdueHandovers"]["count"] == 1
    assert by_id["attention.overdueHandovers"]["priority"] == "urgent"
    assert by_id["attention.pendingReceipts"]["count"] == 1
    assert by_id["attention.outstandingBalances"]["count"] == 1
    assert items[0]["id"] == "attention.overdueHandovers"

    # Finance roles never receive discipline or account-scoped cards.
    assert "attention.openDiscipline" not in by_id
    assert "attention.myBalance" not in by_id
    for item in items:
        assert item["target_path"].startswith("/")


@pytest.mark.asyncio
async def test_member_attention_is_personal_and_leaks_no_tenant_finance(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    context = await create_tenant_with_user(db_session, f"att-member-{uuid.uuid4().hex[:6]}", role_code="member")
    member = await create_user_for_tenant(
        db_session,
        tenant_id=context["tenant"].id,
        email="attention-member2@example.org",
        password="MemberPass1!",
        display_name="Personal Member",
        role_code="member",
        member_code="ATT-002",
    )
    token = await login(client, member["user"].email, member["password"], context["tenant"].slug)

    await _add_outstanding_contribution(db_session, context["tenant"].id, member["profile"].id)
    await _add_unread_notification(db_session, context["tenant"].id, member["user"].id)
    await _add_receipt(db_session, context["tenant"].id, context["user"].id)
    await db_session.commit()

    response = await client.get("/api/v1/attention", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    items = response.json()["items"]
    by_id = {item["id"]: item for item in items}

    assert by_id["attention.myBalance"]["count"] == 1
    assert by_id["attention.unreadNotifications"]["count"] == 1
    assert "attention.pendingReceipts" not in by_id
    assert "attention.outstandingBalances" not in by_id
    assert "attention.overdueHandovers" not in by_id


@pytest.mark.asyncio
async def test_attention_counts_are_tenant_scoped(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    first = await create_tenant_with_user(db_session, f"att-a-{uuid.uuid4().hex[:6]}", role_code="treasurer")
    second = await create_tenant_with_user(db_session, f"att-b-{uuid.uuid4().hex[:6]}", role_code="treasurer")

    await _add_receipt(db_session, first["tenant"].id, first["user"].id)
    await db_session.commit()

    token_b = await login(client, second["user"].email, second["password"], second["tenant"].slug)
    response = await client.get("/api/v1/attention", headers={"Authorization": f"Bearer {token_b}"})
    assert response.status_code == 200, response.text
    assert response.json()["items"] == []


@pytest.mark.asyncio
async def test_disabled_module_suppresses_its_attention_cards(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    context = await create_tenant_with_user(db_session, f"att-off-{uuid.uuid4().hex[:6]}", role_code="treasurer")
    await _add_receipt(db_session, context["tenant"].id, context["user"].id)
    tenant = await db_session.get(Tenant, context["tenant"].id)
    tenant.settings_json = json.dumps({"modules": {"contributions": False}})
    await db_session.commit()

    token = await login(client, context["user"].email, context["password"], context["tenant"].slug)
    response = await client.get("/api/v1/attention", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    assert response.json()["items"] == []


@pytest.mark.asyncio
async def test_attention_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/v1/attention")
    assert response.status_code == 401
