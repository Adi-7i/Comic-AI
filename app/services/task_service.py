"""
Task Service.

Handles database updates for async tasks.
Executed by Celery workers to report progress.
"""

from datetime import datetime
from typing import Optional

from app.models.generation import Generation
from app.models.enums import GenerationStatus


class TaskService:
    """
    Service for managing task state in the database.
    """
    
    async def update_progress(self, task_id: str, progress: int) -> None:
        """
        Update task progress.
        """
        generation = await Generation.find_one(Generation.task_id == task_id)
        if generation:
            generation.progress = progress
            generation.status = GenerationStatus.PROCESSING
            if not generation.started_at:
                generation.started_at = datetime.utcnow()
            await generation.save()

    async def mark_failed(self, task_id: str, error: str) -> None:
        """
        Mark task as failed.
        """
        generation = await Generation.find_one(Generation.task_id == task_id)
        if generation:
            generation.status = GenerationStatus.FAILED
            generation.error_message = error
            generation.completed_at = datetime.utcnow()
            await generation.save()

    async def mark_completed(self, task_id: str, result: dict = None) -> None:
        """
        Mark task as completed.
        """
        generation = await Generation.find_one(Generation.task_id == task_id)
        if generation:
            generation.status = GenerationStatus.COMPLETED
            generation.progress = 100
            generation.completed_at = datetime.utcnow()
            # If result has usage, merge it?
            # For now just status update
            await generation.save()

task_service = TaskService()
