import os

from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "state_reconciliation_platform",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "collect-hn-every-5-minutes": {
            "task": "app.tasks.collect_hn",
            "schedule": 300.0,
        },
        "collect-github-every-10-minutes": {
            "task": "app.tasks.collect_github",
            "schedule": 600.0,
        }
    },
)
