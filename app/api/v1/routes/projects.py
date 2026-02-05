"""
Project management routes.

Handles:
- Project creation, listing, retrieval, deletion
- Status updates (internal)
"""

from typing import List, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, status, Response

from app.models.user import User
from app.models.project import Project
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
)
from app.services.project_service import project_service
from app.api.v1.dependencies.auth import get_active_user
from app.api.v1.dependencies.permissions import get_project_or_404
from app.utils.pagination import Params, pagination_params, paginate, Page


router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    user: User = Depends(get_active_user),
):
    """
    Create a new comic project.
    
    Snapshots the user's current plan for future limits.
    """
    return await project_service.create_project(user, data)


@router.get("/", response_model=Page[ProjectResponse])
async def list_projects(
    params: Params = Depends(pagination_params),
    user: User = Depends(get_active_user),
):
    """
    List user's projects with pagination.
    """
    # Get the base query from service
    # Note: paginate utility expects a Beanie query or similar
    # project_service.list_projects returns a FindMany object
    query = await project_service.list_projects(user, params)
    
    # Use generic pagination utility
    return await paginate(query, params, ProjectResponse)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project: Project = Depends(get_project_or_404),
):
    """
    Get project details.
    
    Requires ownership.
    """
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    data: ProjectUpdate,
    project_id: UUID,  # extracted from path for service call
    user: User = Depends(get_active_user),
):
    """
    Update project metadata (title, description, config).
    """
    return await project_service.update_project(user, project_id, data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    user: User = Depends(get_active_user),
):
    """
    Soft delete a project.
    """
    await project_service.delete_project(user, project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
