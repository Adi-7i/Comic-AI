"""
Azure Image Generation API Configuration.

Manages:
- Azure Image API credentials (from env, never logged)
- Resolution tiers (LOW/STANDARD/HIGH)
- Layout constants (4-panel grid)
- Provider selection for abstraction

SECURITY: API keys are SecretStr - never exposed in logs or errors.
"""

from typing import Literal, Optional
from enum import Enum
from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ImageResolution(str, Enum):
    """
    Resolution tiers mapped to Azure Image API sizes.
    
    - LOW: Free plan, smaller/faster (256x256 or 512x512)
    - STANDARD: Pro plan, balanced (1024x1024)
    - HIGH: Creative plan, print-ready (1792x1024 or higher)
    """
    LOW = "low"
    STANDARD = "standard"
    HIGH = "high"


# Resolution to Azure Image API size mapping
RESOLUTION_SIZE_MAP = {
    ImageResolution.LOW: "256x256",
    ImageResolution.STANDARD: "1024x1024",
    ImageResolution.HIGH: "1792x1024",
}


class AzureImageSettings(BaseSettings):
    """
    Azure Image API configuration.
    Reads from environment variables with 'AZURE_IMAGE_' prefix.
    """
    
    # API Credentials (SecretStr prevents accidental logging)
    API_KEY: Optional[SecretStr] = None
    
    # Azure Endpoint Configuration
    ENDPOINT: Optional[str] = None
    MODEL: str = "dall-e-3"
    API_VERSION: str = "2024-02-01"
    
    # Provider selection (azure or mock for testing)
    PROVIDER: Literal["azure", "mock"] = "azure"
    
    # Request Configuration
    TIMEOUT_SECONDS: int = 120
    MAX_RETRIES: int = 3
    RETRY_DELAY_SECONDS: int = 2
    
    # Layout Configuration (fixed 4-panel grid)
    PANELS_PER_PAGE: int = 4
    PANEL_SPACING_PX: int = 20
    SAFE_MARGIN_PX: int = 40  # Safe zone for text bubbles
    
    # Page Dimensions (pixels)
    PAGE_WIDTH_PX: int = 2048
    PAGE_HEIGHT_PX: int = 2048
    
    @field_validator("API_KEY")
    @classmethod
    def validate_api_key(cls, v: Optional[SecretStr]) -> Optional[SecretStr]:
        """API key validator - presence check done at runtime."""
        return v
    
    @property
    def is_configured(self) -> bool:
        """Check if Azure Image API is properly configured."""
        return self.API_KEY is not None and self.ENDPOINT is not None
    
    def get_resolution_size(self, resolution: ImageResolution) -> str:
        """Get Azure API size string for resolution tier."""
        return RESOLUTION_SIZE_MAP.get(resolution, "1024x1024")
    
    model_config = SettingsConfigDict(
        env_prefix="AZURE_IMAGE_",
        env_file=".env",
        extra="ignore"
    )


class AzureBlobSettings(BaseSettings):
    """
    Azure Blob Storage configuration.
    Reads from environment variables with 'AZURE_BLOB_' prefix.
    """
    
    # Connection (SecretStr to prevent logging)
    CONNECTION_STRING: Optional[SecretStr] = None
    
    # Container Configuration
    CONTAINER_NAME: str = "comic-assets"
    
    # Signed URL Configuration
    SAS_EXPIRY_HOURS: int = 24
    
    @property
    def is_configured(self) -> bool:
        """Check if Azure Blob Storage is properly configured."""
        return self.CONNECTION_STRING is not None
    
    model_config = SettingsConfigDict(
        env_prefix="AZURE_BLOB_",
        env_file=".env",
        extra="ignore"
    )


# Global settings instances
azure_image_settings = AzureImageSettings()
azure_blob_settings = AzureBlobSettings()
