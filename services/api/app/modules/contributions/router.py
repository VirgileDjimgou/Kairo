from typing import Literal
from uuid import UUID

from fastapi import APIRouter, File, Query, UploadFile
from fastapi.responses import StreamingResponse

from app.core.authorization import require_capability
from app.core.capabilities import (
    CAP_CONTRIBUTION_RECEIPT_DECLARE,
    CAP_CONTRIBUTION_RECEIPT_MEMBER_SELF_READ,
    CAP_CONTRIBUTION_RECEIPT_OWN_READ,
    CAP_CONTRIBUTION_RECEIPT_PROCESS,
    CAP_CONTRIBUTION_RECEIPT_TENANT_READ,
    CAP_EXPORT_SENSITIVE,
    CAP_FINANCE_AUDIT,
    CAP_FINANCE_EXPENSES_APPROVE,
    CAP_FINANCE_EXPENSES_WRITE,
    CAP_FINANCE_SELF_READ,
    CAP_FINANCE_TENANT_READ,
    CAP_FINANCE_WRITE,
    CAP_TENANT_ADMINISTRATION,
)
from app.core.dependencies import AuthDep, DbDep, NotificationsDep, ObjectStorageDep
from app.core.import_export import ImportResult
from app.core.module_guard import require_module
from app.modules.audit.service import AuditService
from app.modules.backup.preflight import require_pre_operation_backup
from app.modules.contributions.schemas import (
    AnnualBudgetResponse,
    BudgetPlanResponse,
    BudgetPlanUpdate,
    ContributionReceiptDeclarationCreate,
    ContributionReceiptDeclarationProcess,
    ContributionReceiptDeclarationResponse,
    ContributionReceiptDeclarationUpdate,
    ContributionReceiptHandoverReminderUpdate,
    ContributionReceiptHandoverReport,
    ContributionReceiptMemberOption,
    ContributionReceiptTreasuryConfirmation,
    ContributionRecordCreate,
    ContributionRecordResponse,
    ContributionRecordUpdate,
    ContributionReminderBatchRequest,
    ContributionReminderBatchResponse,
    ContributionReminderResponse,
    ContributionReminderSendRequest,
    ExpenseCategoryCreate,
    ExpenseCategoryResponse,
    ExpenseRecordCreate,
    ExpenseRecordResponse,
    ExpenseRejectRequest,
    ExpenseReversalRequest,
    FinanceAccountResponse,
    FinancePeriodReopenRequest,
    FinancePeriodResponse,
    OpeningBalanceUpdate,
    PaymentRecordCreate,
    PaymentRecordResponse,
    PaymentReversalRequest,
    TreasuryPositionResponse,
)
from app.modules.contributions.service import ContributionService
from app.modules.membership.repository import MembershipRepository

router = APIRouter(
    prefix="/contributions",
    tags=["contributions"],
    dependencies=[require_module("contributions")],
)


@router.post(
    "/receipt-declarations", response_model=ContributionReceiptDeclarationResponse, status_code=201
)
async def create_receipt_declaration(
    data: ContributionReceiptDeclarationCreate, current: AuthDep, db: DbDep
) -> ContributionReceiptDeclarationResponse:
    require_capability(
        current, CAP_CONTRIBUTION_RECEIPT_DECLARE, detail="Receipt declaration capability required"
    )
    declarant_role = next(
        (role for role in current.roles if role != "member"),
        current.roles[0] if current.roles else "unknown",
    )
    return await ContributionService(db).create_receipt_declaration(
        current.tenant_id,
        data,
        declarant_user_id=current.user.id,
        declarant_role_code=declarant_role,
    )


@router.get(
    "/receipt-declarations/mine", response_model=list[ContributionReceiptDeclarationResponse]
)
async def list_my_receipt_declarations(
    current: AuthDep, db: DbDep
) -> list[ContributionReceiptDeclarationResponse]:
    require_capability(
        current,
        CAP_CONTRIBUTION_RECEIPT_OWN_READ,
        detail="Own receipt declaration capability required",
    )
    return await ContributionService(db).list_receipt_declarations(
        current.tenant_id, declarant_user_id=current.user.id
    )


