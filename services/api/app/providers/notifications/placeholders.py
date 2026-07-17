from __future__ import annotations

import asyncio
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid

import httpx

from app.core.config import settings
from app.providers.notifications.base import (
    NotificationChannelDescriptor,
    NotificationDeliveryStatusResult,
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
            polling_supported=False,
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
            delivery_stage="simulated",
            reconciliation_status="not_applicable",
            reconciliation_supported=False,
            polling_supported=False,
        )

    async def fetch_delivery_status(
        self,
        *,
        tenant_id,
        actor_user_id,
        recipient: str,
        provider_reference: str,
    ) -> NotificationDeliveryStatusResult | None:
        return None


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
            polling_supported=False,
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
            provider_reference = await asyncio.to_thread(
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
                delivery_stage="failed",
                reconciliation_status="failed",
                reconciliation_supported=True,
            )

        return NotificationDispatchResult(
            channel=self.channel,
            status="sent",
            message=f"SMTP delivery accepted for {recipient}.",
            delivered=True,
            simulation_only=False,
            delivery_stage="accepted",
            reconciliation_status="pending",
            reconciliation_supported=True,
            provider_reference=provider_reference,
            polling_supported=False,
        )

    def _send_via_smtp(self, *, recipient: str, subject: str, body: str) -> str:
        message = EmailMessage()
        message["From"] = settings.smtp_from_email
        message["To"] = recipient
        message["Subject"] = subject
        message["Message-ID"] = make_msgid()
        message.set_content(body)

        use_ssl = settings.smtp_port == 465
        if use_ssl:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
                self._authenticate_if_needed(smtp)
                smtp.send_message(message)
            return str(message["Message-ID"])

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
            smtp.ehlo()
            if settings.smtp_username or settings.smtp_password:
                smtp.starttls()
                smtp.ehlo()
            self._authenticate_if_needed(smtp)
            smtp.send_message(message)
        return str(message["Message-ID"])

    def _authenticate_if_needed(self, smtp: smtplib.SMTP) -> None:
        if settings.smtp_username and settings.smtp_password:
            smtp.login(settings.smtp_username, settings.smtp_password)


class TelegramNotificationProvider(_PlaceholderNotificationProvider):
    channel = "telegram"
    display_name = "Telegram"
    description = "Bot-based provider placeholder for direct or channel-based Telegram messages."
    target_hint = "Telegram chat ID or @channel username"

    def __init__(self) -> None:
        super().__init__(configured=bool(settings.telegram_bot_token))

    def describe(self) -> NotificationChannelDescriptor:
        descriptor = super().describe()
        if not self._configured:
            return descriptor
        return NotificationChannelDescriptor(
            channel=descriptor.channel,
            display_name=descriptor.display_name,
            description="Telegram Bot API provider for direct operator or channel notifications.",
            configured=True,
            simulation_only=False,
            target_hint=descriptor.target_hint,
            polling_supported=False,
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
            provider_reference = await self._send_via_telegram(
                recipient=recipient or settings.telegram_default_chat_id or "",
                subject=subject,
                body=body,
            )
        except Exception as exc:  # pragma: no cover - exercised via tests with fakes
            return NotificationDispatchResult(
                channel=self.channel,
                status="failed",
                message=f"Telegram delivery failed for {recipient}: {exc}",
                delivered=False,
                simulation_only=False,
                delivery_stage="failed",
                reconciliation_status="failed",
                reconciliation_supported=True,
            )

        return NotificationDispatchResult(
            channel=self.channel,
            status="sent",
            message=f"Telegram delivery accepted for {recipient}.",
            delivered=True,
            simulation_only=False,
            delivery_stage="accepted",
            reconciliation_status="pending",
            reconciliation_supported=True,
            provider_reference=provider_reference,
            polling_supported=False,
        )

    async def _send_via_telegram(self, *, recipient: str, subject: str | None, body: str) -> str | None:
        if not recipient.strip():
            raise ValueError("Telegram target is required for live delivery")

        text = body.strip()
        if subject and subject.strip():
            text = f"*{subject.strip()}*\n\n{text}"

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
                json={
                    "chat_id": recipient,
                    "text": text,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": True,
                },
            )
            response.raise_for_status()
            payload = response.json()
            if not payload.get("ok", False):
                raise ValueError(payload.get("description", "Telegram API rejected the message"))
            result = payload.get("result", {})
            message_id = result.get("message_id")
            return str(message_id) if message_id is not None else None


