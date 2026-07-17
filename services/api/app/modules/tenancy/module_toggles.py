"""
Module toggle utilities.

Reads module enable/disable state from a tenant's settings_json.
Defaults all modules to enabled if no configuration is stored.
"""
import json
from typing import Any

ALL_MODULES = [
    "membership",
    "contributions",
    "policies",
    "disciplinary",
    "events",
    "announcements",
    "chat",
    "notifications",
]


def default_module_toggles() -> dict[str, bool]:
    return {m: True for m in ALL_MODULES}


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
    toggles = default_module_toggles()
    toggles.update({k: bool(v) for k, v in modules.items() if k in ALL_MODULES})
    return toggles


def is_module_enabled(settings_json: dict[str, Any] | None, module: str) -> bool:
    """Check if a specific module is enabled for the tenant."""
    toggles = parse_module_toggles(settings_json)
    return toggles.get(module, True)
