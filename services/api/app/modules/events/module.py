from __future__ import annotations

from app.core.capabilities import CAP_EVENTS_READ, CAP_EVENTS_SPORTS_WRITE, CAP_EVENTS_WRITE
from app.modules.module_registry.descriptor import ModuleDescriptor, NavigationEntry

MODULE = ModuleDescriptor(
    key="events",
    name="Events",
    description="Association calendar, visibility scopes and sports programming.",
    capabilities=(CAP_EVENTS_READ, CAP_EVENTS_WRITE, CAP_EVENTS_SPORTS_WRITE),
    tenant_toggle=True,
    toggle_order=50,
    router_module="app.modules.events.router",
    extra_routers=(("app.modules.events.sports_router", "router"),),
    router_order=140,
    search_order=30,
    search_providers=(("app.modules.search.providers", "EventsSearchProvider"),),
    navigation=(
        NavigationEntry(
            key="events",
            label_key="nav.events",
            path="/events",
            section="member",
            order=50,
        ),
    ),
)
