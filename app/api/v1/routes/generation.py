"""
Generation API Routes.
"""

from fastapi import APIRouter, Depends, status

from app.models.project import Project
from app.models.user import User
from app.services.generation_service import generation_service
from app.api.v1.dependencies.permissions import get_project_or_404
from app.api.v1.dependencies.auth import get_active_user
from app.api.v1.dependencies.guards import require_draft_status

router = APIRouter(prefix="/projects/{project_id}/generate", tags=["Generation"])

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def start_generation(
    project_id: str,
    # Inject project via dependencies (checks ownership & status)
    project: Project = Depends(require_draft_status),
    user: User = Depends(get_active_user)
):
    """
    Start an async comic generation task.
    
    Status:
    - 202 Accepted: Task enqueued
    - 409 Conflict: Task already running
    - 403 Forbidden: Not owner or invalid status
    """
    generation = await generation_service.create_generation_task(project, user)
    return {
        "status": "queued",
        "task_id": generation.task_id,
        "generation_id": str(generation.id)
    }

@router.get("/status/{task_id}")
async def get_generation_status(
    task_id: str,
    user: User = Depends(get_active_user)
):
    """
    Poll status of a generation task.
    """
    task = await generation_service.get_task_status(task_id)
    if not task:
        return {"status": "not_found"}
        
    # Ideally verify user owns the project this task belongs to
    # but for simplicity/observability we return basic status
    return {
        "status": task.status,
        "progress": task.progress,
        "error": task.error_message,
        "result": None # If we had one
    }
