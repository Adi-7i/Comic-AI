"""
Pydantic schemas for Scene (Panel) management.
"""

from datetime import datetime
from typing import Optional, Dict, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator


class NarrativeText(BaseModel):
    """
    Structure for LLM-generated narrative content.
    """
    dialogue: List[str] = Field(default_factory=list, description="List of dialogue lines")
    action: str = Field(description="Action description")
    setting: str = Field(description="Setting description")
    caption: Optional[str] = Field(default=None, description="Narrative caption")


class SceneCreate(BaseModel):
    """
    Schema for creating a single scene (panel).
    """
    page_no: int = Field(ge=1, description="Page number")
    panel_no: int = Field(ge=1, le=4, description="Panel number (1-4)")
    narrative_text: NarrativeText
    language: str = Field(default="en", min_length=2, max_length=5)
    character_ids: List[UUID] = Field(default_factory=list, description="List of character public IDs")
    
    @field_validator('panel_no')
    @classmethod
    def validate_panel_no(cls, v: int) -> int:
        if not 1 <= v <= 4:
            raise ValueError("Panel number must be between 1 and 4")
        return v


class SceneBulkCreate(BaseModel):
    """
    Schema for adding multiple scenes at once (e.g., a whole page).
    """
    scenes: List[SceneCreate] = Field(min_length=1, max_length=20, description="List of scenes to add")


class SceneResponse(BaseModel):
    """
    Full scene response schema.
    """
    model_config = ConfigDict(from_attributes=True)
    
    public_id: UUID
    project_id: UUID
    page_no: int
    panel_no: int
    narrative_text: Dict
    language: str
    generated_image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
