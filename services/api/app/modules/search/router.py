from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from app.core.dependencies import AuthDep, DbDep
from app.modules.search.schemas import SearchResponse
from app.modules.search.service import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
async def global_search(
    current: AuthDep,
    db: DbDep,
    q: Annotated[str, Query(max_length=200)] = "",
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
) -> SearchResponse:
    """Permission-aware global search across authorized domains.

    Providers filter by tenant and role before returning results; titles of
    records the caller may not read are never produced.
    """
    return await SearchService(db).search(
        current.tenant_id,
        current.user.id,
        current.roles,
        q,
        limit,
    )
