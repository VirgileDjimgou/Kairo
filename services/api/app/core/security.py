import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
import pyotp
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


def create_access_token(
    user_id: UUID,
    tenant_id: UUID,
    roles: list[str],
    session_id: UUID,
) -> str:
    now = datetime.now(UTC)
    payload: dict = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "roles": roles,
        "sid": str(session_id),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )


def create_refresh_token(user_id: UUID, session_id: UUID) -> str:
    now = datetime.now(UTC)
    payload: dict = {
        "sub": str(user_id),
        "sid": str(session_id),
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=settings.refresh_token_expire_days),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_mfa_token(user_id: UUID, tenant_id: UUID | None = None) -> str:
    now = datetime.now(UTC)
    payload: dict = {
        "sub": str(user_id),
        "type": "mfa",
        "iat": now,
        "exp": now + timedelta(minutes=5),
    }
    if tenant_id is not None:
        payload["tenant_id"] = str(tenant_id)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str, issuer: str = "Kairo") -> str:
    return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)


def verify_totp(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


def generate_token() -> str:
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    """Deterministic SHA-256 hash for tokens (passlib uses random salt)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_token(token: str, token_hash: str) -> bool:
    return hashlib.sha256(token.encode("utf-8")).hexdigest() == token_hash
