"""Tenant branding parsing shared by settings, memberships and delivery.

Branding is configuration, never business logic: every consumer receives the
canonical `TenantBranding` with safe Kairo defaults, whatever the stored JSON
contains.
"""

from __future__ import annotations

import json

from app.modules.tenancy.schemas import TenantBranding


def branding_from_json(raw: object) -> TenantBranding:
    """Parse stored branding JSON into the canonical contract."""
    parsed: object = raw
    if isinstance(raw, str):
        if not raw.strip():
            parsed = {}
        else:
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = {}
    if not isinstance(parsed, dict):
        parsed = {}
    return TenantBranding(**parsed)
