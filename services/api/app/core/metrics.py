from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from threading import Lock

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.audit.models import AuditEvent
from app.modules.chat.models import ChatQueryLog
from app.modules.documents.models import IngestionJob


def _status_class(status_code: int) -> str:
    return f"{status_code // 100}xx"


def _render_labels(labels: dict[str, str]) -> str:
    if not labels:
        return ""
    joined = ",".join(f'{key}="{value}"' for key, value in labels.items())
    return f"{{{joined}}}"


@dataclass
class ObservabilityMetrics:
    _lock: Lock = field(default_factory=Lock)
    http_requests: Counter[tuple[str, str]] = field(default_factory=Counter)
    http_request_latency_ms_sum: Counter[tuple[str, str]] = field(default_factory=Counter)
    http_request_latency_ms_count: Counter[tuple[str, str]] = field(default_factory=Counter)
    error_counts: Counter[str] = field(default_factory=Counter)
    push_deliveries: Counter[tuple[str, str]] = field(default_factory=Counter)

    def record_http_request(self, method: str, status_code: int, latency_ms: int) -> None:
        key = (method.upper(), _status_class(status_code))
        with self._lock:
            self.http_requests[key] += 1
            self.http_request_latency_ms_sum[key] += max(0, latency_ms)
            self.http_request_latency_ms_count[key] += 1

    def record_error(self, error_code: str) -> None:
        with self._lock:
            self.error_counts[error_code] += 1

    def record_push_delivery(self, channel: str, outcome: str) -> None:
        with self._lock:
            self.push_deliveries[(channel, outcome)] += 1

    def reset(self) -> None:
        with self._lock:
            self.http_requests.clear()
            self.http_request_latency_ms_sum.clear()
            self.http_request_latency_ms_count.clear()
            self.error_counts.clear()
            self.push_deliveries.clear()

    def render(self) -> str:
        lines: list[str] = [
            "# HELP kairo_http_requests_total Total HTTP requests by method and status class.",
            "# TYPE kairo_http_requests_total counter",
        ]
        with self._lock:
            for (method, status_class), count in sorted(self.http_requests.items()):
                lines.append(
                    f'kairo_http_requests_total{_render_labels({"method": method, "status_class": status_class})} {count}'
                )

            lines.extend(
                [
                    "# HELP kairo_http_request_latency_ms_sum Total request latency in milliseconds.",
                    "# TYPE kairo_http_request_latency_ms_sum counter",
                ]
            )
            for (method, status_class), total in sorted(self.http_request_latency_ms_sum.items()):
                lines.append(
                    f'kairo_http_request_latency_ms_sum{_render_labels({"method": method, "status_class": status_class})} {total}'
                )

            lines.extend(
                [
                    "# HELP kairo_http_request_latency_ms_count Total request count for latency aggregation.",
                    "# TYPE kairo_http_request_latency_ms_count counter",
                ]
            )
            for (method, status_class), count in sorted(self.http_request_latency_ms_count.items()):
                lines.append(
                    f'kairo_http_request_latency_ms_count{_render_labels({"method": method, "status_class": status_class})} {count}'
                )

            lines.extend(
                [
                    "# HELP kairo_error_total Total structured errors by error code.",
                    "# TYPE kairo_error_total counter",
                ]
            )
            for error_code, count in sorted(self.error_counts.items()):
                lines.append(f'kairo_error_total{_render_labels({"code": error_code})} {count}')

            lines.extend(
                [
                    "# HELP kairo_push_deliveries_total Push delivery outcomes by channel and result.",
                    "# TYPE kairo_push_deliveries_total counter",
                ]
            )
            for (channel, outcome), count in sorted(self.push_deliveries.items()):
                lines.append(
                    f'kairo_push_deliveries_total{_render_labels({"channel": channel, "outcome": outcome})} {count}'
                )

            for channel, success_metric, failure_metric in (
                ("web_push", "kairo_web_push_success_total", "kairo_web_push_failure_total"),
                ("firebase", "kairo_fcm_success_total", "kairo_fcm_failure_total"),
            ):
                success = self.push_deliveries.get((channel, "delivered"), 0)
                failure = sum(
                    count
                    for (entry_channel, outcome), count in self.push_deliveries.items()
                    if entry_channel == channel and outcome != "delivered"
                )
                lines.extend(
                    [
                        f"# HELP {success_metric} Successful {channel} push deliveries.",
                        f"# TYPE {success_metric} counter",
                        f"{success_metric} {success}",
                        f"# HELP {failure_metric} Failed or invalid {channel} push deliveries.",
                        f"# TYPE {failure_metric} counter",
                        f"{failure_metric} {failure}",
                    ]
                )

        return "\n".join(lines) + "\n"


metrics = ObservabilityMetrics()


def normalize_error_code(status_code: int, detail: object) -> str:
    if status_code == 422:
        return "validation_error"
    if status_code == 400:
        return "bad_request"
    if status_code == 401:
        return "unauthorized"
    if status_code == 403:
        return "forbidden"
    if status_code == 404:
        return "not_found"
    if status_code == 409:
        return "conflict"
    if status_code == 413:
        return "payload_too_large"
    if status_code == 415:
        return "unsupported_media_type"
    if status_code == 429:
        return "rate_limited"
    if status_code >= 500:
        return "internal_error"
    if isinstance(detail, str) and detail:
        return detail.lower().replace(" ", "_")[:80]
    return "request_error"