@router.get("/receipt-declarations/me", response_model=list[ContributionReceiptDeclarationResponse])
async def list_member_receipt_declarations(
    current: AuthDep, db: DbDep
) -> list[ContributionReceiptDeclarationResponse]:
    require_capability(
        current,
        CAP_CONTRIBUTION_RECEIPT_MEMBER_SELF_READ,
        detail="Personal receipt declaration capability required",
    )
    profile = await MembershipRepository(db).get_by_user_id(current.tenant_id, current.user.id)
    if profile is None:
        return []
    return await ContributionService(db).list_receipt_declarations(
        current.tenant_id, membership_profile_id=profile.id
    )


@router.get("/receipt-declarations", response_model=list[ContributionReceiptDeclarationResponse])
async def list_receipt_declarations(
    current: AuthDep, db: DbDep
) -> list[ContributionReceiptDeclarationResponse]:
    require_capability(
        current,
        CAP_CONTRIBUTION_RECEIPT_TENANT_READ,
        detail="Receipt declaration review capability required",
    )
    return await ContributionService(db).list_receipt_declarations(current.tenant_id)


@router.get(
    "/receipt-declarations/member-options", response_model=list[ContributionReceiptMemberOption]
)
async def list_receipt_declaration_member_options(
    current: AuthDep, db: DbDep
) -> list[ContributionReceiptMemberOption]:
    """Return read-only member identity details for authorized receipt declarants."""
    require_capability(
        current, CAP_CONTRIBUTION_RECEIPT_DECLARE, detail="Receipt declaration capability required"
    )
    profiles = await MembershipRepository(db).list_by_tenant(current.tenant_id)
    return [
        ContributionReceiptMemberOption(
            id=profile.id,
            display_name=profile.display_name,
            member_code=profile.member_code,
            first_name=profile.first_name,
            last_name=profile.last_name,
            email=profile.email,
            phone=profile.phone,
            membership_type=profile.membership_type,
            status=profile.status,
            joined_at=profile.joined_at,
        )
        for profile in profiles
    ]


@router.patch(
    "/receipt-declarations/{declaration_id}", response_model=ContributionReceiptDeclarationResponse
)
async def update_receipt_declaration(
    declaration_id: UUID, data: ContributionReceiptDeclarationUpdate, current: AuthDep, db: DbDep
) -> ContributionReceiptDeclarationResponse:
    require_capability(
        current, CAP_CONTRIBUTION_RECEIPT_DECLARE, detail="Receipt declaration capability required"
    )
    return await ContributionService(db).update_receipt_declaration(
        current.tenant_id, declaration_id, data, declarant_user_id=current.user.id
    )


@router.post(
    "/receipt-declarations/{declaration_id}/submit",
    response_model=ContributionReceiptDeclarationResponse,
)
async def submit_receipt_declaration(
    declaration_id: UUID, current: AuthDep, db: DbDep
) -> ContributionReceiptDeclarationResponse:
    require_capability(
        current, CAP_CONTRIBUTION_RECEIPT_DECLARE, detail="Receipt declaration capability required"
    )
    return await ContributionService(db).submit_receipt_declaration(
        current.tenant_id, declaration_id, declarant_user_id=current.user.id
    )


@router.post(
    "/receipt-declarations/{declaration_id}/process",
    response_model=ContributionReceiptDeclarationResponse,
)
async def process_receipt_declaration(
    declaration_id: UUID, data: ContributionReceiptDeclarationProcess, current: AuthDep, db: DbDep
) -> ContributionReceiptDeclarationResponse:
    require_capability(
        current,
        CAP_CONTRIBUTION_RECEIPT_PROCESS,
        detail="Receipt declaration processing capability required",
    )
    return await ContributionService(db).process_receipt_declaration(
        current.tenant_id, declaration_id, data, processor_user_id=current.user.id
    )


@router.post(
    "/receipt-declarations/{declaration_id}/handover",
    response_model=ContributionReceiptDeclarationResponse,
)
async def report_receipt_handover(
    declaration_id: UUID, data: ContributionReceiptHandoverReport, current: AuthDep, db: DbDep
) -> ContributionReceiptDeclarationResponse:
    require_capability(
        current, CAP_CONTRIBUTION_RECEIPT_DECLARE, detail="Receipt declaration capability required"
    )
    return await ContributionService(db).report_receipt_handover(
        current.tenant_id, declaration_id, data, declarant_user_id=current.user.id
    )


