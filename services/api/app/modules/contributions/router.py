from uuid import UUID

from fastapi import APIRouter

from app.core.dependencies import AuthDep, DbDep
from app.modules.contributions.schemas import (
    ContributionRecordCreate,
    ContributionRecordResponse,
    ContributionRecordUpdate,
    PaymentRecordCreate,
    PaymentRecordResponse,
)
from app.modules.contributions.service import ContributionService

router = APIRouter(prefix="/contributions", tags=["contributions"])


@router.post("/", response_model=ContributionRecordResponse, status_code=201)
async def create_contribution(
    data: ContributionRecordCreate, current: AuthDep, db: DbDep
) -> ContributionRecordResponse:
    """Create a contribution record (admin/treasurer only)."""
    service = ContributionService(db)
    return await service.create_contribution(current.tenant_id, data)


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
    return await service.update_contribution(current.tenant_id, contribution_id, data)


@router.delete("/{contribution_id}", status_code=204)
async def delete_contribution(
    contribution_id: UUID, current: AuthDep, db: DbDep
) -> None:
    """Delete a contribution record (admin only)."""
    service = ContributionService(db)
    await service.delete_contribution(current.tenant_id, contribution_id)


@router.post("/payments", response_model=PaymentRecordResponse, status_code=201)
async def record_payment(
    data: PaymentRecordCreate, current: AuthDep, db: DbDep
) -> PaymentRecordResponse:
    """Record a payment against a contribution (admin/treasurer only)."""
    service = ContributionService(db)
    return await service.record_payment(current.tenant_id, data)


@router.get("/{contribution_id}/payments", response_model=list[PaymentRecordResponse])
async def list_payments(
    contribution_id: UUID, current: AuthDep, db: DbDep
) -> list[PaymentRecordResponse]:
    """List payments for a specific contribution."""
    service = ContributionService(db)
    return await service.list_payments(current.tenant_id, contribution_id)
