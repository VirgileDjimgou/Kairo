from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse

from app.core.dependencies import AuthDep, DbDep
from app.core.import_export import ImportResult
from app.core.module_guard import require_module
from app.modules.contributions.schemas import (
    ContributionRecordCreate,
    ContributionRecordResponse,
    ContributionRecordUpdate,
    PaymentRecordCreate,
    PaymentRecordResponse,
)
from app.modules.contributions.service import ContributionService

router = APIRouter(
    prefix="/contributions",
    tags=["contributions"],
    dependencies=[require_module("contributions")],
)


@router.post("/", response_model=ContributionRecordResponse, status_code=201)
async def create_contribution(
    data: ContributionRecordCreate, current: AuthDep, db: DbDep
) -> ContributionRecordResponse:
    """Create a contribution record (admin/treasurer only)."""
    service = ContributionService(db)
    return await service.create_contribution(
        current.tenant_id, data, actor_user_id=current.user.id
    )


@router.get("/", response_model=list[ContributionRecordResponse])
async def list_contributions(
    current: AuthDep, db: DbDep, year: int | None = None
) -> list[ContributionRecordResponse]:
    """List all contribution records for the tenant (admin/treasurer only)."""
    service = ContributionService(db)
    return await service.list_contributions(current.tenant_id, year)


@router.get("/summary")
async def get_contribution_summary(
    current: AuthDep, db: DbDep, year: int | None = None
) -> dict:
    """Return aggregate contribution summary for the tenant."""
    service = ContributionService(db)
    return await service.get_summary(current.tenant_id, year)


@router.get("/by-member/{profile_id}", response_model=list[ContributionRecordResponse])
async def list_member_contributions(
    profile_id: UUID, current: AuthDep, db: DbDep
) -> list[ContributionRecordResponse]:
    """List contributions for a specific member."""
    service = ContributionService(db)
    return await service.list_member_contributions(current.tenant_id, profile_id)


@router.post("/import", response_model=ImportResult)
async def import_contributions(
    file: UploadFile,
    current: AuthDep,
    db: DbDep,
    dry_run: bool = Query(False, description="Validate without persisting"),
) -> ImportResult:
    """Import contribution records from a CSV file (admin only)."""
    if not current.has_role("admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    content = await file.read()
    service = ContributionService(db)
    return await service.import_csv(
        current.tenant_id, content, dry_run=dry_run, actor_user_id=current.user.id
    )


@router.get("/export")
async def export_contributions(current: AuthDep, db: DbDep) -> StreamingResponse:
    """Export contribution records as CSV (admin only)."""
    service = ContributionService(db)
    csv_content = await service.export_csv(current.tenant_id)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=contributions.csv"},
    )


@router.get("/{contribution_id}", response_model=ContributionRecordResponse)
async def get_contribution(
    contribution_id: UUID, current: AuthDep, db: DbDep
) -> ContributionRecordResponse:
    """Get a specific contribution record."""
    service = ContributionService(db)
    return await service.get_contribution(current.tenant_id, contribution_id)


@router.patch("/{contribution_id}", response_model=ContributionRecordResponse)
async def update_contribution(
    contribution_id: UUID, data: ContributionRecordUpdate, current: AuthDep, db: DbDep
) -> ContributionRecordResponse:
    """Update a contribution record (admin/treasurer only)."""
    service = ContributionService(db)
    return await service.update_contribution(
        current.tenant_id,
        contribution_id,
        data,
        actor_user_id=current.user.id,
    )


@router.delete("/{contribution_id}", status_code=204)
async def delete_contribution(
    contribution_id: UUID, current: AuthDep, db: DbDep
) -> None:
    """Delete a contribution record (admin only)."""
    service = ContributionService(db)
    await service.delete_contribution(
        current.tenant_id, contribution_id, actor_user_id=current.user.id
    )


@router.post("/payments", response_model=PaymentRecordResponse, status_code=201)
async def record_payment(
    data: PaymentRecordCreate, current: AuthDep, db: DbDep
) -> PaymentRecordResponse:
    """Record a payment against a contribution (admin/treasurer only)."""
    service = ContributionService(db)
    return await service.record_payment(
        current.tenant_id, data, actor_user_id=current.user.id
    )


@router.get("/{contribution_id}/payments", response_model=list[PaymentRecordResponse])
async def list_payments(
    contribution_id: UUID, current: AuthDep, db: DbDep
) -> list[PaymentRecordResponse]:
    """List payments for a specific contribution."""
    service = ContributionService(db)
    return await service.list_payments(current.tenant_id, contribution_id)
