from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TenantResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    type: str
    status: str
    default_language: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TenantUserResponse(BaseModel):
    tenant_id: UUID
    user_id: UUID
    membership_status: str
    profile_type: str
    joined_at: datetime

    model_config = {"from_attributes": True}


class RoleResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    code: str
    name: str
    description: str | None
    is_system_role: bool

    model_config = {"from_attributes": True}
