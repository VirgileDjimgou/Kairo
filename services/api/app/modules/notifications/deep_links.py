"""Canonical internal deep-link allowlist for notifications.

Every notification target is an internal application path owned by the backend.
The allowlist is a defence-in-depth guard: a producer bug, a stale route or a
malicious payload must never result in an external or unknown navigation. An
unrecognised target is normalized to the authenticated notification inbox,
which is always a safe destination.

This is navigation safety only. Authentication, tenant and capability
authorization still happen in the router guard and in FastAPI.
"""

from __future__ import annotations

SAFE_TARGET_FALLBACK = "/notifications"

# Internal destinations that notifications may reference. Prefix matching is
# boundary-aware: "/finance" matches "/finance" and "/finance/..." but not
# "/finance-secret".
ALLOWED_TARGET_PREFIXES: tuple[str, ...] = (
    "/dashboard",
    "/notifications",
    "/tasks",
    "/more",
    "/search",
    "/finance",
    "/members",
    "/documents",
    "/policies",
    "/events",
    "/announcements",
    "/discipline",
    "/governance",
    "/sports",
    "/operation-journal",
    "/account",
    "/chat",
    "/recovery",
    "/admin",
)


def is_safe_internal_target(raw: str) -> bool:
    """True when the value is a same-origin, allowlisted internal path."""
    value = str(raw or "").strip()
    if not value.startswith("/") or value.startswith("//"):
        return False
    if "://" in value or "\\" in value:
        return False
    path = value.split("?", 1)[0].split("#", 1)[0]
    if path == "/":
        return True
    return any(path == prefix or path.startswith(f"{prefix}/") for prefix in ALLOWED_TARGET_PREFIXES)


def resolve_target_path(raw: str) -> str:
    """Return the allowlisted target or the safe inbox fallback."""
    value = str(raw or "").strip()
    return value if is_safe_internal_target(value) else SAFE_TARGET_FALLBACK
