from __future__ import annotations

from app.core.capabilities import (
    CAP_ROLE_CATALOG_READ,
    CAP_TENANT_ADMINISTRATION,
    CAP_TENANT_SETTINGS_WRITE,
)
from app.modules.module_registry.descriptor import ModuleDescriptor

MODULE = ModuleDescriptor(
    key="tenancy",
    name="Tenancy",
    description="Tenant settings, module toggles, branding, roles and recovery evidence.",
    capabilities=(
        CAP_ROLE_CATALOG_READ,
        CAP_TENANT_ADMINISTRATION,
        CAP_TENANT_SETTINGS_WRITE,
    ),
    router_module="app.modules.tenancy.router",
    router_order=20,
)
