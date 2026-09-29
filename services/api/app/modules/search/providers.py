from __future__ import annotations

from typing import Protocol
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.announcements.models import Announcement
from app.modules.audit.models import AuditEvent
from app.modules.contributions.models import (
    ContributionReceiptDeclaration,
    PaymentRecord,
)
from app.modules.disciplinary.models import DisciplinaryRecord
from app.modules.documents.models import Document
from app.modules.events.models import Event
from app.modules.membership.models import MembershipProfile
from app.modules.rag.policy import AccessPolicy
from app.modules.search.schemas import SearchResult

ELECTED_OFFICE_ROLES = {
    "president",
    "vice_president",
    "secretary_general",
    "treasurer",
    "auditor",
    "censor",
    "sports_manager",
}
ADMIN_ROLES = {"principal_admin", "admin"}


def match_score(query: str, *texts: str | None) -> int:
    """3 exact, 2 prefix, 1 substring. 0 means no match."""
    needle = query.casefold().strip()
    if not needle:
        return 0
    best = 0
    for text in texts:
        if not text:
            continue
        haystack = str(text).casefold()
        if haystack == needle:
            best = max(best, 3)
        elif haystack.startswith(needle):
            best = max(best, 2)
        elif needle in haystack:
            best = max(best, 1)
    return best


def like_pattern(query: str) -> str:
    escaped = (
        query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_").strip()
    )
    return f"%{escaped}%"


def any_role(roles: list[str], *candidates: str) -> bool:
    return any(role in roles for role in candidates)


class SearchProvider(Protocol):
    key: str
    module_key: str | None

    def allowed(self, roles: list[str]) -> bool: ...

    async def search(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        roles: list[str],
        query: str,
        limit: int,
    ) -> list[SearchResult]: ...


class MembersSearchProvider:
    key = "members"
    module_key: str | None = "membership"

    def allowed(self, roles: list[str]) -> bool:
        return any_role(roles, *ELECTED_OFFICE_ROLES, *ADMIN_ROLES)

    async def search(self, db, tenant_id, user_id, roles, query, limit):
        pattern = like_pattern(query)
        result = await db.execute(
            select(MembershipProfile)
            .where(
                MembershipProfile.tenant_id == tenant_id,
                or_(
                    MembershipProfile.display_name.ilike(pattern, escape="\\"),
                    MembershipProfile.member_code.ilike(pattern, escape="\\"),
                    MembershipProfile.email.ilike(pattern, escape="\\"),
                ),
            )
            .limit(limit * 2)
        )
        rows = []
        for profile in result.scalars().all():
            score = match_score(query, profile.display_name, profile.member_code, profile.email)
            if score:
                rows.append(
                    SearchResult(
                        id=str(profile.id),
                        type="members",
                        type_key="search.types.members",
                        title=profile.display_name,
                        subtitle=profile.member_code,
                        target_path="/members/manage",
                        score=score,
                    )
                )
        return rows


class DocumentsSearchProvider:
    key = "documents"
    module_key: str | None = "documents"

    def allowed(self, roles: list[str]) -> bool:
        return True

    async def search(self, db, tenant_id, user_id, roles, query, limit):
        pattern = like_pattern(query)
        result = await db.execute(
            select(Document)
            .where(
                Document.tenant_id == tenant_id,
                Document.title.ilike(pattern, escape="\\"),
            )
            .limit(limit * 3)
        )
        policy = AccessPolicy(tenant_id=tenant_id, user_id=user_id, roles=tuple(roles))
        rows = []
        for document in result.scalars().all():
            # Access filtering happens BEFORE any title is returned.
            if not policy.can_access(document):
                continue
            score = match_score(query, document.title)
            if score:
                rows.append(
                    SearchResult(
                        id=str(document.id),
                        type="documents",
                        type_key="search.types.documents",
                        title=document.title,
                        subtitle=None,
                        target_path="/documents",
                        score=score,
                    )
                )
        return rows


class EventsSearchProvider:
    key = "events"
    module_key: str | None = "events"

    def allowed(self, roles: list[str]) -> bool:
        return True

    async def search(self, db, tenant_id, user_id, roles, query, limit):
        pattern = like_pattern(query)
        statement = select(Event).where(
            Event.tenant_id == tenant_id,
            Event.title.ilike(pattern, escape="\\"),
        )
        if not any_role(roles, *ELECTED_OFFICE_ROLES, *ADMIN_ROLES):
            statement = statement.where(Event.visibility_scope != "admin_only")
        result = await db.execute(statement.limit(limit * 2))
        rows = []
        for event in result.scalars().all():
            score = match_score(query, event.title)
            if score:
                rows.append(
                    SearchResult(
                        id=str(event.id),
                        type="events",
                        type_key="search.types.events",
                        title=event.title,
                        subtitle=None,
                        target_path="/events",
                        score=score,
                    )
                )
        return rows


