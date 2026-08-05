from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import text

from app.db.base import Base


class BackupRun(Base):
    """A request and immutable result record for a protected backup archive.

    The archive itself is intentionally kept outside the database and is never
    exposed through a normal browser download route.
    """

    __tablename__ = "backup_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    requested_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    trigger: Mapped[str] = mapped_column(String(32), nullable=False, server_default="manual")
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="queued", index=True
    )
    storage_reference: Mapped[str | None] = mapped_column(String(512), nullable=True)
    archive_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    manifest_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    archive_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    components_json: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'{}'"))
    error_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
