"""Internal module registry package (framework, composition and API)."""

from app.modules.module_registry.descriptor import (
    ModuleDescriptor,
    ModuleRegistry,
    ModuleRegistryError,
    NavigationEntry,
    default_registry,
    discover_descriptors,
)

__all__ = [
    "ModuleDescriptor",
    "ModuleRegistry",
    "ModuleRegistryError",
    "NavigationEntry",
    "default_registry",
    "discover_descriptors",
]
