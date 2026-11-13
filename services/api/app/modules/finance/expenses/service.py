import io
import uuid as uuid_module
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.import_export import generate_csv
from app.modules.contributions.schemas import ExpenseRecordCreate, ExpenseRecordResponse
from app.modules.domain_events.events import AGGREGATE_EXPENSE, EXPENSE_RECORDED
from app.modules.finance.base import FinanceServiceBase
from app.providers.object_storage.base import ObjectStorageProvider

ALLOWED_RECEIPT_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
}


class ExpensesMixin(FinanceServiceBase):
    async def create_expense(
        self,
        tenant_id: UUID,
        data: ExpenseRecordCreate,
        *,
        actor_user_id: UUID,
    ) -> ExpenseRecordResponse:
        payload = data.model_dump()
        tenant_currency = await self.tenant_currency(tenant_id)
        requested_currency = (
            payload.get("currency")
            if "currency" in getattr(data, "model_fields_set", set())
            else None
        )
        payload["currency"] = self.resolve_currency(requested_currency, tenant_currency)
        payload["spent_at"] = payload["spent_at"] or datetime.now(UTC)
        await self.ensure_year_open(tenant_id, payload["spent_at"].year)
        await self.validate_expense_category(tenant_id, str(payload["category"]))
        payload["account_id"] = await self.resolve_account_id(
            tenant_id, payload.get("account_id"), payload["payment_method"]
        )
        payload["created_by"] = actor_user_id
        payload["status"] = "recorded"
        record = await self._repo.create_expense(tenant_id, payload)
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="expense_recorded",
            entity_type="expense_record",
            entity_id=record.id,
            module_key="contributions",
            details={
                "category": record.category,
                "amount": str(record.amount),
                "currency": record.currency,
                "payee": record.payee,
                "description": record.description,
            },
        )
        await self._events.publish(
            tenant_id=tenant_id,
            event_type=EXPENSE_RECORDED,
            aggregate_type=AGGREGATE_EXPENSE,
            aggregate_id=record.id,
            deduplication_key=f"expense-recorded:{record.id}",
            actor_user_id=actor_user_id,
            payload={
                "category": record.category,
                "amount": str(record.amount),
                "currency": record.currency,
            },
        )
        await self._db.commit()
        return ExpenseRecordResponse.model_validate(record)

    async def list_expenses(
        self,
        tenant_id: UUID,
        *,
        year: int | None = None,
        category: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ExpenseRecordResponse]:
        records = await self._repo.list_expenses_by_tenant(
            tenant_id,
            year=year,
            category=category,
            limit=limit,
            offset=offset,
        )
        return [ExpenseRecordResponse.model_validate(record) for record in records]

    async def get_expense(
        self, tenant_id: UUID, expense_id: UUID
    ) -> ExpenseRecordResponse:
        record = await self._repo.get_expense(tenant_id, expense_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found",
            )
        return ExpenseRecordResponse.model_validate(record)

    async def export_expenses_csv(
        self, tenant_id: UUID, *, year: int | None = None
    ) -> str:
        records = await self._repo.list_expenses_by_tenant(
            tenant_id, year=year, limit=None
        )
        rows = [
            {
                "expense_id": str(record.id),
                "category": record.category,
                "amount": str(record.amount),
                "currency": record.currency,
                "spent_at": record.spent_at.isoformat(),
                "description": record.description,
                "payee": record.payee or "",
                "payment_method": record.payment_method,
                "reference": record.reference or "",
                "attachment_file_name": record.attachment_file_name or "",
                "status": "reversed" if record.reversed_at else record.status,
                "reversed_at": (
                    record.reversed_at.isoformat() if record.reversed_at else ""
                ),
                "reversal_reason": record.reversal_reason or "",
            }
            for record in records
        ]
        return generate_csv(rows)

    async def export_expenses_xlsx(
        self, tenant_id: UUID, *, year: int | None = None
    ) -> bytes:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font, PatternFill

        records = await self._repo.list_expenses_by_tenant(
            tenant_id, year=year, limit=None
        )
        currency = await self.tenant_currency(tenant_id)
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Depenses"
        sheet.sheet_view.showGridLines = False
        headers = [
            "Date",
            "Categorie",
            "Montant",
            "Devise",
            "Beneficiaire",
            "Description",
            "Moyen",
            "Reference",
            "Justificatif",
            "Statut",
            "Motif",
        ]
        sheet.append(headers)
        for cell in sheet[1]:
            cell.font = Font(bold=True, color="17365D")
            cell.fill = PatternFill("solid", fgColor="DCE6F1")
            cell.alignment = Alignment(wrap_text=True)
        for record in records:
            sheet.append(
                [
                    record.spent_at.date().isoformat(),
                    record.category,
                    float(record.amount),
                    record.currency,
                    record.payee or "",
                    record.description,
                    record.payment_method,
                    record.reference or "",
                    record.attachment_file_name or "",
                    "reversed" if record.reversed_at else record.status,
                    record.reversal_reason or "",
                ]
            )
        for row in sheet.iter_rows(min_row=2, min_col=3, max_col=3):
            row[0].number_format = f'#,##0.00 "{currency}"'
        widths = [14, 18, 14, 8, 24, 40, 16, 20, 28, 14, 28]
        for index, width in enumerate(widths, start=1):
            sheet.column_dimensions[chr(64 + index)].width = width
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = f"A1:K{max(1, sheet.max_row)}"
        output = io.BytesIO()
        workbook.save(output)
        return output.getvalue()

    async def attach_expense_receipt(
        self,
        tenant_id: UUID,
        expense_id: UUID,
        *,
        file_name: str,
        content_type: str,
        data: bytes,
        storage: ObjectStorageProvider,
        actor_user_id: UUID,
    ) -> ExpenseRecordResponse:
        record = await self._repo.get_expense(tenant_id, expense_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found",
            )
        await self.ensure_year_open(tenant_id, record.spent_at.year)

        normalized_type = (content_type or "").split(";")[0].strip().lower()
        if normalized_type not in ALLOWED_RECEIPT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Receipt must be a PDF, JPEG or PNG file",
            )
        if not data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Receipt file is empty",
            )
        if len(data) > settings.max_upload_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Receipt exceeds {settings.max_upload_mb} MB",
            )

        extension = Path(file_name or "").suffix.lower()
        if extension not in ALLOWED_RECEIPT_TYPES.values():
            extension = ALLOWED_RECEIPT_TYPES[normalized_type]
        bucket = settings.minio_bucket_documents
        object_key = (
            f"finance/{tenant_id}/expenses/{expense_id}/"
            f"{uuid_module.uuid4().hex}{extension}"
        )
        storage.ensure_bucket(bucket)
        storage.upload_bytes(bucket, object_key, data, normalized_type)

        updated = await self._repo.update_expense_attachment(
            tenant_id,
            expense_id,
            {
                "attachment_bucket": bucket,
                "attachment_key": object_key,
                "attachment_file_name": file_name or f"receipt{extension}",
                "attachment_content_type": normalized_type,
                "attachment_size_bytes": len(data),
                "attachment_uploaded_at": datetime.now(UTC),
                "attachment_uploaded_by": actor_user_id,
            },
        )
        assert updated is not None
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="expense_receipt_attached",
            entity_type="expense_record",
            entity_id=expense_id,
            module_key="contributions",
            details={
                "file_name": updated.attachment_file_name,
                "content_type": updated.attachment_content_type,
                "size_bytes": updated.attachment_size_bytes,
            },
        )
        await self._db.commit()
        return ExpenseRecordResponse.model_validate(updated)

    async def reverse_expense(
        self,
        tenant_id: UUID,
        expense_id: UUID,
        *,
        reason: str,
        actor_user_id: UUID,
    ) -> ExpenseRecordResponse:
        """Reverse an expense while keeping the original row in the ledger."""
        record = await self._repo.get_expense(tenant_id, expense_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found",
            )
        if record.reversed_at is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Expense is already reversed",
            )
        await self.ensure_year_open(tenant_id, record.spent_at.year)

        updated = await self._repo.update_expense(
            tenant_id,
            expense_id,
            {
                "reversed_at": datetime.now(UTC),
                "reversed_by": actor_user_id,
                "reversal_reason": reason,
            },
        )
        assert updated is not None
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="expense_reversed",
            entity_type="expense_record",
            entity_id=expense_id,
            module_key="contributions",
            details={
                "category": updated.category,
                "amount": str(updated.amount),
                "currency": updated.currency,
                "reason": reason,
            },
        )
        await self._db.commit()
        return ExpenseRecordResponse.model_validate(updated)

    async def approve_expense(
        self,
        tenant_id: UUID,
        expense_id: UUID,
        *,
        actor_user_id: UUID,
    ) -> ExpenseRecordResponse:
        record = await self._repo.get_expense(tenant_id, expense_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found",
            )
        if record.reversed_at is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A reversed expense cannot be approved",
            )
        if record.status != "recorded":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Expense is already {record.status}",
            )
        await self.ensure_year_open(tenant_id, record.spent_at.year)
        updated = await self._repo.update_expense(
            tenant_id,
            expense_id,
            {
                "status": "approved",
                "approved_at": datetime.now(UTC),
                "approved_by": actor_user_id,
                "approval_note": None,
            },
        )
        assert updated is not None
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="expense_approved",
            entity_type="expense_record",
            entity_id=expense_id,
            module_key="contributions",
            details={
                "category": updated.category,
                "amount": str(updated.amount),
                "currency": updated.currency,
            },
        )
        await self._db.commit()
        return ExpenseRecordResponse.model_validate(updated)

    async def reject_expense(
        self,
        tenant_id: UUID,
        expense_id: UUID,
        *,
        note: str,
        actor_user_id: UUID,
    ) -> ExpenseRecordResponse:
        record = await self._repo.get_expense(tenant_id, expense_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found",
            )
        if record.reversed_at is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A reversed expense cannot be rejected",
            )
        if record.status != "recorded":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Expense is already {record.status}",
            )
        await self.ensure_year_open(tenant_id, record.spent_at.year)
        updated = await self._repo.update_expense(
            tenant_id,
            expense_id,
            {
                "status": "rejected",
                "approved_at": datetime.now(UTC),
                "approved_by": actor_user_id,
                "approval_note": note,
            },
        )
        assert updated is not None
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="expense_rejected",
            entity_type="expense_record",
            entity_id=expense_id,
            module_key="contributions",
            details={
                "category": updated.category,
                "amount": str(updated.amount),
                "currency": updated.currency,
                "reason": note,
            },
        )
        await self._db.commit()
        return ExpenseRecordResponse.model_validate(updated)

    async def read_expense_receipt(
        self,
        tenant_id: UUID,
        expense_id: UUID,
        *,
        storage: ObjectStorageProvider,
    ) -> tuple[bytes, str, str]:
        record = await self._repo.get_expense(tenant_id, expense_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found",
            )
        if not record.attachment_bucket or not record.attachment_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No receipt attached to this expense",
            )
        data = storage.download_bytes(record.attachment_bucket, record.attachment_key)
        return (
            data,
            record.attachment_content_type or "application/octet-stream",
            record.attachment_file_name or "receipt",
        )
