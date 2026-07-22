import json
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.capabilities import (
    CAP_ROLE_CATALOG_READ,
    CAP_TENANT_SETTINGS_WRITE,
    capabilities_for_roles,
    has_capability,
)
from app.modules.audit.service import AuditService
from app.modules.tenancy.module_toggles import default_module_toggles, parse_module_toggles
from app.modules.tenancy.repository import TenancyRepository
from app.modules.tenancy.role_catalog import is_canonical_role
from app.modules.tenancy.schemas import (
    BrandingConfig,
    ModuleToggles,
    RecoveryEvidenceConfig,
    RecoveryEvidenceResponse,
    RoleResponse,
    TenantResponse,
    TenantSettingsResponse,
    TenantSettingsUpdate,
)

_BACKUP_STALE_AFTER_DAYS = 7
_RESTORE_DRILL_STALE_AFTER_DAYS = 90


class TenancyService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = TenancyRepository(db)
        self._audit = AuditService(db)

    async def get_user_tenants(self, user_id: UUID) -> list[TenantResponse]:
        memberships = await self._repo.get_user_active_memberships(user_id)
        tenants = []
        for membership in memberships:
            tenant = await self._repo.get_tenant_by_id(membership.tenant_id)
            if tenant:
                tenants.append(TenantResponse.model_validate(tenant))
        return tenants

    async def get_tenant(
        self, tenant_id: UUID, requesting_user_id: UUID
    ) -> TenantResponse:
        membership = await self._repo.get_tenant_user(tenant_id, requesting_user_id)
        if not membership or membership.membership_status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organization",
            )
        tenant = await self._repo.get_tenant_by_id(tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        return TenantResponse.model_validate(tenant)

    async def get_tenant_roles(
        self, tenant_id: UUID, requesting_user_id: UUID
    ) -> list[RoleResponse]:
        membership = await self._repo.get_tenant_user(tenant_id, requesting_user_id)
        if not membership or membership.membership_status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organization",
            )

        await self._repo.ensure_canonical_role_catalog(tenant_id)
        role_codes = await self._repo.get_user_role_codes(tenant_id, requesting_user_id)
        if not has_capability(role_codes, CAP_ROLE_CATALOG_READ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only authorized tenant administrators can view tenant roles",
            )

        roles = await self._repo.get_roles_for_tenant(tenant_id)
        return [
            RoleResponse(
                id=role.id,
                tenant_id=role.tenant_id,
                code=role.code,
                name=role.name,
                description=role.description,
                is_system_role=role.is_system_role,
                is_canonical=is_canonical_role(role.code),
                capabilities=list(capabilities_for_roles([role.code])),
            )
            for role in roles
        ]

    # ── Tenant Settings ─────────────────────────────────────────────────────

    async def get_tenant_settings(
        self, tenant_id: UUID, requesting_user_id: UUID
    ) -> TenantSettingsResponse:
        membership = await self._repo.get_tenant_user(tenant_id, requesting_user_id)
        if not membership or membership.membership_status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organization",
            )
        tenant = await self._repo.get_tenant_by_id(tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        branding_raw: dict[str, Any] = {}
        if isinstance(tenant.branding_json, str) and tenant.branding_json.strip():
            try:
                branding_raw = json.loads(tenant.branding_json)
            except json.JSONDecodeError:
                branding_raw = {}

        settings_raw: dict[str, Any] = {}
        if isinstance(tenant.settings_json, str) and tenant.settings_json.strip():
            try:
                settings_raw = json.loads(tenant.settings_json)
            except json.JSONDecodeError:
                settings_raw = {}

        module_toggles = parse_module_toggles(settings_raw)
        branding = BrandingConfig(**branding_raw) if branding_raw else BrandingConfig()
        operations = self._build_recovery_evidence(settings_raw)

        return TenantSettingsResponse(
            tenant_id=tenant.id,
            name=tenant.name,
            slug=tenant.slug,
            default_language=tenant.default_language,
            branding=branding,
            modules=ModuleToggles(**module_toggles),
            operations=operations,
            updated_at=tenant.updated_at,
        )

    async def update_tenant_settings(
        self, tenant_id: UUID, requesting_user_id: UUID, settings: TenantSettingsUpdate
    ) -> TenantSettingsResponse:
        membership = await self._repo.get_tenant_user(tenant_id, requesting_user_id)
        if not membership or membership.membership_status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organization",
            )
        tenant = await self._repo.get_tenant_by_id(tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        role_codes = await self._repo.get_user_role_codes(tenant_id, requesting_user_id)
        if not has_capability(role_codes, CAP_TENANT_SETTINGS_WRITE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only authorized tenant administrators can update tenant settings",
            )

        name = settings.name
        default_language = settings.default_language

        current_branding_raw = {}
        if isinstance(tenant.branding_json, str) and tenant.branding_json.strip():
            try:
                current_branding_raw = json.loads(tenant.branding_json)
            except json.JSONDecodeError:
                current_branding_raw = {}

        current_settings_raw = {}
        if isinstance(tenant.settings_json, str) and tenant.settings_json.strip():
            try:
                current_settings_raw = json.loads(tenant.settings_json)
            except json.JSONDecodeError:
                current_settings_raw = {}

        if settings.branding is not None:
            current_branding_raw.update(settings.branding.model_dump(exclude_unset=True))
        if settings.modules is not None:
            current_settings_raw["modules"] = {
                **default_module_toggles(),
                **settings.modules.model_dump(exclude_unset=True),
            }
        if settings.operations is not None:
            operations_raw = current_settings_raw.get("operations", {})
            if not isinstance(operations_raw, dict):
                operations_raw = {}
            operations_raw["recovery"] = settings.operations.model_dump(mode="json", exclude_unset=True)
            current_settings_raw["operations"] = operations_raw

        branding_json = json.dumps(current_branding_raw)
        settings_json = json.dumps(current_settings_raw)

        updated = await self._repo.update_tenant(
            tenant_id,
            name=name,
            default_language=default_language,
            branding_json=branding_json,
            settings_json=settings_json,
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update tenant settings",
            )

        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=requesting_user_id,
            action="settings_updated",
            entity_type="tenant_settings",
            entity_id=tenant_id,
            module_key="tenancy",
            details={
                "name": updated.name,
                "default_language": updated.default_language,
                "branding_changed": settings.branding is not None,
                "modules_changed": settings.modules is not None,
                "operations_changed": settings.operations is not None,
            },
        )
        await self._db.commit()

        module_toggles = parse_module_toggles(
            json.loads(settings_json) if settings_json else {}
        )
        branding = BrandingConfig(**current_branding_raw)
        operations = self._build_recovery_evidence(
            json.loads(settings_json) if settings_json else {}
        )

        return TenantSettingsResponse(
            tenant_id=updated.id,
            name=updated.name,
            slug=updated.slug,
            default_language=updated.default_language,
            branding=branding,
            modules=ModuleToggles(**module_toggles),
            operations=operations,
            updated_at=updated.updated_at,
        )

    def _build_recovery_evidence(self, settings_raw: dict) -> RecoveryEvidenceResponse:
        operations_raw = settings_raw.get("operations", {})
        if not isinstance(operations_raw, dict):
            operations_raw = {}
        recovery_raw = operations_raw.get("recovery", {})
        if not isinstance(recovery_raw, dict):
            recovery_raw = {}

        config = RecoveryEvidenceConfig(**recovery_raw)
        now = datetime.now(UTC)

        backup_is_stale = True
        if config.last_backup_at is not None:
            backup_is_stale = now - config.last_backup_at > timedelta(days=_BACKUP_STALE_AFTER_DAYS)

        restore_drill_is_stale = True
        if config.last_restore_drill_at is not None:
            restore_drill_is_stale = (
                now - config.last_restore_drill_at > timedelta(days=_RESTORE_DRILL_STALE_AFTER_DAYS)
            )

        backup_state = config.last_backup_status.lower().strip() if config.last_backup_status else "unknown"
        restore_state = (
            config.last_restore_drill_status.lower().strip() if config.last_restore_drill_status else "unknown"
        )
        alert_state = config.alert_posture.lower().strip() if config.alert_posture else "unknown"

        notes: list[str] = []
        if config.last_backup_at is None:
            notes.append("No backup has been recorded yet.")
        elif backup_is_stale:
            notes.append("The latest backup evidence is older than the recommended 7-day threshold.")
        elif backup_state not in {"completed", "ok", "success"}:
            notes.append("The latest backup is not marked as completed.")

        if config.last_restore_drill_at is None:
            notes.append("No restore drill has been recorded yet.")
        elif restore_drill_is_stale:
            notes.append("The latest restore drill evidence is older than the recommended 90-day threshold.")
        elif restore_state not in {"passed", "ok", "success"}:
            notes.append("The latest restore drill is not marked as passed.")

        if not config.alert_contacts_configured:
            notes.append("Alert contacts are not configured.")
        elif alert_state not in {"healthy", "ok", "green"}:
            notes.append("The alert posture is not marked healthy.")

        if notes:
            if (
                config.last_backup_at is None
                or config.last_restore_drill_at is None
                or not config.alert_contacts_configured
                or alert_state in {"critical", "disabled", "failed"}
                or backup_state in {"failed", "error"}
                or restore_state in {"failed", "error"}
            ):
                overall_status = "critical"
            else:
                overall_status = "warning"
            status_message = " ".join(notes)
        else:
            overall_status = "healthy"
            status_message = "Recovery evidence looks current and healthy."

        alert_is_healthy = config.alert_contacts_configured and alert_state in {"healthy", "ok", "green"}

        return RecoveryEvidenceResponse(
            last_backup_at=config.last_backup_at,
            last_backup_status=config.last_backup_status,
            last_backup_reference=config.last_backup_reference,
            last_restore_drill_at=config.last_restore_drill_at,
            last_restore_drill_status=config.last_restore_drill_status,
            alert_posture=config.alert_posture,
            alert_contacts_configured=config.alert_contacts_configured,
            backup_retention_days=config.backup_retention_days,
            notes=config.notes,
            backup_is_stale=backup_is_stale,
            restore_drill_is_stale=restore_drill_is_stale,
            alert_is_healthy=alert_is_healthy,
            overall_status=overall_status,
            status_message=status_message,
        )
