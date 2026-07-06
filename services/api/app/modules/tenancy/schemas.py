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
    is_canonical: bool = False
    capabilities: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# ── Tenant Settings ──────────────────────────────────────────────────────────


class ModuleToggles(BaseModel):
    membership: bool = True
    contributions: bool = True
    policies: bool = True
    disciplinary: bool = True
    events: bool = True
    announcements: bool = True
    chat: bool = True
    notifications: bool = True


class BrandingConfig(BaseModel):
    primary_color: str = "#1f4f8f"
    logo_url: str = ""


class RecoveryEvidenceConfig(BaseModel):
    last_backup_at: datetime | None = None
    last_backup_status: str = "unknown"
    last_backup_reference: str = ""
    last_restore_drill_at: datetime | None = None
    last_restore_drill_status: str = "unknown"
    alert_posture: str = "unknown"
    alert_contacts_configured: bool = False
    backup_retention_days: int | None = None
    notes: str = ""


class RecoveryEvidenceResponse(RecoveryEvidenceConfig):
    backup_is_stale: bool
    restore_drill_is_stale: bool
    alert_is_healthy: bool
    overall_status: str
    status_message: str


class TenantSettingsResponse(BaseModel):
    tenant_id: UUID
    name: str
    slug: str
    default_language: str
    branding: BrandingConfig
    modules: ModuleToggles
    operations: RecoveryEvidenceResponse = Field(default_factory=lambda: RecoveryEvidenceResponse(
        backup_is_stale=True,
        restore_drill_is_stale=True,
        alert_is_healthy=False,
        overall_status="warning",
        status_message="No recovery evidence has been recorded yet.",
    ))
    updated_at: datetime


class TenantSettingsUpdate(BaseModel):
    name: str | None = None
    default_language: str | None = None
    branding: BrandingConfig | None = None
    modules: ModuleToggles | None = None
    operations: RecoveryEvidenceConfig | None = None
