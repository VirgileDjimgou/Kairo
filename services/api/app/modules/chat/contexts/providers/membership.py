from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat.contexts.contracts import ContextOutcome, ContextRequest
from app.modules.chat.contexts.messages import message
from app.modules.chat.contexts.patterns import question_mentions_personal_finance
from app.modules.chat.payloads import StructuredContext
from app.modules.membership.service import MembershipService


class MembershipContextProvider:
    key = "membership"

    def __init__(self, db: AsyncSession) -> None:
        self._membership_service = MembershipService(db)

    async def collect(self, request: ContextRequest) -> ContextOutcome:
        if not question_mentions_personal_finance(request.normalized_question):
            return ContextOutcome()
        if not request.domain_policy.member_finance:
            return ContextOutcome(
                refusal=message("personal_finance_forbidden", request.response_language)
            )
        balance = await self._membership_service.get_my_balance(request.tenant_id, request.user_id)
        return ContextOutcome(
            context=StructuredContext(
                source_type="structured:member_balance",
                title="Personal contribution balance",
                content=(
                    f"Member: {balance.profile.display_name} "
                    f"(code {balance.profile.member_code})\n"
                    f"Total expected: {balance.total_expected} EUR\n"
                    f"Total paid: {balance.total_paid} EUR\n"
                    f"Outstanding balance: {balance.total_balance} EUR\n"
                    f"Contribution records: {balance.contribution_count}"
                ),
            )
        )