class AnnouncementsSearchProvider:
    key = "announcements"
    module_key: str | None = "announcements"

    def allowed(self, roles: list[str]) -> bool:
        return True

    async def search(self, db, tenant_id, user_id, roles, query, limit):
        pattern = like_pattern(query)
        statement = select(Announcement).where(
            Announcement.tenant_id == tenant_id,
            Announcement.title.ilike(pattern, escape="\\"),
        )
        if not any_role(roles, *ELECTED_OFFICE_ROLES, *ADMIN_ROLES):
            statement = statement.where(Announcement.visibility_scope != "admin_only")
        result = await db.execute(statement.limit(limit * 2))
        rows = []
        for announcement in result.scalars().all():
            score = match_score(query, announcement.title)
            if score:
                rows.append(
                    SearchResult(
                        id=str(announcement.id),
                        type="announcements",
                        type_key="search.types.announcements",
                        title=announcement.title,
                        subtitle=None,
                        target_path="/announcements",
                        score=score,
                    )
                )
        return rows


class PaymentsSearchProvider:
    key = "payments"
    module_key: str | None = "contributions"

    def allowed(self, roles: list[str]) -> bool:
        return any_role(roles, "treasurer", "auditor", "president", "vice_president", *ADMIN_ROLES)

    async def search(self, db, tenant_id, user_id, roles, query, limit):
        pattern = like_pattern(query)
        result = await db.execute(
            select(PaymentRecord)
            .where(
                PaymentRecord.tenant_id == tenant_id,
                PaymentRecord.reference.ilike(pattern, escape="\\"),
            )
            .limit(limit * 2)
        )
        target = "/finance-audit" if any_role(roles, "auditor", "president", "vice_president") else "/finance"
        rows = []
        for payment in result.scalars().all():
            score = match_score(query, payment.reference)
            if score:
                rows.append(
                    SearchResult(
                        id=str(payment.id),
                        type="payments",
                        type_key="search.types.payments",
                        title=payment.reference or f"Payment {payment.amount}",
                        subtitle=str(payment.amount),
                        target_path=target,
                        score=score,
                    )
                )
        return rows


class ReceiptsSearchProvider:
    key = "receipts"
    module_key: str | None = "contributions"

    def allowed(self, roles: list[str]) -> bool:
        return any_role(roles, *ELECTED_OFFICE_ROLES, *ADMIN_ROLES)

    async def search(self, db, tenant_id, user_id, roles, query, limit):
        pattern = like_pattern(query)
        result = await db.execute(
            select(ContributionReceiptDeclaration)
            .where(
                ContributionReceiptDeclaration.tenant_id == tenant_id,
                or_(
                    ContributionReceiptDeclaration.source_name.ilike(pattern, escape="\\"),
                    ContributionReceiptDeclaration.note.ilike(pattern, escape="\\"),
                ),
            )
            .limit(limit * 2)
        )
        target = "/finance" if any_role(roles, "treasurer") else "/receipts"
        rows = []
        for receipt in result.scalars().all():
            score = match_score(query, receipt.source_name, receipt.note)
            if score:
                rows.append(
                    SearchResult(
                        id=str(receipt.id),
                        type="receipts",
                        type_key="search.types.receipts",
                        title=receipt.source_name or f"Receipt {receipt.amount}",
                        subtitle=str(receipt.amount),
                        target_path=target,
                        score=score,
                    )
                )
        return rows


class AuditSearchProvider:
    key = "audit"
    module_key: str | None = None

    def allowed(self, roles: list[str]) -> bool:
        # Mirrors the operation-journal access rule: elected office roles only.
        return any_role(roles, *ELECTED_OFFICE_ROLES)

    async def search(self, db, tenant_id, user_id, roles, query, limit):
        pattern = like_pattern(query)
        result = await db.execute(
            select(AuditEvent)
            .where(
                AuditEvent.tenant_id == tenant_id,
                or_(
                    AuditEvent.action.ilike(pattern, escape="\\"),
                    AuditEvent.entity_type.ilike(pattern, escape="\\"),
                ),
            )
            .limit(limit * 2)
        )
        rows = []
        for event in result.scalars().all():
            score = match_score(query, event.action, event.entity_type)
            if score:
                rows.append(
                    SearchResult(
                        id=str(event.id),
                        type="audit",
                        type_key="search.types.audit",
                        title=f"{event.action} Â· {event.entity_type}",
                        subtitle=None,
                        target_path="/operation-journal",
                        score=score,
                    )
                )
        return rows


class DisciplineSearchProvider:
    key = "discipline"
    module_key: str | None = "disciplinary"

    def allowed(self, roles: list[str]) -> bool:
        return any_role(roles, "censor", "president", "secretary_general", *ADMIN_ROLES)

    async def search(self, db, tenant_id, user_id, roles, query, limit):
        pattern = like_pattern(query)
        result = await db.execute(
            select(DisciplinaryRecord)
            .where(
                DisciplinaryRecord.tenant_id == tenant_id,
                DisciplinaryRecord.title.ilike(pattern, escape="\\"),
            )
            .limit(limit * 2)
        )
        target = "/censor" if any_role(roles, "censor") else "/disciplinary"
        rows = []
        for record in result.scalars().all():
            score = match_score(query, record.title)
            if score:
                rows.append(
                    SearchResult(
                        id=str(record.id),
                        type="discipline",
                        type_key="search.types.discipline",
                        title=record.title,
                        subtitle=None,
                        target_path=target,
                        score=score,
                    )
                )
        return rows


def default_providers() -> list[SearchProvider]:
    """Compose providers from module registry metadata (order preserved)."""
    from app.modules.module_registry.descriptor import default_registry

    return list(default_registry().search_providers())
