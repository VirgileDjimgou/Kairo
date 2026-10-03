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

HEX_COLOR_PATTERN = r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$"
SAFE_ASSET_PATTERN = r"^(?:|https?://[^\s]+|/[^\s]*)$"
HOSTNAME_PATTERN = r"^(?:|[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)*)$"


class ModuleToggles(BaseModel):
    membership: bool = True
    contributions: bool = True
    policies: bool = True
    disciplinary: bool = True
    events: bool = True
    announcements: bool = True
    chat: bool = True
    notifications: bool = True


class TenantBranding(BaseModel):
    """Canonical white-label identity for one tenant.

    Platform identity and tenant identity are separate: every field has a safe
    Kairo default, a tenant overrides only what it needs, and no business logic
    may depend on a branding value. Assets accept only https(s) URLs or
    site-relative paths so a branding value can never inject an unsafe URI.
    """

    display_name: str = Field(default="Kairo", max_length=120)
    short_name: str = Field(default="Kairo", max_length=40)
    legal_name: str = Field(default="", max_length=200)
    logo_url: str = Field(default="", max_length=2048, pattern=SAFE_ASSET_PATTERN)
    logo_dark_url: str = Field(default="", max_length=2048, pattern=SAFE_ASSET_PATTERN)
    favicon_url: str = Field(default="", max_length=2048, pattern=SAFE_ASSET_PATTERN)
    icon_192_url: str = Field(default="", max_length=2048, pattern=SAFE_ASSET_PATTERN)
    icon_512_url: str = Field(default="", max_length=2048, pattern=SAFE_ASSET_PATTERN)
    maskable_icon_url: str = Field(default="", max_length=2048, pattern=SAFE_ASSET_PATTERN)
    primary_color: str = Field(default="#1f4f8f", pattern=HEX_COLOR_PATTERN)
    secondary_color: str = Field(default="#2f6f55", pattern=HEX_COLOR_PATTERN)
    background_color: str = Field(default="#f8f9fb", pattern=HEX_COLOR_PATTERN)
    theme_color: str = Field(default="#1a3f6b", pattern=HEX_COLOR_PATTERN)
    notification_name: str = Field(default="Kairo", max_length=80)
    support_name: str = Field(default="Kairo Support", max_length=120)
    support_email: str = Field(default="", max_length=254)
    custom_domain: str = Field(default="", max_length=253, pattern=HOSTNAME_PATTERN)


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
    branding: TenantBranding
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
    branding: TenantBranding | None = None
    modules: ModuleToggles | None = None
    operations: RecoveryEvidenceConfig | None = None


class RoleBundleCreate(BaseModel):
    """A tenant-specific role bundle over canonical capabilities."""

    code: str = Field(min_length=3, max_length=100, pattern=r"^[a-z][a-z0-9_]*$")
    name: str = Field(min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    capabilities: list[str] = Field(min_length=1, max_length=100)
