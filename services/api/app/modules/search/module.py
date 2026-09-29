from __future__ import annotations

from app.modules.module_registry.descriptor import ModuleDescriptor

MODULE = ModuleDescriptor(
    key="search",
    name="Global search",
    description="Permission-aware search across module-provided providers.",
    router_module="app.modules.search.router",
    router_order=120,
)
