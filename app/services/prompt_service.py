"""
Prompt Service.

Manages prompt templates and formatting for story generation.
Ensures consistent JSON output structure.
"""

from typing import Dict, Any

from app.schemas.scene_llm import StoryLLM

class PromptService:
    """
    Service for managing prompts.
    """
    
    # System prompt enforcing strict JSON and 4-panel structure
    SYSTEM_PROMPT = """
You are an expert comic book writer and storyboard artist.
Your task is to turn a story description into a structured comic script.

STRICT RULES:
1. Output MUST be valid JSON matching the specified schema.
2. The comic MUST be divided into pages, with EXACTLY 4 panels per page.
3. If the story is short, pad it to fill 4 panels. If long, split into multiple pages (each with 4 panels).
4. Each panel needs:
   - description: Visual details for an artist (or AI) to draw.
   - dialogue: Character dialogue (or null).
   - caption: Narrative text (or null).
5. Do NOT include markdown formatting (like ```json). Just the raw JSON.
6. Language: Output in {language}, but keep keys in English.

JSON SCHEMA:
{{
  "pages": [
    {{
      "page_no": 1,
      "panels": [
        {{
          "panel_no": 1,
          "description": "...",
          "dialogue": "...",
          "caption": "..."
        }},
        ... (exactly 4 panels)
      ]
    }}
  ]
}}
"""

    def get_system_prompt(self, language: str = "English") -> str:
        """
        Get the system prompt formatted with language.
        """
        return self.SYSTEM_PROMPT.format(language=language)

    def format_story_prompt(
        self, 
        input_text: str, 
        style: str, 
        theme: str = "standard"
    ) -> str:
        """
        Format the user input into a prompt.
        """
        return f"""
STORY INPUT:
{input_text}

STYLE: {style}
THEME: {theme}

Generate the comic script now. Remember: Exactly 4 panels per page.
"""

prompt_service = PromptService()
