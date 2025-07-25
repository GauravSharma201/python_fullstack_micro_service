# task-service/celery_app.py
from celery import Celery
import os

celery_app = Celery(
    "task_service",
    broker=os.getenv("CELERY_BROKER_URL", "pyamqp://admin:password@localhost:5672//"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379"),
    include=["tasks.background_tasks"]
)

celery_app.conf.task_routes = {
    "tasks.background_tasks.*": "background_queue",
}

celery_app.conf.beat_schedule = {
    "cleanup-old-tasks": {
        "task": "tasks.background_tasks.cleanup_old_tasks",
        "schedule": 3600.0,  # Run every hour
    },
}