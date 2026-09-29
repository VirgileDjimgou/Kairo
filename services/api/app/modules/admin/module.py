from __future__ import annotations

from app.core.capabilities import CAP_AUDIT_READ, CAP_DOCUMENTS_WRITE, CAP_TENANT_ADMINISTRATION
from app.modules.module_registry.descriptor import ModuleDescriptor

MODULE = ModuleDescriptor(
    key="admin",
    name="Administration",
    description="Tenant operator console: ingestion health, module usage and chat audit.",
    capabilities=(CAP_TENANT_ADMINISTRATION, CAP_AUDIT_READ, CAP_DOCUMENTS_WRITE),
    router_module="app.modules.admin.router",
    router_order=30,
)
