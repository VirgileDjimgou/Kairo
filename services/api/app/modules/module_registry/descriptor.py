"""Internal Module Registry framework.

A module is a small package under ``app.modules`` that exposes a ``module.py``
file with a ``MODULE`` descriptor. The registry discovers those descriptors from
the repository itself (never from untrusted runtime input), validates them, and
lets the application compose routers, search providers, optional AI context
providers, health checks and navigation metadata from one place.

Adding a module therefore means creating one package with a descriptor; central
files consume the registry instead of importing the module directly.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any

MODULES_PACKAGE = "app.modules"
DESCRIPTOR_FILENAME = "module"


class ModuleRegistryError(ValueError):
    """Raised for invalid module descriptors (duplicate keys, bad dependencies)."""


@dataclass(frozen=True)
class NavigationEntry:
    """Presentation metadata owned by the module, consumed by clients.

    ``label_key`` is an i18n key and ``capabilities`` gate visibility in the
    client; the backend still enforces every authorization decision.
    """

    key: str
    label_key: str
    path: str
    section: str = "office"
    order: int = 0
    capabilities: tuple[str, ...] = ()


@dataclass(frozen=True)
class ModuleDescriptor:
    key: str
    name: str
    description: str = ""
    capabilities: tuple[str, ...] = ()
    depends_on: tuple[str, ...] = ()
    default_enabled: bool = True
    tenant_toggle: bool = False
    toggle_order: int = 100
    feature_flag: str | None = None
    router_module: str | None = None
    router_attrs: tuple[str, ...] = ("router",)
    extra_routers: tuple[tuple[str, str], ...] = ()
    router_order: int = 100
    search_order: int = -1
    search_providers: tuple[tuple[str, str], ...] = ()
    ai_context_providers: tuple[tuple[str, str], ...] = ()
    domain_event_types: tuple[str, ...] = ()
    navigation: tuple[NavigationEntry, ...] = ()
    health_check_module: str | None = None
    health_check_attr: str | None = None

    def health_check(self) -> Callable[[AsyncSessionLike], Any] | None:
        if not self.health_check_module or not self.health_check_attr:
            return None
        module = import_module(self.health_check_module)
        return getattr(module, self.health_check_attr)


# Typed loosely on purpose: the framework never touches the session itself.
AsyncSessionLike = Any


class ModuleRegistry:
    def __init__(self, descriptors: list[ModuleDescriptor]) -> None:
        self._descriptors = list(descriptors)
        self._by_key: dict[str, ModuleDescriptor] = {}
        self._validate()

    def _validate(self) -> None:
        for descriptor in self._descriptors:
            if not descriptor.key:
                raise ModuleRegistryError("Module descriptor without a key")
            if not descriptor.key.replace("_", "").isalnum():
                raise ModuleRegistryError(
                    f"Module key '{descriptor.key}' must be an identifier"
                )
            if descriptor.key in self._by_key:
                raise ModuleRegistryError(f"Duplicate module key '{descriptor.key}'")
            self._by_key[descriptor.key] = descriptor

        for descriptor in self._descriptors:
            for dependency in descriptor.depends_on:
                if dependency == descriptor.key:
                    raise ModuleRegistryError(
                        f"Module '{descriptor.key}' cannot depend on itself"
                    )
                if dependency not in self._by_key:
                    raise ModuleRegistryError(
                        f"Module '{descriptor.key}' depends on unknown module '{dependency}'"
                    )

        visited: dict[str, int] = {}

        def visit(key: str, trail: list[str]) -> None:
            state = visited.get(key)
            if state == 1:
                raise ModuleRegistryError(
                    "Module dependency cycle detected: " + " -> ".join([*trail, key])
                )
            if state == 2:
                return
            visited[key] = 1
            for dependency in self._by_key[key].depends_on:
                visit(dependency, [*trail, key])
            visited[key] = 2

        for descriptor in self._descriptors:
            visit(descriptor.key, [])

        navigation_keys: set[str] = set()
        for descriptor in self._descriptors:
            for entry in descriptor.navigation:
                if entry.key in navigation_keys:
                    raise ModuleRegistryError(
                        f"Duplicate navigation key '{entry.key}'"
                    )
                navigation_keys.add(entry.key)
                if not entry.label_key or not entry.path.startswith("/"):
                    raise ModuleRegistryError(
                        f"Navigation '{entry.key}' needs an i18n label key and an internal path"
                    )

    @property
    def keys(self) -> tuple[str, ...]:
        return tuple(descriptor.key for descriptor in self._descriptors)

    def descriptors(self) -> tuple[ModuleDescriptor, ...]:
        return tuple(self._descriptors)

    def tenant_toggle_keys(self) -> tuple[str, ...]:
        return tuple(
            descriptor.key
            for descriptor in sorted(
                self._descriptors,
                key=lambda item: (item.toggle_order, item.key),
            )
            if descriptor.tenant_toggle
        )

    def get(self, key: str) -> ModuleDescriptor | None:
        return self._by_key.get(key)

    def require(self, key: str) -> ModuleDescriptor:
        descriptor = self._by_key.get(key)
        if descriptor is None:
            raise ModuleRegistryError(f"Unknown module '{key}'")
        return descriptor

    def routers(self) -> list[tuple[Any, str]]:
        """Import and return ``(router, attribute_name)`` in registration order."""
        ordered = sorted(self._descriptors, key=lambda item: item.router_order)
        routers: list[tuple[Any, str]] = []
        for descriptor in ordered:
            if descriptor.router_module:
                module = import_module(descriptor.router_module)
                for attr in descriptor.router_attrs:
                    routers.append((getattr(module, attr), attr))
            for module_path, attr in descriptor.extra_routers:
                routers.append((getattr(import_module(module_path), attr), attr))
        return routers

    def search_providers(self) -> list[Any]:
        refs: list[tuple[int, int, tuple[str, str]]] = []
        position = 0
        for descriptor in self._descriptors:
            for ref in descriptor.search_providers:
                refs.append((descriptor.search_order, position, ref))
                position += 1
        refs.sort(key=lambda item: (item[0], item[1]))
        providers: list[Any] = []
        for _order, _position, (module_path, attr) in refs:
            provider_class = getattr(import_module(module_path), attr)
            providers.append(provider_class())
        return providers

    def ai_context_providers(self, db: AsyncSessionLike) -> list[Any]:
        providers: list[Any] = []
        for descriptor in sorted(self._descriptors, key=lambda item: item.router_order):
            for module_path, attr in descriptor.ai_context_providers:
                provider_class = getattr(import_module(module_path), attr)
                providers.append(provider_class(db))
        return providers

    def health_checks(self) -> dict[str, Callable[[AsyncSessionLike], Any]]:
        checks: dict[str, Callable[[AsyncSessionLike], Any]] = {}
        for descriptor in self._descriptors:
            check = descriptor.health_check()
            if check is not None:
                checks[descriptor.key] = check
        return checks


def discover_descriptors() -> list[ModuleDescriptor]:
    """Discover ``app.modules.<package>.module.MODULE`` descriptors.

    Scanning the filesystem handles both regular and namespace packages
    (packages without ``__init__.py``) and keeps discovery deterministic.
    """
    package = import_module(MODULES_PACKAGE)
    descriptors: list[ModuleDescriptor] = []
    names: list[str] = []
    for package_path in package.__path__:
        for descriptor_file in Path(package_path).glob(f"*/{DESCRIPTOR_FILENAME}.py"):
            names.append(descriptor_file.parent.name)
    for name in sorted(set(names)):
        if name.startswith("__"):
            continue
        module = import_module(f"{MODULES_PACKAGE}.{name}.{DESCRIPTOR_FILENAME}")
        descriptor = getattr(module, "MODULE", None)
        if descriptor is None:
            continue
        descriptors.append(descriptor)
    return descriptors


def known_capabilities() -> frozenset[str]:
    from app.core.capabilities import known_capabilities as catalog_known_capabilities

    return catalog_known_capabilities()


def validate_capabilities(registry: ModuleRegistry) -> list[str]:
    """Return declared capabilities that are not part of the catalog."""
    known = known_capabilities()
    unknown: set[str] = set()
    for descriptor in registry.descriptors():
        for capability in descriptor.capabilities:
            if capability not in known:
                unknown.add(capability)
    return sorted(unknown)


_default_registry: ModuleRegistry | None = None


def default_registry() -> ModuleRegistry:
    global _default_registry
    if _default_registry is None:
        registry = ModuleRegistry(discover_descriptors())
        unknown = validate_capabilities(registry)
        if unknown:
            raise ModuleRegistryError(
                "Module descriptors declare unknown capabilities: " + ", ".join(unknown)
            )
        _default_registry = registry
    return _default_registry


def registered_health_checks() -> dict[str, Callable[[AsyncSessionLike], Any]]:
    return default_registry().health_checks()
