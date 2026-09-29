from __future__ import annotations

from app.core.capabilities import CAP_POLICIES_READ, CAP_POLICIES_WRITE
from app.modules.module_registry.descriptor import ModuleDescriptor, NavigationEntry

MODULE = ModuleDescriptor(
    key="policies",
    name="Policies",
    description="Public and tenant policy catalog and rule records.",
    capabilities=(CAP_POLICIES_READ, CAP_POLICIES_WRITE),
    tenant_toggle=True,
    toggle_order=30,
    router_module="app.modules.policies.router",
    router_order=110,
    navigation=(
        NavigationEntry(
            key="policies",
            label_key="nav.policies",
            path="/policies",
            section="member",
            order=30,
        ),
    ),
)
