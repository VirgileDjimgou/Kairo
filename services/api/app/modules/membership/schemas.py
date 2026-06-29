from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_serializer

from app.modules.membership.models import MembershipStatus


class MembershipProfileCreate(BaseModel):
    member_code: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)
    status: MembershipStatus = MembershipStatus.active


class MembershipProfileUpdate(BaseModel):
    member_code: str | None = Field(None, min_length=1, max_length=50)
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    display_name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)
    status: MembershipStatus | None = None


class MembershipProfileResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    user_id: UUID | None
    member_code: str
    first_name: str
    last_name: str
    display_name: str
    email: str | None
    phone: str | None
    status: str
    joined_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MemberBalanceResponse(BaseModel):
    profile: MembershipProfileResponse
    total_expected: Decimal = Decimal("0.00")
    total_paid: Decimal = Decimal("0.00")
    total_balance: Decimal = Decimal("0.00")
    contribution_count: int = 0

    model_config = {"from_attributes": True}

    @field_serializer("total_expected", "total_paid", "total_balance")
    def serialize_decimal(self, value: Decimal) -> str:
        return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
