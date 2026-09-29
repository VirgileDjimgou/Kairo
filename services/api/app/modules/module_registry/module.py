from __future__ import annotations

from app.modules.module_registry.descriptor import ModuleDescriptor

MODULE = ModuleDescriptor(
    key="module_registry",
    name="Module registry",
    description="Registry metadata endpoint for registered modules and navigation.",
    router_module="app.modules.module_registry.router",
    router_order=170,
)
