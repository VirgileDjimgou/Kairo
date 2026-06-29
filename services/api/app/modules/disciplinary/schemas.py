from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from app.modules.disciplinary.models import DisciplinaryStatus


class DisciplinaryRecordCreate(BaseModel):
    membership_profile_id: UUID
    policy_record_id: UUID | None = None
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(None, max_length=10000)
    amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    currency: str = Field(default="EUR", max_length=3)
    status: DisciplinaryStatus = DisciplinaryStatus.open


class DisciplinaryRecordUpdate(BaseModel):
    policy_record_id: UUID | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=10000)
    amount: Decimal | None = Field(default=None, ge=0)
    currency: str | None = Field(None, max_length=3)
    status: DisciplinaryStatus | None = None


class DisciplinaryRecordResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    membership_profile_id: UUID
    membership_display_name: str | None = None
    policy_record_id: UUID | None
    policy_title: str | None = None
    title: str
    description: str | None
    amount: Decimal
    currency: str
    status: str
    recorded_by: UUID | None
    recorded_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("amount")
    def serialize_amount(self, value: Decimal) -> str:
        return str(value.quantize(Decimal("0.01")))