class WhatsAppNotificationProvider(_PlaceholderNotificationProvider):
    channel = "whatsapp"
    display_name = "WhatsApp"
    description = "Gateway-based provider placeholder for WhatsApp notifications."
    target_hint = "Phone number or WhatsApp target"

    def __init__(self) -> None:
        super().__init__(configured=bool(settings.whatsapp_api_base_url and settings.whatsapp_api_token))

    def describe(self) -> NotificationChannelDescriptor:
        descriptor = super().describe()
        if not self._configured:
            return descriptor
        return NotificationChannelDescriptor(
            channel=descriptor.channel,
            display_name=descriptor.display_name,
            description="Gateway-backed provider for operator WhatsApp notifications.",
            configured=True,
            simulation_only=False,
            target_hint=descriptor.target_hint,
            polling_supported=True,
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
            provider_reference = await self._send_via_gateway(
                recipient=recipient,
                subject=subject,
                body=body,
            )
        except Exception as exc:  # pragma: no cover - exercised via tests with fakes
            return NotificationDispatchResult(
                channel=self.channel,
                status="failed",
                message=f"WhatsApp delivery failed for {recipient}: {exc}",
                delivered=False,
                simulation_only=False,
                delivery_stage="failed",
                reconciliation_status="failed",
                reconciliation_supported=True,
            )

        return NotificationDispatchResult(
            channel=self.channel,
            status="sent",
            message=f"WhatsApp delivery accepted for {recipient}.",
            delivered=True,
            simulation_only=False,
            delivery_stage="accepted",
            reconciliation_status="pending",
            reconciliation_supported=True,
            provider_reference=provider_reference,
            polling_supported=True,
        )

    async def _send_via_gateway(self, *, recipient: str, subject: str | None, body: str) -> str | None:
        if not recipient.strip():
            raise ValueError("WhatsApp target is required for live delivery")

        payload = {
            "to": recipient,
            "body": body,
        }
        if subject and subject.strip():
            payload["subject"] = subject.strip()

        base_url = (settings.whatsapp_api_base_url or "").rstrip("/")
        if not base_url:
            raise ValueError("WhatsApp gateway base URL is required")

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{base_url}/messages",
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.whatsapp_api_token}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            if response.headers.get("content-type", "").startswith("application/json"):
                response_payload = response.json()
                if response_payload.get("ok") is False:
                    raise ValueError(response_payload.get("detail", "WhatsApp gateway rejected the message"))
                for key in ("message_id", "id", "reference"):
                    value = response_payload.get(key)
                    if value is not None:
                        return str(value)
        return None

    async def fetch_delivery_status(
        self,
        *,
        tenant_id,
        actor_user_id,
        recipient: str,
        provider_reference: str,
    ) -> NotificationDeliveryStatusResult | None:
        if not self._configured:
            return None

        base_url = (settings.whatsapp_api_base_url or "").rstrip("/")
        if not base_url:
            return None

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                f"{base_url}/messages/{provider_reference}",
                headers={
                    "Authorization": f"Bearer {settings.whatsapp_api_token}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            payload = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}

        normalized = str(
            payload.get("delivery_stage")
            or payload.get("reconciliation_status")
            or payload.get("status")
            or payload.get("state")
            or "pending"
        ).lower()
        message = str(
            payload.get("provider_message")
            or payload.get("message")
            or payload.get("detail")
            or "WhatsApp gateway reconciliation is still pending."
        )

        if normalized in {"delivered", "sent", "success"}:
            return NotificationDeliveryStatusResult(
                delivery_stage="delivered",
                reconciliation_status="delivered",
                delivered=True,
                provider_message=message,
                external_status=normalized,
                terminal=True,
            )

        if normalized in {"failed", "error", "rejected", "undelivered"}:
            return NotificationDeliveryStatusResult(
                delivery_stage="failed",
                reconciliation_status="failed",
                delivered=False,
                provider_message=message,
                external_status=normalized,
                terminal=True,
            )

        return NotificationDeliveryStatusResult(
            delivery_stage="accepted",
            reconciliation_status="pending",
            delivered=False,
            provider_message=message,
            external_status=normalized,
            terminal=False,
        )
