import io
from datetime import UTC, datetime
from decimal import Decimal
from typing import TypedDict
from uuid import UUID

from fastapi import HTTPException

from app.core.import_export import ImportResult, ImportRowError, generate_csv, parse_csv
from app.modules.contributions.models import (
    ContributionReceiptStatus,
    ContributionStatus,
    FinancialIncomeType,
)
from app.modules.finance.base import FinanceServiceBase
from app.modules.finance.ledger import as_decimal
from app.modules.membership.repository import MembershipRepository
from app.modules.tenancy.models import Tenant


class FinanceExportRow(TypedDict):
    member_code: str
    last_name: str
    first_name: str
    email: str
    phone: str
    membership_type: str
    membership_status: str
    expected: Decimal
    paid: Decimal
    contribution_balance: Decimal
    contribution_status: str


class ReportingMixin(FinanceServiceBase):
    async def import_csv(
        self,
        tenant_id: UUID,
        content: bytes,
        *,
        dry_run: bool = False,
        actor_user_id: UUID | None = None,
    ) -> ImportResult:
        rows = parse_csv(content)
        member_repo = MembershipRepository(self._db)
        errors: list[ImportRowError] = []
        success_count = 0
        skipped_count = 0
        tenant_currency = await self.tenant_currency(tenant_id)

        for i, row in enumerate(rows, start=2):
            row_errors: list[ImportRowError] = []

            member_code = row.get("member_code", "").strip()
            year_str = row.get("year", "").strip()
            expected_str = row.get("expected_amount", "0").strip()
            paid_str = row.get("paid_amount", "0").strip()
            currency = (row.get("currency") or tenant_currency).strip().upper()
            status_val = row.get("status", "pending").strip()

            if not member_code:
                row_errors.append(ImportRowError(row_number=i, column="member_code", message="member_code is required"))

            year: int | None = None
            try:
                year = int(year_str)
                if year < 2000 or year > 2100:
                    row_errors.append(ImportRowError(row_number=i, column="year", message="year must be between 2000 and 2100"))
            except (ValueError, TypeError):
                row_errors.append(ImportRowError(row_number=i, column="year", message="year must be an integer"))

            expected = Decimal("0")
            paid = Decimal("0")
            try:
                expected = Decimal(expected_str)
                if expected < 0:
                    row_errors.append(ImportRowError(row_number=i, column="expected_amount", message="expected_amount must be >= 0"))
            except Exception:
                row_errors.append(ImportRowError(row_number=i, column="expected_amount", message="expected_amount must be a valid number"))

            try:
                paid = Decimal(paid_str)
                if paid < 0:
                    row_errors.append(ImportRowError(row_number=i, column="paid_amount", message="paid_amount must be >= 0"))
            except Exception:
                row_errors.append(ImportRowError(row_number=i, column="paid_amount", message="paid_amount must be a valid number"))

            if status_val not in ("pending", "partial", "paid", "overdue", "waived"):
                row_errors.append(ImportRowError(row_number=i, column="status", message=f"Invalid status '{status_val}'"))

            if not row_errors:
                profile = await member_repo.get_by_member_code(tenant_id, member_code)
                if not profile:
                    row_errors.append(ImportRowError(
                        row_number=i, column="member_code", message=f"Unknown member_code '{member_code}'"
                    ))

            if row_errors:
                errors.extend(row_errors)
                continue

            assert profile is not None
            assert year is not None
            existing = await self._repo.get_contribution_by_member_year(
                tenant_id, profile.id, year
            )
            if existing is not None:
                # Replaying the same import must never duplicate the ledger.
                skipped_count += 1
                continue

            if dry_run:
                success_count += 1
                continue

            try:
                await self.ensure_year_open(tenant_id, year)
                resolved_currency = self.resolve_currency(currency, tenant_currency)
            except HTTPException as exc:
                row_errors.append(
                    ImportRowError(
                        row_number=i,
                        column="currency",
                        message=str(exc.detail),
                    )
                )
                errors.extend(row_errors)
                continue
            waived = status_val == "waived"
            record = await self._repo.create_contribution(
                tenant_id,
                {
                    "membership_profile_id": profile.id,
                    "year": year,
                    "expected_amount": expected,
                    "paid_amount": Decimal("0.00"),
                    "balance": expected,
                    "currency": resolved_currency,
                    "status": (
                        ContributionStatus.waived.value
                        if waived
                        else ContributionStatus.pending.value
                    ),
                },
            )
            if paid > 0 and not waived:
                # An imported balance is materialised as a payment so the ledger
                # and the annual budget agree on every imported amount.
                await self._repo.create_payment(
                    tenant_id,
                    {
                        "contribution_record_id": record.id,
                        "amount": paid,
                        "currency": resolved_currency,
                        "paid_at": datetime(year, 12, 31, 23, 59, 59, tzinfo=UTC),
                        "payment_method": "other",
                        "reference": "imported balance",
                        "recorded_by": actor_user_id,
                        "idempotency_key": f"import:{profile.id}:{year}",
                        "metadata_json": '{"source":"csv_import"}',
                    },
                )
            record = await self.sync_contribution_totals(tenant_id, record)
            await self._audit.record_event(
                tenant_id=tenant_id,
                actor_user_id=actor_user_id,
                action="import",
                entity_type="contribution_record",
                entity_id=record.id,
                module_key="contributions",
                details={"member_code": member_code, "year": year, "source": "csv_import"},
            )
            success_count += 1

        if not dry_run:
            await self._db.commit()

        return ImportResult(
            total_rows=len(rows),
            success_count=success_count,
            error_count=len(errors),
            skipped_count=skipped_count,
            errors=errors,
            dry_run=dry_run,
        )

    async def export_csv(self, tenant_id: UUID) -> str:
        records = await self._repo.list_by_tenant(tenant_id)
        rows = [
            {
                "membership_profile_id": str(r.membership_profile_id),
                "year": str(r.year),
                "expected_amount": str(r.expected_amount),
                "paid_amount": str(r.paid_amount),
                "balance": str(r.balance),
                "currency": r.currency,
                "status": r.status,
                "due_date": str(r.due_date) if r.due_date else "",
            }
            for r in records
        ]
        return generate_csv(rows)

    async def export_finance_report_csv(self, tenant_id: UUID) -> str:
        records = await self._repo.list_by_tenant(tenant_id)
        payments = await self._repo.list_payments_by_tenant(tenant_id)

        payment_count_by_contribution: dict[str, int] = {}
        for payment in payments:
            key = str(payment.contribution_record_id)
            payment_count_by_contribution[key] = payment_count_by_contribution.get(key, 0) + 1

        rows = [
            {
                "contribution_id": str(record.id),
                "membership_profile_id": str(record.membership_profile_id),
                "year": str(record.year),
                "expected_amount": str(record.expected_amount),
                "paid_amount": str(record.paid_amount),
                "balance": str(record.balance),
                "currency": record.currency,
                "status": record.status,
                "payment_count": str(payment_count_by_contribution.get(str(record.id), 0)),
                "due_date": str(record.due_date) if record.due_date else "",
            }
            for record in records
        ]
        return generate_csv(rows)

    async def export_finance_journal(
        self, tenant_id: UUID, *, year: int | None = None
    ) -> str:
        """Chronological audit pack of every treasury movement."""
        profiles = {
            profile.id: profile
            for profile in await MembershipRepository(self._db).list_by_tenant(tenant_id)
        }
        contributions = {
            contribution.id: contribution
            for contribution in await self._repo.list_by_tenant(tenant_id)
        }
        accounts = {
            account.id: account
            for account in await self._repo.list_finance_accounts(tenant_id)
        }
        rows: list[dict[str, str]] = []

        for payment in await self._repo.list_payments_by_tenant(tenant_id):
            if year is not None and payment.paid_at.year != year:
                continue
            contribution = contributions.get(payment.contribution_record_id)
            profile = (
                profiles.get(contribution.membership_profile_id)
                if contribution is not None
                else None
            )
            rows.append(
                {
                    "date": payment.paid_at.date().isoformat(),
                    "direction": "in",
                    "type": "payment",
                    "reference": payment.receipt_number or str(payment.id),
                    "counterparty": (
                        f"{profile.member_code} {profile.display_name}"
                        if profile is not None
                        else ""
                    ),
                    "description": payment.reference or "",
                    "amount": str(as_decimal(payment.amount)),
                    "currency": payment.currency,
                    "status": "reversed" if payment.reversed_at else "recorded",
                }
            )

        for expense in await self._repo.list_expenses_by_tenant(
            tenant_id, year=year, limit=None
        ):
            rows.append(
                {
                    "date": expense.spent_at.date().isoformat(),
                    "direction": "out",
                    "type": "expense",
                    "reference": expense.reference or str(expense.id),
                    "counterparty": expense.payee or "",
                    "description": expense.description,
                    "amount": str(as_decimal(expense.amount)),
                    "currency": expense.currency,
                    "status": "reversed" if expense.reversed_at else expense.status,
                }
            )

        accepted_statuses = {
            ContributionReceiptStatus.validated.value,
            ContributionReceiptStatus.partially_validated.value,
        }
        for receipt in await self._repo.list_receipt_declarations(tenant_id):
            if (
                receipt.status not in accepted_statuses
                or receipt.processed_at is None
                or receipt.income_type == FinancialIncomeType.membership_contribution.value
            ):
                continue
            if year is not None and receipt.received_at.year != year:
                continue
            rows.append(
                {
                    "date": receipt.received_at.date().isoformat(),
                    "direction": "in",
                    "type": "receipt_declaration",
                    "reference": str(receipt.id),
                    "counterparty": receipt.source_name or "",
                    "description": receipt.income_type,
                    "amount": str(as_decimal(receipt.processed_amount or receipt.amount)),
                    "currency": receipt.currency,
                    "status": receipt.status,
                }
            )

        if year is not None:
            for opening in await self._repo.list_opening_balances(tenant_id, year):
                account = accounts.get(opening.account_id)
                rows.append(
                    {
                        "date": f"{year}-01-01",
                        "direction": "opening",
                        "type": "opening_balance",
                        "reference": str(opening.account_id),
                        "counterparty": account.name if account is not None else "",
                        "description": "opening balance",
                        "amount": str(as_decimal(opening.amount)),
                        "currency": opening.currency,
                        "status": "recorded",
                    }
                )

        rows.sort(key=lambda row: (row["date"], row["type"]))
        return generate_csv(rows)

    async def export_member_finance_report(
        self,
        tenant_id: UUID,
        *,
        year: int,
        export_format: str,
    ) -> tuple[bytes | str, str, str]:
        """Build a share-safe, human-readable finance export for audit roles."""
        tenant = await self._db.get(Tenant, tenant_id)
        profiles = await MembershipRepository(self._db).list_by_tenant(tenant_id)
        contributions = await self._repo.list_by_tenant(tenant_id, year)
        contribution_totals: dict[UUID, dict[str, Decimal]] = {}
        for record in contributions:
            totals = contribution_totals.setdefault(
                record.membership_profile_id,
                {"expected": Decimal("0"), "paid": Decimal("0"), "balance": Decimal("0")},
            )
            totals["expected"] += record.expected_amount
            totals["paid"] += record.paid_amount
            totals["balance"] += record.balance

        rows: list[FinanceExportRow] = []
        for profile in sorted(profiles, key=lambda item: (item.last_name.lower(), item.first_name.lower())):
            totals = contribution_totals.get(
                profile.id,
                {"expected": Decimal("0"), "paid": Decimal("0"), "balance": Decimal("0")},
            )
            contribution_balance = totals["balance"]
            if totals["expected"] == Decimal("0"):
                contribution_status = "Non enregistrée"
            elif contribution_balance <= Decimal("0"):
                contribution_status = "Soldée"
            elif totals["paid"] > Decimal("0"):
                contribution_status = "Partiellement payée"
            else:
                contribution_status = "À payer"
            rows.append(
                {
                    "member_code": profile.member_code,
                    "last_name": profile.last_name,
                    "first_name": profile.first_name,
                    "email": profile.email or "",
                    "phone": profile.phone or "",
                    "membership_type": "Famille" if profile.membership_type == "family" else "Individuel",
                    "membership_status": profile.status,
                    "expected": totals["expected"],
                    "paid": totals["paid"],
                    "contribution_balance": contribution_balance,
                    "contribution_status": contribution_status,
                }
            )

        organization_name = tenant.name if tenant else "Association"
        currency = await self.tenant_currency(tenant_id)
        if export_format == "xlsx":
            return self._build_finance_xlsx(organization_name, year, rows, currency), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", f"rapport-financier-{year}.xlsx"
        if export_format == "pdf":
            return self._build_finance_pdf(organization_name, year, rows, currency), "application/pdf", f"rapport-financier-{year}.pdf"
        if export_format == "whatsapp":
            return self._build_whatsapp_summary(organization_name, year, rows, currency), "text/plain; charset=utf-8", f"rapport-financier-{year}-whatsapp.txt"
        raise ValueError(f"Unsupported finance export format: {export_format}")

    def _build_finance_xlsx(self, organization_name: str, year: int, rows: list[FinanceExportRow], currency: str) -> bytes:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font, PatternFill

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Cotisations"
        sheet.sheet_view.showGridLines = False
        headers = ["Matricule", "Nom", "Prénom", "E-mail", "Téléphone", "Adhésion", "Statut membre", "Cotisation attendue (EUR)", "Cotisation versée (EUR)", "Reste cotisation (EUR)", "Statut cotisation"]
        headers = [header.replace("EUR", currency) for header in headers]
        sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
        sheet["A1"] = f"{organization_name} - Rapport des cotisations {year}"
        sheet["A1"].font = Font(bold=True, size=16, color="FFFFFF")
        sheet["A1"].fill = PatternFill("solid", fgColor="1F4F8F")
        sheet["A1"].alignment = Alignment(horizontal="center")
        sheet.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(headers))
        sheet["A2"] = "Document de suivi financier confidentiel - trésorerie et commissariat aux comptes"
        sheet["A2"].font = Font(italic=True, color="5B677A")
        sheet["A2"].alignment = Alignment(horizontal="center")
        sheet.append([])
        sheet.append(headers)
        for row in rows:
            sheet.append([
                row["member_code"],
                row["last_name"],
                row["first_name"],
                row["email"] or None,
                row["phone"] or None,
                row["membership_type"],
                row["membership_status"],
                float(row["expected"]),
                float(row["paid"]),
                float(row["contribution_balance"]),
                row["contribution_status"],
            ])
        header_row = 4
        header_fill = PatternFill("solid", fgColor="DCE6F1")
        for cell in sheet[header_row]:
            cell.font = Font(bold=True, color="17365D")
            cell.fill = header_fill
            cell.alignment = Alignment(wrap_text=True, vertical="center")
        for column in (8, 9, 10):
            for cell in sheet.iter_cols(
                min_col=column,
                max_col=column,
                min_row=header_row + 1,
                max_row=header_row + len(rows),
            ):
                cell[0].number_format = f'#,##0.00 "{currency}"'
        widths = [18, 18, 18, 28, 18, 14, 16, 20, 20, 22, 20]
        for index, width in enumerate(widths, start=1):
            sheet.column_dimensions[chr(64 + index)].width = width
        sheet.freeze_panes = "A5"
        # Use a standard worksheet filter instead of an Excel Table.  Some mobile
        # spreadsheet readers repair the generated table XML and consequently make
        # the workbook appear corrupted, while a native filter is universally read.
        sheet.auto_filter.ref = f"A{header_row}:K{max(header_row, header_row + len(rows))}"
        output = io.BytesIO()
        workbook.save(output)
        return output.getvalue()

    def _build_finance_pdf(self, organization_name: str, year: int, rows: list[FinanceExportRow], currency: str) -> bytes:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

        output = io.BytesIO()
        document = SimpleDocTemplate(output, pagesize=landscape(A4), leftMargin=10 * mm, rightMargin=10 * mm, topMargin=12 * mm, bottomMargin=12 * mm)
        styles = getSampleStyleSheet()
        story = [Paragraph(f"<b>{organization_name}</b>", styles["Title"]), Paragraph(f"Rapport des cotisations - {year}", styles["Heading2"]), Paragraph("Document confidentiel destiné à la trésorerie et au commissariat aux comptes.", styles["BodyText"]), Spacer(1, 6 * mm)]
        header = ["Matricule", "Nom", "Prénom", "E-mail", "Téléphone", "Cotisation attendue", "Versée", "Reste", "Statut"]
        data = [header]
        for row in rows:
            data.append([str(row["member_code"]), str(row["last_name"]), str(row["first_name"]), str(row["email"]), str(row["phone"]), f"{row['expected']:.2f} {currency}", f"{row['paid']:.2f} {currency}", f"{row['contribution_balance']:.2f} {currency}", str(row["contribution_status"])])
        table = Table(data, repeatRows=1, colWidths=[30 * mm, 18 * mm, 18 * mm, 32 * mm, 21 * mm, 21 * mm, 19 * mm, 19 * mm, 24 * mm])
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4F8F")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 6), ("LEADING", (0, 0), (-1, -1), 7), ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D9E2EC")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F6F8FB")]), ("ALIGN", (5, 1), (-1, -1), "RIGHT")]))
        story.append(table)
        document.build(story)
        return output.getvalue()

    def _build_whatsapp_summary(self, organization_name: str, year: int, rows: list[FinanceExportRow], currency: str) -> str:
        lines = [
            f"*{organization_name}*",
            f"*Situation complète des cotisations - {year}*",
            f"{len(rows)} membre(s) inclus.",
            "",
        ]
        for index, row in enumerate(rows, start=1):
            lines.extend([f"*{index}. {row['first_name']} {row['last_name']}* ({row['member_code']})", f"Cotisation : {row['expected']:.2f} {currency} | Versée : {row['paid']:.2f} {currency} | Reste : {row['contribution_balance']:.2f} {currency}", f"Statut : {row['contribution_status']}", ""])
        return "\n".join(lines).strip() + "\n"
