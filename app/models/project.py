"""
Project collection model.

Represents a comic generation project with metadata, status tracking, and plan snapshot.
"""

from datetime import datetime
from typing import Optional, Dict

from beanie import PydanticObjectId
from pydantic import Field
from pymongo import IndexModel, ASCENDING

from app.models.base import BaseDocument
from app.models.enums import ProjectStatus, UserPlan


class Project(BaseDocument):
    """
    Comic project model.
    
    A project represents a complete comic generation task owned by a user.
    Tracks status, configuration, and captures the user's plan at creation time.
    """
    
    # Ownership
    user_id: PydanticObjectId = Field(
        description="Reference to User who owns this project"
    )
    
    # Project metadata
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Project title"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Project description (optional)"
    )
    
    # Status tracking
    status: ProjectStatus = Field(
        default=ProjectStatus.DRAFT,
        description="Current project status"
    )
    
    # Content structure
    total_pages: int = Field(
        default=1,
        ge=1,
        le=100,  # Reasonable limit
        description="Total number of pages in this comic"
    )
    
    # Plan snapshot - captures user's plan at creation time
    # This ensures quota/feature checks use the plan active during creation
    plan_snapshot: UserPlan = Field(
        description="User's plan tier when project was created"
    )
    
    # Flexible configuration
    config: Dict = Field(
        default_factory=dict,
        description="Project-specific settings (style, theme, language, etc.)"
    )
    
    # Completion tracking
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when generation was completed (if status=completed)"
    )
    
    class Settings:
        name = "projects"
        
        indexes = [
            # User's projects - most common query
            IndexModel([("user_id", ASCENDING)]),
            
            # User's projects by status (e.g., find all completed projects for user)
            IndexModel([("user_id", ASCENDING), ("status", ASCENDING)]),
            
            # Global status queries (e.g., find all generating projects)
            IndexModel([("status", ASCENDING)]),
            
            # Inherit base indexes (public_id, is_deleted, created_at)
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "title": "My Superhero Comic",
                "description": "A story about a hero saving the city",
                "status": "draft",
                "total_pages": 5,
                "plan_snapshot": "pro",
                "config": {
                    "style": "manga",
                    "theme": "action",
                    "language": "en"
                },
            }
        }