@router.post(
    "/receipt-declarations/{declaration_id}/confirm-treasury-receipt",
    response_model=ContributionReceiptDeclarationResponse,
)
async def confirm_receipt_in_treasury(
    declaration_id: UUID,
    data: ContributionReceiptTreasuryConfirmation,
    current: AuthDep,
    db: DbDep,
    notifications: NotificationsDep,
) -> ContributionReceiptDeclarationResponse:
    require_capability(
        current,
        CAP_CONTRIBUTION_RECEIPT_PROCESS,
        detail="Receipt declaration processing capability required",
    )
    return (
        await ContributionService(db)
        .with_notification_providers(notifications)
        .confirm_receipt_in_treasury(
            current.tenant_id, declaration_id, data, treasurer_user_id=current.user.id
        )
    )


@router.post(
    "/receipt-declarations/{declaration_id}/handover-reminder",
    response_model=ContributionReceiptDeclarationResponse,
)
async def update_receipt_handover_reminder(
    declaration_id: UUID,
    data: ContributionReceiptHandoverReminderUpdate,
    current: AuthDep,
    db: DbDep,
    notifications: NotificationsDep,
) -> ContributionReceiptDeclarationResponse:
    require_capability(
        current,
        CAP_CONTRIBUTION_RECEIPT_PROCESS,
        detail="Receipt declaration processing capability required",
    )
    return (
        await ContributionService(db)
        .with_notification_providers(notifications)
        .update_receipt_handover_reminder(
            current.tenant_id, declaration_id, data, treasurer_user_id=current.user.id
        )
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
    return await service.create_contribution(current.tenant_id, data, actor_user_id=current.user.id)


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
async def get_contribution_summary(current: AuthDep, db: DbDep, year: int | None = None) -> dict:
    """Return aggregate contribution summary for the tenant."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    service = ContributionService(db)
    return await service.get_summary(current.tenant_id, year)


@router.get("/payments", response_model=list[PaymentRecordResponse])
async def list_tenant_payments(current: AuthDep, db: DbDep) -> list[PaymentRecordResponse]:
    """List payment records across the tenant for finance read roles."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    service = ContributionService(db)
    return await service.list_tenant_payments(current.tenant_id)


@router.get("/annual-budget", response_model=AnnualBudgetResponse)
async def get_annual_budget(
    current: AuthDep,
    db: DbDep,
    year: int = Query(..., ge=2000, le=2100),
) -> AnnualBudgetResponse:
    """Return the annual treasury budget for finance and audit roles."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    return await ContributionService(db).get_annual_budget(current.tenant_id, year=year)


@router.post("/expenses", response_model=ExpenseRecordResponse, status_code=201)
async def create_expense(
    data: ExpenseRecordCreate,
    current: AuthDep,
    db: DbDep,
) -> ExpenseRecordResponse:
    """Record an association cash outflow, restricted to the treasurer."""
    require_capability(
        current,
        CAP_FINANCE_EXPENSES_WRITE,
        detail="Treasurer expense capability required",
    )
    return await ContributionService(db).create_expense(
        current.tenant_id, data, actor_user_id=current.user.id
    )


@router.get("/expenses", response_model=list[ExpenseRecordResponse])
async def list_expenses(
    current: AuthDep,
    db: DbDep,
    year: int | None = Query(None, ge=2000, le=2100),
    category: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[ExpenseRecordResponse]:
    """List the expense ledger for treasurer and auditor review."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    return await ContributionService(db).list_expenses(
        current.tenant_id,
        year=year,
        category=category,
        limit=limit,
        offset=offset,
    )


