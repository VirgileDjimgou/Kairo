from dataclasses import dataclass
from functools import lru_cache
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import async_session_factory
from app.providers.llm.base import LLMProvider
from app.providers.embeddings.base import EmbeddingProvider
from app.providers.vector_store.base import VectorStoreProvider
from app.providers.object_storage.base import ObjectStorageProvider
from app.providers.notifications.base import NotificationProvider
from app.providers.reranker.interface import RerankerProvider

_bearer_scheme = HTTPBearer(auto_error=True)


@dataclass(frozen=True)
class CurrentUser:
    """
    Resolved auth context attached to every protected request.

    Carries the authenticated User ORM object, the active tenant UUID,
    and the list of role codes resolved from the JWT.
    """

    user: object  # app.modules.identity.models.User (typed here to avoid circular import)
    tenant_id: UUID
    roles: list[str]
    session_id: UUID

    def has_role(self, *role_codes: str) -> bool:
        return any(r in self.roles for r in role_codes)

    def has_capability(self, capability: str) -> bool:
        from app.core.capabilities import has_capability

        return has_capability(self.roles, capability)


async def get_db() -> AsyncSession:  # type: ignore[misc]
    """FastAPI dependency: yields an async SQLAlchemy session."""
    async with async_session_factory() as session:
        yield session


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
    request: Request,
) -> CurrentUser:
    """
    FastAPI dependency: decode JWT, validate, load User from DB.

    Raises HTTP 401 on any invalid token or inactive user.
    """
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id_str: str | None = payload.get("sub")
        tenant_id_str: str | None = payload.get("tenant_id")
        session_id_str: str | None = payload.get("sid")
        token_type: str | None = payload.get("type")

        if not user_id_str or not tenant_id_str or not session_id_str or token_type != "access":
            raise unauthorized

        user_id = UUID(user_id_str)
        tenant_id = UUID(tenant_id_str)
        session_id = UUID(session_id_str)
        roles: list[str] = payload.get("roles", [])

    except (jwt.PyJWTError, ValueError):
        raise unauthorized

    # Import locally to break circular dependency
    from app.modules.identity.repository import UserRepository, UserSessionRepository
    from app.modules.tenancy.repository import TenancyRepository

    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    session_repo = UserSessionRepository(db)
    session = await session_repo.get_active_by_id(session_id)
    tenancy_repo = TenancyRepository(db)
    membership = await tenancy_repo.get_tenant_user(tenant_id, user_id)

    if (
        user is None
        or user.status != "active"
        or session is None
        or session.user_id != user_id
        or membership is None
        or membership.membership_status != "active"
    ):
        raise unauthorized

    forwarded = request.headers.get("X-Forwarded-For") if request else None
    ip_address = (
        forwarded.split(",")[0].strip()
        if forwarded
        else request.client.host if request and request.client else None
    )
    user_agent = request.headers.get("User-Agent") if request else None
    await session_repo.touch(
        session_id,
        tenant_id=tenant_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return CurrentUser(user=user, tenant_id=tenant_id, roles=roles, session_id=session_id)


# Convenience type alias for route signatures
AuthDep = Annotated[CurrentUser, Depends(get_current_user)]
DbDep = Annotated[AsyncSession, Depends(get_db)]


@lru_cache(maxsize=1)
def get_object_storage_provider() -> ObjectStorageProvider:
    """Return the singleton object storage provider (MinIO in production)."""
    from app.providers.object_storage.minio import MinIOObjectStorageProvider

    return MinIOObjectStorageProvider()


ObjectStorageDep = Annotated[ObjectStorageProvider, Depends(get_object_storage_provider)]


@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:
    from app.providers.embeddings.ollama import OllamaEmbeddingProvider

    return OllamaEmbeddingProvider()


@lru_cache(maxsize=1)
def get_vector_store_provider() -> VectorStoreProvider:
    from app.providers.vector_store.qdrant import QdrantVectorStoreProvider

    return QdrantVectorStoreProvider()


EmbeddingDep = Annotated[EmbeddingProvider, Depends(get_embedding_provider)]
VectorStoreDep = Annotated[VectorStoreProvider, Depends(get_vector_store_provider)]


@lru_cache(maxsize=1)
def get_llm_provider() -> LLMProvider:
    from app.providers.llm.ollama import OllamaLLMProvider

    return OllamaLLMProvider()


LlmDep = Annotated[LLMProvider, Depends(get_llm_provider)]


@lru_cache(maxsize=1)
def get_notification_providers() -> list[NotificationProvider]:
    from app.providers.notifications import (
        EmailNotificationProvider,
        TelegramNotificationProvider,
        WhatsAppNotificationProvider,
    )

    return [
        EmailNotificationProvider(),
        TelegramNotificationProvider(),
        WhatsAppNotificationProvider(),
    ]


NotificationsDep = Annotated[list[NotificationProvider], Depends(get_notification_providers)]


@lru_cache(maxsize=1)
def get_reranker_provider() -> RerankerProvider:
    from app.providers.reranker.sentence_transformers import SentenceTransformersReranker

    return SentenceTransformersReranker()


RerankerDep = Annotated[RerankerProvider, Depends(get_reranker_provider)]
