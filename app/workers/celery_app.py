"""
Celery Application Entrypoint.
"""

from celery import Celery
from app.core.celery_config import celery_settings

celery = Celery(
    "comic_worker",
    broker=celery_settings.CELERY_BROKER_URL,
    backend=celery_settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"]
)

celery.conf.update(
    task_serializer=celery_settings.CELERY_TASK_SERIALIZER,
    result_serializer=celery_settings.CELERY_RESULT_SERIALIZER,
    accept_content=celery_settings.CELERY_ACCEPT_CONTENT,
    timezone=celery_settings.CELERY_TIMEZONE,
    # result_expires=3600,
)

if __name__ == "__main__":
    celery.start()
