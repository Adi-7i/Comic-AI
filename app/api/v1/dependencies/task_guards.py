"""
Task Guards.
"""

from fastapi import Depends

from app.api.v1.dependencies.permissions import get_project_or_404
from app.models.project import Project
from app.models.generation import Generation
from app.models.enums import GenerationStatus
from app.core.exceptions import TaskAlreadyRunning


async def ensure_no_active_task(
    project_id: str,
    project: Project = Depends(get_project_or_404)
) -> Project:
    """
    Ensure the project has no active generation tasks.
    """
    active_states = [GenerationStatus.QUEUED, GenerationStatus.PROCESSING]
    active_task = await Generation.find_one(
        Generation.project_id == project.id,
        { "status": { "$in": active_states } }
    )
    
    if active_task:
        raise TaskAlreadyRunning(
            detail=f"Project already has an active task ({active_task.status})"
        )
    
    return project
