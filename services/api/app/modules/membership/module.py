from __future__ import annotations

from app.core.capabilities import (
    CAP_MEMBERSHIP_DELETE,
    CAP_MEMBERSHIP_INVITE,
    CAP_MEMBERSHIP_SELF_READ,
    CAP_MEMBERSHIP_TENANT_READ,
    CAP_MEMBERSHIP_WRITE,
)
from app.modules.module_registry.descriptor import ModuleDescriptor, NavigationEntry

MODULE = ModuleDescriptor(
    key="membership",
    name="Membership",
    description="Member profiles, lifecycle, directory and personal statements.",
    capabilities=(
        CAP_MEMBERSHIP_SELF_READ,
        CAP_MEMBERSHIP_TENANT_READ,
        CAP_MEMBERSHIP_WRITE,
        CAP_MEMBERSHIP_DELETE,
        CAP_MEMBERSHIP_INVITE,
    ),
    tenant_toggle=True,
    toggle_order=10,
    router_module="app.modules.membership.router",
    router_order=90,
    search_order=10,
    search_providers=(("app.modules.search.providers", "MembersSearchProvider"),),
    navigation=(
        NavigationEntry(
            key="members",
            label_key="nav.members",
            path="/members/manage",
            section="office",
            order=10,
            capabilities=(CAP_MEMBERSHIP_TENANT_READ,),
        ),
    ),
)
