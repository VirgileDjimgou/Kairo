import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import text as sql_text

from app.db.base import Base


class ContributionStatus(StrEnum):
    pending = "pending"
    partial = "partial"
    paid = "paid"
    overdue = "overdue"
    waived = "waived"


class PaymentMethod(StrEnum):
    cash = "cash"
    bank_transfer = "bank_transfer"
    card = "card"
    check = "check"
    other = "other"


class ReminderDeliveryStatus(StrEnum):
    sent = "sent"
    simulated = "simulated"
    failed = "failed"
    skipped = "skipped"


class ContributionReceiptStatus(StrEnum):
    draft = "draft"
    submitted = "submitted"
    clarification_requested = "clarification_requested"
    validated = "validated"
    partially_validated = "partially_validated"
    rejected = "rejected"
    cancelled = "cancelled"


class FinancialIncomeType(StrEnum):
    """Business meaning of a declared incoming payment."""

    membership_contribution = "membership_contribution"
    donation = "donation"
    sponsorship = "sponsorship"
    tournament_proceeds = "tournament_proceeds"
    other_income = "other_income"
    disciplinary_payment = "disciplinary_payment"


class CashHandoverStatus(StrEnum):
    pending_handover = "pending_handover"
    handover_reported = "handover_reported"
    received_in_treasury = "received_in_treasury"


class ExpenseCategory(StrEnum):
    """Treasury expense categories used by the annual budget."""

    sport_equipment = "sport_equipment"
    fuel_transport = "fuel_transport"
    tournament = "tournament"
    cultural_event = "cultural_event"
    administration = "administration"
    other = "other"


class ContributionRecord(Base):
    """
    Expected and paid contribution for a member in a specific year/period.

    Balance is calculated as expected_amount - paid_amount.
    """

    __tablename__ = "contribution_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    membership_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("membership_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    expected_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, server_default=sql_text("0.00"))
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, server_default=sql_text("0.00"))
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, server_default=sql_text("0.00"))
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="EUR")
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default=ContributionStatus.pending.value
    )
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(
        Text, nullable=False, server_default=sql_text("'{}'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sql_text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sql_text("CURRENT_TIMESTAMP")
    )

    def __repr__(self) -> str:
        return f"<ContributionRecord tenant={self.tenant_id} member={self.membership_profile_id} year={self.year} balance={self.balance}>"


class PaymentRecord(Base):
    """
    Individual payment toward a contribution record.
    """

    __tablename__ = "payment_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contribution_record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contribution_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="EUR")
    paid_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sql_text("CURRENT_TIMESTAMP")
    )
    payment_method: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default=PaymentMethod.other.value
    )
    reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    recorded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    metadata_json: Mapped[dict] = mapped_column(
        Text, nullable=False, server_default=sql_text("'{}'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sql_text("CURRENT_TIMESTAMP")
    )

    def __repr__(self) -> str:
        return f"<PaymentRecord tenant={self.tenant_id} contribution={self.contribution_record_id} amount={self.amount}>"


class ExpenseRecord(Base):
    """A treasury-only cash outflow recorded in the association budget."""

    __tablename__ = "expense_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="EUR")
    spent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    payee: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payment_method: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default=PaymentMethod.other.value
    )
    reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sql_text("CURRENT_TIMESTAMP")
    )

    def __repr__(self) -> str:
        return f"<ExpenseRecord tenant={self.tenant_id} category={self.category} amount={self.amount}>"


class ContributionReceiptDeclaration(Base):
    """A reported physical receipt that is not an official payment until processed."""

    __tablename__ = "contribution_receipt_declarations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    membership_profile_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("membership_profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    income_type: Mapped[str] = mapped_column(String(64), nullable=False, server_default=FinancialIncomeType.membership_contribution.value, index=True)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    disciplinary_record_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("disciplinary_records.id", ondelete="SET NULL"), nullable=True)
    declarant_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    declarant_role_code: Mapped[str] = mapped_column(String(64), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="EUR")
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False, server_default=PaymentMethod.cash.value)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    evidence_json: Mapped[str] = mapped_column(Text, nullable=False, server_default=sql_text("'{}'"))
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=ContributionReceiptStatus.draft.value, index=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    processed_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    processing_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    contribution_record_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("contribution_records.id", ondelete="SET NULL"), nullable=True)
    payment_record_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("payment_records.id", ondelete="SET NULL"), nullable=True)
    cash_handover_status: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    handover_reminder_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    handover_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    handover_reminder_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    handover_reminder_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    handover_reported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    handover_reported_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    handover_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    treasury_received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    treasury_received_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    treasury_receipt_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=sql_text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=sql_text("CURRENT_TIMESTAMP"))


class ContributionReminder(Base):
    """Reminder dispatch history for outstanding contribution follow-up."""

    __tablename__ = "contribution_reminders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contribution_record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contribution_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    membership_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("membership_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    member_display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    member_code: Mapped[str] = mapped_column(String(50), nullable=False)
    balance_snapshot: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default=sql_text("0.00")
    )
    due_date_snapshot: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    channel: Mapped[str] = mapped_column(String(50), nullable=False, server_default="email")
    delivery_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=ReminderDeliveryStatus.simulated.value,
    )
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    provider_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    reminded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    metadata_json: Mapped[dict] = mapped_column(
        Text, nullable=False, server_default=sql_text("'{}'")
    )
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sql_text("CURRENT_TIMESTAMP")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sql_text("CURRENT_TIMESTAMP")
    )

    def __repr__(self) -> str:
        return (
            f"<ContributionReminder tenant={self.tenant_id} contribution={self.contribution_record_id} "
            f"status={self.delivery_status}>"
        )
