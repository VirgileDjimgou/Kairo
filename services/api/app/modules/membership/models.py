import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import text as sql_text

from app.db.base import Base


class MembershipStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"
    resigned = "resigned"


class MembershipProfile(Base):
    """
    Structured member profile within a tenant.

    Can be linked to a platform User (if the member has login access)
    or exist independently (for non-digital members).
    """

    __tablename__ = "membership_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    member_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default=MembershipStatus.active.value
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sql_text("CURRENT_TIMESTAMP")
    )
    metadata_json: Mapped[dict] = mapped_column(
        Text, nullable=False, server_default=sql_text("'{}'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sql_text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sql_text("CURRENT_TIMESTAMP")
    )

    def __repr__(self) -> str:
        return f"<MembershipProfile tenant={self.tenant_id} code={self.member_code} name={self.display_name}>"