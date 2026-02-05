"""
Celery Configuration.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class CelerySettings(BaseSettings):
    """
    Celery-specific settings.
    """
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: list = ["json"]
    CELERY_TIMEZONE: str = "UTC"
    
    # Task Routes (Future optimization for different queues)
    # CELERY_TASK_ROUTES: dict = {
    #     "app.workers.tasks.image_generation": "heavy_tasks",
    # }

    model_config = SettingsConfigDict(
        env_prefix="CELERY_",
        env_file=".env",
        extra="ignore"
    )


celery_settings = CelerySettings()
