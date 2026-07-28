from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from app.modules.contributions.models import (
    ContributionReceiptStatus,
    ContributionStatus,
    PaymentMethod,
    ReminderDeliveryStatus,
)


class ContributionRecordCreate(BaseModel):
    membership_profile_id: UUID
    year: int = Field(..., ge=2000, le=2100)
    expected_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    paid_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    currency: str = Field(default="EUR", max_length=3)
    status: ContributionStatus = ContributionStatus.pending
    due_date: datetime | None = None


class ContributionRecordUpdate(BaseModel):
    expected_amount: Decimal | None = Field(None, ge=0)
    paid_amount: Decimal | None = Field(None, ge=0)
    currency: str | None = Field(None, max_length=3)
    status: ContributionStatus | None = None
    due_date: datetime | None = None


class ContributionRecordResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    membership_profile_id: UUID
    year: int
    expected_amount: Decimal
    paid_amount: Decimal
    balance: Decimal
    currency: str
    status: str
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("expected_amount", "paid_amount", "balance")
    def serialize_decimal(self, value: Decimal) -> str:
        return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


class PaymentRecordCreate(BaseModel):
    contribution_record_id: UUID
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="EUR", max_length=3)
    paid_at: datetime | None = None
    payment_method: PaymentMethod = PaymentMethod.other
    reference: str | None = Field(None, max_length=255)


class PaymentRecordResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    contribution_record_id: UUID
    amount: Decimal
    currency: str
    paid_at: datetime
    payment_method: str
    reference: str | None
    recorded_by: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("amount")
    def serialize_decimal(self, value: Decimal) -> str:
        return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


class ContributionReceiptDeclarationCreate(BaseModel):
    membership_profile_id: UUID
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    received_at: datetime | None = None
    payment_method: PaymentMethod = PaymentMethod.cash
    note: str | None = Field(default=None, max_length=2000)
    reference: str | None = Field(default=None, max_length=255)
    evidence_json: str = Field(default="{}", max_length=10000)


class ContributionReceiptMemberOption(BaseModel):
    """Read-only member identity available to authorized receipt declarants."""

    id: UUID
    display_name: str
    member_code: str
    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    membership_type: str
    status: str
    joined_at: datetime


class ContributionReceiptDeclarationUpdate(BaseModel):
    membership_profile_id: UUID | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    received_at: datetime | None = None
    payment_method: PaymentMethod | None = None
    note: str | None = Field(default=None, max_length=2000)
    reference: str | None = Field(default=None, max_length=255)
    evidence_json: str | None = Field(default=None, max_length=10000)


class ContributionReceiptDeclarationProcess(BaseModel):
    action: Literal["validated", "partially_validated", "rejected", "clarification_requested", "cancelled"]
    contribution_record_id: UUID | None = None
    processed_amount: Decimal | None = Field(default=None, gt=0)
    note: str | None = Field(default=None, max_length=2000)


class ContributionReceiptDeclarationResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    membership_profile_id: UUID
    declarant_user_id: UUID
    declarant_role_code: str
    amount: Decimal
    currency: str
    received_at: datetime
    payment_method: str
    note: str | None
    reference: str | None
    evidence_json: str
    status: ContributionReceiptStatus
    submitted_at: datetime | None
    processed_at: datetime | None
    processed_by_user_id: UUID | None
    processed_amount: Decimal | None
    processing_note: str | None
    contribution_record_id: UUID | None
    payment_record_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("amount", "processed_amount")
    def serialize_receipt_decimal(self, value: Decimal | None) -> str | None:
        return None if value is None else str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


class ContributionReminderSendRequest(BaseModel):
    channel: Literal["email"] = "email"


class ContributionReminderBatchRequest(BaseModel):
    channel: Literal["email"] = "email"
    year: int | None = Field(default=None, ge=2000, le=2100)
    status: ContributionStatus | None = None
    due_scope: Literal["all_outstanding", "overdue", "due_soon"] = "overdue"
    limit: int = Field(default=25, ge=1, le=100)


class ContributionReminderResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    contribution_record_id: UUID
    membership_profile_id: UUID
    member_display_name: str
    member_code: str
    balance_snapshot: Decimal
    due_date_snapshot: datetime | None
    channel: str
    delivery_status: ReminderDeliveryStatus
    recipient: str
    subject: str
    body: str
    provider_message: str | None
    reminded_by: UUID | None
    sent_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("balance_snapshot")
    def serialize_balance(self, value: Decimal) -> str:
        return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


class ContributionReminderBatchResponse(BaseModel):
    attempted_count: int
    reminder_count: int
    reminders: list[ContributionReminderResponse]
