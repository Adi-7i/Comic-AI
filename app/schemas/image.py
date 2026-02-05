"""
Image generation schemas.

Request/response schemas for comic image generation API.
"""

from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, Field


class ImageGenerationRequest(BaseModel):
    """Request to generate comic images for a project."""
    
    project_id: str = Field(
        description="Project public_id to generate images for"
    )
    pages: Optional[List[int]] = Field(
        default=None,
        description="Specific page numbers to generate. None = all pages."
    )
    force_regenerate: bool = Field(
        default=False,
        description="Regenerate even if images exist (plan-dependent)"
    )


class PanelImageData(BaseModel):
    """Metadata for a single panel in image generation."""
    
    panel_no: int = Field(
        ge=1, le=4,
        description="Panel position (1-4)"
    )
    prompt: str = Field(
        description="Image generation prompt derived from narrative"
    )
    character_ids: List[str] = Field(
        default_factory=list,
        description="Characters appearing in this panel"
    )


class PageGenerationData(BaseModel):
    """Data for generating a single page."""
    
    page_no: int = Field(
        ge=1,
        description="Page number"
    )
    panels: List[PanelImageData] = Field(
        min_length=4,
        max_length=4,
        description="Exactly 4 panels per page"
    )
    style_prompt: Optional[str] = Field(
        default=None,
        description="Additional style guidance for the page"
    )


class ComicAssetResponse(BaseModel):
    """Response schema for a comic asset."""
    
    page_no: int
    blob_url: str
    resolution: str
    watermarked: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ImageGenerationStatus(BaseModel):
    """Status response for image generation task."""
    
    task_id: str = Field(
        description="Celery task ID for tracking"
    )
    status: str = Field(
        description="Task status: queued/processing/completed/failed"
    )
    progress: int = Field(
        ge=0, le=100,
        description="Progress percentage"
    )
    pages_completed: int = Field(
        default=0,
        description="Number of pages successfully generated"
    )
    total_pages: int = Field(
        description="Total pages to generate"
    )
    assets: List[ComicAssetResponse] = Field(
        default_factory=list,
        description="Generated assets (populated as completed)"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if failed"
    )


class ImageGenerationResponse(BaseModel):
    """Response when image generation is initiated."""
    
    generation_id: str = Field(
        description="Generation record ID"
    )
    task_id: str = Field(
        description="Celery task ID for polling"
    )
    status: str = Field(
        description="Initial status (typically 'queued')"
    )
    message: str = Field(
        description="Human-readable status message"
    )
