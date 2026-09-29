"""Operational health, metrics privacy and query-count regression coverage."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from fakes import FakeEmailNotificationProvider
from helpers import create_tenant_with_user, create_user_for_tenant
from httpx import AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.modules.contributions.models import (
    ContributionRecord,
    ContributionStatus,
)
from app.modules.contributions.schemas import ContributionReminderBatchRequest
from app.modules.identity.models import User
from app.modules.identity.service import AuthService
from app.modules.membership.models import MembershipProfile
from app.modules.membership.service import MembershipService
from app.modules.notifications.user_models import UserNotification
from app.modules.notifications.user_service import UserNotificationService
from app.modules.tenancy.models import TenantUser


class StatementRecorder:
    def __init__(self, db_session: AsyncSession) -> None:
        self._target = self._resolve_target(db_session)
        self.statements: list[str] = []
        event.listen(self._target, "before_cursor_execute", self._record)

    @staticmethod
    def _resolve_target(db_session: AsyncSession):
        bind = db_session.bind
        return (
            getattr(bind, "sync_connection", None)
            or getattr(bind, "sync_engine", None)
            or bind
        )

    def _record(self, *args, **kwargs) -> None:
        statement = str(args[2]).lstrip()
        if statement.upper().startswith(("SAVEPOINT", "RELEASE SAVEPOINT", "ROLLBACK TO")):
            return
        self.statements.append(statement)

    def reset(self) -> None:
        self.statements.clear()

    def close(self, db_session: AsyncSession) -> None:
        event.remove(self._target, "before_cursor_execute", self._record)


@pytest.mark.asyncio
async def test_liveness_probe_is_always_ok(client: AsyncClient) -> None:
    response = await client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_readiness_probe_reports_critical_dependencies(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def redis_ok() -> dict:
        return {"status": "ok", "latency_ms": 1}

    monkeypatch.setattr("app.core.health_checks._check_redis", redis_ok)
    ready = await client.get("/health/ready")
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"
    assert set(ready.json()["checks"]) == {"database", "redis"}

    async def redis_down() -> dict:
        return {"status": "unavailable", "latency_ms": 1}

    monkeypatch.setattr("app.core.health_checks._check_redis", redis_down)
    not_ready = await client.get("/health/ready")
    assert not_ready.status_code == 503
    assert not_ready.json()["status"] == "not_ready"


@pytest.mark.asyncio
async def test_health_surfaces_outbox_and_backup_checks(client: AsyncClient) -> None:
    response = await client.get("/health")
    body = response.json()
    for name in ("notification_outbox", "domain_event_outbox", "backup"):
        check = body["checks"].get(name)
        assert check is not None, f"{name} missing from health checks"
        assert check["status"] in ("ok", "degraded", "unavailable", "disabled", "error")
        assert "latency_ms" in check
    outbox_check = body["checks"]["notification_outbox"]
    assert set(outbox_check["detail"]) == {"pending", "failed", "oldest_pending_seconds"}


@pytest.mark.asyncio
async def test_metrics_include_operational_gauges(client: AsyncClient) -> None:
    response = await client.get("/metrics")
    text = response.text
    for name in (
        "kairo_notification_outbox_pending",
        "kairo_domain_event_outbox_pending",
        "kairo_domain_event_outbox_failed",
        "kairo_domain_event_outbox_oldest_age_seconds",
        "kairo_backup_last_success_age_seconds",
        "kairo_backup_failed_runs",
    ):
        assert name in text, f"missing metric {name}"


@pytest.mark.asyncio
async def test_metrics_never_expose_tenant_or_member_data(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    context = await create_tenant_with_user(db_session, f"privacy-{uuid.uuid4().hex[:6]}")
    context["tenant"].name = "UltraSecretOrg"
    db_session.add(
        UserNotification(
            tenant_id=context["tenant"].id,
            recipient_user_id=context["user"].id,
            event_type="finance.payment_recorded",
            category="finance",
            priority="normal",
            target_path="/finance",
            metadata_json='{"secret_note": "member-private-data"}',
            deduplication_key="privacy-probe",
            created_at=datetime.now(UTC),
        )
    )
    await db_session.commit()

    response = await client.get("/metrics")
    text = response.text
    for forbidden in (
        "UltraSecretOrg",
        context["user"].email,
        "Secret Person",
        "member-private-data",
        "privacy-probe",
        "p256dh",
    ):
        assert forbidden not in text, f"metrics leaked {forbidden}"


@pytest.mark.asyncio
async def test_managed_users_directory_is_batched(db_session: AsyncSession) -> None:
    context = await create_tenant_with_user(db_session, f"nplus1-managed-{uuid.uuid4().hex[:6]}")
    for index in range(40):
        await create_user_for_tenant(
            db_session,
            tenant_id=context["tenant"].id,
            email=f"member-{index}-{uuid.uuid4().hex[:4]}@test.org",
            password="MemberPass123!",
            display_name=f"Member {index}",
            role_code="member",
            profile_type="member",
        )
    await db_session.commit()

    recorder = StatementRecorder(db_session)
    try:
        users = await AuthService(db_session).list_managed_users(
            tenant_id=context["tenant"].id, requesting_user_id=context["user"].id
        )
    finally:
        recorder.close(db_session)

    assert len(users) == 41
    assert all(isinstance(entry.roles, list) for entry in users)
    assert len(recorder.statements) <= 12, recorder.statements


@pytest.mark.asyncio
async def test_unreachable_recipients_is_batched(db_session: AsyncSession) -> None:
    context = await create_tenant_with_user(db_session, f"nplus1-unreachable-{uuid.uuid4().hex[:6]}")
    now = datetime.now(UTC)
    for index in range(40):
        user = User(
            id=uuid.uuid4(),
            email=f"unreachable-{index}-{uuid.uuid4().hex[:4]}@test.org",
            password_hash=hash_password("MemberPass123!"),
            display_name=f"Unreachable {index}",
            status="active",
        )
        db_session.add(user)
        db_session.add(
            TenantUser(
                id=uuid.uuid4(),
                tenant_id=context["tenant"].id,
                user_id=user.id,
                profile_type="member",
                membership_status="active",
            )
        )
        db_session.add(
            UserNotification(
                tenant_id=context["tenant"].id,
                recipient_user_id=user.id,
                event_type="finance.payment_recorded",
                category="finance",
                priority="normal",
                target_path="/finance",
                metadata_json="{}",
                deduplication_key=f"unreachable-{index}",
                created_at=now,
            )
        )
    await db_session.commit()

    recorder = StatementRecorder(db_session)
    try:
        recipients = await UserNotificationService(db_session).unreachable_recipients(
            context["tenant"].id
        )
    finally:
        recorder.close(db_session)

    assert len(recipients) == 40
    assert len(recorder.statements) <= 6, recorder.statements


@pytest.mark.asyncio
async def test_batch_reminders_loads_profiles_once(db_session: AsyncSession) -> None:
    context = await create_tenant_with_user(db_session, f"nplus1-reminders-{uuid.uuid4().hex[:6]}")
    profiles: list[MembershipProfile] = []
    for index in range(10):
        profile = MembershipProfile(
            id=uuid.uuid4(),
            tenant_id=context["tenant"].id,
            member_code=f"REM-{index:03d}",
            first_name=f"Reminder{index}",
            last_name="Perf",
            display_name=f"Reminder {index}",
            email=f"reminder-{index}@test.org",
            membership_type="individual",
            status="active",
        )
        profiles.append(profile)
        db_session.add(profile)
    await db_session.flush()
    for profile in profiles:
        db_session.add(
            ContributionRecord(
                id=uuid.uuid4(),
                tenant_id=context["tenant"].id,
                membership_profile_id=profile.id,
                year=2026,
                expected_amount=60,
                paid_amount=0,
                balance=60,
                currency="EUR",
                status=ContributionStatus.pending.value,
            )
        )
    await db_session.commit()

    recorder = StatementRecorder(db_session)
    try:
        from app.modules.finance.service import ContributionService

        result = await (
            ContributionService(db_session)
            .with_notification_providers([FakeEmailNotificationProvider()])
            .send_batch_reminders(
                context["tenant"].id,
                ContributionReminderBatchRequest(year=2026, due_scope="all_outstanding", limit=10),
                actor_user_id=context["user"].id,
            )
        )
    finally:
        recorder.close(db_session)

    assert result.reminder_count == 10
    profile_queries = [
        statement
        for statement in recorder.statements
        if "FROM membership_profiles" in statement
    ]
    assert len(profile_queries) == 1, recorder.statements


@pytest.mark.asyncio
async def test_member_statement_does_not_duplicate_queries(db_session: AsyncSession) -> None:
    context = await create_tenant_with_user(db_session, f"nplus1-statement-{uuid.uuid4().hex[:6]}")
    await db_session.commit()
    user_id = context["user"].id
    tenant_id = context["tenant"].id
    profile = MembershipProfile(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        user_id=user_id,
        member_code="STMT-001",
        first_name="Statement",
        last_name="Member",
        display_name="Statement Member",
        email=context["user"].email,
        membership_type="individual",
        status="active",
    )
    db_session.add(profile)
    await db_session.flush()
    for year in (2025, 2026):
        db_session.add(
            ContributionRecord(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                membership_profile_id=profile.id,
                year=year,
                expected_amount=60,
                paid_amount=20,
                balance=40,
                currency="EUR",
                status=ContributionStatus.pending.value,
            )
        )
    await db_session.commit()

    recorder = StatementRecorder(db_session)
    try:
        statement = await MembershipService(db_session).get_my_statement(tenant_id, user_id)
    finally:
        recorder.close(db_session)

    assert statement.summary.contribution_count == 2
    assert len(recorder.statements) <= 2, recorder.statements
