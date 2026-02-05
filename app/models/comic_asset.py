"""
Comic Asset collection model.

Stores metadata for generated comic page images.
NEVER stores binary image data - images go to Azure Blob Storage.
"""

from typing import Optional
from datetime import datetime

from beanie import PydanticObjectId
from pydantic import Field
from pymongo import IndexModel, ASCENDING

from app.models.base import BaseDocument
from app.models.enums import UserPlan


class ComicAsset(BaseDocument):
    """
    Comic asset metadata model.
    
    Tracks generated comic page images stored in Azure Blob.
    Contains only metadata - binary images stored externally.
    """
    
    # Relationships
    project_id: PydanticObjectId = Field(
        description="Reference to Project this asset belongs to"
    )
    
    # Page identification
    page_no: int = Field(
        ge=1,
        description="Page number (1-indexed)"
    )
    
    # Blob Storage
    blob_url: str = Field(
        description="Time-limited signed URL for accessing the image"
    )
    blob_path: str = Field(
        description="Internal blob storage path (for regenerating URLs)"
    )
    
    # Generation metadata
    resolution: str = Field(
        description="Resolution tier used: low/standard/high"
    )
    plan_snapshot: UserPlan = Field(
        description="User's plan when asset was created"
    )
    watermarked: bool = Field(
        default=True,
        description="Whether watermark was applied"
    )
    
    # Reproducibility
    seed: Optional[int] = Field(
        default=None,
        description="Random seed used for generation (for consistency)"
    )
    
    # URL expiry tracking
    url_expires_at: Optional[datetime] = Field(
        default=None,
        description="When the signed URL expires (for refresh logic)"
    )
    
    # Generation tracking
    generation_id: Optional[PydanticObjectId] = Field(
        default=None,
        description="Reference to Generation task that created this asset"
    )
    
    class Settings:
        name = "comic_assets"
        
        indexes = [
            # Project's assets - most common query
            IndexModel([("project_id", ASCENDING)]),
            
            # Unique constraint: one asset per page per project
            IndexModel(
                [("project_id", ASCENDING), ("page_no", ASCENDING)],
                unique=True
            ),
            
            # URL expiry queries (for refresh batch jobs)
            IndexModel([("url_expires_at", ASCENDING)]),
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "507f1f77bcf86cd799439011",
                "page_no": 1,
                "blob_url": "https://storage.blob.core.windows.net/comic-assets/...",
                "blob_path": "projects/507f1f77bcf86cd799439011/pages/1.png",
                "resolution": "standard",
                "plan_snapshot": "pro",
                "watermarked": True,
                "seed": 42,
            }
        }
