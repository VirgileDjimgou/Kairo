from __future__ import annotations

from datetime import datetime, UTC
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.disciplinary.models import DisciplinaryRecord
from app.modules.disciplinary.repository import DisciplinaryRepository
from app.modules.disciplinary.schemas import (
    DisciplinaryRecordCreate,
    DisciplinaryRecordResponse,
    DisciplinaryRecordUpdate,
)
from app.modules.membership.repository import MembershipRepository
from app.modules.policies.repository import PolicyRepository


class DisciplinaryService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = DisciplinaryRepository(db)
        self._membership_repo = MembershipRepository(db)
        self._policy_repo = PolicyRepository(db)

    async def list_records(self, tenant_id: UUID) -> list[DisciplinaryRecordResponse]:
        records = await self._repo.list_by_tenant(tenant_id)
        return [await self._to_response(tenant_id, record) for record in records]

    async def list_my_records(self, tenant_id: UUID, user_id: UUID) -> list[DisciplinaryRecordResponse]:
        profile = await self._membership_repo.get_by_user_id(tenant_id, user_id)
        if profile is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member profile not found")
        records = await self._repo.list_by_membership_profile(tenant_id, profile.id)
        return [await self._to_response(tenant_id, record) for record in records]

    async def get_record(
        self,
        *,
        tenant_id: UUID,
        record_id: UUID,
        user_id: UUID,
        is_admin_or_treasurer: bool,
    ) -> DisciplinaryRecordResponse:
        record = await self._repo.get_by_id(tenant_id, record_id)
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplinary record not found")
        if not is_admin_or_treasurer:
            profile = await self._membership_repo.get_by_user_id(tenant_id, user_id)
            if profile is None or profile.id != record.membership_profile_id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplinary record not found")
        return await self._to_response(tenant_id, record)

    async def create_record(
        self,
        tenant_id: UUID,
        created_by: UUID,
        data: DisciplinaryRecordCreate,
    ) -> DisciplinaryRecordResponse:
        profile = await self._membership_repo.get_by_id(tenant_id, data.membership_profile_id)
        if profile is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member profile not found")
        if data.policy_record_id is not None:
            policy = await self._policy_repo.get_by_id(tenant_id, data.policy_record_id)
            if policy is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
        record = DisciplinaryRecord(
            tenant_id=tenant_id,
            membership_profile_id=data.membership_profile_id,
            policy_record_id=data.policy_record_id,
            title=data.title.strip(),
            description=data.description.strip() if data.description else None,
            amount=data.amount,
            currency=data.currency,
            status=data.status,
            recorded_by=created_by,
            recorded_at=datetime.now(UTC),
        )
        await self._repo.create(record)
        await self._db.commit()
        return await self._to_response(tenant_id, record)

    async def update_record(
        self,
        tenant_id: UUID,
        record_id: UUID,
        data: DisciplinaryRecordUpdate,
    ) -> DisciplinaryRecordResponse:
        payload = data.model_dump(exclude_unset=True)
        if payload.get("policy_record_id") is not None:
            policy = await self._policy_repo.get_by_id(tenant_id, payload["policy_record_id"])
            if policy is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
        record = await self._repo.update(tenant_id, record_id, payload)
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplinary record not found")
        record.updated_at = datetime.now(UTC)
        await self._db.commit()
        return await self._to_response(tenant_id, record)

    async def delete_record(self, tenant_id: UUID, record_id: UUID) -> None:
        deleted = await self._repo.delete(tenant_id, record_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplinary record not found")
        await self._db.commit()

    async def _to_response(self, tenant_id: UUID, record: DisciplinaryRecord) -> DisciplinaryRecordResponse:
        profile = await self._membership_repo.get_by_id(tenant_id, record.membership_profile_id)
        policy_title = None
        if record.policy_record_id is not None:
            policy = await self._policy_repo.get_by_id(tenant_id, record.policy_record_id)
            policy_title = policy.title if policy else None
        return DisciplinaryRecordResponse(
            id=record.id,
            tenant_id=record.tenant_id,
            membership_profile_id=record.membership_profile_id,
            membership_display_name=profile.display_name if profile else None,
            policy_record_id=record.policy_record_id,
            policy_title=policy_title,
            title=record.title,
            description=record.description,
            amount=Decimal(str(record.amount)),
            currency=record.currency,
            status=record.status,
            recorded_by=record.recorded_by,
            recorded_at=record.recorded_at,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
