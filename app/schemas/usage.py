"""
Schemas for tracking LLM usage and cost metadata.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class GenerationUsage(BaseModel):
    """
    Metadata for a single LLM generation request.
    """
    provider: str = Field(description="LLM Provider (openai, anthropic)")
    model: str = Field(description="Model name used")
    tokens_in: int = Field(default=0, description="Input/Prompt tokens")
    tokens_out: int = Field(default=0, description="Output/Completion tokens")
    estimated_cost: float = Field(default=0.0, description="Estimated cost in USD")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
