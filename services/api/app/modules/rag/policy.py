from __future__ import annotations

import json
from dataclasses import dataclass
from uuid import UUID

from app.modules.documents.models import Document, DocumentAccessScope

PRIVILEGED_DOCUMENT_ACCESS_ROLES = frozenset({"admin", "principal_admin"})


@dataclass(frozen=True)
class AccessPolicy:
    tenant_id: UUID
    user_id: UUID
    roles: tuple[str, ...]

    def can_access(self, document: Document) -> bool:
        if document.tenant_id != self.tenant_id:
            return False

        scope = document.access_scope
        if scope == DocumentAccessScope.tenant_public.value:
            return True
        if scope == DocumentAccessScope.members_only.value:
            return True
        if scope == DocumentAccessScope.admin_only.value:
            return self._has_privileged_document_access()
        if scope == DocumentAccessScope.user_private.value:
            return document.owner_user_id == self.user_id or self._has_privileged_document_access()
        if scope == DocumentAccessScope.role_restricted.value:
            if self._has_privileged_document_access():
                return True
            return bool(self._allowed_roles(document))
        return False

    def _has_privileged_document_access(self) -> bool:
        return any(role in PRIVILEGED_DOCUMENT_ACCESS_ROLES for role in self.roles)

    def _allowed_roles(self, document: Document) -> list[str]:
        raw = getattr(document, "allowed_role_ids_json", None)
        if not raw:
            return []
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return []
        if not isinstance(parsed, list):
            return []
        current_roles = set(self.roles)
        return [str(role) for role in parsed if str(role) in current_roles]
