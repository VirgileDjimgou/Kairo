from uuid import UUID

from fastapi import APIRouter, Query, UploadFile
from fastapi.responses import StreamingResponse

from app.core.authorization import require_capability
from app.core.capabilities import (
    CAP_FINANCE_TENANT_READ,
    CAP_MEMBERSHIP_TENANT_READ,
    CAP_MEMBERSHIP_WRITE,
    CAP_TENANT_ADMINISTRATION,
)
from app.core.dependencies import AuthDep, DbDep
from app.core.import_export import ImportResult
from app.core.module_guard import require_module
from app.modules.contributions.schemas import ContributionRecordResponse
from app.modules.membership.schemas import (
    MemberBalanceResponse,
    MemberStatementResponse,
    MembershipProfileCreate,
    MembershipProfileResponse,
    MembershipProfileUpdate,
)
from app.modules.membership.service import MembershipService

router = APIRouter(
    prefix="/memberships",
    tags=["membership"],
    dependencies=[require_module("membership")],
)


@router.get("/me", response_model=MembershipProfileResponse)
async def get_my_profile(current: AuthDep, db: DbDep) -> MembershipProfileResponse:
    """Return the member profile linked to the current user."""
    service = MembershipService(db)
    return await service.get_my_profile(current.tenant_id, current.user.id)


@router.get("/me/balance", response_model=MemberBalanceResponse)
async def get_my_balance(current: AuthDep, db: DbDep) -> MemberBalanceResponse:
    """Return the current user's contribution balance."""
    service = MembershipService(db)
    return await service.get_my_balance(current.tenant_id, current.user.id)


@router.get("/me/contributions", response_model=list[ContributionRecordResponse])
async def get_my_contributions(
    current: AuthDep, db: DbDep
) -> list[ContributionRecordResponse]:
    """Return the current user's personal contribution history."""
    service = MembershipService(db)
    return await service.get_my_contributions(current.tenant_id, current.user.id)


@router.get("/me/statement", response_model=MemberStatementResponse)
async def get_my_statement(current: AuthDep, db: DbDep) -> MemberStatementResponse:
    """Return the current user's personal contribution statement."""
    service = MembershipService(db)
    return await service.get_my_statement(current.tenant_id, current.user.id)


@router.get("/me/statement.pdf")
async def download_my_statement_pdf(current: AuthDep, db: DbDep) -> StreamingResponse:
    """Download a PDF contribution statement for the authenticated member only."""
    service = MembershipService(db)
    pdf_bytes = await service.generate_my_statement_pdf(current.tenant_id, current.user.id)
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="my-contribution-statement.pdf"'
        },
    )


@router.post("/import", response_model=ImportResult)
async def import_members(
    file: UploadFile,
    current: AuthDep,
    db: DbDep,
    dry_run: bool = Query(False, description="Validate without persisting"),
) -> ImportResult:
    """Import member profiles from a CSV file (admin only)."""
    require_capability(
        current,
        CAP_MEMBERSHIP_WRITE,
        detail="Membership write capability required",
    )
    content = await file.read()
    service = MembershipService(db)
    return await service.import_csv(
        current.tenant_id, content, dry_run=dry_run, actor_user_id=current.user.id
    )


@router.get("/export")
async def export_members(current: AuthDep, db: DbDep) -> StreamingResponse:
    """Export member profiles as CSV (admin only)."""
    require_capability(
        current,
        CAP_TENANT_ADMINISTRATION,
        detail="Tenant administration capability required",
    )
    service = MembershipService(db)
    csv_content = await service.export_csv(current.tenant_id)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=members.csv"},
    )


@router.get("/{profile_id}", response_model=MembershipProfileResponse)
async def get_profile(
    profile_id: UUID, current: AuthDep, db: DbDep
) -> MembershipProfileResponse:
    """Return a specific member profile (admin/treasurer only)."""
    require_capability(
        current,
        CAP_MEMBERSHIP_TENANT_READ,
        detail="Membership directory read capability required",
    )
    service = MembershipService(db)
    return await service.get_profile(current.tenant_id, profile_id)


@router.get("/{profile_id}/balance", response_model=MemberBalanceResponse)
async def get_member_balance(
    profile_id: UUID, current: AuthDep, db: DbDep
) -> MemberBalanceResponse:
    """Return a specific member's contribution balance (admin/treasurer only)."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    service = MembershipService(db)
    return await service.get_member_balance(current.tenant_id, profile_id)


@router.get("/", response_model=list[MembershipProfileResponse])
async def list_profiles(
    current: AuthDep, db: DbDep, status: str | None = None
) -> list[MembershipProfileResponse]:
    """List all member profiles for the current tenant (admin/treasurer only)."""
    require_capability(
        current,
        CAP_MEMBERSHIP_TENANT_READ,
        detail="Membership directory read capability required",
    )
    service = MembershipService(db)
    return await service.list_profiles(current.tenant_id, status)


@router.post("/", response_model=MembershipProfileResponse, status_code=201)
async def create_profile(
    data: MembershipProfileCreate, current: AuthDep, db: DbDep
) -> MembershipProfileResponse:
    """Create a new member profile (admin only)."""
    require_capability(
        current,
        CAP_MEMBERSHIP_WRITE,
        detail="Membership write capability required",
    )
    service = MembershipService(db)
    return await service.create_profile(current.tenant_id, data, actor_user_id=current.user.id)


@router.patch("/{profile_id}", response_model=MembershipProfileResponse)
async def update_profile(
    profile_id: UUID, data: MembershipProfileUpdate, current: AuthDep, db: DbDep
) -> MembershipProfileResponse:
    """Update a member profile (admin only)."""
    require_capability(
        current,
        CAP_MEMBERSHIP_WRITE,
        detail="Membership write capability required",
    )
    service = MembershipService(db)
    return await service.update_profile(
        current.tenant_id, profile_id, data, actor_user_id=current.user.id
    )


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(
    profile_id: UUID, current: AuthDep, db: DbDep
) -> None:
    """Delete a member profile (admin only)."""
    require_capability(
        current,
        CAP_MEMBERSHIP_WRITE,
        detail="Membership write capability required",
    )
    service = MembershipService(db)
    await service.delete_profile(
        current.tenant_id, profile_id, actor_user_id=current.user.id
    )
