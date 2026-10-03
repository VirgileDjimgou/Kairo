from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import text

from app.db.base import Base

EVENT_STATUS_PENDING = "pending"
EVENT_STATUS_PROCESSING = "processing"
EVENT_STATUS_COMPLETED = "completed"
EVENT_STATUS_FAILED = "failed"


class DomainEvent(Base):
    """An internal domain event with PostgreSQL-backed transactional outbox semantics.

    The row is written in the same transaction as the business mutation. Consumer
    handlers (audit projection, notifications, custody workflow) are either applied
    inline in that transaction or retried by the worker from this durable record.
    """

    __tablename__ = "domain_events"
    __table_args__ = (
        UniqueConstraint("tenant_id", "deduplication_key", name="uq_domain_events_dedup"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    aggregate_type: Mapped[str] = mapped_column(String(120), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    correlation_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    deduplication_key: Mapped[str] = mapped_column(String(255), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'{}'"))
    applied_handlers_json: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'[]'")
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=EVENT_STATUS_PENDING, index=True
    )
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    available_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    processing_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    @property
    def payload(self) -> dict[str, Any]:
        try:
            parsed = json.loads(self.payload_json)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {"value": parsed}

    @property
    def applied_handlers(self) -> list[str]:
        try:
            parsed = json.loads(self.applied_handlers_json)
        except json.JSONDecodeError:
            return []
        return [str(name) for name in parsed] if isinstance(parsed, list) else []

    def __repr__(self) -> str:
        return (
            f"<DomainEvent tenant={self.tenant_id} type={self.event_type} "
            f"aggregate={self.aggregate_type}:{self.aggregate_id} status={self.status}>"
        )
