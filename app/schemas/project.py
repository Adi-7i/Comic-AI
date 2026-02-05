"""
Pydantic schemas for Project management.
"""

from datetime import datetime
from typing import Optional, Dict
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import ProjectStatus, UserPlan


class ProjectCreate(BaseModel):
    """
    Schema for creating a new project.
    """
    title: str = Field(min_length=1, max_length=200, description="Project title")
    description: Optional[str] = Field(default=None, max_length=2000, description="Project description")
    config: Dict = Field(default_factory=dict, description="Project configuration (style, etc.)")


class ProjectUpdate(BaseModel):
    """
    Schema for updating an existing project.
    Only allows updating metadata, not core structure/plans.
    """
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    config: Optional[Dict] = Field(default=None)


class ProjectResponse(BaseModel):
    """
    Full project response schema.
    """
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID = Field(description="Project unique public ID")
    title: str
    description: Optional[str] = None
    status: ProjectStatus
    total_pages: int
    plan_snapshot: UserPlan
    config: Dict
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
