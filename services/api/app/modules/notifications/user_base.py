from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.providers.push.base import FirebasePushProvider, WebPushProvider
from app.providers.push.firebase import build_default_firebase_push_provider
from app.providers.push.web_push import build_default_web_push_provider


class UserNotificationServiceBase:
    """Inbox, device binding and push delivery hints.

    Browser and Android push payloads are deliberately generic: the user must
    authenticate before seeing any financial or disciplinary detail in the inbox.
    Push transports are injected so delivery stays testable and replaceable.
    """

    def __init__(
        self,
        db: AsyncSession,
        *,
        web_push_provider: WebPushProvider | None = None,
        firebase_push_provider: FirebasePushProvider | None = None,
    ) -> None:
        self._db = db
        self._web_push_provider = web_push_provider
        self._firebase_push_provider = firebase_push_provider

    @property
    def web_push_provider(self) -> WebPushProvider:
        if self._web_push_provider is None:
            self._web_push_provider = build_default_web_push_provider()
        return self._web_push_provider

    @property
    def firebase_push_provider(self) -> FirebasePushProvider:
        if self._firebase_push_provider is None:
            self._firebase_push_provider = build_default_firebase_push_provider()
        return self._firebase_push_provider
