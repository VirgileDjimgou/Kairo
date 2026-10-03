import structlog
from celery import Celery
from celery.signals import task_postrun, task_prerun

from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()
logger = structlog.get_logger(__name__)


@task_prerun.connect
def _bind_celery_task_context(task_id=None, task=None, **kwargs) -> None:
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        task_id=task_id,
        task_name=getattr(task, "name", None),
    )
    headers = getattr(getattr(task, "request", None), "headers", None) or {}
    correlation_id = headers.get("kairo_correlation_id")
    if correlation_id:
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)


@task_postrun.connect
def _clear_celery_task_context(**kwargs) -> None:
    structlog.contextvars.clear_contextvars()

celery_app = Celery(
    "kairo_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.worker.tasks.ingestion",
        "app.worker.tasks.chat_cleanup",
        "app.worker.tasks.receipt_handover_reminders",
        "app.worker.tasks.user_notifications",
        "app.worker.tasks.domain_events",
        "app.worker.tasks.backups",
    ],
    beat_schedule={
        "cleanup-old-conversations": {
            "task": "chat.cleanup_old_conversations",
            "schedule": 86400.0,  # daily
            "kwargs": {"days": 30},
        },
    },
)

celery_app.conf.beat_schedule["resume-awaiting-ai-ingestion"] = {
    "task": "ingestion.resume_awaiting_ai_jobs",
    "schedule": 60.0,
}

celery_app.conf.beat_schedule["send-due-receipt-handover-reminders"] = {
    "task": "contributions.send_due_receipt_handover_reminders",
    "schedule": 60.0,
}

celery_app.conf.beat_schedule["process-user-notification-outbox"] = {
    "task": "notifications.process_user_outbox",
    "schedule": 15.0,
}

celery_app.conf.beat_schedule["reconcile-user-notification-outbox"] = {
    "task": "notifications.reconcile_user_outbox",
    "schedule": 300.0,
}

celery_app.conf.beat_schedule["process-domain-event-outbox"] = {
    "task": "domain_events.process_outbox",
    "schedule": 15.0,
}

celery_app.conf.beat_schedule["run-daily-encrypted-recovery-backup"] = {
    "task": "recovery.run_daily_backup",
    "schedule": 86400.0,
}

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
