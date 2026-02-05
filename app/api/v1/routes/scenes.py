"""
Scene management routes.

Handles:
- Bulk adding scenes to pages
- Listing project scenes
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.models.project import Project
from app.schemas.scene import SceneBulkCreate, SceneResponse
from app.services.scene_service import scene_service
from app.api.v1.dependencies.permissions import get_project_or_404


# Note: These routes are nested under /projects/{project_id}
# In main.py, we might include this with a prefix or just handle the path here
# Standard pattern: /projects/{id}/scenes
router = APIRouter(prefix="/projects/{project_id}/scenes", tags=["Scenes"])


@router.post("/", response_model=List[SceneResponse], status_code=status.HTTP_201_CREATED)
async def add_scenes(
    data: SceneBulkCreate,
    project: Project = Depends(get_project_or_404),
):
    """
    Add scenes (panels) to a project.
    
    - Validates 4-panel limit per page
    - Validates plan page limits
    - Only allowed for DRAFT projects
    - Handles bulk insertion for a page
    """
    return await scene_service.add_scenes(project, data.scenes)


@router.get("/", response_model=List[SceneResponse])
async def list_scenes(
    project: Project = Depends(get_project_or_404),
):
    """
    List all scenes for a project.
    
    Returns scenes ordered by page_no, panel_no.
    """
    return await scene_service.get_project_scenes(project)
