from __future__ import annotations

from app.core.capabilities import CAP_DOCUMENTS_READ, CAP_DOCUMENTS_WRITE
from app.modules.module_registry.descriptor import ModuleDescriptor

MODULE = ModuleDescriptor(
    key="documents",
    name="Documents",
    description="Document ingestion, versions, access scopes and RAG sources.",
    capabilities=(CAP_DOCUMENTS_READ, CAP_DOCUMENTS_WRITE),
    router_module="app.modules.documents.router",
    router_order=70,
    search_order=20,
    search_providers=(("app.modules.search.providers", "DocumentsSearchProvider"),),
)
