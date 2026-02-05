"""
Generation collection model.

Tracks async comic generation tasks with status, cost, and retry metadata.
"""

from datetime import datetime
from typing import Optional, Dict

from beanie import PydanticObjectId
from pydantic import Field
from pymongo import IndexModel, ASCENDING

from app.models.base import BaseDocument
from app.models.enums import GenerationStatus


class Generation(BaseDocument):
    """
    Generation task model.
    
    Tracks async AI generation tasks (text + images).
    Stores status, cost metadata, retry count, and task references.
    """
    
    # Relationships
    project_id: PydanticObjectId = Field(
        description="Reference to Project being generated"
    )
    user_id: PydanticObjectId = Field(
        description="Reference to User who initiated generation"
    )
    scene_id: Optional[PydanticObjectId] = Field(
        default=None,
        description="Reference to specific Scene being generated (optional)"
    )
    
    # Task status
    status: GenerationStatus = Field(
        default=GenerationStatus.QUEUED,
        description="Current generation task status"
    )
    
    progress: int = Field(
        default=0,
        ge=0, 
        le=100,
        description="Task progress percentage (0-100)"
    )
    
    task_type: str = Field(
        default="story_generation",
        description="Type of task (story, image, compile)"
    )
    
    # Retry logic
    retry_count: int = Field(
        default=0,
        ge=0,
        description="Number of retry attempts (incremented on failures)"
    )
    
    # Cost tracking
    # Example: {
    #   "llm_tokens": 1500,
    #   "image_count": 4,
    #   "estimated_cost_usd": 0.25
    # }
    cost_metadata: Dict = Field(
        default_factory=dict,
        description="Resource usage tracking (tokens, images, API costs)"
    )
    
    # Error handling
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if status=failed"
    )
    
    # Timing
    started_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when processing started"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when task completed (success or failure)"
    )
    
    # External task tracking (e.g., Celery task ID)
    task_id: Optional[str] = Field(
        default=None,
        description="External async task ID (Celery, RQ, etc.)"
    )
    
    class Settings:
        name = "generations"
        
        indexes = [
            # User's generation history
            IndexModel([("user_id", ASCENDING)]),
            
            # Project's generations
            IndexModel([("project_id", ASCENDING)]),
            
            # Queue processing - find queued tasks ordered by creation time
            IndexModel([("status", ASCENDING), ("created_at", ASCENDING)]),
            
            # Task ID lookup for async workers
            IndexModel([("task_id", ASCENDING)]),
            
            # Inherit base indexes (public_id, is_deleted, created_at)
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "scene_id": "507f1f77bcf86cd799439013",
                "status": "processing",
                "retry_count": 0,
                "cost_metadata": {
                    "llm_tokens": 1500,
                    "image_count": 4,
                    "estimated_cost_usd": 0.25
                },
                "started_at": "2026-02-05T12:00:00",
                "task_id": "celery-task-abc123"
            }
        }
