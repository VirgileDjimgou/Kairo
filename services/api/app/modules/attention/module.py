from __future__ import annotations

from app.modules.module_registry.descriptor import ModuleDescriptor

MODULE = ModuleDescriptor(
    key="attention",
    name="Attention center",
    description="Role-aware action cards aggregated for the dashboard.",
    router_module="app.modules.attention.router",
    router_order=40,
)