@router.get("/expense-categories", response_model=list[ExpenseCategoryResponse])
async def list_expense_categories(
    current: AuthDep,
    db: DbDep,
) -> list[ExpenseCategoryResponse]:
    """List the tenant expense categories, seeding the defaults on first use."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    return await ContributionService(db).list_expense_categories(current.tenant_id)


@router.post(
    "/expense-categories",
    response_model=ExpenseCategoryResponse,
    status_code=201,
)
async def create_expense_category(
    data: ExpenseCategoryCreate,
    current: AuthDep,
    db: DbDep,
) -> ExpenseCategoryResponse:
    """Add a tenant-specific expense category."""
    require_capability(
        current,
        CAP_FINANCE_EXPENSES_WRITE,
        detail="Treasurer expense capability required",
    )
    return await ContributionService(db).create_expense_category(
        current.tenant_id, data.name, actor_user_id=current.user.id
    )


@router.get("/expenses/export")
async def export_expenses(
    current: AuthDep,
    db: DbDep,
    year: int | None = Query(None, ge=2000, le=2100),
    export_format: Literal["csv", "xlsx"] = "csv",
) -> StreamingResponse:
    """Export the expense ledger for the treasurer, auditor or fiduciary."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    service = ContributionService(db)
    if export_format == "xlsx":
        content: bytes | str = await service.export_expenses_xlsx(
            current.tenant_id, year=year
        )
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"depenses-{year or 'all'}.xlsx"
    else:
        content = await service.export_expenses_csv(current.tenant_id, year=year)
        media_type = "text/csv"
        filename = f"depenses-{year or 'all'}.csv"
    await AuditService(db).record_event(
        tenant_id=current.tenant_id,
        actor_user_id=current.user.id,
        action="export",
        entity_type="expense_ledger",
        module_key="contributions",
        details={"format": export_format, "year": year},
    )
    await db.commit()
    return StreamingResponse(
        iter([content]),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/expenses/{expense_id}", response_model=ExpenseRecordResponse)
async def get_expense(
    expense_id: UUID,
    current: AuthDep,
    db: DbDep,
) -> ExpenseRecordResponse:
    """Return one expense with its attachment metadata."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    return await ContributionService(db).get_expense(current.tenant_id, expense_id)


@router.post(
    "/expenses/{expense_id}/attachment",
    response_model=ExpenseRecordResponse,
)
async def upload_expense_attachment(
    expense_id: UUID,
    current: AuthDep,
    db: DbDep,
    storage: ObjectStorageDep,
    file: UploadFile = File(...),
) -> ExpenseRecordResponse:
    """Attach the invoice or receipt supporting an expense."""
    require_capability(
        current,
        CAP_FINANCE_EXPENSES_WRITE,
        detail="Treasurer expense capability required",
    )
    data = await file.read()
    return await ContributionService(db).attach_expense_receipt(
        current.tenant_id,
        expense_id,
        file_name=file.filename or "receipt",
        content_type=file.content_type or "application/octet-stream",
        data=data,
        storage=storage,
        actor_user_id=current.user.id,
    )


@router.get("/expenses/{expense_id}/attachment")
async def download_expense_attachment(
    expense_id: UUID,
    current: AuthDep,
    db: DbDep,
    storage: ObjectStorageDep,
) -> StreamingResponse:
    """Download the supporting document attached to an expense."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    content, media_type, filename = await ContributionService(db).read_expense_receipt(
        current.tenant_id, expense_id, storage=storage
    )
    return StreamingResponse(
        iter([content]),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post(
    "/expenses/{expense_id}/reverse",
    response_model=ExpenseRecordResponse,
)
async def reverse_expense(
    expense_id: UUID,
    data: ExpenseReversalRequest,
    current: AuthDep,
    db: DbDep,
) -> ExpenseRecordResponse:
    """Reverse an expense without deleting its audit history."""
    require_capability(
        current,
        CAP_FINANCE_EXPENSES_WRITE,
        detail="Treasurer expense capability required",
    )
    return await ContributionService(db).reverse_expense(
        current.tenant_id,
        expense_id,
        reason=data.reason,
        actor_user_id=current.user.id,
    )


@router.post(
    "/expenses/{expense_id}/approve",
    response_model=ExpenseRecordResponse,
)
async def approve_expense(
    expense_id: UUID,
    current: AuthDep,
    db: DbDep,
) -> ExpenseRecordResponse:
    """Approve a recorded expense (president, vice-president or administrator)."""
    require_capability(
        current,
        CAP_FINANCE_EXPENSES_APPROVE,
        detail="Expense approval capability required",
    )
    return await ContributionService(db).approve_expense(
        current.tenant_id, expense_id, actor_user_id=current.user.id
    )


@router.post(
    "/expenses/{expense_id}/reject",
    response_model=ExpenseRecordResponse,
)
async def reject_expense(
    expense_id: UUID,
    data: ExpenseRejectRequest,
    current: AuthDep,
    db: DbDep,
) -> ExpenseRecordResponse:
    """Reject a recorded expense with a mandatory note."""
    require_capability(
        current,
        CAP_FINANCE_EXPENSES_APPROVE,
        detail="Expense approval capability required",
    )
    return await ContributionService(db).reject_expense(
        current.tenant_id,
        expense_id,
        note=data.note,
        actor_user_id=current.user.id,
    )


@router.get("/periods", response_model=list[FinancePeriodResponse])
async def list_finance_periods(
    current: AuthDep,
    db: DbDep,
) -> list[FinancePeriodResponse]:
    """List closed exercises and their audit metadata."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    return await ContributionService(db).list_finance_periods(current.tenant_id)


@router.get("/periods/{year}", response_model=FinancePeriodResponse)
async def get_finance_period(
    year: int,
    current: AuthDep,
    db: DbDep,
) -> FinancePeriodResponse:
    """Return the closing status of one exercise."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    return await ContributionService(db).get_finance_period(current.tenant_id, year)


@router.post("/periods/{year}/close", response_model=FinancePeriodResponse)
async def close_finance_period(
    year: int,
    current: AuthDep,
    db: DbDep,
) -> FinancePeriodResponse:
    """Close an exercise so no further financial write can alter it."""
    require_capability(
        current,
        CAP_FINANCE_WRITE,
        detail="Finance write capability required",
    )
    return await ContributionService(db).close_finance_period(
        current.tenant_id, year, actor_user_id=current.user.id
    )


@router.post("/periods/{year}/reopen", response_model=FinancePeriodResponse)
async def reopen_finance_period(
    year: int,
    data: FinancePeriodReopenRequest,
    current: AuthDep,
    db: DbDep,
) -> FinancePeriodResponse:
    """Reopen a closed exercise, reserved to tenant administration."""
    require_capability(
        current,
        CAP_TENANT_ADMINISTRATION,
        detail="Tenant administration capability required",
    )
    return await ContributionService(db).reopen_finance_period(
        current.tenant_id,
        year,
        reason=data.reason,
        actor_user_id=current.user.id,
    )


@router.get("/accounts", response_model=list[FinanceAccountResponse])
async def list_treasury_accounts(
    current: AuthDep,
    db: DbDep,
) -> list[FinanceAccountResponse]:
    """List the cash and bank accounts used by the treasury position."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    return await ContributionService(db).list_accounts(current.tenant_id)


@router.get("/treasury-position", response_model=TreasuryPositionResponse)
async def get_treasury_position(
    current: AuthDep,
    db: DbDep,
    year: int = Query(..., ge=2000, le=2100),
) -> TreasuryPositionResponse:
    """Return opening, movements and closing balance per treasury account."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    return await ContributionService(db).get_treasury_position(
        current.tenant_id, year
    )


