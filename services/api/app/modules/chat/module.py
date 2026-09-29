from __future__ import annotations

from app.core.capabilities import CAP_CHAT_USE
from app.modules.module_registry.descriptor import ModuleDescriptor, NavigationEntry

MODULE = ModuleDescriptor(
    key="chat",
    name="Assistant",
    description="Private assistant with authorized domain context providers and citations.",
    capabilities=(CAP_CHAT_USE,),
    tenant_toggle=True,
    toggle_order=70,
    router_module="app.modules.chat.router",
    router_order=80,
    navigation=(
        NavigationEntry(
            key="chat",
            label_key="nav.chat",
            path="/chat",
            section="member",
            order=60,
        ),
    ),
)
