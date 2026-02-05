"""
Strict output schemas for LLM Story Generation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class PanelLLM(BaseModel):
    """
    LLM output for a single panel.
    Strictly enforces fields needed for image generation and display.
    """
    panel_no: int = Field(description="Panel number (1-4)")
    description: str = Field(description="Visual description for image generation")
    dialogue: Optional[str] = Field(default=None, description="Dialogue text (if any)")
    caption: Optional[str] = Field(default=None, description="Narrative caption (if any)")
    
    @field_validator('panel_no')
    @classmethod
    def validate_panel_no(cls, v: int) -> int:
        if not 1 <= v <= 4:
            raise ValueError("panel_no must be between 1 and 4")
        return v


class PageLLM(BaseModel):
    """
    LLM output for a single page.
    Enforces exactly 4 panels logic (or fewer depending on style, but task says fixed 4).
    Task rule: Fixed 4 panels per page.
    """
    page_no: int = Field(description="Page number")
    panels: List[PanelLLM] = Field(description="List of panels", min_length=4, max_length=4)
    
    @field_validator('panels')
    @classmethod
    def validate_panel_count(cls, v: List[PanelLLM]) -> List[PanelLLM]:
        if len(v) != 4:
            raise ValueError("Each page must have exactly 4 panels")
        # Ensure panel numbers are unique and 1-4
        panel_nums = sorted([p.panel_no for p in v])
        if panel_nums != [1, 2, 3, 4]:
            raise ValueError("Panels must be numbered 1 through 4 sequentially")
        return v


class StoryLLM(BaseModel):
    """
    Root schema for LLM story output.
    """
    pages: List[PageLLM] = Field(description="List of pages")
