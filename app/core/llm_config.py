"""
LLM Configuration and Settings.

Manages:
- Provider selection (OpenAI, Anthropic, Mock, Azure)
- API Keys (Securely from env)
- Model selection
- Retry configuration
"""

from typing import Literal, Optional
from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """
    LLM-specific configuration.
    Reads from environment variables with 'LLM_' prefix.
    """
    # Provider selection
    PROVIDER: Literal["openai", "anthropic", "mock", "azure"] = "openai"
    
    # API Key (SecretStr prevents logging)
    API_KEY: Optional[SecretStr] = None
    
    # Azure Specifics
    AZURE_BASE_URL: Optional[str] = None
    AZURE_API_VERSION: Optional[str] = None
    AZURE_DEPLOYMENT: Optional[str] = None
    
    # Model selection (For Azure, this might be redundant if using DEPLOYMENT, but kept for consistency)
    MODEL: str = "gpt-3.5-turbo"
    
    # Parameters
    TEMPERATURE: float = 0.7
    MAX_RETRIES: int = 2
    TIMEOUT_SECONDS: int = 60
    
    @field_validator("API_KEY")
    @classmethod
    def validate_api_key(cls, v: Optional[SecretStr], info) -> Optional[SecretStr]:
        return v

    model_config = SettingsConfigDict(
        env_prefix="LLM_",
        env_file=".env",
        extra="ignore"
    )


llm_settings = LLMSettings()
