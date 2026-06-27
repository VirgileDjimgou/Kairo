from fastapi import APIRouter

from app.core.dependencies import AuthDep, DbDep
from app.modules.identity.schemas import LoginRequest, TokenResponse, UserResponse
from app.modules.identity.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: DbDep) -> TokenResponse:
    """Authenticate with email + password and receive a JWT access token."""
    service = AuthService(db)
    return await service.login(request)


@router.get("/me", response_model=UserResponse)
async def get_me(current: AuthDep) -> UserResponse:
    """Return the currently authenticated user's profile."""
    user = current.user
    return UserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        status=user.status,
        tenant_id=current.tenant_id,
        roles=current.roles,
        last_login_at=user.last_login_at,
    )


@router.get("/protected", response_model=dict)
async def protected_test(current: AuthDep) -> dict:
    """
    Sprint 1 acceptance test endpoint.
    Returns 200 only with a valid JWT. Used in integration tests.
    """
    return {
        "message": "Protected endpoint works",
        "user_id": str(current.user.id),
        "tenant_id": str(current.tenant_id),
        "roles": current.roles,
    }