@router.put(
    "/accounts/{account_id}/opening-balance/{year}",
    response_model=TreasuryPositionResponse,
)
async def set_opening_balance(
    account_id: UUID,
    year: int,
    data: OpeningBalanceUpdate,
    current: AuthDep,
    db: DbDep,
) -> TreasuryPositionResponse:
    """Set or correct the opening balance of an account for an exercise."""
    require_capability(
        current,
        CAP_FINANCE_WRITE,
        detail="Finance write capability required",
    )
    return await ContributionService(db).set_opening_balance(
        current.tenant_id,
        account_id,
        year,
        data.amount,
        actor_user_id=current.user.id,
    )


@router.get("/budget-plan", response_model=BudgetPlanResponse)
async def get_budget_plan(
    current: AuthDep,
    db: DbDep,
    year: int = Query(..., ge=2000, le=2100),
) -> BudgetPlanResponse:
    """Return the voted budget plan, including empty categories."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    return await ContributionService(db).get_budget_plan(current.tenant_id, year=year)


@router.put("/budget-plan/{year}", response_model=BudgetPlanResponse)
async def set_budget_plan(
    year: int,
    data: BudgetPlanUpdate,
    current: AuthDep,
    db: DbDep,
) -> BudgetPlanResponse:
    """Replace the voted budget plan of an exercise."""
    require_capability(
        current,
        CAP_FINANCE_WRITE,
        detail="Finance write capability required",
    )
    return await ContributionService(db).set_budget_plan(
        current.tenant_id, year, data, actor_user_id=current.user.id
    )


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
    """Import contribution records from a CSV file with replay protection."""
    require_capability(
        current,
        CAP_FINANCE_WRITE,
        detail="Finance write capability required",
    )
    content = await file.read()
    if not dry_run:
        await require_pre_operation_backup(
            db,
            tenant_id=current.tenant_id,
            actor_user_id=current.user.id,
            reason="contribution_csv_import",
        )
    service = ContributionService(db)
    return await service.import_csv(
        current.tenant_id, content, dry_run=dry_run, actor_user_id=current.user.id
    )


@router.get("/journal/export")
async def export_finance_journal(
    current: AuthDep,
    db: DbDep,
    year: int | None = Query(None, ge=2000, le=2100),
) -> StreamingResponse:
    """Export a chronological journal of every treasury movement."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    content = await ContributionService(db).export_finance_journal(
        current.tenant_id, year=year
    )
    await AuditService(db).record_event(
        tenant_id=current.tenant_id,
        actor_user_id=current.user.id,
        action="export",
        entity_type="finance_journal",
        module_key="contributions",
        details={"format": "csv", "year": year},
    )
    await db.commit()
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="journal-financier-{year or "all"}.csv"'
        },
    )


