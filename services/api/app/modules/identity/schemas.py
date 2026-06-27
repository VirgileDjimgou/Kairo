from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ── Request DTOs ───────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)
    tenant_slug: str | None = Field(
        default=None,
        description="Slug of the tenant to log into. Uses first membership if omitted.",
    )


# ── Response DTOs ──────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Seconds until the token expires")
    tenant_id: UUID
    user_id: UUID


class UserResponse(BaseModel):
    id: UUID
    email: str
    display_name: str
    status: str
    tenant_id: UUID
    roles: list[str]
    last_login_at: datetime | None = None

    model_config = {"from_attributes": True}
