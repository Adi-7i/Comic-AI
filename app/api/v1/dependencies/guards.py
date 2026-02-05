"""
Project Guards Dependencies.

Reusable checks for project state.
"""

from fastapi import Depends
from app.models.project import Project
from app.models.enums import ProjectStatus
from app.core.exceptions import ProjectInvalidStatus
from app.api.v1.dependencies.permissions import get_project_or_404


def require_draft_status(project: Project = Depends(get_project_or_404)) -> Project:
    """Dependency to ensure project is in DRAFT status."""
    if project.status != ProjectStatus.DRAFT:
        raise ProjectInvalidStatus(detail="Operation requires DRAFT status")
    return project
