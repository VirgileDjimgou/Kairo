"""Minimal non-critical sample module proving registry extensibility.

It exists to demonstrate that a new package with a ``module.py`` descriptor is
discovered automatically: the router is registered without editing central
files, the descriptor declares metadata (dependencies, capabilities) and the
module participates in registry validation. It deliberately owns no business
data and no tenant toggle, and is safe to remove.
"""

from __future__ import annotations

from app.core.capabilities import CAP_AUDIT_READ
from app.modules.module_registry.descriptor import ModuleDescriptor

MODULE = ModuleDescriptor(
    key="sample",
    name="Sample extension module",
    description=(
        "Read-only extension example used to validate the module registry; "
        "not part of any association workflow."
    ),
    capabilities=(CAP_AUDIT_READ,),
    depends_on=("audit",),
    router_module="app.modules.sample.router",
    router_order=900,
)
