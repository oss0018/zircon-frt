from celery import Celery
from app.config import settings

celery_app = Celery(
    "zircon",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.file_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    beat_schedule={
        # Placeholder for Phase 2 monitoring tasks
        # "check-monitors": {
        #     "task": "app.tasks.monitoring_tasks.check_monitors",
        #     "schedule": 60.0,
        # },
    },
)
