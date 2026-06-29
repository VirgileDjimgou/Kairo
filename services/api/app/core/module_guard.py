import json
from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.core.dependencies import AuthDep, DbDep
from app.modules.tenancy.module_toggles import is_module_enabled
from app.modules.tenancy.repository import TenancyRepository


def require_module(module_key: str) -> Callable:
    """
    FastAPI dependency factory that rejects requests when a module
    is disabled for the current tenant.

    Usage::

        router = APIRouter(..., dependencies=[require_module("membership")])
    """

    async def _guard(current: AuthDep, db: DbDep) -> None:
        repo = TenancyRepository(db)
        tenant = await repo.get_tenant_by_id(current.tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        raw_json = {}
        if isinstance(tenant.settings_json, str) and tenant.settings_json.strip():
            try:
                raw_json = json.loads(tenant.settings_json)
            except json.JSONDecodeError:
                raw_json = {}
        if not is_module_enabled(raw_json, module_key):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"The '{module_key}' module is disabled for this organization",
            )

    return Depends(_guard)
