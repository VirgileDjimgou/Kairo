from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.chat.models import ChatConversation, ChatMessage


class ChatRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_conversation(self, *, tenant_id: UUID, user_id: UUID, title: str = "Nouvelle conversation") -> ChatConversation:
        conv = ChatConversation(tenant_id=tenant_id, user_id=user_id, title=title)
        self._db.add(conv)
        await self._db.flush()
        return conv

    async def list_conversations(self, *, tenant_id: UUID, user_id: UUID, limit: int = 50) -> list[ChatConversation]:
        stmt = (
            select(ChatConversation)
            .where(ChatConversation.tenant_id == tenant_id, ChatConversation.user_id == user_id)
            .order_by(ChatConversation.updated_at.desc())
            .limit(limit)
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def get_conversation(self, *, conversation_id: UUID, tenant_id: UUID, user_id: UUID) -> ChatConversation | None:
        stmt = (
            select(ChatConversation)
            .where(
                ChatConversation.id == conversation_id,
                ChatConversation.tenant_id == tenant_id,
                ChatConversation.user_id == user_id,
            )
            .options(joinedload(ChatConversation.messages))
        )
        result = await self._db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def add_message(
        self,
        *,
        conversation_id: UUID,
        role: str,
        content: str,
        citations_json: str = "[]",
    ) -> ChatMessage:
        msg = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            citations_json=citations_json,
        )
        self._db.add(msg)
        await self._db.flush()
        return msg

    async def update_conversation_timestamp(self, *, conversation_id: UUID) -> None:
        from datetime import datetime, timezone
        from sqlalchemy import update as sa_update

        stmt = (
            sa_update(ChatConversation)
            .where(ChatConversation.id == conversation_id)
            .values(updated_at=datetime.now(timezone.utc))
        )
        await self._db.execute(stmt)

    async def update_conversation_title(self, *, conversation_id: UUID, title: str) -> None:
        from sqlalchemy import update as sa_update

        stmt = (
            sa_update(ChatConversation)
            .where(ChatConversation.id == conversation_id)
            .values(title=title)
        )
        await self._db.execute(stmt)

    async def delete_conversation(self, *, conversation_id: UUID, tenant_id: UUID, user_id: UUID) -> bool:
        stmt = (
            select(ChatConversation)
            .where(
                ChatConversation.id == conversation_id,
                ChatConversation.tenant_id == tenant_id,
                ChatConversation.user_id == user_id,
            )
        )
        result = await self._db.execute(stmt)
        conv = result.scalar_one_or_none()
        if conv is None:
            return False
        await self._db.delete(conv)
        return True

    async def get_messages_for_conversation(
        self, *, conversation_id: UUID, limit: int = 50
    ) -> list[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def get_old_conversations(self, *, days: int) -> list[ChatConversation]:
        from datetime import datetime, timedelta, timezone
        from sqlalchemy import select

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = (
            select(ChatConversation)
            .where(ChatConversation.updated_at < cutoff)
            .options(joinedload(ChatConversation.messages))
        )
        result = await self._db.execute(stmt)
        return list(result.unique().scalars().all())
