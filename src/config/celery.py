import os

from celery.app import Celery
from celery.schedules import crontab

from src.config.settings import settings


redis_url = settings.CELEREY_BROKER_URL

celery_app = Celery(
    __name__, broker=redis_url, backend=redis_url, include=["src.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    beat_schedule={
        # "consume-kafka-messages-every-10s": {
        #     "task": "src.tasks.message_task.consume_kafka_messages_batch",
        #     "schedule": 60.0,
        #     "args": (),
        #     "kwargs": {"batch_size": 20, "poll_timeout": 1.0, "max_polls": 10},
        # },
    },
)
