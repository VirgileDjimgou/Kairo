from __future__ import annotations

from collections.abc import Mapping
from typing import Any

_SENSITIVE_KEY_EXACT = {
    "answer",
    "body",
    "comment",
    "comments",
    "content",
    "description",
    "display_name",
    "email",
    "excerpt",
    "first_name",
    "full_name",
    "last_name",
    "message",
    "mobile",
    "name",
    "note",
    "notes",
    "phone",
    "postal_code",
    "postcode",
    "prompt",
    "question",
    "reason",
    "refusal_reason",
    "response",
    "street",
    "summary",
    "text",
    "title",
}

_SENSITIVE_KEY_SUBSTRINGS = (
    "access_token",
    "api_key",
    "auth",
    "credential",
    "firstname",
    "lastname",
    "mfa",
    "otp",
    "passphrase",
    "password",
    "refresh_token",
    "secret",
    "token",
    "verification",
)


def preview_text(value: str, *, max_length: int = 160) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= max_length:
        return normalized
    return f"{normalized[: max_length - 3].rstrip()}..."


def redact_nested_data(value: Any, *, max_string_length: int = 120) -> Any:
    if isinstance(value, Mapping):
        redacted: dict[str, Any] = {}
        for raw_key, raw_value in value.items():
            key = str(raw_key)
            if _is_sensitive_key(key):
                redacted[key] = "[redacted]"
            else:
                redacted[key] = redact_nested_data(raw_value, max_string_length=max_string_length)
        return redacted
    if isinstance(value, list):
        return [redact_nested_data(item, max_string_length=max_string_length) for item in value]
    if isinstance(value, tuple):
        return [redact_nested_data(item, max_string_length=max_string_length) for item in value]
    if isinstance(value, str):
        return preview_text(value, max_length=max_string_length)
    return value


def _is_sensitive_key(key: str) -> bool:
    normalized = key.strip().lower()
    if normalized in _SENSITIVE_KEY_EXACT:
        return True
    return any(fragment in normalized for fragment in _SENSITIVE_KEY_SUBSTRINGS)
