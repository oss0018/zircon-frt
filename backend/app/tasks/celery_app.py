from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "zircon",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.file_tasks",
        "app.tasks.monitoring_tasks",
        "app.tasks.brand_tasks",
    ],
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
        # Folder monitoring — every 5 minutes
        "rescan-monitored-folder": {
            "task": "app.tasks.monitoring_tasks.rescan_monitored_folder",
            "schedule": 300.0,  # 5 minutes
        },
        # Watchlist polling — every hour
        "poll-osint-watchlist": {
            "task": "app.tasks.monitoring_tasks.poll_osint_watchlist",
            "schedule": 3600.0,  # 1 hour
        },
        # Brand protection — daily at 03:00 UTC
        "daily-brand-scan": {
            "task": "app.tasks.brand_tasks.daily_brand_scan",
            "schedule": crontab(hour=3, minute=0),
        },
    },
)
