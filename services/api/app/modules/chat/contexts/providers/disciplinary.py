from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat.contexts.contracts import ContextOutcome, ContextRequest
from app.modules.chat.contexts.messages import message
from app.modules.chat.contexts.patterns import (
    DISCIPLINARY_SUMMARY_PATTERNS,
    question_mentions_any,
)
from app.modules.chat.payloads import StructuredContext
from app.modules.disciplinary.repository import DisciplinaryRepository


class DisciplinaryContextProvider:
    key = "disciplinary"

    def __init__(self, db: AsyncSession) -> None:
        self._disciplinary_repo = DisciplinaryRepository(db)

    async def collect(self, request: ContextRequest) -> ContextOutcome:
        if not question_mentions_any(request.normalized_question, DISCIPLINARY_SUMMARY_PATTERNS):
            return ContextOutcome()
        if not request.domain_policy.disciplinary:
            return ContextOutcome(
                refusal=message("disciplinary_forbidden", request.response_language)
            )

        records = await self._disciplinary_repo.list_by_tenant(request.tenant_id)
        status_counts = {"open": 0, "under_review": 0, "resolved": 0, "waived": 0}
        for record in records:
            status_counts[record.status] = status_counts.get(record.status, 0) + 1

        summary_lines = [
            f"Disciplinary cases: {len(records)}",
            f"Open cases: {status_counts['open']}",
            f"Under review: {status_counts['under_review']}",
            f"Resolved: {status_counts['resolved']}",
            f"Waived: {status_counts['waived']}",
        ]

        return ContextOutcome(
            context=StructuredContext(
                source_type="structured:disciplinary_summary",
                title="Disciplinary summary",
                content="\n".join(summary_lines),
            )
        )
