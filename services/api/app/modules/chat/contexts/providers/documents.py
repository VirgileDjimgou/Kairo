from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.announcements.repository import AnnouncementRepository
from app.modules.chat.contexts.contracts import ContextOutcome, ContextRequest
from app.modules.chat.contexts.formatting import format_datetime
from app.modules.chat.contexts.messages import message
from app.modules.chat.contexts.patterns import (
    PUBLICATION_CONTEXT_PATTERNS,
    question_mentions_any,
)
from app.modules.chat.payloads import StructuredContext
from app.modules.policies.service import PolicyService


class DocumentsContextProvider:
    key = "documents"

    def __init__(self, db: AsyncSession) -> None:
        self._policy_service = PolicyService(db)
        self._announcement_repo = AnnouncementRepository(db)

    async def collect(self, request: ContextRequest) -> ContextOutcome:
        if not question_mentions_any(request.normalized_question, PUBLICATION_CONTEXT_PATTERNS):
            return ContextOutcome()
        if not request.domain_policy.publication:
            return ContextOutcome(
                refusal=message("publication_forbidden", request.response_language)
            )

        tenant_id = request.tenant_id
        policies = await self._policy_service.list_all(tenant_id)
        announcements = await self._announcement_repo.list_visible_active_by_tenant(tenant_id)
        policy_counts = {"published": 0, "draft": 0, "archived": 0}
        for policy in policies:
            policy_counts[policy.status] = policy_counts.get(policy.status, 0) + 1

        summary_lines = [
            f"Policies in workspace: {len(policies)}",
            f"Published policies: {policy_counts['published']}",
            f"Draft policies: {policy_counts['draft']}",
            f"Archived policies: {policy_counts['archived']}",
            f"Active announcements: {len(announcements)}",
        ]
        if announcements:
            summary_lines.append("Recent active announcements:")
            summary_lines.extend(
                f"- {announcement.title} ({format_datetime(announcement.published_at)})"
                for announcement in announcements[:3]
            )
        if policies:
            summary_lines.append("Recent policies:")
            summary_lines.extend(
                f"- {policy.title} ({policy.status})" for policy in policies[:3]
            )

        return ContextOutcome(
            context=StructuredContext(
                source_type="structured:publication_context",
                title="Official publication context",
                content="\n".join(summary_lines),
            )
        )
