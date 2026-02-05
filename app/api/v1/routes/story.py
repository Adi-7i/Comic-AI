"""
Story API Routes.

Endpoints for LLM generation tasks.
"""

from typing import Dict, Any

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, status

from app.models.project import Project
from app.models.user import User
from app.models.enums import ProjectStatus
from app.services.story_service import story_service
from app.api.v1.dependencies.permissions import get_project_or_404, require_project_status
from app.api.v1.dependencies.auth import get_active_user


router = APIRouter(prefix="/projects/{project_id}/story", tags=["Story Engine"])


class GenerateRequest(BaseModel):
    input_text: str = Field(min_length=10, max_length=5000, description="Story description")


@router.post("/parse", status_code=status.HTTP_200_OK)
async def parse_story(
    project_id: str, # From path
    request: GenerateRequest,
    # Inject project via dependency that checks ID and ownership
    project: Project = Depends(get_project_or_404),
    user: User = Depends(get_active_user)
):
    """
    Generate comic scenes from a text story.
    
    1. Validates project is in DRAFT status
    2. Calls LLM to generate structured scenes
    3. Enforces Plan Limits (Cost & Pages)
    4. Saves scenes to database
    
    Returns:
        JSON with generation status and usage stats
    """
    # Enforce Draft Status explicitly
    if project.status != ProjectStatus.DRAFT:
        # Use common status dependency or check here
        # Since get_project_or_404 returns project, we can just check
        # Reuse existing exception logic if desired
        from app.core.exceptions import ProjectInvalidStatus
        raise ProjectInvalidStatus(detail="Story generation only allowed in DRAFT status")

    return await story_service.parse_story(user, project, request.input_text)
