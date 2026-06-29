from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from app.modules.contributions.models import ContributionStatus, PaymentMethod


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
