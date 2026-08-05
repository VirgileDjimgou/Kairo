from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "kairo_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.worker.tasks.ingestion",
        "app.worker.tasks.chat_cleanup",
        "app.worker.tasks.receipt_handover_reminders",
        "app.worker.tasks.user_notifications",
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
