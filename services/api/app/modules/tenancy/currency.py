"""Tenant currency helpers.

The currency is an organization-level setting stored in ``tenants.settings_json``
under the ``currency`` key. Financial records inherit it and must never be recorded
in a different currency: a mixed ledger cannot be reported, budgeted or audited.
"""

from __future__ import annotations

import json

DEFAULT_CURRENCY = "EUR"


def normalize_currency(value: str | None) -> str | None:
    """Return a normalized ISO-4217 code, or ``None`` when the value is invalid."""
    if value is None:
        return None
    normalized = str(value).strip().upper()
    if len(normalized) != 3 or not normalized.isalpha():
        return None
    return normalized


def currency_from_settings(raw_settings: object) -> str:
    """Read the tenant currency from the raw ``settings_json`` value."""
    payload: dict = {}
    if isinstance(raw_settings, str) and raw_settings.strip():
        try:
            decoded = json.loads(raw_settings)
            if isinstance(decoded, dict):
                payload = decoded
        except json.JSONDecodeError:
            payload = {}
    elif isinstance(raw_settings, dict):
        payload = raw_settings
    return normalize_currency(payload.get("currency")) or DEFAULT_CURRENCY
