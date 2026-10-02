from __future__ import annotations

from app.providers.push.base import (
    FirebasePushProvider,
    FirebasePushTarget,
    PushMessage,
    PushOutcome,
)


class FirebaseAdminPushProvider:
    """Firebase Cloud Messaging HTTP v1 delivery through firebase-admin."""

    def __init__(self, *, service_account_path: str | None) -> None:
        self._service_account_path = service_account_path

    def _ensure_app(self):
        import firebase_admin
        from firebase_admin import credentials

        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(self._service_account_path))

    def send(self, target: FirebasePushTarget, message: PushMessage) -> PushOutcome:
        try:
            from firebase_admin import exceptions as firebase_exceptions
            from firebase_admin import messaging
        except ImportError:
            return PushOutcome.FAILED
        try:
            self._ensure_app()
        except Exception:
            return PushOutcome.FAILED

        unregistered = getattr(messaging, "UnregisteredError", None)
        sender_mismatch = getattr(messaging, "SenderIdMismatchError", None)
        transient_types = tuple(
            error_type
            for error_type in (
                getattr(firebase_exceptions, "UnavailableError", None),
                getattr(firebase_exceptions, "InternalError", None),
                getattr(firebase_exceptions, "ResourceExhaustedError", None),
                getattr(firebase_exceptions, "AbortedError", None),
            )
            if error_type is not None
        )
        try:
            messaging.send(
                messaging.Message(
                    token=target.token,
                    notification=messaging.Notification(
                        title=message.title, body=message.body
                    ),
                    data={"target_path": message.target_path},
                    # Financial workflow alerts must wake a background Android
                    # client promptly; the inbox remains the authoritative detail.
                    android=messaging.AndroidConfig(priority="high"),
                )
            )
            return PushOutcome.DELIVERED
        except Exception as exc:
            if unregistered is not None and isinstance(exc, unregistered):
                return PushOutcome.INVALID_TARGET
            if sender_mismatch is not None and isinstance(exc, sender_mismatch):
                return PushOutcome.INVALID_TARGET
            if transient_types and isinstance(exc, transient_types):
                return PushOutcome.TRANSIENT
            return PushOutcome.TRANSIENT


class DisabledFirebasePushProvider:
    """Used when Firebase messaging is intentionally not configured."""

    def send(self, target: FirebasePushTarget, message: PushMessage) -> PushOutcome:
        return PushOutcome.FAILED


def build_default_firebase_push_provider() -> FirebasePushProvider:
    from app.core.config import settings

    return FirebaseAdminPushProvider(
        service_account_path=settings.firebase_service_account_path
    )
