from typing import Union
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status

from app.core.dependencies import AuthDep, DbDep
from app.core.rate_limiter import rate_limiter
from app.modules.identity.schemas import (
    AcceptInviteRequest,
    AcceptInviteResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    InvitationStatusResponse,
    InviteRequest,
    InviteResponse,
    LoginRequest,
    MfaCompleteLoginRequest,
    MfaEnrollResponse,
    MfaLoginResponse,
    MfaRequiredResponse,
    MfaVerifyRequest,
    MfaVerifyResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    SwitchTenantRequest,
    SwitchTenantResponse,
    TokenResponse,
    UserResponse,
    UserWithMembershipsResponse,
)
from app.modules.identity.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _rate_limit_or_429(key: str, *, max_requests: int, window_seconds: int) -> None:
    if not rate_limiter.check(key, max_requests=max_requests, window_seconds=window_seconds):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
        )


@router.post("/login", response_model=Union[TokenResponse, MfaRequiredResponse])
async def login(
    request: LoginRequest,
    db: DbDep,
    fastapi_request: Request,
) -> Union[TokenResponse, MfaRequiredResponse]:
    """Authenticate with email + password. Returns JWT or MFA challenge."""
    ip = _client_ip(fastapi_request)
    if not rate_limiter.check(f"login:{ip}", max_requests=10, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
        )
    service = AuthService(db)
    return await service.login(request)


@router.post("/mfa/complete", response_model=MfaLoginResponse)
async def mfa_complete_login(
    request: MfaCompleteLoginRequest,
    db: DbDep,
    fastapi_request: Request,
) -> MfaLoginResponse:
    """Complete a login that requires MFA by providing a TOTP code."""
    ip = _client_ip(fastapi_request)
    if not rate_limiter.check(f"mfa:{ip}", max_requests=5, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many MFA attempts. Please try again later.",
        )
    service = AuthService(db)
    return await service.complete_mfa_login(request)


@router.get("/me", response_model=UserWithMembershipsResponse)
async def get_me(current: AuthDep, db: DbDep) -> UserWithMembershipsResponse:
    """Return the currently authenticated user's profile with all tenant memberships."""
    service = AuthService(db)
    memberships = await service.get_user_memberships(current.user.id)
    return UserWithMembershipsResponse(
        id=current.user.id,
        email=current.user.email,
        display_name=current.user.display_name,
        status=current.user.status,
        tenant_id=current.tenant_id,
        roles=current.roles,
        last_login_at=current.user.last_login_at,
        memberships=memberships,
    )


@router.post("/switch-tenant", response_model=SwitchTenantResponse)
async def switch_tenant(
    request: SwitchTenantRequest, current: AuthDep, db: DbDep
) -> SwitchTenantResponse:
    """Switch the active tenant for the current user."""
    service = AuthService(db)
    return await service.switch_tenant(current.user.id, request)


# ── Invitation Endpoints ──────────────────────────────────────────────────────

@router.post("/invite", response_model=InviteResponse, status_code=201)
async def invite_user(
    request: InviteRequest,
    current: AuthDep,
    db: DbDep,
    fastapi_request: Request,
) -> InviteResponse:
    """Invite a user to join an organization (admin only)."""
    _rate_limit_or_429(
        f"invite:{current.user.id}:{_client_ip(fastapi_request)}",
        max_requests=10,
        window_seconds=300,
    )
    service = AuthService(db)
    return await service.invite_user(
        request,
        current.user.id,
        actor_user_id=current.user.id,
    )


@router.post("/accept-invite", response_model=AcceptInviteResponse)
async def accept_invite(
    request: AcceptInviteRequest,
    db: DbDep,
    fastapi_request: Request,
) -> AcceptInviteResponse:
    """Accept an invitation using the token received from the invite flow."""
    _rate_limit_or_429(
        f"accept-invite:{_client_ip(fastapi_request)}",
        max_requests=5,
        window_seconds=300,
    )
    service = AuthService(db)
    return await service.accept_invite(request)


@router.get(
    "/invitations/{tenant_id}",
    response_model=list[InvitationStatusResponse],
)
async def list_invitations(
    tenant_id: UUID,
    current: AuthDep,
    db: DbDep,
) -> list[InvitationStatusResponse]:
    """List all invitations for an organization (admin only)."""
    service = AuthService(db)
    return await service.list_invitations(tenant_id, current.user.id)


@router.delete(
    "/invitations/{invitation_id}",
    status_code=204,
)
async def cancel_invitation(
    invitation_id: UUID,
    current: AuthDep,
    db: DbDep,
) -> None:
    """Cancel a pending invitation (admin only)."""
    service = AuthService(db)
    await service.cancel_invitation(
        invitation_id,
        current.tenant_id,
        current.user.id,
        actor_user_id=current.user.id,
    )


# ── Password Reset Endpoints ──────────────────────────────────────────────────

@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: DbDep,
    fastapi_request: Request,
) -> ForgotPasswordResponse:
    """Request a password reset token."""
    ip = _client_ip(fastapi_request)
    _rate_limit_or_429(f"forgot-password:{ip}", max_requests=3, window_seconds=300)
    service = AuthService(db)
    return await service.forgot_password(request)


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: DbDep,
    fastapi_request: Request,
) -> ResetPasswordResponse:
    """Reset password using a valid reset token."""
    _rate_limit_or_429(
        f"reset-password:{_client_ip(fastapi_request)}",
        max_requests=5,
        window_seconds=300,
    )
    service = AuthService(db)
    return await service.reset_password(request)


# ── MFA Endpoints ─────────────────────────────────────────────────────────────

@router.post("/mfa/enroll", response_model=MfaEnrollResponse)
async def enroll_mfa(
    current: AuthDep,
    db: DbDep,
    fastapi_request: Request,
) -> MfaEnrollResponse:
    """Generate and configure a TOTP secret for MFA."""
    _rate_limit_or_429(
        f"mfa-enroll:{current.user.id}:{_client_ip(fastapi_request)}",
        max_requests=5,
        window_seconds=300,
    )
    service = AuthService(db)
    return await service.enroll_mfa(current.user.id, current.user.email)


@router.post("/mfa/verify", response_model=MfaVerifyResponse)
async def verify_mfa(
    request: MfaVerifyRequest,
    current: AuthDep,
    db: DbDep,
    fastapi_request: Request,
) -> MfaVerifyResponse:
    """Verify a TOTP code and enable MFA on the account."""
    _rate_limit_or_429(
        f"mfa-verify:{current.user.id}:{_client_ip(fastapi_request)}",
        max_requests=5,
        window_seconds=300,
    )
    service = AuthService(db)
    return await service.verify_and_enable_mfa(
        current.user.id, request, tenant_id=current.tenant_id
    )


@router.delete("/mfa", status_code=204)
async def disable_mfa(
    current: AuthDep,
    db: DbDep,
) -> None:
    """Disable MFA on the current account."""
    service = AuthService(db)
    await service.disable_mfa(current.user.id, tenant_id=current.tenant_id)


# ── Token Refresh ─────────────────────────────────────────────────────────────

@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: DbDep,
) -> RefreshTokenResponse:
    """Issue a new access token using a valid refresh token."""
    service = AuthService(db)
    return await service.refresh_token(request)


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
