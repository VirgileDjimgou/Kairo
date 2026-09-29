from __future__ import annotations

from app.core.capabilities import CAP_AUDIT_READ
from app.modules.module_registry.descriptor import ModuleDescriptor

MODULE = ModuleDescriptor(
    key="audit",
    name="Audit",
    description="Tenant audit trail and operation journal.",
    capabilities=(CAP_AUDIT_READ,),
    router_module="app.modules.audit.router",
    router_order=50,
    search_order=70,
    search_providers=(("app.modules.search.providers", "AuditSearchProvider"),),
)
