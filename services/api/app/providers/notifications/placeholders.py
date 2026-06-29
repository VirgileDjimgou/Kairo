from __future__ import annotations

import asyncio
import smtplib
from email.message import EmailMessage

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

    async def send_message(
        self,
        *,
        tenant_id,
        actor_user_id,
        recipient: str,
        subject: str | None,
        body: str,
    ) -> NotificationDispatchResult:
        return await self._send_simulated(recipient=recipient, subject=subject, body=body)

    async def send_test_message(
        self,
        *,
        tenant_id,
        actor_user_id,
        recipient: str,
        subject: str | None,
        body: str,
    ) -> NotificationDispatchResult:
        return await self._send_simulated(recipient=recipient, subject=subject, body=body)

    async def _send_simulated(
        self,
        *,
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

    def describe(self) -> NotificationChannelDescriptor:
        descriptor = super().describe()
        if not self._configured:
            return descriptor
        return NotificationChannelDescriptor(
            channel=descriptor.channel,
            display_name=descriptor.display_name,
            description="SMTP-backed provider for transactional identity or operational email.",
            configured=True,
            simulation_only=False,
            target_hint=descriptor.target_hint,
        )

    async def send_message(
        self,
        *,
        tenant_id,
        actor_user_id,
        recipient: str,
        subject: str | None,
        body: str,
    ) -> NotificationDispatchResult:
        if not self._configured:
            return await self._send_simulated(recipient=recipient, subject=subject, body=body)

        try:
            await asyncio.to_thread(
                self._send_via_smtp,
                recipient=recipient,
                subject=subject or "Kairo notification",
                body=body,
            )
        except Exception as exc:  # pragma: no cover - exercised via tests with fakes
            return NotificationDispatchResult(
                channel=self.channel,
                status="failed",
                message=f"SMTP delivery failed for {recipient}: {exc}",
                delivered=False,
                simulation_only=False,
            )

        return NotificationDispatchResult(
            channel=self.channel,
            status="sent",
            message=f"SMTP delivery accepted for {recipient}.",
            delivered=True,
            simulation_only=False,
        )

    def _send_via_smtp(self, *, recipient: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["From"] = settings.smtp_from_email
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        use_ssl = settings.smtp_port == 465
        if use_ssl:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
                self._authenticate_if_needed(smtp)
                smtp.send_message(message)
            return

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
            smtp.ehlo()
            if settings.smtp_username or settings.smtp_password:
                smtp.starttls()
                smtp.ehlo()
            self._authenticate_if_needed(smtp)
            smtp.send_message(message)

    def _authenticate_if_needed(self, smtp: smtplib.SMTP) -> None:
        if settings.smtp_username and settings.smtp_password:
            smtp.login(settings.smtp_username, settings.smtp_password)


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
