from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.core.authorization import require_capability
from app.core.capabilities import (
    CAP_ANNOUNCEMENTS_WRITE,
    CAP_TENANT_ADMINISTRATION,
)
from app.core.dependencies import AuthDep, DbDep
from app.core.module_guard import require_module
from app.modules.announcements.schemas import (
    AnnouncementCreate,
    AnnouncementResponse,
    AnnouncementUpdate,
)
from app.modules.announcements.service import AnnouncementService

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"],
    dependencies=[require_module("announcements")],
)


@router.get("/active", response_model=list[AnnouncementResponse])
async def list_active_announcements(
    current: AuthDep, db: DbDep
) -> list[AnnouncementResponse]:
    """Return active (published, not expired) announcements visible to the user."""
    service = AnnouncementService(db)
    return await service.list_visible_announcements(
        current.tenant_id, is_admin=current.has_capability(CAP_ANNOUNCEMENTS_WRITE)
    )


@router.get("/", response_model=list[AnnouncementResponse])
async def list_all_announcements(
    current: AuthDep, db: DbDep
) -> list[AnnouncementResponse]:
    """List all announcements for the tenant (admin only)."""
    require_capability(
        current,
        CAP_ANNOUNCEMENTS_WRITE,
        detail="Announcement write capability required",
    )
    service = AnnouncementService(db)
    return await service.list_announcements(current.tenant_id)


@router.get("/export")
async def export_announcements(current: AuthDep, db: DbDep) -> StreamingResponse:
    """Export announcements as CSV (admin only)."""
    require_capability(
        current,
        CAP_TENANT_ADMINISTRATION,
        detail="Tenant administration capability required",
    )
    service = AnnouncementService(db)
    csv_content = await service.export_csv(current.tenant_id)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=announcements.csv"},
    )


@router.get("/{announcement_id}", response_model=AnnouncementResponse)
async def get_announcement(
    announcement_id: UUID, current: AuthDep, db: DbDep
) -> AnnouncementResponse:
    """Get a specific announcement."""
    service = AnnouncementService(db)
    return await service.get_announcement(current.tenant_id, announcement_id)


@router.post("/", response_model=AnnouncementResponse, status_code=201)
async def create_announcement(
    data: AnnouncementCreate, current: AuthDep, db: DbDep
) -> AnnouncementResponse:
    """Create a new announcement (admin only)."""
    require_capability(
        current,
        CAP_ANNOUNCEMENTS_WRITE,
        detail="Announcement write capability required",
    )
    service = AnnouncementService(db)
    return await service.create_announcement(
        current.tenant_id, data, actor_user_id=current.user.id
    )


@router.patch("/{announcement_id}", response_model=AnnouncementResponse)
async def update_announcement(
    announcement_id: UUID, data: AnnouncementUpdate, current: AuthDep, db: DbDep
) -> AnnouncementResponse:
    """Update an announcement (admin only)."""
    require_capability(
        current,
        CAP_ANNOUNCEMENTS_WRITE,
        detail="Announcement write capability required",
    )
    service = AnnouncementService(db)
    return await service.update_announcement(
        current.tenant_id, announcement_id, data, actor_user_id=current.user.id
    )


@router.delete("/{announcement_id}", status_code=204)
async def delete_announcement(
    announcement_id: UUID, current: AuthDep, db: DbDep
) -> None:
    """Delete an announcement (admin only)."""
    require_capability(
        current,
        CAP_ANNOUNCEMENTS_WRITE,
        detail="Announcement write capability required",
    )
    service = AnnouncementService(db)
    await service.delete_announcement(
        current.tenant_id, announcement_id, actor_user_id=current.user.id
    )
