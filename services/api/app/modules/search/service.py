from __future__ import annotations

import json
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.search.providers import SearchProvider, default_providers
from app.modules.search.schemas import SearchResponse, SearchResult
from app.modules.tenancy.module_toggles import is_module_enabled
from app.modules.tenancy.repository import TenancyRepository


class SearchService:
    """Aggregates modular search providers.

    Every provider enforces its own permission and tenant filtering BEFORE a
    result is produced; the service never receives unauthorized rows and never
    hides them client-side. Providers for disabled tenant modules are skipped.
    """

    def __init__(self, db: AsyncSession, providers: list[SearchProvider] | None = None) -> None:
        self._db = db
        self._providers = providers if providers is not None else default_providers()

    async def search(
        self,
        tenant_id: UUID,
        user_id: UUID,
        roles: list[str],
        query: str,
        limit: int = 20,
    ) -> SearchResponse:
        cleaned = query.strip()
        if not cleaned:
            return SearchResponse(query=query, results=[])

        modules = await self._module_toggles(tenant_id)
        collected: list[SearchResult] = []
        for provider in self._providers:
            if not provider.allowed(roles):
                continue
            if provider.module_key and not is_module_enabled(modules, provider.module_key):
                continue
            collected.extend(
                await provider.search(self._db, tenant_id, user_id, roles, cleaned, limit)
            )

        collected.sort(key=lambda row: (-row.score, row.type, row.title))
        return SearchResponse(query=query, results=collected[:limit])

    async def _module_toggles(self, tenant_id: UUID) -> dict[str, object]:
        repo = TenancyRepository(self._db)
        tenant = await repo.get_tenant_by_id(tenant_id)
        if not tenant:
            return {}
        if isinstance(tenant.settings_json, str) and tenant.settings_json.strip():
            try:
                parsed = json.loads(tenant.settings_json)
            except json.JSONDecodeError:
                return {}
            if isinstance(parsed, dict):
                return parsed
        return {}
