from __future__ import annotations

from uuid import UUID

from qdrant_client.models import FieldCondition, Filter, MatchValue

from app.modules.rag.policy import AccessPolicy


def build_tenant_filter(tenant_id: UUID) -> Filter:
    return Filter(
        must=[
            FieldCondition(key="tenant_id", match=MatchValue(value=str(tenant_id))),
        ]
    )


def build_access_policy(*, tenant_id: UUID, user_id: UUID, roles: list[str]) -> AccessPolicy:
    return AccessPolicy(tenant_id=tenant_id, user_id=user_id, roles=tuple(roles))
