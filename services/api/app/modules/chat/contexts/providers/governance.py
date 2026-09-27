from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.announcements.repository import AnnouncementRepository
from app.modules.chat.contexts.contracts import ContextOutcome, ContextRequest
from app.modules.chat.contexts.formatting import format_datetime, is_future_datetime
from app.modules.chat.contexts.messages import message
from app.modules.chat.contexts.patterns import (
    GOVERNANCE_SUMMARY_PATTERNS,
    question_mentions_any,
)
from app.modules.chat.payloads import StructuredContext
from app.modules.documents.repository import DocumentRepository
from app.modules.events.repository import EventRepository
from app.modules.membership.service import MembershipService
from app.modules.policies.service import PolicyService


class GovernanceContextProvider:
    key = "governance"

    def __init__(self, db: AsyncSession) -> None:
        self._documents = DocumentRepository(db)
        self._membership_service = MembershipService(db)
        self._policy_service = PolicyService(db)
        self._announcement_repo = AnnouncementRepository(db)
        self._event_repo = EventRepository(db)

    async def collect(self, request: ContextRequest) -> ContextOutcome:
        if not question_mentions_any(request.normalized_question, GOVERNANCE_SUMMARY_PATTERNS):
            return ContextOutcome()
        if not request.domain_policy.governance:
            return ContextOutcome(
                refusal=message("governance_forbidden", request.response_language)
            )

        tenant_id = request.tenant_id
        documents = await self._documents.list_documents(tenant_id)
        members = await self._membership_service.list_profiles(tenant_id)
        policies = await self._policy_service.list_public(tenant_id)
        announcements = await self._announcement_repo.list_visible_active_by_tenant(tenant_id)
        events = await self._event_repo.list_visible_by_tenant(tenant_id)
        upcoming_events = [event for event in events if is_future_datetime(event.start_at)]
        summary_lines = [
            f"Members in tenant: {len(members)}",
            f"Documents available: {len(documents)}",
            f"Published policies: {len(policies)}",
            f"Active announcements: {len(announcements)}",
            f"Upcoming events: {len(upcoming_events)}",
        ]
        if policies:
            summary_lines.append("Recent policies:")
            summary_lines.extend(
                f"- {policy.title} ({policy.status})" for policy in policies[:3]
            )
        if announcements:
            summary_lines.append("Recent announcements:")
            summary_lines.extend(
                f"- {announcement.title} ({format_datetime(announcement.published_at)})"
                for announcement in announcements[:3]
            )

        return ContextOutcome(
            context=StructuredContext(
                source_type="structured:governance_summary",
                title="Tenant governance summary",
                content="\n".join(summary_lines),
            )
        )
