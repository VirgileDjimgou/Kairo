from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from threading import Lock

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

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

    def record_http_request(self, method: str, status_code: int, latency_ms: int) -> None:
        key = (method.upper(), _status_class(status_code))
        with self._lock:
            self.http_requests[key] += 1
            self.http_request_latency_ms_sum[key] += max(0, latency_ms)
            self.http_request_latency_ms_count[key] += 1

    def record_error(self, error_code: str) -> None:
        with self._lock:
            self.error_counts[error_code] += 1

    def reset(self) -> None:
        with self._lock:
            self.http_requests.clear()
            self.http_request_latency_ms_sum.clear()
            self.http_request_latency_ms_count.clear()
            self.error_counts.clear()

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
        ]
    )
    return "\n".join(lines) + "\n"
