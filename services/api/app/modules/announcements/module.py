from __future__ import annotations

from app.core.capabilities import CAP_ANNOUNCEMENTS_READ, CAP_ANNOUNCEMENTS_WRITE
from app.modules.module_registry.descriptor import ModuleDescriptor, NavigationEntry

MODULE = ModuleDescriptor(
    key="announcements",
    name="Announcements",
    description="Tenant announcements with publication windows and visibility scopes.",
    capabilities=(CAP_ANNOUNCEMENTS_READ, CAP_ANNOUNCEMENTS_WRITE),
    tenant_toggle=True,
    toggle_order=60,
    router_module="app.modules.announcements.router",
    router_order=150,
    search_order=40,
    search_providers=(("app.modules.search.providers", "AnnouncementsSearchProvider"),),
    navigation=(
        NavigationEntry(
            key="announcements",
            label_key="nav.announcements",
            path="/announcements",
            section="member",
            order=40,
        ),
    ),
)
