from __future__ import annotations

from fastapi import APIRouter

from app.core.dependencies import AuthDep, DbDep
from app.modules.attention.schemas import AttentionOverview
from app.modules.attention.service import AttentionService

router = APIRouter(prefix="/attention", tags=["attention"])


@router.get("", response_model=AttentionOverview)
async def get_attention_overview(current: AuthDep, db: DbDep) -> AttentionOverview:
    """Role-aware attention cards for the action center.

    The endpoint is authenticated and tenant-scoped; every card is computed
    only from records the caller's roles may already read. No card exposes a
    count the role could not obtain through its own module surfaces.
    """
    items = await AttentionService(db).overview(
        current.tenant_id,
        current.user.id,
        current.roles,
    )
    return AttentionOverview(items=items)
