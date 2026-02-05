"""
Authorization rules and permission checkers.

Reusable dependencies for:
- Resource ownership verification
- Status-based access control
"""

from typing import Callable
from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.models.user import User
from app.models.project import Project
from app.models.enums import ProjectStatus
from app.api.v1.dependencies.auth import get_active_user
from app.services.project_service import project_service
from app.core.exceptions import ProjectInvalidStatus


async def get_project_or_404(
    project_id: UUID,
    user: User = Depends(get_active_user),
) -> Project:
    """
    Dependency to fetch a project and verify availability.
    
    Checks:
    1. Project exists
    2. User owns the project (via service check)
    3. User account is active (via get_active_user)
    
    Args:
        project_id: Project public ID (UUID)
        user: Authenticated user
        
    Returns:
        Project document
        
    Raises:
        ProjectNotFound: If project doesn't exist
        ProjectAccessDenied: If user doesn't own project
    """
    # Service handles finding and ownership verify
    return await project_service.get_project(user, project_id)


def require_project_status(required_status: ProjectStatus) -> Callable:
    """
    Dependency factory to enforce project status.
    
    Args:
        required_status: Status the project must be in
        
    Returns:
        Dependency function
        
    Usage:
        @router.post("/")
        def action(project: Project = Depends(require_project_status(ProjectStatus.DRAFT)))
    """
    async def check_status(
        project: Project = Depends(get_project_or_404)
    ) -> Project:
        if project.status != required_status:
            raise ProjectInvalidStatus(
                detail=f"Operation requires project status '{required_status.value}', "
                f"but current status is '{project.status.value}'"
            )
        return project
        
    return check_status
