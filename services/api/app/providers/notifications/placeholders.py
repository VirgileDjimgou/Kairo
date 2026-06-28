from __future__ import annotations

from app.core.config import settings
from app.providers.notifications.base import (
    NotificationChannelDescriptor,
    NotificationDispatchResult,
)


class _PlaceholderNotificationProvider:
    channel = "base"
    display_name = "Base provider"
    description = "Simulation-only notification provider."
    target_hint = "Target"

    def __init__(self, *, configured: bool) -> None:
        self._configured = configured

    def describe(self) -> NotificationChannelDescriptor:
        return NotificationChannelDescriptor(
            channel=self.channel,
            display_name=self.display_name,
            description=self.description,
            configured=self._configured,
            simulation_only=True,
            target_hint=self.target_hint,
        )

    async def send_test_message(
        self,
        *,
        tenant_id,
        actor_user_id,
        recipient: str,
        subject: str | None,
        body: str,
    ) -> NotificationDispatchResult:
        label = "configured placeholder" if self._configured else "unconfigured placeholder"
        message = (
            f"{self.display_name} accepted a simulated message for {recipient}. "
            f"No external delivery was attempted ({label})."
        )
        if subject:
            message = f"{message} Subject: {subject}"
        if not body.strip():
            message = f"{message} Empty body received."
        return NotificationDispatchResult(
            channel=self.channel,
            status="simulated",
            message=message,
            delivered=False,
            simulation_only=True,
        )


class EmailNotificationProvider(_PlaceholderNotificationProvider):
    channel = "email"
    display_name = "Email"
    description = "SMTP-backed provider placeholder for transactional or broadcast email."
    target_hint = "Email address"

    def __init__(self) -> None:
        super().__init__(configured=bool(settings.smtp_host and settings.smtp_from_email))


class TelegramNotificationProvider(_PlaceholderNotificationProvider):
    channel = "telegram"
    display_name = "Telegram"
    description = "Bot-based provider placeholder for direct or channel-based Telegram messages."
    target_hint = "Telegram chat ID"

    def __init__(self) -> None:
        super().__init__(configured=bool(settings.telegram_bot_token))


class WhatsAppNotificationProvider(_PlaceholderNotificationProvider):
    channel = "whatsapp"
    display_name = "WhatsApp"
    description = "Gateway-based provider placeholder for WhatsApp notifications."
    target_hint = "Phone number or WhatsApp target"

    def __init__(self) -> None:
        super().__init__(configured=bool(settings.whatsapp_api_base_url and settings.whatsapp_api_token))
