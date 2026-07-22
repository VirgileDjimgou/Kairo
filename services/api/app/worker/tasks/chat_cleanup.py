from __future__ import annotations

from app.db.session import async_session_factory
from app.modules.chat.repository import ChatRepository
from app.worker.celery_app import celery_app


@celery_app.task(name="chat.cleanup_old_conversations", bind=True, max_retries=2)
def cleanup_old_conversations(self, days: int = 30) -> int:
    """Delete conversations and messages older than `days`."""
    import asyncio

    async def _run() -> int:
        async with async_session_factory() as session:
            repo = ChatRepository(session)
            old = await repo.get_old_conversations(days=days)
            count = len(old)
            for conv in old:
                await session.delete(conv)
            await session.commit()
            return count

    loop = asyncio.new_event_loop()
    try:
        deleted = loop.run_until_complete(_run())
    finally:
        loop.close()

    return deleted
