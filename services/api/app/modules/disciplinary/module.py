from __future__ import annotations

from app.core.capabilities import (
    CAP_DISCIPLINARY_OVERSIGHT_READ,
    CAP_DISCIPLINARY_SELF_READ,
    CAP_DISCIPLINARY_TENANT_READ,
    CAP_DISCIPLINARY_WRITE,
)
from app.modules.module_registry.descriptor import ModuleDescriptor, NavigationEntry

MODULE = ModuleDescriptor(
    key="disciplinary",
    name="Discipline",
    description="Private disciplinary records, sanctions and payment state.",
    capabilities=(
        CAP_DISCIPLINARY_SELF_READ,
        CAP_DISCIPLINARY_TENANT_READ,
        CAP_DISCIPLINARY_WRITE,
        CAP_DISCIPLINARY_OVERSIGHT_READ,
    ),
    tenant_toggle=True,
    toggle_order=40,
    router_module="app.modules.disciplinary.router",
    router_order=130,
    search_order=80,
    search_providers=(("app.modules.search.providers", "DisciplineSearchProvider"),),
    navigation=(
        NavigationEntry(
            key="disciplinary",
            label_key="nav.disciplinaryConsole",
            path="/disciplinary",
            section="member",
            order=90,
            capabilities=(CAP_DISCIPLINARY_SELF_READ,),
        ),
    ),
)
