from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

import re

from pydantic import BaseModel, EmailStr, Field, field_serializer, field_validator, model_validator

from app.modules.contributions.schemas import ContributionRecordResponse
from app.modules.membership.models import MembershipStatus, MembershipType


PHONE_PATTERN = re.compile(r"^\+[1-9]\d{7,14}$")
LOGIN_IDENTIFIER_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")


class MembershipProfileCreate(BaseModel):
    member_code: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)
    status: MembershipStatus = MembershipStatus.active
    membership_type: MembershipType | None = None
    provision_access: bool = False
    login_identifier: str | None = Field(None, min_length=3, max_length=64)
    temporary_password: str | None = Field(None, min_length=8, max_length=128)

    @field_validator("login_identifier")
    @classmethod
    def validate_login_identifier(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        normalized = value.strip().lower()
        if not LOGIN_IDENTIFIER_PATTERN.fullmatch(normalized):
            raise ValueError("Login identifier must use 3-64 letters, numbers, dots, hyphens, or underscores")
        return normalized

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        return re.sub(r"[\s()-]", "", value.strip())

    @model_validator(mode="after")
    def validate_direct_access(self) -> "MembershipProfileCreate":
        if not self.provision_access:
            return self
        if not self.temporary_password:
            raise ValueError("A temporary password is required when direct access is enabled")
        if not any((self.email, self.phone, self.login_identifier)):
            raise ValueError("Provide an email address, an international phone number, or a login identifier")
        if self.phone and not PHONE_PATTERN.fullmatch(self.phone.strip()):
            raise ValueError("Phone number must use international format, for example +49123456789")
        return self


class MembershipProfileUpdate(BaseModel):
    member_code: str | None = Field(None, min_length=1, max_length=50)
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    display_name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)
    status: MembershipStatus | None = None
    membership_type: MembershipType | None = None


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
    membership_type: str
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


class MemberStatementResponse(BaseModel):
    profile: MembershipProfileResponse
    summary: MemberBalanceResponse
    contributions: list[ContributionRecordResponse]
