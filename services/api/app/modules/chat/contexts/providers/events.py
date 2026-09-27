from __future__ import annotations

import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat.contexts.contracts import ContextOutcome, ContextRequest
from app.modules.chat.contexts.formatting import format_datetime, is_future_datetime
from app.modules.chat.contexts.messages import message
from app.modules.chat.contexts.patterns import (
    SPORTS_SCHEDULE_PATTERNS,
    question_mentions_any,
)
from app.modules.chat.payloads import StructuredContext
from app.modules.events.models import Event
from app.modules.events.repository import EventRepository


def parse_metadata(value: str | dict | None) -> dict[str, object]:
    if value in (None, ""):
        return {}
    if isinstance(value, dict):
        return dict(value)
    if not isinstance(value, str):
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def is_sports_event(event: Event) -> bool:
    return parse_metadata(event.metadata_json).get("workspace") == "sports"


class EventsContextProvider:
    key = "events"

    def __init__(self, db: AsyncSession) -> None:
        self._event_repo = EventRepository(db)

    async def collect(self, request: ContextRequest) -> ContextOutcome:
        if not question_mentions_any(request.normalized_question, SPORTS_SCHEDULE_PATTERNS):
            return ContextOutcome()
        if not request.domain_policy.sports:
            return ContextOutcome(
                refusal=message("sports_forbidden", request.response_language)
            )

        events = await self._event_repo.list_by_tenant(request.tenant_id)
        sports_events = [event for event in events if is_sports_event(event)]
        upcoming_events = [
            event
            for event in sports_events
            if event.status == "published" and is_future_datetime(event.start_at)
        ]
        summary_lines = [
            f"Sports events in tenant: {len(sports_events)}",
            f"Upcoming sports events: {len(upcoming_events)}",
        ]
        if upcoming_events:
            summary_lines.append("Next sports events:")
            summary_lines.extend(
                (
                    f"- {event.title} ({format_datetime(event.start_at)})"
                    + (f" at {event.location}" if event.location else "")
                )
                for event in upcoming_events[:3]
            )

        return ContextOutcome(
            context=StructuredContext(
                source_type="structured:sports_schedule",
                title="Sports schedule",
                content="\n".join(summary_lines),
            )
        )
