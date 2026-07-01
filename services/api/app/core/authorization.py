from fastapi import HTTPException, status

from app.core.dependencies import CurrentUser


def require_capability(
    current: CurrentUser,
    capability: str,
    *,
    detail: str | None = None,
) -> None:
    if current.has_capability(capability):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail or f"Capability '{capability}' required",
    )