async def build_runtime_metrics(db: AsyncSession) -> str:
    # Imported lazily: the notifications package re-exports its router, and a
    # module-level import here would create a cycle for tools that import
    # ``app.main`` for schema generation.
    from app.modules.backup.models import BackupRun
    from app.modules.domain_events.models import DomainEvent
    from app.modules.notifications.user_models import (
        FirebasePushSubscription,
        NotificationOutboxEvent,
        WebPushSubscription,
    )

    lines = [line for line in metrics.render().rstrip().splitlines() if line]

    ingestion_counts = await db.execute(
        select(IngestionJob.status, func.count()).group_by(IngestionJob.status)
    )
    status_counts: dict[str, int] = dict(ingestion_counts.all())  # type: ignore[arg-type]
    queued = int(status_counts.get("pending", 0))
    processing = int(status_counts.get("processing", 0))
    failed = int(status_counts.get("failed", 0))
    completed = int(status_counts.get("completed", 0))
    retried = await db.scalar(
        select(func.count()).select_from(AuditEvent).where(AuditEvent.action == "ingestion_retried")
    )
    chat_total = await db.scalar(select(func.count()).select_from(ChatQueryLog))
    chat_refused = await db.scalar(
        select(func.count()).select_from(ChatQueryLog).where(ChatQueryLog.refused.is_(True))
    )
    pending_outbox = int(
        await db.scalar(
            select(func.count(NotificationOutboxEvent.id)).where(
                NotificationOutboxEvent.status == "pending"
            )
        )
        or 0
    )
    failed_outbox = int(
        await db.scalar(
            select(func.count(NotificationOutboxEvent.id)).where(
                NotificationOutboxEvent.status == "failed"
            )
        )
        or 0
    )
    oldest_pending_at = await db.scalar(
        select(func.min(NotificationOutboxEvent.created_at)).where(
            NotificationOutboxEvent.status == "pending"
        )
    )
    if oldest_pending_at is not None and oldest_pending_at.tzinfo is None:
        oldest_pending_at = oldest_pending_at.replace(tzinfo=UTC)
    oldest_pending_age = (
        int((datetime.now(UTC) - oldest_pending_at).total_seconds())
        if oldest_pending_at is not None
        else 0
    )
    disabled_web = int(
        await db.scalar(
            select(func.count(WebPushSubscription.id)).where(
                WebPushSubscription.disabled_at.is_not(None)
            )
        )
        or 0
    )
    disabled_fcm = int(
        await db.scalar(
            select(func.count(FirebasePushSubscription.id)).where(
                FirebasePushSubscription.disabled_at.is_not(None)
            )
        )
        or 0
    )
    notification_processing = int(
        await db.scalar(
            select(func.count(NotificationOutboxEvent.id)).where(
                NotificationOutboxEvent.status == "processing"
            )
        )
        or 0
    )
    notification_lease_cutoff = datetime.now(UTC) - timedelta(
        seconds=max(1, settings.outbox_processing_lease_seconds)
    )
    notification_stranded = int(
        await db.scalar(
            select(func.count(NotificationOutboxEvent.id)).where(
                NotificationOutboxEvent.status == "processing",
                NotificationOutboxEvent.processing_started_at.is_not(None),
                NotificationOutboxEvent.processing_started_at < notification_lease_cutoff,
            )
        )
        or 0
    )
    notification_retrying = int(
        await db.scalar(
            select(func.count(NotificationOutboxEvent.id)).where(
                NotificationOutboxEvent.status == "pending",
                NotificationOutboxEvent.attempts > 0,
            )
        )
        or 0
    )
    domain_pending = int(
        await db.scalar(
            select(func.count(DomainEvent.id)).where(DomainEvent.status == "pending")
        )
        or 0
    )
    domain_failed = int(
        await db.scalar(
            select(func.count(DomainEvent.id)).where(DomainEvent.status == "failed")
        )
        or 0
    )
    domain_stranded = int(
        await db.scalar(
            select(func.count(DomainEvent.id)).where(
                DomainEvent.status == "processing",
                DomainEvent.processing_started_at.is_not(None),
                DomainEvent.processing_started_at < notification_lease_cutoff,
            )
        )
        or 0
    )
    domain_oldest = await db.scalar(
        select(func.min(DomainEvent.created_at)).where(DomainEvent.status == "pending")
    )
    if domain_oldest is not None and domain_oldest.tzinfo is None:
        domain_oldest = domain_oldest.replace(tzinfo=UTC)
    domain_oldest_age = (
        int((datetime.now(UTC) - domain_oldest).total_seconds())
        if domain_oldest is not None
        else 0
    )
    last_backup_at = await db.scalar(
        select(func.max(BackupRun.completed_at)).where(
            BackupRun.status.in_(("available", "restore_drill_passed"))
        )
    )
    if last_backup_at is not None and last_backup_at.tzinfo is None:
        last_backup_at = last_backup_at.replace(tzinfo=UTC)
    backup_age = (
        int((datetime.now(UTC) - last_backup_at).total_seconds())
        if last_backup_at is not None
        else -1
    )
    backup_failed = int(
        await db.scalar(
            select(func.count(BackupRun.id)).where(BackupRun.status == "failed")
        )
        or 0
    )

    lines.extend(
        [
            "# HELP kairo_ingestion_jobs_total Ingestion jobs grouped by runtime status.",
            "# TYPE kairo_ingestion_jobs_total gauge",
            f'kairo_ingestion_jobs_total{_render_labels({"status": "queued"})} {queued}',
            f'kairo_ingestion_jobs_total{_render_labels({"status": "processing"})} {processing}',
            f'kairo_ingestion_jobs_total{_render_labels({"status": "failed"})} {failed}',
            f'kairo_ingestion_jobs_total{_render_labels({"status": "completed"})} {completed}',
            "# HELP kairo_ingestion_retries_total Ingestion retry actions recorded by audit trail.",
            "# TYPE kairo_ingestion_retries_total counter",
            f'kairo_ingestion_retries_total {int(retried or 0)}',
            "# HELP kairo_chat_queries_total Chat queries recorded in the tenant database.",
            "# TYPE kairo_chat_queries_total counter",
            f'kairo_chat_queries_total {int(chat_total or 0)}',
            "# HELP kairo_chat_queries_refused_total Chat queries refused due to retrieval or policy constraints.",
            "# TYPE kairo_chat_queries_refused_total counter",
            f'kairo_chat_queries_refused_total {int(chat_refused or 0)}',
            "# HELP kairo_notification_outbox_pending Notification outbox events awaiting delivery.",
            "# TYPE kairo_notification_outbox_pending gauge",
            f"kairo_notification_outbox_pending {pending_outbox}",
            "# HELP kairo_notification_outbox_failed Notification outbox events in a terminal failed state.",
            "# TYPE kairo_notification_outbox_failed gauge",
            f"kairo_notification_outbox_failed {failed_outbox}",
            "# HELP kairo_notification_outbox_oldest_age_seconds Age of the oldest pending notification outbox event.",
            "# TYPE kairo_notification_outbox_oldest_age_seconds gauge",
            f"kairo_notification_outbox_oldest_age_seconds {oldest_pending_age}",
            "# HELP kairo_disabled_web_subscriptions Disabled Web Push subscriptions.",
            "# TYPE kairo_disabled_web_subscriptions gauge",
            f"kairo_disabled_web_subscriptions {disabled_web}",
            "# HELP kairo_disabled_fcm_tokens Disabled Android FCM tokens.",
            "# TYPE kairo_disabled_fcm_tokens gauge",
            f"kairo_disabled_fcm_tokens {disabled_fcm}",
            "# HELP kairo_notification_outbox_processing Notification outbox events currently claimed by a worker.",
            "# TYPE kairo_notification_outbox_processing gauge",
            f"kairo_notification_outbox_processing {notification_processing}",
            "# HELP kairo_notification_outbox_stranded Notification outbox events whose processing lease expired.",
            "# TYPE kairo_notification_outbox_stranded gauge",
            f"kairo_notification_outbox_stranded {notification_stranded}",
            "# HELP kairo_notification_outbox_retrying Notification outbox events waiting for a retry attempt.",
            "# TYPE kairo_notification_outbox_retrying gauge",
            f"kairo_notification_outbox_retrying {notification_retrying}",
            "# HELP kairo_domain_event_outbox_pending Domain events awaiting consumer dispatch.",
            "# TYPE kairo_domain_event_outbox_pending gauge",
            f"kairo_domain_event_outbox_pending {domain_pending}",
            "# HELP kairo_domain_event_outbox_failed Domain events in a terminal failed state.",
            "# TYPE kairo_domain_event_outbox_failed gauge",
            f"kairo_domain_event_outbox_failed {domain_failed}",
            "# HELP kairo_domain_event_outbox_stranded Domain events whose processing lease expired.",
            "# TYPE kairo_domain_event_outbox_stranded gauge",
            f"kairo_domain_event_outbox_stranded {domain_stranded}",
            "# HELP kairo_domain_event_outbox_oldest_age_seconds Age of the oldest pending domain event.",
            "# TYPE kairo_domain_event_outbox_oldest_age_seconds gauge",
            f"kairo_domain_event_outbox_oldest_age_seconds {domain_oldest_age}",
            "# HELP kairo_backup_last_success_age_seconds Seconds since the last successful backup (-1 when none).",
            "# TYPE kairo_backup_last_success_age_seconds gauge",
            f"kairo_backup_last_success_age_seconds {backup_age}",
            "# HELP kairo_backup_failed_runs Backup runs recorded as failed.",
            "# TYPE kairo_backup_failed_runs gauge",
            f"kairo_backup_failed_runs {backup_failed}",
        ]
    )
    return "\n".join(lines) + "\n"
