from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat.contexts.contracts import ContextOutcome, ContextRequest
from app.modules.chat.contexts.messages import message
from app.modules.chat.contexts.patterns import question_mentions_tenant_finance
from app.modules.chat.payloads import StructuredContext
from app.modules.contributions.service import ContributionService


class FinanceContextProvider:
    key = "finance"

    def __init__(self, db: AsyncSession) -> None:
        self._contribution_service = ContributionService(db)

    async def collect(self, request: ContextRequest) -> ContextOutcome:
        if not question_mentions_tenant_finance(request.normalized_question):
            return ContextOutcome()
        if not request.domain_policy.tenant_finance:
            return ContextOutcome(
                refusal=message("tenant_finance_forbidden", request.response_language)
            )
        summary = await self._contribution_service.get_summary(request.tenant_id)
        return ContextOutcome(
            context=StructuredContext(
                source_type="structured:finance_summary",
                title="Tenant contribution summary",
                content=(
                    f"Contribution records: {summary['total_count']}\n"
                    f"Total expected: {summary['total_expected']} EUR\n"
                    f"Total paid: {summary['total_paid']} EUR\n"
                    f"Outstanding balance: {summary['total_balance']} EUR"
                ),
            )
        )
