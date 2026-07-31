from datetime import datetime, timezone
from decimal import Decimal
import secrets
import unicodedata
from uuid import UUID

import fitz
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.import_export import ImportResult, ImportRowError, generate_csv, parse_csv
from app.modules.audit.service import AuditService
from app.modules.contributions.repository import ContributionRepository
from app.modules.contributions.models import ContributionStatus
from app.modules.contributions.schemas import ContributionRecordResponse
from app.modules.membership.models import MembershipProfile, MembershipStatus, MembershipType
from app.modules.membership.repository import MembershipRepository
from app.modules.membership.schemas import (
    MemberBalanceResponse,
    MembershipProfileCreate,
    MembershipProfileResponse,
    MembershipProfileUpdate,
    MemberStatementResponse,
)
from app.modules.identity.repository import UserRepository
from app.modules.tenancy.repository import TenancyRepository
from app.core.security import hash_password


class MembershipService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = MembershipRepository(db)
        self._contrib_repo = ContributionRepository(db)
        self._audit = AuditService(db)
        self._user_repo = UserRepository(db)
        self._tenancy_repo = TenancyRepository(db)

    async def create_profile(
        self,
        tenant_id: UUID,
        data: MembershipProfileCreate,
        *,
        actor_user_id: UUID | None = None,
    ) -> MembershipProfileResponse:
        profile_data = data.model_dump(exclude_unset=True)
        requested_member_code = profile_data.pop("member_code", None)
        if requested_member_code:
            existing = await self._repo.get_by_member_code(tenant_id, requested_member_code)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A member with this code already exists",
                )
            profile_data["member_code"] = requested_member_code
        else:
            profile_data["member_code"] = await self._generate_member_code(
                tenant_id=tenant_id,
                last_name=data.last_name,
            )
        membership_type = profile_data.pop("membership_type", None)
        provision_access = profile_data.pop("provision_access", False)
        login_identifier = profile_data.pop("login_identifier", None)
        temporary_password = profile_data.pop("temporary_password", None)
        profile = await self._repo.create(tenant_id, profile_data)
        account_user_id = None
        if provision_access:
            account_user_id = await self._provision_direct_member_access(
                tenant_id=tenant_id,
                profile=profile,
                login_identifier=login_identifier,
                temporary_password=temporary_password,
            )
        contribution = None
        if membership_type is not None:
            expected_amount = Decimal("60.00") if membership_type == MembershipType.individual else Decimal("100.00")
            contribution = await self._contrib_repo.create_contribution(
                tenant_id,
                {
                    "membership_profile_id": profile.id,
                    "year": datetime.now(timezone.utc).year,
                    "expected_amount": expected_amount,
                    "paid_amount": Decimal("0.00"),
                    "currency": "EUR",
                    "status": ContributionStatus.pending.value,
                },
            )
            profile.membership_type = membership_type.value
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
                "membership_type": profile.membership_type,
                "initial_contribution_id": str(contribution.id) if contribution else None,
                "initial_expected_amount": str(contribution.expected_amount) if contribution else None,
                "direct_account_provisioned": account_user_id is not None,
                "account_user_id": str(account_user_id) if account_user_id else None,
            },
        )
        await self._db.commit()
        return MembershipProfileResponse.model_validate(profile)

    async def _generate_member_code(self, *, tenant_id: UUID, last_name: str) -> str:
        normalized_name = unicodedata.normalize("NFKD", last_name)
        ascii_name = "".join(character for character in normalized_name if not unicodedata.combining(character))
        name_token = "".join(character for character in ascii_name.upper() if character.isalnum())[:24] or "MEMBRE"
        for _ in range(32):
            candidate = f"{name_token}-COMBIS-{secrets.randbelow(10_001)}"
            if await self._repo.get_by_member_code(tenant_id, candidate) is None:
                return candidate
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to allocate a unique member code. Please retry.",
        )

    async def _provision_direct_member_access(
        self,
        *,
        tenant_id: UUID,
        profile: MembershipProfile,
        login_identifier: str | None,
        temporary_password: str | None,
    ) -> UUID:
        if temporary_password is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A temporary password is required for direct member access",
            )
        phone = profile.phone.strip() if profile.phone else None
        if profile.email and await self._user_repo.get_by_email(profile.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This email address is already linked to an account")
        if login_identifier and await self._user_repo.get_by_login_identifier(login_identifier):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This login identifier is already in use")
        if phone and await self._user_repo.get_by_phone(phone):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This phone number is already linked to an account")

        internal_email = profile.email or f"member-{profile.id.hex}@member.kairo.local"
        user = await self._user_repo.create(
            email=internal_email,
            password_hash=hash_password(temporary_password),
            display_name=profile.display_name,
            status=profile.status,
            login_identifier=login_identifier,
            phone=phone,
            password_change_required=True,
        )
        await self._tenancy_repo.create_tenant_user(
            tenant_id=tenant_id,
            user_id=user.id,
            profile_type="member",
            membership_status="active",
        )
        member_role = await self._tenancy_repo.get_role_by_code(tenant_id, "member")
        if member_role is None:
            member_role = await self._tenancy_repo.create_role(
                tenant_id=tenant_id,
                code="member",
                name="Member",
                description="Ordinary association member",
                is_system_role=True,
            )
        await self._tenancy_repo.assign_role_to_user(tenant_id, user.id, member_role.id)
        profile.user_id = user.id
        await self._db.flush()
        return user.id

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
        self, tenant_id: UUID, status: str | None = None, query_text: str | None = None
    ) -> list[MembershipProfileResponse]:
        profiles = await self._repo.list_by_tenant(tenant_id, status, query_text)
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

    async def get_my_contributions(
        self, tenant_id: UUID, user_id: UUID
    ) -> list[ContributionRecordResponse]:
        profile = await self._repo.get_by_user_id(tenant_id, user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No member profile linked to your account",
            )
        contributions = await self._contrib_repo.list_by_profile(tenant_id, profile.id)
        return [ContributionRecordResponse.model_validate(c) for c in contributions]

    async def get_my_statement(
        self, tenant_id: UUID, user_id: UUID
    ) -> MemberStatementResponse:
        balance = await self.get_my_balance(tenant_id, user_id)
        contributions = await self.get_my_contributions(tenant_id, user_id)
        return MemberStatementResponse(
            profile=balance.profile,
            summary=balance,
            contributions=contributions,
        )

    async def generate_my_statement_pdf(
        self, tenant_id: UUID, user_id: UUID
    ) -> bytes:
        statement = await self.get_my_statement(tenant_id, user_id)
        profile = statement.profile
        summary = statement.summary

        document = fitz.open()
        page = document.new_page()

        margin_x = 50
        cursor_y = 56
        line_height = 18

        def write_line(text: str, *, size: float = 11, indent: float = 0) -> None:
            nonlocal cursor_y, page
            if cursor_y > 780:
                page = document.new_page()
                cursor_y = 56
            page.insert_text(
                (margin_x + indent, cursor_y),
                text,
                fontsize=size,
                fontname="helv",
            )
            cursor_y += line_height if size <= 11 else line_height + 4

        generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        write_line("Kairo Personal Contribution Statement", size=16)
        write_line(f"Generated: {generated_at}", size=10)
        cursor_y += 6
        write_line(f"Member: {profile.display_name}")
        write_line(f"Member code: {profile.member_code}")
        write_line(f"Tenant ID: {profile.tenant_id}", size=10)
        write_line(f"Status: {profile.status}", size=10)
        if profile.email:
            write_line(f"Email: {profile.email}", size=10)
        cursor_y += 6
        write_line("Summary", size=13)
        write_line(f"Total expected: {summary.total_expected} EUR", indent=10)
        write_line(f"Total paid: {summary.total_paid} EUR", indent=10)
        write_line(f"Outstanding balance: {summary.total_balance} EUR", indent=10)
        write_line(f"Contribution records: {summary.contribution_count}", indent=10)
        cursor_y += 6
        write_line("Contribution history", size=13)

        if not statement.contributions:
            write_line("No contribution records available.", indent=10)
        else:
            for contribution in statement.contributions:
                write_line(
                    (
                        f"{contribution.year}  "
                        f"Expected {contribution.expected_amount} {contribution.currency}  "
                        f"Paid {contribution.paid_amount} {contribution.currency}  "
                        f"Balance {contribution.balance} {contribution.currency}"
                    ),
                    indent=10,
                )
                write_line(f"Status: {contribution.status}", size=10, indent=22)
                if contribution.due_date:
                    due_label = contribution.due_date.strftime("%Y-%m-%d")
                    write_line(f"Due date: {due_label}", size=10, indent=22)

        pdf_bytes = document.tobytes()
        document.close()
        return pdf_bytes

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
                    status=MembershipStatus(status_val),
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
