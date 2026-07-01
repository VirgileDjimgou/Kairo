from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Query, Response
from fastapi.responses import JSONResponse

from app.core.authorization import require_capability
from app.core.capabilities import CAP_AUDIT_READ
from app.core.dependencies import AuthDep, DbDep
from app.modules.audit.schemas import AuditEventResponse
from app.modules.audit.service import AuditService

router = APIRouter(prefix="/admin/audit", tags=["audit"])


@router.get("/events", response_model=list[AuditEventResponse])
async def list_audit_events(
    current: AuthDep,
    db: DbDep,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    actor_user_id: UUID | None = Query(default=None),
    action: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    entity_id: str | None = Query(default=None),
    module_key: str | None = Query(default=None),
    search: str | None = Query(default=None),
    created_from: datetime | None = Query(default=None),
    created_to: datetime | None = Query(default=None),
) -> list[AuditEventResponse]:
    require_capability(
        current,
        CAP_AUDIT_READ,
        detail="Audit read capability required",
    )
    service = AuditService(db)
    return await service.list_events(
        current.tenant_id,
        limit=limit,
        offset=offset,
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        module_key=module_key,
        search=search,
        created_from=created_from,
        created_to=created_to,
    )


@router.get("/events/export")
async def export_audit_events(
    current: AuthDep,
    db: DbDep,
    format: Annotated[Literal["csv", "json"], Query(description="Export format")] = "csv",
    actor_user_id: UUID | None = Query(default=None),
    action: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    entity_id: str | None = Query(default=None),
    module_key: str | None = Query(default=None),
    search: str | None = Query(default=None),
    created_from: datetime | None = Query(default=None),
    created_to: datetime | None = Query(default=None),
) -> Response:
    require_capability(
        current,
        CAP_AUDIT_READ,
        detail="Audit read capability required",
    )
    service = AuditService(db)
    rows = await service.list_events(
        current.tenant_id,
        limit=5000,
        offset=0,
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        module_key=module_key,
        search=search,
        created_from=created_from,
        created_to=created_to,
    )

    if format == "json":
        return JSONResponse(
            content=[row.model_dump(mode="json") for row in rows],
        )

    csv_payload = await service.export_csv(
        current.tenant_id,
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        module_key=module_key,
        search=search,
        created_from=created_from,
        created_to=created_to,
    )
    return Response(
        content=csv_payload,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="audit-events.csv"'},
    )
