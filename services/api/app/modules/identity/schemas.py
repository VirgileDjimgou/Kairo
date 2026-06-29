from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.modules.tenancy.schemas import BrandingConfig, ModuleToggles


# ── Auth Request DTOs ──────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)
    tenant_slug: str | None = Field(
        default=None,
        description="Slug of the tenant to log into. Uses first membership if omitted.",
    )


class SwitchTenantRequest(BaseModel):
    tenant_id: UUID


# ── Auth Response DTOs ─────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Seconds until the token expires")
    tenant_id: UUID
    user_id: UUID


class MfaRequiredResponse(BaseModel):
    mfa_required: bool = True
    mfa_token: str
    expires_in: int


class TenantMembershipResponse(BaseModel):
    tenant_id: UUID
    slug: str
    name: str
    roles: list[str]
    branding: BrandingConfig
    modules: ModuleToggles
    profile_type: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    display_name: str
    status: str
    tenant_id: UUID
    roles: list[str]
    last_login_at: datetime | None = None

    model_config = {"from_attributes": True}


class UserWithMembershipsResponse(UserResponse):
    memberships: list[TenantMembershipResponse]


class SwitchTenantResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    tenant_id: UUID
    user_id: UUID
    memberships: list[TenantMembershipResponse]


# ── Invitation DTOs ────────────────────────────────────────────────────────────

class InviteRequest(BaseModel):
    email: EmailStr
    role_code: str = Field(default="member", description="Role code to assign on acceptance")
    tenant_id: UUID


class InviteResponse(BaseModel):
    invitation_id: UUID
    email: str
    role_code: str
    status: str
    expires_at: datetime
    invite_token: str = Field(description="Raw token — share with the invitee securely")


class AcceptInviteRequest(BaseModel):
    token: str
    display_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class AcceptInviteResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    tenant_id: UUID
    user_id: UUID


class InvitationStatusResponse(BaseModel):
    id: UUID
    email: str
    role_code: str
    status: str
    expires_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Password Reset DTOs ────────────────────────────────────────────────────────

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str = "If the email exists, a reset token has been generated"
    reset_token: str | None = Field(
        default=None,
        description="Raw reset token (returned in dev; emailed in production)",
    )


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class ResetPasswordResponse(BaseModel):
    message: str = "Password has been reset successfully"


# ── MFA DTOs ───────────────────────────────────────────────────────────────────

class MfaEnrollResponse(BaseModel):
    secret: str
    uri: str
    qr_code_url: str = ""


class MfaVerifyRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6)


class MfaVerifyResponse(BaseModel):
    enabled: bool = True
    message: str = "MFA has been enabled"


class MfaCompleteLoginRequest(BaseModel):
    mfa_token: str
    code: str = Field(min_length=6, max_length=6)


class MfaLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    tenant_id: UUID
    user_id: UUID


# ── Token Refresh DTOs ─────────────────────────────────────────────────────────

class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
