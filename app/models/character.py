"""
Character collection model.

Represents a character in a comic project with appearance details and consistency data.
"""

from typing import Optional, Dict, List

from beanie import PydanticObjectId
from pydantic import Field
from pymongo import IndexModel, ASCENDING

from app.models.base import BaseDocument


class Character(BaseDocument):
    """
    Character model for comic projects.
    
    Stores character metadata, appearance details, and consistency information
    to ensure the AI generates the same character across multiple panels/pages.
    """
    
    # Relationship to project
    project_id: PydanticObjectId = Field(
        description="Reference to Project this character belongs to"
    )
    
    # Character identity
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Character name"
    )
    
    # Appearance metadata - flexible JSON structure
    # Example: {"hair": "long black", "clothing": "red cape", "build": "muscular"}
    appearance: Dict = Field(
        default_factory=dict,
        description="Flexible JSON for physical traits, clothing, accessories, etc."
    )
    
    # Personality (optional, may be used for dialogue generation)
    personality_traits: Optional[List[str]] = Field(
        default=None,
        description="List of personality traits (brave, funny, shy, etc.)"
    )
    
    # AI consistency
    consistency_seed: Optional[str] = Field(
        default=None,
        description="Seed or identifier for AI to maintain visual consistency"
    )
    
    # Reference image
    reference_image_url: Optional[str] = Field(
        default=None,
        description="URL to reference image for character appearance"
    )
    
    class Settings:
        name = "characters"
        
        indexes = [
            # Project's characters - most common query
            IndexModel([("project_id", ASCENDING)]),
            
            # Ensure unique character names within a project
            IndexModel(
                [("project_id", ASCENDING), ("name", ASCENDING)],
                unique=True
            ),
            
            # Inherit base indexes (public_id, is_deleted, created_at)
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "507f1f77bcf86cd799439011",
                "name": "Captain Thunder",
                "appearance": {
                    "hair": "short blonde",
                    "eyes": "blue",
                    "clothing": "blue superhero suit with lightning emblem",
                    "build": "athletic"
                },
                "personality_traits": ["brave", "determined", "protective"],
                "consistency_seed": "capt_thunder_v1",
                "reference_image_url": "https://storage.example.com/chars/hero1.jpg"
            }
        }
