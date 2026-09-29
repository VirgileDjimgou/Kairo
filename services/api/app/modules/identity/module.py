from __future__ import annotations

from app.core.capabilities import (
    CAP_AUDIT_READ,
    CAP_IDENTITY_ACCESS_RECOVERY,
    CAP_ROLE_ASSIGN,
    CAP_ROLE_CATALOG_READ,
    CAP_TENANT_ADMINISTRATION,
)
from app.modules.module_registry.descriptor import ModuleDescriptor

MODULE = ModuleDescriptor(
    key="identity",
    name="Identity",
    description="Authentication, MFA, sessions, invitations and account recovery.",
    capabilities=(
        CAP_AUDIT_READ,
        CAP_IDENTITY_ACCESS_RECOVERY,
        CAP_ROLE_ASSIGN,
        CAP_ROLE_CATALOG_READ,
        CAP_TENANT_ADMINISTRATION,
    ),
    router_module="app.modules.identity.router",
    router_order=10,
)
