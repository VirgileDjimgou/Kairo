from __future__ import annotations

from datetime import UTC, datetime


def format_datetime(value: datetime | None) -> str:
    if value is None:
        return "unknown date"
    if value.tzinfo is None:
        normalized = value.replace(tzinfo=UTC)
    else:
        normalized = value.astimezone(UTC)
    return normalized.strftime("%Y-%m-%d %H:%M UTC")


def is_future_datetime(value: datetime | None) -> bool:
    if value is None:
        return False
    if value.tzinfo is None:
        normalized = value.replace(tzinfo=UTC)
    else:
        normalized = value.astimezone(UTC)
    return normalized >= datetime.now(UTC)
