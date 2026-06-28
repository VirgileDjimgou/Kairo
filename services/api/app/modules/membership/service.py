from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.membership.models import MembershipProfile
from app.modules.membership.repository import MembershipRepository
from app.modules.membership.schemas import (
    MemberBalanceResponse,
    MembershipProfileCreate,
    MembershipProfileResponse,
    MembershipProfileUpdate,
)
from app.modules.contributions.repository import ContributionRepository


class MembershipService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = MembershipRepository(db)
        self._contrib_repo = ContributionRepository(db)

    async def create_profile(
        self, tenant_id: UUID, data: MembershipProfileCreate
    ) -> MembershipProfileResponse:
        existing = await self._repo.get_by_member_code(tenant_id, data.member_code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A member with this code already exists",
            )
        profile = await self._repo.create(
            tenant_id, data.model_dump(exclude_unset=True)
        )
        return MembershipProfileResponse.model_validate(profile)

    async def get_profile(
        self, tenant_id: UUID, profile_id: UUID
    ) -> MembershipProfileResponse:
        profile = await self._repo.get_by_id(tenant_id, profile_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member profile not found",
            )
        return MembershipProfileResponse.model_validate(profile)

    async def get_my_profile(
        self, tenant_id: UUID, user_id: UUID
    ) -> MembershipProfileResponse:
        profile = await self._repo.get_by_user_id(tenant_id, user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No member profile linked to your account",
            )
        return MembershipProfileResponse.model_validate(profile)

    async def list_profiles(
        self, tenant_id: UUID, status: str | None = None
    ) -> list[MembershipProfileResponse]:
        profiles = await self._repo.list_by_tenant(tenant_id, status)
        return [MembershipProfileResponse.model_validate(p) for p in profiles]

    async def update_profile(
        self, tenant_id: UUID, profile_id: UUID, data: MembershipProfileUpdate
    ) -> MembershipProfileResponse:
        profile = await self._repo.update(
            tenant_id, profile_id, data.model_dump(exclude_unset=True)
        )
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member profile not found",
            )
        return MembershipProfileResponse.model_validate(profile)

    async def delete_profile(self, tenant_id: UUID, profile_id: UUID) -> None:
        deleted = await self._repo.delete(tenant_id, profile_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member profile not found",
            )

    async def get_my_balance(
        self, tenant_id: UUID, user_id: UUID
    ) -> MemberBalanceResponse:
        profile = await self._repo.get_by_user_id(tenant_id, user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No member profile linked to your account",
            )
        contributions = await self._contrib_repo.list_by_profile(
            tenant_id, profile.id
        )
        profile_resp = MembershipProfileResponse.model_validate(profile)
        total_expected = sum(c.expected_amount for c in contributions)
        total_paid = sum(c.paid_amount for c in contributions)
        total_balance = sum(c.balance for c in contributions)
        return MemberBalanceResponse(
            profile=profile_resp,
            total_expected=Decimal(str(total_expected)),
            total_paid=Decimal(str(total_paid)),
            total_balance=Decimal(str(total_balance)),
            contribution_count=len(contributions),
        )

    async def get_member_balance(
        self, tenant_id: UUID, profile_id: UUID
    ) -> MemberBalanceResponse:
        profile = await self._repo.get_by_id(tenant_id, profile_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member profile not found",
            )
        contributions = await self._contrib_repo.list_by_profile(
            tenant_id, profile.id
        )
        profile_resp = MembershipProfileResponse.model_validate(profile)
        total_expected = sum(c.expected_amount for c in contributions)
        total_paid = sum(c.paid_amount for c in contributions)
        total_balance = sum(c.balance for c in contributions)
        return MemberBalanceResponse(
            profile=profile_resp,
            total_expected=Decimal(str(total_expected)),
            total_paid=Decimal(str(total_paid)),
            total_balance=Decimal(str(total_balance)),
            contribution_count=len(contributions),
        )

    async def get_profile_by_user_id(
        self, tenant_id: UUID, user_id: UUID
    ) -> MembershipProfile | None:
        return await self._repo.get_by_user_id(tenant_id, user_id)
