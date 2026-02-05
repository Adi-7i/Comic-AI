"""
Generation Service.

Handles enqueueing of generation tasks.
Enforces idempotency and project constraints.
"""

from datetime import datetime
from uuid import uuid4
from typing import Optional

from app.models.project import Project
from app.models.user import User
from app.models.generation import Generation
from app.models.enums import GenerationStatus
from app.workers.tasks import generate_comic_task
from app.core.exceptions import TaskAlreadyRunning


class GenerationService:
    """
    Service for managing generation requests.
    """
    
    async def create_generation_task(
        self, 
        project: Project, 
        user: User, 
        task_type: str = "story"
    ) -> Generation:
        """
        Enqueue a new generation task.
        
        Enforces idempotency: Only one active task per project.
        """
        # 1. Idempotency Check
        active_task = await Generation.find_one(
            Generation.project_id == project.id,
            Generation.status == GenerationStatus.PROCESSING
            # Or QUEUED? Yes, check both active states
        ) 
        # Better query: status in [QUEUED, PROCESSING]
        # Beanie In operator?
        
        active_states = [GenerationStatus.QUEUED, GenerationStatus.PROCESSING]
        active_task = await Generation.find_one(
            Generation.project_id == project.id,
            { "status": { "$in": active_states } }
        )
        
        if active_task:
            raise TaskAlreadyRunning(
                detail=f"Project already has an active task ({active_task.task_type})"
            )
            
        # 2. Create DB Record
        generation = Generation(
            project_id=project.id,
            user_id=user.id,
            task_type=task_type,
            status=GenerationStatus.QUEUED,
            progress=0,
            created_at=datetime.utcnow()
        )
        await generation.save()
        
        # 3. Enqueue to Celery
        # We pass the DB ID (PydanticObjectId) or str(id)
        # Choosing str(id) for serializability
        celery_task = generate_comic_task.delay(str(generation.id))
        
        # 4. Update with Celery Task ID
        generation.task_id = celery_task.id
        await generation.save()
        
        return generation

    async def get_task_status(self, task_id: str) -> Optional[Generation]:
        """
        Get task by Celery ID.
        """
        return await Generation.find_one(Generation.task_id == task_id)


generation_service = GenerationService()
