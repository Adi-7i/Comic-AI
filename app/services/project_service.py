"""
Project service business logic.

Handles:
- Project creation with plan snapshot
- Lifecycle management (CRUD)
- Status transitions
"""

from typing import Optional, List
from uuid import UUID

from beanie import PydanticObjectId
from fastapi import HTTPException

from app.models.project import Project
from app.models.user import User
from app.models.enums import ProjectStatus
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.core.exceptions import (
    ProjectNotFound,
    ProjectAccessDenied,
    ProjectInvalidStatus,
)
from app.utils.pagination import Params


class ProjectService:
    """
    Service for Project management.
    """
    
    async def create_project(self, user: User, data: ProjectCreate) -> Project:
        """
        Create a new project and snapshot the user's plan.
        
        Args:
            user: Authenticated user
            data: Project creation data
            
        Returns:
            Created Project document
        """
        project = Project(
            user_id=user.id,
            title=data.title,
            description=data.description,
            config=data.config,
            status=ProjectStatus.DRAFT,
            # CRITICAL: Snapshot the plan at creation time
            plan_snapshot=user.plan,
        )
        await project.save()
        return project

    async def get_project(self, user: User, project_id: UUID) -> Project:
        """
        Get a project by public ID and verify ownership.
        
        Args:
            user: Authenticated user
            project_id: Project public ID
            
        Returns:
            Project document
            
        Raises:
            ProjectNotFound: If not found
            ProjectAccessDenied: If user doesn't own project
        """
        project = await Project.find_one(Project.public_id == project_id)
        
        if not project:
            raise ProjectNotFound()
            
        if project.user_id != user.id:
            raise ProjectAccessDenied()
            
        return project

    async def list_projects(self, user: User, params: Params) -> List[Project]:
        """
        List user's projects with pagination.
        
        Args:
            user: Authenticated user
            params: Pagination parameters
            
        Returns:
            List of Project documents (paginated query logic is handled by caller/utils)
        """
        # Note: Actual pagination execution happens in the route using utils.paginate
        # This just returns the query object for the user's projects
        return Project.find(Project.user_id == user.id, sort="-created_at")

    async def update_project(
        self, user: User, project_id: UUID, data: ProjectUpdate
    ) -> Project:
        """
        Update project metadata.
        
        Args:
            user: Authenticated user
            project_id: Project public ID
            data: Update data
            
        Returns:
            Updated Project document
        """
        project = await self.get_project(user, project_id)
        
        # Only allow updates in appropriate statuses (e.g., not when failed/archived?)
        # For now, allow updates in any status except deleted
        
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return project
            
        await project.set(update_data)
        return project

    async def delete_project(self, user: User, project_id: UUID) -> None:
        """
        Soft delete a project.
        
        Args:
            user: Authenticated user
            project_id: Project public ID
        """
        project = await self.get_project(user, project_id)
        
        # Soft delete
        project.is_deleted = True
        project.deleted_at = project.created_at  # using datetime.utcnow() in BaseDocument logic usually
        # Actually BaseDocument.delete() might be overridden or we use soft delete manually
        # Let's use the explicit soft delete field setting for now as BaseDocument likely handles logic
        # But wait, BaseDocument usually has a logic for this. 
        # Let's check BaseDocument if needed, but safe bet:
        from datetime import datetime
        project.deleted_at = datetime.utcnow()
        await project.save()

    async def update_status(self, project: Project, status: ProjectStatus) -> Project:
        """
        Internal method to update project status.
        
        Args:
            project: Project document
            status: New status
            
        Returns:
            Updated Project document
        """
        project.status = status
        if status == ProjectStatus.COMPLETED:
            from datetime import datetime
            project.completed_at = datetime.utcnow()
            
        await project.save()
        return project


# Singleton
project_service = ProjectService()
