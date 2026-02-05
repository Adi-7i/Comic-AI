"""
LLM Client Service.

Abstracts the LLM provider interaction.
Currently supports:
- OpenAI (standard)
- Mock (for testing/dev)
"""

import json
import logging
from typing import List, Dict, Any, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.llm_config import llm_settings
from app.core.exceptions import LLMApiKeyMissing, LLMProviderError
from app.schemas.usage import GenerationUsage

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Provider-agnostic LLM client.
    """
    
    def __init__(self):
        self.provider = llm_settings.PROVIDER
        self.api_key = llm_settings.API_KEY.get_secret_value() if llm_settings.API_KEY else None
        self.model = llm_settings.MODEL
        
        # Validation for non-mock providers
        if self.provider != "mock" and not self.api_key:
            # We log warning instead of crashing init, as app might run in restricted mode
            logger.warning("LLM API Key missing for provider %s", self.provider)

    @retry(
        stop=stop_after_attempt(llm_settings.MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def generate_json(
        self, 
        system_prompt: str, 
        user_prompt: str
    ) -> Dict[str, Any]:
        """
        Generate JSON output from LLM.
        
        Returns:
            Tuple of (parsed_json_dict, usage_metadata)
        """
        if self.provider == "mock":
            return self._mock_generation()
            
        if not self.api_key:
            raise LLMApiKeyMissing()
            
        if self.provider == "openai":
            return await self._openai_generation(system_prompt, user_prompt)
            
        if self.provider == "azure":
            return await self._azure_generation(system_prompt, user_prompt)
            
        raise NotImplementedError(f"Provider {self.provider} not supported")

    async def _openai_generation(self, system: str, user: str):
        """
        Call OpenAI API compatible endpoint.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            "temperature": llm_settings.TEMPERATURE,
            "response_format": {"type": "json_object"}
        }
        
        url = "https://api.openai.com/v1/chat/completions"
        
        return await self._make_request(url, headers, payload, "openai")

    async def _azure_generation(self, system: str, user: str):
        """
        Call Azure OpenAI Endpoint.
        """
        if not llm_settings.AZURE_BASE_URL or not llm_settings.AZURE_DEPLOYMENT:
            raise LLMProviderError(detail="Azure configuration missing (Base URL or Deployment)")
            
        # Format: https://{your-resource-name}.openai.azure.com/openai/deployments/{deployment-id}/chat/completions?api-version={api-version}
        base_url = llm_settings.AZURE_BASE_URL.rstrip('/')
        url = f"{base_url}/openai/deployments/{llm_settings.AZURE_DEPLOYMENT}/chat/completions"
        
        params = {
            "api-version": llm_settings.AZURE_API_VERSION or "2023-05-15"
        }
        
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            "temperature": llm_settings.TEMPERATURE,
            "response_format": {"type": "json_object"}
        }
        
        return await self._make_request(url, headers, payload, "azure", params=params)

    async def _make_request(self, url: str, headers: Dict, payload: Dict, provider_name: str, params: Dict = None):
        """
        Shared request logic.
        """
        try:
            async with httpx.AsyncClient(timeout=llm_settings.TIMEOUT_SECONDS) as client:
                response = await client.post(url, json=payload, headers=headers, params=params)
                
                if response.status_code != 200:
                    logger.error("LLM Provider Error (%s): %s", provider_name, response.text)
                    raise LLMProviderError(detail=f"{provider_name} Error: {response.status_code}")
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                usage_raw = data.get("usage", {})
                usage = GenerationUsage(
                    provider=provider_name,
                    model=self.model,
                    tokens_in=usage_raw.get("prompt_tokens", 0),
                    tokens_out=usage_raw.get("completion_tokens", 0),
                    estimated_cost=0.0
                )
                
                return json.loads(content), usage
                
        except httpx.RequestError as e:
            logger.error("LLM Network Error: %s", str(e))
            raise LLMProviderError(detail="Network error connecting to LLM provider")
        except json.JSONDecodeError:
            logger.error("Failed to decode LLM JSON output")
            raise LLMProviderError(detail="LLM returned invalid JSON structure")

    def _mock_generation(self):
        """
        Mock response for testing/dev without API key.
        """
        mock_output = {
            "pages": [
                {
                    "page_no": 1,
                    "panels": [
                        {
                            "panel_no": 1,
                            "description": "A futuristic city skyline with neon lights.",
                            "dialogue": "Welcome to Neo-Tokyo.",
                            "caption": "The year 2077."
                        },
                        {
                            "panel_no": 2,
                            "description": "Protagonist walking down rain-slicked street.",
                            "dialogue": None,
                            "caption": "It never stops raining here."
                        },
                        {
                            "panel_no": 3,
                            "description": "Close up of protagonist's cybernetic eye.",
                            "dialogue": "I see everything.",
                            "caption": None
                        },
                        {
                            "panel_no": 4,
                            "description": "A mysterious figure in the shadows.",
                            "dialogue": "Are you the one?",
                            "caption": None
                        }
                    ]
                }
            ]
        }
        
        usage = GenerationUsage(
            provider="mock",
            model="mock-gpt",
            tokens_in=100,
            tokens_out=200,
            estimated_cost=0.0
        )
        
        return mock_output, usage


llm_client = LLMClient()
