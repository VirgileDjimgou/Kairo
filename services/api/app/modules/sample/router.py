from __future__ import annotations

from fastapi import APIRouter

from app.core.authorization import require_capability
from app.core.capabilities import CAP_AUDIT_READ
from app.core.dependencies import AuthDep

router = APIRouter(prefix="/sample", tags=["sample"])


@router.get("/status")
async def sample_status(current: AuthDep) -> dict[str, str]:
    """Read-only extension probe; authority still comes from the backend."""
    require_capability(current, CAP_AUDIT_READ, detail="Audit read capability required")
    return {"module": "sample", "status": "ok"}
