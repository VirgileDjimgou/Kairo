from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.core.dependencies import AuthDep, DbDep
from app.modules.chat.models import ChatQueryLog
from app.modules.chat.schemas import ChatQueryLogResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/chat-queries", response_model=list[ChatQueryLogResponse])
async def list_chat_queries(
    current: AuthDep,
    db: DbDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[ChatQueryLogResponse]:
    if not current.has_role("admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")

    result = await db.execute(
        select(ChatQueryLog)
        .where(ChatQueryLog.tenant_id == current.tenant_id)
        .order_by(ChatQueryLog.created_at.desc())
        .limit(limit)
    )
    return [
        ChatQueryLogResponse(
            id=log.id,
            tenant_id=log.tenant_id,
            user_id=log.user_id,
            question=log.question,
            answer=log.answer,
            refused=log.refused,
            refusal_reason=log.refusal_reason,
            confidence=log.confidence,
            citations_json=log.citations_json,
            created_at=log.created_at,
        )
        for log in result.scalars().all()
    ]
