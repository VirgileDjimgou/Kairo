from collections.abc import Sequence
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.import_export import ImportResult, ImportRowError, generate_csv, parse_csv
from app.modules.audit.service import AuditService
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
        self._db = db
        self._repo = MembershipRepository(db)
        self._contrib_repo = ContributionRepository(db)
        self._audit = AuditService(db)

    async def create_profile(
        self,
        tenant_id: UUID,
        data: MembershipProfileCreate,
        *,
        actor_user_id: UUID | None = None,
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
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="create",
            entity_type="membership_profile",
            entity_id=profile.id,
            module_key="membership",
            details={
                "member_code": profile.member_code,
                "display_name": profile.display_name,
                "status": profile.status,
            },
        )
        await self._db.commit()
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
        self,
        tenant_id: UUID,
        profile_id: UUID,
        data: MembershipProfileUpdate,
        *,
        actor_user_id: UUID | None = None,
    ) -> MembershipProfileResponse:
        profile = await self._repo.update(
            tenant_id, profile_id, data.model_dump(exclude_unset=True)
        )
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member profile not found",
            )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="update",
            entity_type="membership_profile",
            entity_id=profile.id,
            module_key="membership",
            details={"changes": data.model_dump(exclude_unset=True)},
        )
        await self._db.commit()
        return MembershipProfileResponse.model_validate(profile)

    async def delete_profile(
        self,
        tenant_id: UUID,
        profile_id: UUID,
        *,
        actor_user_id: UUID | None = None,
    ) -> None:
        profile = await self._repo.get_by_id(tenant_id, profile_id)
        if profile:
            details = {
                "member_code": profile.member_code,
                "display_name": profile.display_name,
            }
        else:
            details = {"profile_id": str(profile_id)}
        deleted = await self._repo.delete(tenant_id, profile_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member profile not found",
            )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="delete",
            entity_type="membership_profile",
            entity_id=profile_id,
            module_key="membership",
            details=details,
        )
        await self._db.commit()

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

    async def import_csv(
        self,
        tenant_id: UUID,
        content: bytes,
        *,
        dry_run: bool = False,
        actor_user_id: UUID | None = None,
    ) -> ImportResult:
        rows = parse_csv(content)
        errors: list[ImportRowError] = []
        success_count = 0

        for i, row in enumerate(rows, start=2):
            row_errors: list[ImportRowError] = []

            member_code = row.get("member_code", "").strip()
            first_name = row.get("first_name", "").strip()
            last_name = row.get("last_name", "").strip()
            display_name = row.get("display_name", "").strip() or f"{first_name} {last_name}"
            email = row.get("email", "").strip() or None
            phone = row.get("phone", "").strip() or None
            status_val = row.get("status", "active").strip()

            if not member_code:
                row_errors.append(ImportRowError(row_number=i, column="member_code", message="member_code is required"))
            if not first_name:
                row_errors.append(ImportRowError(row_number=i, column="first_name", message="first_name is required"))
            if not last_name:
                row_errors.append(ImportRowError(row_number=i, column="last_name", message="last_name is required"))
            if status_val not in ("active", "inactive", "suspended", "resigned"):
                row_errors.append(ImportRowError(row_number=i, column="status", message=f"Invalid status '{status_val}'"))

            if not row_errors and not dry_run:
                existing = await self._repo.get_by_member_code(tenant_id, member_code)
                if existing:
                    row_errors.append(ImportRowError(
                        row_number=i, column="member_code", message=f"Duplicate member_code '{member_code}'"
                    ))

            if row_errors:
                errors.extend(row_errors)
                continue

            if not dry_run:
                data = MembershipProfileCreate(
                    member_code=member_code,
                    first_name=first_name,
                    last_name=last_name,
                    display_name=display_name,
                    email=email,
                    phone=phone,
                    status=status_val,
                )
                profile = await self._repo.create(tenant_id, data.model_dump(exclude_unset=True))
                await self._audit.record_event(
                    tenant_id=tenant_id,
                    actor_user_id=actor_user_id,
                    action="import",
                    entity_type="membership_profile",
                    entity_id=profile.id,
                    module_key="membership",
                    details={"member_code": member_code, "source": "csv_import"},
                )

            success_count += 1

        if not dry_run:
            await self._db.commit()

        return ImportResult(
            total_rows=len(rows),
            success_count=success_count,
            error_count=len(errors),
            errors=errors,
            dry_run=dry_run,
        )

    async def export_csv(self, tenant_id: UUID) -> str:
        profiles = await self._repo.list_by_tenant(tenant_id)
        rows = [
            {
                "member_code": p.member_code,
                "first_name": p.first_name,
                "last_name": p.last_name,
                "display_name": p.display_name,
                "email": p.email or "",
                "phone": p.phone or "",
                "status": p.status,
                "joined_at": str(p.joined_at),
            }
            for p in profiles
        ]
        return generate_csv(rows)
