from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "kairo_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.worker.tasks.ingestion",
        "app.worker.tasks.chat_cleanup",
    ],
    beat_schedule={
        "cleanup-old-conversations": {
            "task": "chat.cleanup_old_conversations",
            "schedule": 86400.0,  # daily
            "kwargs": {"days": 30},
        },
    },
)

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
