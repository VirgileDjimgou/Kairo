from __future__ import annotations

import json

from fastapi import APIRouter

from app.core.dependencies import AuthDep, DbDep
from app.modules.module_registry.descriptor import (
    ModuleDescriptor,
    default_registry,
)
from app.modules.module_registry.schemas import (
    ModuleNavigationEntryResponse,
    RegisteredModuleResponse,
    RegisteredModulesResponse,
)
from app.modules.tenancy.module_toggles import parse_module_toggles
from app.modules.tenancy.repository import TenancyRepository

router = APIRouter(prefix="/modules", tags=["modules"])


def _tenant_toggles(raw_settings: object) -> dict[str, bool]:
    if isinstance(raw_settings, str) and raw_settings.strip():
        try:
            raw_settings = json.loads(raw_settings)
        except json.JSONDecodeError:
            raw_settings = {}
    return parse_module_toggles(raw_settings if isinstance(raw_settings, dict) else None)


def _module_enabled(
    descriptor: ModuleDescriptor, toggles: dict[str, bool]
) -> bool:
    if descriptor.tenant_toggle:
        return toggles.get(descriptor.key, descriptor.default_enabled)
    return descriptor.default_enabled


def _to_response(
    descriptor: ModuleDescriptor,
    *,
    toggles: dict[str, bool],
    capabilities: set[str],
) -> RegisteredModuleResponse:
    navigation = [
        ModuleNavigationEntryResponse(
            key=entry.key,
            label_key=entry.label_key,
            path=entry.path,
            section=entry.section,
            order=entry.order,
            capabilities=list(entry.capabilities),
        )
        for entry in descriptor.navigation
        if all(capability in capabilities for capability in entry.capabilities)
    ]
    return RegisteredModuleResponse(
        key=descriptor.key,
        name=descriptor.name,
        description=descriptor.description,
        enabled=_module_enabled(descriptor, toggles),
        capabilities=list(descriptor.capabilities),
        depends_on=list(descriptor.depends_on),
        domain_event_types=list(descriptor.domain_event_types),
        navigation=navigation,
    )


@router.get("", response_model=RegisteredModulesResponse)
async def list_registered_modules(
    current: AuthDep, db: DbDep
) -> RegisteredModulesResponse:
    """Return registry metadata for the active tenant and authenticated user."""
    tenancy = TenancyRepository(db)
    tenant = await tenancy.get_tenant_by_id(current.tenant_id)
    toggles = _tenant_toggles(tenant.settings_json if tenant is not None else None)
    role_codes = await tenancy.get_user_role_codes(current.tenant_id, current.user.id)
    from app.core.capabilities import capabilities_for_roles

    capabilities = set(capabilities_for_roles(role_codes))
    registry = default_registry()
    return RegisteredModulesResponse(
        modules=[
            _to_response(descriptor, toggles=toggles, capabilities=capabilities)
            for descriptor in registry.descriptors()
        ]
    )


@router.get("/{module_key}", response_model=RegisteredModuleResponse)
async def get_registered_module(
    module_key: str, current: AuthDep, db: DbDep
) -> RegisteredModuleResponse:
    """Return registry metadata for one registered module."""
    tenancy = TenancyRepository(db)
    tenant = await tenancy.get_tenant_by_id(current.tenant_id)
    toggles = _tenant_toggles(tenant.settings_json if tenant is not None else None)
    role_codes = await tenancy.get_user_role_codes(current.tenant_id, current.user.id)
    from app.core.capabilities import capabilities_for_roles

    capabilities = set(capabilities_for_roles(role_codes))
    descriptor = default_registry().require(module_key)
    return _to_response(descriptor, toggles=toggles, capabilities=capabilities)