@router.get("/export")
async def export_contributions(current: AuthDep, db: DbDep) -> StreamingResponse:
    """Export contribution records as CSV for finance roles."""
    require_capability(
        current,
        CAP_FINANCE_TENANT_READ,
        detail="Finance read capability required",
    )
    service = ContributionService(db)
    csv_content = await service.export_csv(current.tenant_id)
    await AuditService(db).record_event(
        tenant_id=current.tenant_id,
        actor_user_id=current.user.id,
        action="export",
        entity_type="contribution_ledger",
        module_key="contributions",
        details={"format": "csv"},
    )
    await db.commit()
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


@router.get("/report/export/{export_format}")
async def export_member_finance_report(
    export_format: Literal["xlsx", "pdf", "whatsapp"],
    current: AuthDep,
    db: DbDep,
    year: int = Query(..., ge=2000, le=2100),
) -> StreamingResponse:
    """Export the member finance register for the treasurer and auditor roles."""
    if not (
        current.has_capability(CAP_FINANCE_AUDIT)
        or current.has_capability(CAP_FINANCE_WRITE)
        or current.has_capability(CAP_EXPORT_SENSITIVE)
    ):
        require_capability(
            current,
            CAP_FINANCE_AUDIT,
            detail="Finance audit capability required",
        )
    content, media_type, filename = await ContributionService(db).export_member_finance_report(
        current.tenant_id,
        year=year,
        export_format=export_format,
    )
    await AuditService(db).record_event(
        tenant_id=current.tenant_id,
        actor_user_id=current.user.id,
        action="export",
        entity_type="member_finance_report",
        module_key="contributions",
        details={"format": export_format, "year": year},
    )
    await db.commit()
    return StreamingResponse(
        iter([content]),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
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
async def delete_contribution(contribution_id: UUID, current: AuthDep, db: DbDep) -> None:
    """Delete a contribution record (admin only)."""
    require_capability(
        current,
        CAP_TENANT_ADMINISTRATION,
        detail="Tenant administration capability required",
    )
    await require_pre_operation_backup(
        db,
        tenant_id=current.tenant_id,
        actor_user_id=current.user.id,
        reason="contribution_delete",
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
    return await service.record_payment(current.tenant_id, data, actor_user_id=current.user.id)


@router.post(
    "/payments/{payment_id}/reverse",
    response_model=PaymentRecordResponse,
)
async def reverse_payment(
    payment_id: UUID,
    data: PaymentReversalRequest,
    current: AuthDep,
    db: DbDep,
) -> PaymentRecordResponse:
    """Reverse a recorded payment while keeping its audit history."""
    require_capability(
        current,
        CAP_FINANCE_WRITE,
        detail="Finance write capability required",
    )
    service = ContributionService(db)
    return await service.reverse_payment(
        current.tenant_id, payment_id, data, actor_user_id=current.user.id
    )


@router.get("/payments/{payment_id}/receipt.pdf")
async def download_payment_receipt(
    payment_id: UUID,
    current: AuthDep,
    db: DbDep,
) -> StreamingResponse:
    """Download the numbered receipt for a payment (own receipt or finance role)."""
    require_capability(
        current,
        CAP_FINANCE_SELF_READ,
        detail="Finance read capability required",
    )
    content, filename = await ContributionService(db).build_payment_receipt(
        current.tenant_id,
        payment_id,
        user_id=current.user.id,
        can_read_tenant=current.has_capability(CAP_FINANCE_TENANT_READ),
    )
    return StreamingResponse(
        iter([content]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
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
