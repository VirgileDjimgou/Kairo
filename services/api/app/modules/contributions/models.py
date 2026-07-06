import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import text as sql_text

from app.db.base import Base


class ContributionStatus(str, Enum):
    pending = "pending"
    partial = "partial"
    paid = "paid"
    overdue = "overdue"
    waived = "waived"


class PaymentMethod(str, Enum):
    cash = "cash"
    bank_transfer = "bank_transfer"
    card = "card"
    check = "check"
    other = "other"


class ReminderDeliveryStatus(str, Enum):
    sent = "sent"
    simulated = "simulated"
    failed = "failed"
    skipped = "skipped"


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
