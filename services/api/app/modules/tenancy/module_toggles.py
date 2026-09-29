"""
Module toggle utilities.

Reads module enable/disable state from a tenant's settings_json.
Defaults all modules to enabled if no configuration is stored.

The toggle key set is derived lazily from the Module Registry: a descriptor with
``tenant_toggle=True`` becomes a tenant-configurable module. The lookup is lazy
so that importing this module never triggers registry discovery (which imports
module packages and their routers).
"""
import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    ALL_MODULES: list[str]


def _toggle_keys() -> list[str]:
    from app.modules.module_registry.descriptor import default_registry

    return list(default_registry().tenant_toggle_keys())


def __getattr__(name: str) -> Any:
    if name == "ALL_MODULES":
        return _toggle_keys()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def default_module_toggles() -> dict[str, bool]:
    return {module: True for module in _toggle_keys()}


def parse_module_toggles(settings_json: dict[str, Any] | str | None) -> dict[str, bool]:
    """
    Extract module toggles from a tenant's settings_json.

    Returns full default set when settings_json is empty or missing modules key.
    """
    if not settings_json:
        return default_module_toggles()
    if isinstance(settings_json, str):
        try:
            parsed = json.loads(settings_json)
        except json.JSONDecodeError:
            return default_module_toggles()
        if not isinstance(parsed, dict):
            return default_module_toggles()
        settings_json = parsed
    modules = settings_json.get("modules", {})
    if not isinstance(modules, dict):
        return default_module_toggles()
    toggle_keys = _toggle_keys()
    toggles = default_module_toggles()
    toggles.update({k: bool(v) for k, v in modules.items() if k in toggle_keys})
    return toggles


def is_module_enabled(settings_json: dict[str, Any] | None, module: str) -> bool:
    """Check if a specific module is enabled for the tenant."""
    toggles = parse_module_toggles(settings_json)
    return toggles.get(module, True)
