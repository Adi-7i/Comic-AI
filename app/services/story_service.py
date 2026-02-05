"""
Story Orchestration Service.

Handles:
- Input validation & moderation
- Prompt assembly
- LLM interaction with validation retries
- Parsing strictly typed JSON
- Conversion to scene models
- Saving to database
"""

import json
import logging
from typing import Dict, Any, List

from pydantic import ValidationError

from app.models.project import Project
from app.models.user import User
from app.schemas.scene_llm import StoryLLM
from app.schemas.scene import SceneCreate, NarrativeText, SceneBulkCreate
from app.services.llm_client import llm_client
from app.services.prompt_service import prompt_service
from app.services.scene_service import scene_service
from app.core.exceptions import (
    StoryParseFailed, 
    ContentBlocked, 
    ProjectInvalidStatus,
    LLMProviderError
)

logger = logging.getLogger(__name__)


class StoryService:
    """
    Service for generating stories via LLM.
    """
    
    async def parse_story(
        self, 
        user: User, 
        project: Project, 
        input_text: str
    ) -> Dict[str, Any]:
        """
        Parse raw story input into structured scenes.
        
        Flow:
        1. Moderate content (stub)
        2. Format prompts
        3. Call LLM (with retries handled by client + logic here)
        4. Validate JSON against strict schema
        5. Save scenes to DB
        6. Return success + usage
        
        Args:
            user: Authenticated user
            project: Target project (must be writable)
            input_text: Raw story description
            
        Returns:
            Dict with status, generated pages, and usage stats
        """
        # 1. Moderation Check (Stub)
        if "forbidden_content" in input_text.lower():
            raise ContentBlocked()
            
        # 2. Prepare Prompts
        # Extract config from project or defaults
        style = project.config.get("style", "standard")
        # Default to 'en' to satisfy SceneCreate schema (max_length=5)
        language = project.config.get("language", "en")
        
        system_prompt = prompt_service.get_system_prompt(language)
        user_prompt = prompt_service.format_story_prompt(input_text, style)
        
        # 3. Generate & Validate Loop
        # LLMClient handles network retries, but we handle Schema validation retries here
        max_schema_retries = 2
        last_error = None
        
        for attempt in range(max_schema_retries + 1):
            try:
                # Call LLM
                raw_json, usage = await llm_client.generate_json(system_prompt, user_prompt)
                
                # Validate Schema
                story_data = StoryLLM(**raw_json)
                
                # If valid, break loop
                break
            except ValidationError as e:
                logger.warning(f"Schema validation failed (attempt {attempt+1}): {e}")
                last_error = e
                # Context for retry? In a real system we'd append error to prompt
                # For now, just retry generation (randomness might fix it)
            except LLMProviderError as e:
                # Basic provider errors already retried by client, if bubbling up it's fatal
                raise e
        else:
            # Loop exhausted
            logger.error("Failed to parse valid story after retries")
            raise StoryParseFailed(detail=f"Output didn't match schema: {last_error}")

        # 4. Convert & Save
        # Iterate pages and add scenes
        saved_pages = []
        
        for page in story_data.pages:
            # Convert PanelLLM -> SceneCreate
            scene_creates = []
            for panel in page.panels:
                scene = SceneCreate(
                    page_no=page.page_no,
                    panel_no=panel.panel_no,
                    narrative_text=NarrativeText(
                        description=panel.description,
                        dialogue=[panel.dialogue] if panel.dialogue else [],
                        caption=panel.caption,
                        action=panel.description, # Mapping desc to action for now
                        setting="implied" # LLM didn't give setting explicitly yet, simplify
                    ),
                    language=language,
                    character_ids=[] # Todo: Link characters
                )
                scene_creates.append(scene)
            
            # Save using SceneService (handles strict validation & limits)
            # Make sure we catch limit exceptions from plan enforcement
            added_scenes = await scene_service.add_scenes(project, scene_creates)
            saved_pages.append({
                "page_no": page.page_no,
                "scenes": [s.dict() for s in added_scenes] # Simple dict dump
            })
            
        return {
            "status": "success",
            "pages": len(saved_pages),
            "usage": usage.model_dump(),
            "first_page_scenes": len(saved_pages[0]["scenes"]) if saved_pages else 0
        }


story_service = StoryService()
