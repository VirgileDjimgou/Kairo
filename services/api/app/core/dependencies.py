from dataclasses import dataclass
from functools import lru_cache
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import async_session_factory

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

    def has_role(self, *role_codes: str) -> bool:
        return any(r in self.roles for r in role_codes)


async def get_db() -> AsyncSession:  # type: ignore[misc]
    """FastAPI dependency: yields an async SQLAlchemy session."""
    async with async_session_factory() as session:
        yield session


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
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
        token_type: str | None = payload.get("type")

        if not user_id_str or not tenant_id_str or token_type != "access":
            raise unauthorized

        user_id = UUID(user_id_str)
        tenant_id = UUID(tenant_id_str)
        roles: list[str] = payload.get("roles", [])

    except (jwt.PyJWTError, ValueError):
        raise unauthorized

    # Import locally to break circular dependency
    from app.modules.identity.repository import UserRepository

    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)

    if user is None or user.status != "active":
        raise unauthorized

    return CurrentUser(user=user, tenant_id=tenant_id, roles=roles)


# Convenience type alias for route signatures
AuthDep = Annotated[CurrentUser, Depends(get_current_user)]
DbDep = Annotated[AsyncSession, Depends(get_db)]


@lru_cache(maxsize=1)
def get_object_storage_provider():
    """Return the singleton object storage provider (MinIO in production)."""
    from app.providers.object_storage.minio import MinIOObjectStorageProvider

    return MinIOObjectStorageProvider()


ObjectStorageDep = Annotated[object, Depends(get_object_storage_provider)]
