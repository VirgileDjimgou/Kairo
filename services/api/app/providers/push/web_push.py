from __future__ import annotations

import json

from app.providers.push.base import (
    PushMessage,
    PushOutcome,
    WebPushProvider,
    WebPushTarget,
)


class WebPushLibProvider:
    """Standards-based Web Push + VAPID. Kept transport-neutral behind the protocol."""

    def __init__(self, *, vapid_private_key: str, vapid_subject: str) -> None:
        self._vapid_private_key = vapid_private_key
        self._vapid_subject = vapid_subject

    def send(self, target: WebPushTarget, message: PushMessage) -> PushOutcome:
        try:
            from pywebpush import WebPushException, webpush
        except ImportError:
            return PushOutcome.FAILED
        try:
            webpush(
                subscription_info={
                    "endpoint": target.endpoint,
                    "keys": {"p256dh": target.p256dh, "auth": target.auth},
                },
                data=json.dumps(
                    {
                        "title": message.title,
                        "body": message.body,
                        "url": message.target_path,
                    }
                ),
                vapid_private_key=self._vapid_private_key.replace(r"\n", "\n"),
                vapid_claims={"sub": self._vapid_subject},
            )
            return PushOutcome.DELIVERED
        except WebPushException as exc:
            response = getattr(exc, "response", None)
            status_code = getattr(response, "status_code", None)
            if status_code in {404, 410}:
                return PushOutcome.INVALID_TARGET
            return PushOutcome.TRANSIENT
        except Exception:
            return PushOutcome.TRANSIENT


class DisabledWebPushProvider:
    """Used when Web Push is intentionally not configured."""

    def send(self, target: WebPushTarget, message: PushMessage) -> PushOutcome:
        return PushOutcome.FAILED


def build_default_web_push_provider() -> WebPushProvider:
    from app.core.config import settings

    return WebPushLibProvider(
        vapid_private_key=settings.web_push_vapid_private_key or "",
        vapid_subject=settings.web_push_vapid_subject,
    )
