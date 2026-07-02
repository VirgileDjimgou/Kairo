from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.core.authorization import require_capability
from app.core.capabilities import (
    CAP_AUDIT_READ,
    CAP_DOCUMENTS_WRITE,
    CAP_TENANT_ADMINISTRATION,
)
from app.core.dependencies import AuthDep, DbDep
from app.core.module_guard import require_module
from app.modules.admin.schemas import (
    IngestionJobHealthItemResponse,
    IngestionJobHealthResponse,
)
from app.modules.audit.models import AuditEvent
from app.modules.admin.module_usage import module_has_data
from app.modules.chat.models import ChatQueryLog
from app.modules.chat.schemas import ChatQueryLogResponse
from app.modules.documents.models import IngestionJob

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/chat-queries", response_model=list[ChatQueryLogResponse])
async def list_chat_queries(
    current: AuthDep,
    db: DbDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    _chat_guard: None = require_module("chat"),
) -> list[ChatQueryLogResponse]:
    require_capability(
        current,
        CAP_AUDIT_READ,
        detail="Audit read capability required",
    )

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
            source_types_json=log.source_types_json,
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
    _documents_guard: None = require_module("documents"),
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
    counts = dict(status_rows.all())
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
