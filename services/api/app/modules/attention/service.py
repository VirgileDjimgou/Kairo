from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.announcements.models import Announcement
from app.modules.attention.schemas import AttentionItem
from app.modules.contributions.models import (
    CashHandoverStatus,
    ContributionReceiptDeclaration,
    ContributionReceiptStatus,
    ContributionRecord,
)
from app.modules.disciplinary.models import DisciplinaryRecord
from app.modules.documents.models import IngestionJob
from app.modules.events.models import Event
from app.modules.membership.models import MembershipProfile
from app.modules.notifications.user_models import UserNotification
from app.modules.tenancy.module_toggles import is_module_enabled
from app.modules.tenancy.repository import TenancyRepository

OPEN_DISCIPLINE_STATUSES = ("open", "under_review")
OUTSTANDING_CONTRIBUTION_STATUSES = ("pending", "partial", "overdue")


class AttentionService:
    """Backend-authorized task/attention aggregation for the action center.

    Every count is computed from records the requesting role is already allowed
    to read through its own module surfaces; the service never widens access.
    Items belonging to disabled tenant modules are omitted.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def overview(
        self,
        tenant_id: UUID,
        user_id: UUID,
        roles: list[str],
    ) -> list[AttentionItem]:
        modules = await self._module_toggles(tenant_id)
        items: list[AttentionItem] = []

        def module_on(key: str) -> bool:
            return is_module_enabled(modules, key)

        def has(*role_codes: str) -> bool:
            return any(role in roles for role in role_codes)

        if has("treasurer", "principal_admin", "admin") and module_on("contributions"):
            overdue_handovers = await self._count(
                select(func.count(ContributionReceiptDeclaration.id)).where(
                    ContributionReceiptDeclaration.tenant_id == tenant_id,
                    ContributionReceiptDeclaration.cash_handover_status
                    == CashHandoverStatus.pending_handover.value,
                    ContributionReceiptDeclaration.handover_due_at.is_not(None),
                    ContributionReceiptDeclaration.handover_due_at < datetime.now(UTC),
                )
            )
            if overdue_handovers:
                items.append(
                    self._item(
                        "attention.overdueHandovers",
                        "urgent",
                        "finance",
                        "attention.overdueHandovers",
                        overdue_handovers,
                        "/finance",
                    )
                )
            pending_receipts = await self._count(
                select(func.count(ContributionReceiptDeclaration.id)).where(
                    ContributionReceiptDeclaration.tenant_id == tenant_id,
                    ContributionReceiptDeclaration.status == ContributionReceiptStatus.submitted.value,
                )
            )
            if pending_receipts:
                items.append(
                    self._item(
                        "attention.pendingReceipts",
                        "attention",
                        "finance",
                        "attention.pendingReceipts",
                        pending_receipts,
                        "/finance",
                    )
                )

        if has("treasurer", "auditor", "president", "vice_president", "principal_admin", "admin") and module_on(
            "contributions"
        ):
            balances = await self._count(
                select(func.count(ContributionRecord.id)).where(
                    ContributionRecord.tenant_id == tenant_id,
                    ContributionRecord.status.in_(OUTSTANDING_CONTRIBUTION_STATUSES),
                    ContributionRecord.balance > 0,
                )
            )
            if balances:
                target = "/finance-audit" if has("auditor", "president", "vice_president") else "/finance"
                items.append(
                    self._item(
                        "attention.outstandingBalances",
                        "attention",
                        "finance",
                        "attention.outstandingBalances",
                        balances,
                        target,
                    )
                )

        if has("secretary_general", "president", "principal_admin", "admin"):
            if module_on("documents"):
                failed_jobs = await self._count(
                    select(func.count(IngestionJob.id)).where(
                        IngestionJob.tenant_id == tenant_id,
                        IngestionJob.status == "failed",
                    )
                )
                if failed_jobs:
                    items.append(
                        self._item(
                            "attention.failedIngestion",
                            "urgent",
                            "knowledge",
                            "attention.failedIngestion",
                            failed_jobs,
                            "/secretary/documents" if has("secretary_general") else "/admin/documents",
                        )
                    )
            if module_on("announcements"):
                drafts = await self._count(
                    select(func.count(Announcement.id)).where(
                        Announcement.tenant_id == tenant_id,
                        Announcement.published_at.is_(None),
                    )
                )
                if drafts:
                    items.append(
                        self._item(
                            "attention.pendingAnnouncements",
                            "attention",
                            "governance",
                            "attention.pendingAnnouncements",
                            drafts,
                            "/secretary/announcements" if has("secretary_general") else "/admin/announcements",
                        )
                    )

        if has("president", "vice_president", "censor", "principal_admin", "admin") and module_on("disciplinary"):
            open_records = await self._count(
                select(func.count(DisciplinaryRecord.id)).where(
                    DisciplinaryRecord.tenant_id == tenant_id,
                    DisciplinaryRecord.status.in_(OPEN_DISCIPLINE_STATUSES),
                )
            )
            if open_records:
                items.append(
                    self._item(
                        "attention.openDiscipline",
                        "attention",
                        "governance",
                        "attention.openDiscipline",
                        open_records,
                        "/censor" if has("censor") else "/governance",
                    )
                )

        if has(
            "treasurer",
            "auditor",
            "president",
            "vice_president",
            "secretary_general",
            "censor",
            "sports_manager",
            "principal_admin",
            "admin",
        ) and module_on("events"):
            upcoming = await self._count(
                select(func.count(Event.id)).where(
                    Event.tenant_id == tenant_id,
                    Event.start_at >= datetime.now(UTC),
                )
            )
            if upcoming:
                items.append(
                    self._item(
                        "attention.upcomingEvents",
                        "normal",
                        "community",
                        "attention.upcomingEvents",
                        upcoming,
                        "/events",
                    )
                )

        if has("member") and module_on("membership"):
            profile_id = await self._member_profile_id(tenant_id, user_id)
            if profile_id is not None and module_on("contributions"):
                outstanding = await self._count(
                    select(func.count(ContributionRecord.id)).where(
                        ContributionRecord.tenant_id == tenant_id,
                        ContributionRecord.membership_profile_id == profile_id,
                        ContributionRecord.status.in_(OUTSTANDING_CONTRIBUTION_STATUSES),
                        ContributionRecord.balance > 0,
                    )
                )
                if outstanding:
                    items.append(
                        self._item(
                            "attention.myBalance",
                            "attention",
                            "account",
                            "attention.myBalance",
                            outstanding,
                            "/members/profile",
                        )
                    )

        if has("member"):
            unread = await self._count(
                select(func.count(UserNotification.id)).where(
                    UserNotification.tenant_id == tenant_id,
                    UserNotification.recipient_user_id == user_id,
                    UserNotification.read_at.is_(None),
                )
            )
            if unread:
                items.append(
                    self._item(
                        "attention.unreadNotifications",
                        "informational",
                        "account",
                        "attention.unreadNotifications",
                        unread,
                        "/notifications",
                    )
                )
            if module_on("events"):
                upcoming = await self._count(
                    select(func.count(Event.id)).where(
                        Event.tenant_id == tenant_id,
                        Event.start_at >= datetime.now(UTC),
                    )
                )
                if upcoming:
                    items.append(
                        self._item(
                            "attention.upcomingEvents",
                            "normal",
                            "community",
                            "attention.upcomingEvents",
                            upcoming,
                            "/events",
                        )
                    )
            if module_on("announcements"):
                active = await self._count(
                    select(func.count(Announcement.id)).where(
                        Announcement.tenant_id == tenant_id,
                        Announcement.published_at.is_not(None),
                        Announcement.published_at <= datetime.now(UTC),
                    )
                )
                if active:
                    items.append(
                        self._item(
                            "attention.activeAnnouncements",
                            "informational",
                            "community",
                            "attention.activeAnnouncements",
                            active,
                            "/announcements",
                        )
                    )

        priority_order = {"urgent": 0, "attention": 1, "normal": 2, "informational": 3}
        items.sort(key=lambda item: (priority_order[item.priority], item.id))
        return items

    def _item(
        self,
        item_id: str,
        priority: str,
        category: str,
        title_key: str,
        count: int,
        target_path: str,
    ) -> AttentionItem:
        return AttentionItem(
            id=item_id,
            priority=priority,
            category=category,
            title_key=title_key,
            count=count,
            target_path=target_path,
        )

    async def _count(self, statement) -> int:
        result = await self._db.execute(statement)
        return int(result.scalar_one())

    async def _member_profile_id(self, tenant_id: UUID, user_id: UUID) -> UUID | None:
        result = await self._db.execute(
            select(MembershipProfile.id).where(
                MembershipProfile.tenant_id == tenant_id,
                MembershipProfile.user_id == user_id,
            )
        )
        return result.scalars().first()

    async def _module_toggles(self, tenant_id: UUID) -> dict[str, object]:
        repo = TenancyRepository(self._db)
        tenant = await repo.get_tenant_by_id(tenant_id)
        if not tenant:
            return {}
        if isinstance(tenant.settings_json, str) and tenant.settings_json.strip():
            try:
                parsed = json.loads(tenant.settings_json)
            except json.JSONDecodeError:
                return {}
            if isinstance(parsed, dict):
                return parsed
        return {}
