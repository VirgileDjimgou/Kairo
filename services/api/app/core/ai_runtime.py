from fastapi import HTTPException, status

from app.core.config import settings


def require_ai_runtime() -> None:
    """Reject AI operations while leaving all business modules operational."""
    if not settings.ai_runtime_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Assistant IA désactivé par l’association",
        )
