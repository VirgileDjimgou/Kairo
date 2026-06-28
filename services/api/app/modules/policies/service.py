from __future__ import annotations

from datetime import datetime, UTC
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.documents.repository import DocumentRepository
from app.modules.policies.models import PolicyRecord, PolicyStatus
from app.modules.policies.repository import PolicyRepository
from app.modules.policies.schemas import (
    PolicyCategoryResponse,
    PolicyRecordCreate,
    PolicyRecordResponse,
    PolicyRecordUpdate,
)


class PolicyService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = PolicyRepository(db)
        self._document_repo = DocumentRepository(db)

    async def list_public(self, tenant_id: UUID) -> list[PolicyRecordResponse]:
        records = await self._repo.list_by_tenant(tenant_id, published_only=True)
        return [self._to_response(record) for record in records]

    async def list_all(self, tenant_id: UUID) -> list[PolicyRecordResponse]:
        records = await self._repo.list_by_tenant(tenant_id, published_only=False)
        return [self._to_response(record) for record in records]

    async def list_categories(self, tenant_id: UUID) -> PolicyCategoryResponse:
        categories = await self._repo.list_categories(tenant_id)
        return PolicyCategoryResponse(categories=categories)

    async def get_policy(
        self,
        *,
        tenant_id: UUID,
        policy_id: UUID,
        is_admin: bool = False,
    ) -> PolicyRecordResponse:
        policy = await self._repo.get_by_id(tenant_id, policy_id)
        if not policy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
        if policy.status != PolicyStatus.published.value and not is_admin:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
        return self._to_response(policy)

    async def create_policy(self, tenant_id: UUID, data: PolicyRecordCreate, created_by: UUID) -> PolicyRecordResponse:
        document = None
        if data.document_id is not None:
            document = await self._document_repo.get_document(tenant_id, data.document_id)
            if document is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        policy = PolicyRecord(
            tenant_id=tenant_id,
            title=data.title.strip(),
            category=data.category.strip(),
            description=data.description.strip() if data.description else None,
            document_id=document.id if document else None,
            status=data.status,
            created_by=created_by,
        )
        await self._repo.create(policy)
        await self._db.commit()
        return self._to_response(policy, document_title=document.title if document else None)

    async def update_policy(self, tenant_id: UUID, policy_id: UUID, data: PolicyRecordUpdate) -> PolicyRecordResponse:
        payload = data.model_dump(exclude_unset=True)
        if "document_id" in payload and payload["document_id"] is not None:
            document = await self._document_repo.get_document(tenant_id, payload["document_id"])
            if document is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        policy = await self._repo.update(tenant_id, policy_id, payload)
        if policy is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
        policy.updated_at = datetime.now(UTC)
        await self._db.commit()
        document_title = None
        if policy.document_id is not None:
            doc = await self._document_repo.get_document(tenant_id, policy.document_id)
            document_title = doc.title if doc else None
        return self._to_response(policy, document_title=document_title)

    async def delete_policy(self, tenant_id: UUID, policy_id: UUID) -> None:
        deleted = await self._repo.delete(tenant_id, policy_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
        await self._db.commit()

    def _to_response(self, policy: PolicyRecord, *, document_title: str | None = None) -> PolicyRecordResponse:
        return PolicyRecordResponse(
            id=policy.id,
            tenant_id=policy.tenant_id,
            title=policy.title,
            category=policy.category,
            description=policy.description,
            document_id=policy.document_id,
            document_title=document_title,
            status=policy.status,
            created_by=policy.created_by,
            created_at=policy.created_at,
            updated_at=policy.updated_at,
        )
