from uuid import UUID

from fastapi import APIRouter, Query, UploadFile
from fastapi.responses import StreamingResponse

from app.core.authorization import require_capability
from app.core.capabilities import (
    CAP_EXPORT_SENSITIVE,
    CAP_FINANCE_AUDIT,
    CAP_FINANCE_TENANT_READ,
    CAP_FINANCE_WRITE,
    CAP_TENANT_ADMINISTRATION,
)
from app.core.dependencies import AuthDep, DbDep, NotificationsDep
from app.core.import_export import ImportResult
from app.core.module_guard import require_module
from app.modules.contributions.schemas import (
    ContributionReminderBatchRequest,
    ContributionReminderBatchResponse,
    ContributionReminderResponse,
    ContributionReminderSendRequest,
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
    require_capability(
        current,
        CAP_FINANCE_WRITE,
        detail="Finance write capability required",
    )
    service = ContributionService(db)
    return await service.create_contribution(
        current.tenant_id, data, actor_user_id=current.user.id
    )


@router.get("/", response_model=list[ContributionRecordResponse])
async def list_contributions(
    current: AuthDep, db: DbDep, year: int | None = None
) -> list[ContributionRecordResponse]:
    """List all contribution records for the tenant (admin/treasurer only)."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    service = ContributionService(db)
    return await service.list_contributions(current.tenant_id, year)


@router.get("/summary")
async def get_contribution_summary(
    current: AuthDep, db: DbDep, year: int | None = None
) -> dict:
    """Return aggregate contribution summary for the tenant."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    service = ContributionService(db)
    return await service.get_summary(current.tenant_id, year)


@router.get("/payments", response_model=list[PaymentRecordResponse])
async def list_tenant_payments(
    current: AuthDep, db: DbDep
) -> list[PaymentRecordResponse]:
    """List payment records across the tenant for finance read roles."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    service = ContributionService(db)
    return await service.list_tenant_payments(current.tenant_id)


@router.get("/reminders", response_model=list[ContributionReminderResponse])
async def list_contribution_reminders(
    current: AuthDep,
    db: DbDep,
    year: int | None = None,
    profile_id: UUID | None = None,
    limit: int = Query(20, ge=1, le=100),
) -> list[ContributionReminderResponse]:
    """List reminder history for finance support and audit review."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    service = ContributionService(db)
    return await service.list_reminders(
        current.tenant_id,
        year=year,
        profile_id=profile_id,
        limit=limit,
    )


@router.post(
    "/reminders/send",
    response_model=ContributionReminderBatchResponse,
    dependencies=[require_module("notifications")],
)
async def send_batch_contribution_reminders(
    payload: ContributionReminderBatchRequest,
    current: AuthDep,
    db: DbDep,
    notifications: NotificationsDep,
) -> ContributionReminderBatchResponse:
    """Send reminder messages to a filtered cohort of outstanding contributions."""
    require_capability(
        current,
        CAP_FINANCE_WRITE,
        detail="Finance write capability required",
    )
    service = ContributionService(db).with_notification_providers(notifications)
    return await service.send_batch_reminders(
        current.tenant_id,
        payload,
        actor_user_id=current.user.id,
    )


@router.get("/by-member/{profile_id}", response_model=list[ContributionRecordResponse])
async def list_member_contributions(
    profile_id: UUID, current: AuthDep, db: DbDep
) -> list[ContributionRecordResponse]:
    """List contributions for a specific member."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
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
    require_capability(
        current,
        CAP_TENANT_ADMINISTRATION,
        detail="Tenant administration capability required",
    )
    content = await file.read()
    service = ContributionService(db)
    return await service.import_csv(
        current.tenant_id, content, dry_run=dry_run, actor_user_id=current.user.id
    )


@router.get("/export")
async def export_contributions(current: AuthDep, db: DbDep) -> StreamingResponse:
    """Export contribution records as CSV (admin only)."""
    require_capability(
        current,
        CAP_TENANT_ADMINISTRATION,
        detail="Tenant administration capability required",
    )
    service = ContributionService(db)
    csv_content = await service.export_csv(current.tenant_id)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=contributions.csv"},
    )


@router.get("/report/export")
async def export_finance_report(current: AuthDep, db: DbDep) -> StreamingResponse:
    """Export a tenant finance report for audit-capable roles."""
    if not (
        current.has_capability(CAP_FINANCE_AUDIT)
        or current.has_capability(CAP_TENANT_ADMINISTRATION)
        or current.has_capability(CAP_EXPORT_SENSITIVE)
    ):
        require_capability(
            current,
            CAP_FINANCE_AUDIT,
            detail="Finance audit capability required",
        )
    service = ContributionService(db)
    csv_content = await service.export_finance_report_csv(current.tenant_id)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="finance-report.csv"'},
    )


@router.get("/{contribution_id}", response_model=ContributionRecordResponse)
async def get_contribution(
    contribution_id: UUID, current: AuthDep, db: DbDep
) -> ContributionRecordResponse:
    """Get a specific contribution record."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    service = ContributionService(db)
    return await service.get_contribution(current.tenant_id, contribution_id)


@router.patch("/{contribution_id}", response_model=ContributionRecordResponse)
async def update_contribution(
    contribution_id: UUID, data: ContributionRecordUpdate, current: AuthDep, db: DbDep
) -> ContributionRecordResponse:
    """Update a contribution record (admin/treasurer only)."""
    require_capability(
        current,
        CAP_FINANCE_WRITE,
        detail="Finance write capability required",
    )
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
    require_capability(
        current,
        CAP_TENANT_ADMINISTRATION,
        detail="Tenant administration capability required",
    )
    service = ContributionService(db)
    await service.delete_contribution(
        current.tenant_id, contribution_id, actor_user_id=current.user.id
    )


@router.post("/payments", response_model=PaymentRecordResponse, status_code=201)
async def record_payment(
    data: PaymentRecordCreate, current: AuthDep, db: DbDep
) -> PaymentRecordResponse:
    """Record a payment against a contribution (admin/treasurer only)."""
    require_capability(
        current,
        CAP_FINANCE_WRITE,
        detail="Finance write capability required",
    )
    service = ContributionService(db)
    return await service.record_payment(
        current.tenant_id, data, actor_user_id=current.user.id
    )


@router.post(
    "/{contribution_id}/reminders/send",
    response_model=ContributionReminderResponse,
    dependencies=[require_module("notifications")],
)
async def send_contribution_reminder(
    contribution_id: UUID,
    payload: ContributionReminderSendRequest,
    current: AuthDep,
    db: DbDep,
    notifications: NotificationsDep,
) -> ContributionReminderResponse:
    """Send a reminder for a single contribution record."""
    require_capability(
        current,
        CAP_FINANCE_WRITE,
        detail="Finance write capability required",
    )
    service = ContributionService(db).with_notification_providers(notifications)
    return await service.send_reminder(
        current.tenant_id,
        contribution_id,
        payload,
        actor_user_id=current.user.id,
    )


@router.get("/{contribution_id}/payments", response_model=list[PaymentRecordResponse])
async def list_payments(
    contribution_id: UUID, current: AuthDep, db: DbDep
) -> list[PaymentRecordResponse]:
    """List payments for a specific contribution."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    service = ContributionService(db)
    return await service.list_payments(current.tenant_id, contribution_id)
