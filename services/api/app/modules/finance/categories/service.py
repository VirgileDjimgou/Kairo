"""Tenant-defined expense categories."""

import uuid
from uuid import UUID

from fastapi import HTTPException, status

from app.modules.contributions.schemas import ExpenseCategoryResponse
from app.modules.finance.base import FinanceServiceBase

DEFAULT_EXPENSE_CATEGORIES = (
    ("sport_equipment", "Sport equipment"),
    ("fuel_transport", "Fuel and transport"),
    ("tournament", "Tournament"),
    ("cultural_event", "Cultural event"),
    ("administration", "Administration"),
    ("other", "Other"),
)


class CategoriesMixin(FinanceServiceBase):
    async def ensure_default_expense_categories(self, tenant_id: UUID):
        categories = await self._repo.list_expense_categories(tenant_id)
        if categories:
            return categories
        created = []
        for code, name in DEFAULT_EXPENSE_CATEGORIES:
            created.append(
                await self._repo.create_expense_category(
                    tenant_id, code=code, name=name, is_default=True
                )
            )
        await self._db.flush()
        return created

    async def list_expense_categories(
        self, tenant_id: UUID
    ) -> list[ExpenseCategoryResponse]:
        categories = await self.ensure_default_expense_categories(tenant_id)
        await self._db.commit()
        return [
            ExpenseCategoryResponse(
                id=category.id,
                code=category.code,
                name=category.name,
                is_default=category.is_default,
                is_active=category.is_active,
            )
            for category in categories
        ]

    async def expense_category_codes(
        self, tenant_id: UUID, *, commit: bool = False
    ) -> list[str]:
        categories = await self.ensure_default_expense_categories(tenant_id)
        if commit:
            await self._db.commit()
        return [category.code for category in categories if category.is_active]

    async def validate_expense_category(self, tenant_id: UUID, code: str) -> None:
        codes = await self.expense_category_codes(tenant_id)
        if code not in codes:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Unknown expense category '{code}'. "
                    f"Allowed values: {', '.join(codes)}"
                ),
            )

    async def create_expense_category(
        self, tenant_id: UUID, name: str, *, actor_user_id: UUID
    ) -> ExpenseCategoryResponse:
        await self.ensure_default_expense_categories(tenant_id)
        normalized_name = " ".join(name.split())
        if len(normalized_name) < 2:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Category name is too short",
            )
        code = f"custom_{uuid.uuid4().hex[:10]}"
        category = await self._repo.create_expense_category(
            tenant_id, code=code, name=normalized_name, is_default=False
        )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="expense_category_created",
            entity_type="finance_expense_category",
            entity_id=category.id,
            module_key="contributions",
            details={"code": code, "name": normalized_name},
        )
        await self._db.commit()
        return ExpenseCategoryResponse(
            id=category.id,
            code=category.code,
            name=category.name,
            is_default=category.is_default,
            is_active=category.is_active,
        )
