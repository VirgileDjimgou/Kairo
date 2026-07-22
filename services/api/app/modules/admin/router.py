from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import func, or_, select

from app.core.authorization import require_capability
from app.core.capabilities import (
    CAP_AUDIT_READ,
    CAP_DOCUMENTS_WRITE,
    CAP_TENANT_ADMINISTRATION,
)
from app.core.dependencies import AuthDep, DbDep
from app.core.module_guard import require_module
from app.modules.admin.module_usage import module_has_data
from app.modules.admin.schemas import (
    IngestionJobHealthItemResponse,
    IngestionJobHealthResponse,
)
from app.modules.audit.models import AuditEvent
from app.modules.chat.models import ChatQueryLog
from app.modules.chat.schemas import ChatQueryLogResponse
from app.modules.documents.models import IngestionJob

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/chat-queries", response_model=list[ChatQueryLogResponse])
async def list_chat_queries(
    current: AuthDep,
    db: DbDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    search: Annotated[str | None, Query(max_length=200)] = None,
    refused: Annotated[bool | None, Query()] = None,
    _chat_guard: None = require_module("chat"),  # type: ignore[assignment]
) -> list[ChatQueryLogResponse]:
    require_capability(
        current,
        CAP_AUDIT_READ,
        detail="Audit read capability required",
    )

    query = select(ChatQueryLog).where(ChatQueryLog.tenant_id == current.tenant_id)
    if refused is not None:
        query = query.where(ChatQueryLog.refused == refused)
    if search:
        pattern = f"%{search.lower()}%"
        query = query.where(
            or_(
                func.lower(ChatQueryLog.question).like(pattern),
                func.lower(ChatQueryLog.answer).like(pattern),
                func.lower(func.coalesce(ChatQueryLog.refusal_reason, "")).like(pattern),
                func.lower(func.coalesce(ChatQueryLog.citations_json, "")).like(pattern),
                func.lower(func.coalesce(ChatQueryLog.source_types_json, "")).like(pattern),
            )
        )
    result = await db.execute(
        query.order_by(ChatQueryLog.created_at.desc(), ChatQueryLog.id.desc()).limit(limit)
    )
    return [
        ChatQueryLogResponse(
            id=log.id,
            tenant_id=log.tenant_id,
            user_id=log.user_id,
            question_preview=log.question,
            answer_preview=log.answer,
            refused=log.refused,
            refusal_reason_preview=log.refusal_reason,
            confidence=log.confidence,
            citation_count=len(json.loads(log.citations_json)) if log.citations_json else 0,
            source_types=json.loads(log.source_types_json) if log.source_types_json else [],
            created_at=log.created_at,
        )
        for log in result.scalars().all()
    ]


@router.get("/module-has-data")
async def check_module_has_data(
    current: AuthDep,
    db: DbDep,
    module: Annotated[str, Query(description="Module key to check")],
) -> dict:
    require_capability(
        current,
        CAP_TENANT_ADMINISTRATION,
        detail="Tenant administration capability required",
    )
    has_data = await module_has_data(db, current.tenant_id, module)
    return {"module": module, "has_data": has_data}


@router.get(
    "/ingestion-jobs/health",
    response_model=IngestionJobHealthResponse,
)
async def ingestion_jobs_health(
    current: AuthDep,
    db: DbDep,
    _documents_guard: None = require_module("documents"),  # type: ignore[assignment]
) -> IngestionJobHealthResponse:
    require_capability(
        current,
        CAP_DOCUMENTS_WRITE,
        detail="Document governance write capability required",
    )

    status_rows = await db.execute(
        select(IngestionJob.status, func.count()).where(
            IngestionJob.tenant_id == current.tenant_id
        ).group_by(IngestionJob.status)
    )
    counts: dict[str, int] = dict(status_rows.all())  # type: ignore[arg-type]
    failed_rows = await db.execute(
        select(IngestionJob)
        .where(
            IngestionJob.tenant_id == current.tenant_id,
            IngestionJob.status == "failed",
        )
        .order_by(IngestionJob.created_at.desc())
        .limit(10)
    )
    retried_count = await db.scalar(
        select(func.count()).select_from(AuditEvent).where(
            AuditEvent.tenant_id == current.tenant_id,
            AuditEvent.action == "ingestion_retried",
        )
    )
    return IngestionJobHealthResponse(
        queued_count=int(counts.get("pending", 0)),
        processing_count=int(counts.get("processing", 0)),
        failed_count=int(counts.get("failed", 0)),
        completed_count=int(counts.get("completed", 0)),
        retried_count=int(retried_count or 0),
        recent_failures=[
            IngestionJobHealthItemResponse(
                job_id=job.id,
                document_id=job.document_id,
                document_version_id=job.document_version_id,
                status=job.status,
                error_message=job.error_message,
                started_at=job.started_at,
                finished_at=job.finished_at,
                created_at=job.created_at,
            )
            for job in failed_rows.scalars().all()
        ],
    )
