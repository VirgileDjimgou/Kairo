from datetime import UTC, datetime
from uuid import UUID

from app.modules.contributions.schemas import ExpenseRecordCreate, ExpenseRecordResponse
from app.modules.finance.base import FinanceServiceBase


class ExpensesMixin(FinanceServiceBase):
    async def create_expense(
        self,
        tenant_id: UUID,
        data: ExpenseRecordCreate,
        *,
        actor_user_id: UUID,
    ) -> ExpenseRecordResponse:
        payload = data.model_dump()
        payload["spent_at"] = payload["spent_at"] or datetime.now(UTC)
        payload["created_by"] = actor_user_id
        record = await self._repo.create_expense(tenant_id, payload)
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="expense_recorded",
            entity_type="expense_record",
            entity_id=record.id,
            module_key="contributions",
            details={
                "category": record.category,
                "amount": str(record.amount),
                "currency": record.currency,
                "payee": record.payee,
                "description": record.description,
            },
        )
        await self._db.commit()
        return ExpenseRecordResponse.model_validate(record)
