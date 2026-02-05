"""
Scene collection model.

Represents a single comic panel/scene with narrative content and generation metadata.
"""

from typing import Optional, Dict, List

from beanie import PydanticObjectId
from pydantic import Field, field_validator
from pymongo import IndexModel, ASCENDING

from app.models.base import BaseDocument


class Scene(BaseDocument):
    """
    Scene (panel) model for comic projects.
    
    Each scene represents one panel in the comic (fixed 4-panel layout).
    Contains narrative text from LLM and tracks generated images.
    """
    
    # Relationship to project
    project_id: PydanticObjectId = Field(
        description="Reference to Project this scene belongs to"
    )
    
    # Panel location
    page_no: int = Field(
        ge=1,
        description="Page number (1-indexed)"
    )
    panel_no: int = Field(
        ge=1,
        le=4,
        description="Panel number on the page (1-4 for fixed layout)"
    )
    
    # Narrative content from LLM
    # Example: {
    #   "dialogue": ["Hero: I'll save you!", "Villain: Never!"],
    #   "action": "Hero flies toward villain",
    #   "setting": "City rooftop at sunset"
    # }
    narrative_text: Dict = Field(
        description="Structured JSON from LLM with dialogue, actions, setting"
    )
    
    # Language support
    language: str = Field(
        default="en",
        min_length=2,
        max_length=5,
        description="Language code (ISO 639-1, e.g., 'en', 'es', 'ja')"
    )
    
    # Character references
    character_ids: List[PydanticObjectId] = Field(
        default_factory=list,
        description="List of characters appearing in this scene"
    )
    
    # Generated image
    generated_image_url: Optional[str] = Field(
        default=None,
        description="URL to the generated comic panel image"
    )
    
    # Prompt tracking for reproducibility
    prompt_used: Optional[str] = Field(
        default=None,
        description="AI prompt used to generate this panel (for debugging/reproducibility)"
    )
    
    @field_validator('panel_no')
    @classmethod
    def validate_panel_number(cls, v: int) -> int:
        """Ensure panel number is within fixed 4-panel layout."""
        if not 1 <= v <= 4:
            raise ValueError("Panel number must be between 1 and 4 (fixed layout)")
        return v
    
    class Settings:
        name = "scenes"
        
        indexes = [
            # Project's scenes - most common query
            IndexModel([("project_id", ASCENDING)]),
            
            # Ensure one scene per panel location (unique constraint)
            IndexModel(
                [("project_id", ASCENDING), ("page_no", ASCENDING), ("panel_no", ASCENDING)],
                unique=True
            ),
            
            # Language-based queries (for multi-language support)
            IndexModel([("language", ASCENDING)]),
            
            # Inherit base indexes (public_id, is_deleted, created_at)
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "507f1f77bcf86cd799439011",
                "page_no": 1,
                "panel_no": 1,
                "narrative_text": {
                    "dialogue": ["Captain Thunder: The city needs me!"],
                    "action": "Hero standing on rooftop looking at city",
                    "setting": "City skyline at dusk"
                },
                "language": "en",
                "character_ids": ["507f1f77bcf86cd799439012"],
                "generated_image_url": "https://storage.example.com/panels/p1_panel1.jpg",
                "prompt_used": "Comic panel: superhero on rooftop..."
            }
        }
