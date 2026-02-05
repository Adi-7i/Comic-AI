"""
Azure Image Generation API client.

Provides:
- Abstract protocol for swappable providers
- AzureImageClient for Azure DALL-E API
- MockImageClient for testing without API calls

SECURITY: API keys never logged. Provider errors sanitized.
"""

import logging
import httpx
from typing import Optional, Protocol
from io import BytesIO

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from app.core.azure_image_config import (
    azure_image_settings,
    ImageResolution,
    RESOLUTION_SIZE_MAP
)
from app.core.exceptions import (
    AzureImageApiKeyMissing,
    AzureImageProviderError,
    ImageGenerationFailed
)


logger = logging.getLogger(__name__)


class ImageProviderProtocol(Protocol):
    """
    Protocol for image generation providers.
    
    Implement this to add new providers (Stability AI, Midjourney, etc.)
    """
    
    async def generate_image(
        self,
        prompt: str,
        resolution: ImageResolution,
        seed: Optional[int] = None
    ) -> bytes:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt: Text description of the image to generate
            resolution: Resolution tier (LOW/STANDARD/HIGH)
            seed: Random seed for reproducibility (if supported)
            
        Returns:
            Image data as bytes (PNG format preferred)
            
        Raises:
            AzureImageApiKeyMissing: API key not configured
            AzureImageProviderError: Provider returned an error
            ImageGenerationFailed: Generation failed after retries
        """
        ...


class AzureImageClient:
    """
    Azure Image Generation API client (DALL-E compatible).
    
    Uses Azure OpenAI Service endpoint for image generation.
    """
    
    def __init__(self):
        self._http_client: Optional[httpx.AsyncClient] = None
    
    def _get_client(self) -> httpx.AsyncClient:
        """Lazy-initialize HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(azure_image_settings.TIMEOUT_SECONDS)
            )
        return self._http_client
    
    def _validate_config(self):
        """Ensure API is configured before making requests."""
        if not azure_image_settings.is_configured:
            raise AzureImageApiKeyMissing(
                detail="Azure Image API key or endpoint not configured"
            )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
        reraise=True
    )
    async def generate_image(
        self,
        prompt: str,
        resolution: ImageResolution = ImageResolution.STANDARD,
        seed: Optional[int] = None
    ) -> bytes:
        """
        Generate an image using Azure Image API.
        
        Args:
            prompt: Image generation prompt
            resolution: Resolution tier
            seed: Optional seed for consistency (may not be supported by all models)
            
        Returns:
            PNG image bytes
        """
        self._validate_config()
        
        client = self._get_client()
        
        # Build Azure OpenAI Image API endpoint
        endpoint = azure_image_settings.ENDPOINT.rstrip("/")
        api_version = azure_image_settings.API_VERSION
        url = f"{endpoint}/openai/deployments/{azure_image_settings.MODEL}/images/generations?api-version={api_version}"
        
        # Get size from resolution
        size = azure_image_settings.get_resolution_size(resolution)
        
        # Build request payload
        payload = {
            "prompt": prompt,
            "n": 1,
            "size": size,
            "response_format": "b64_json"  # Get base64 directly
        }
        
        # Note: Seed support varies by model - DALL-E 3 may not support it
        # We track it for consistency across generations but may not use it in API
        
        headers = {
            "api-key": azure_image_settings.API_KEY.get_secret_value(),
            "Content-Type": "application/json"
        }
        
        try:
            logger.info(f"Generating image: size={size}, prompt_length={len(prompt)}")
            
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code == 429:
                raise AzureImageProviderError(
                    detail="Image generation rate limit exceeded. Please try again later."
                )
            
            if response.status_code >= 500:
                raise AzureImageProviderError(
                    detail="Azure Image service temporarily unavailable"
                )
            
            if response.status_code != 200:
                # Don't leak error details
                logger.error(f"Azure Image API error: status={response.status_code}")
                raise ImageGenerationFailed(
                    detail="Image generation failed. Please try again."
                )
            
            data = response.json()
            
            # Extract image from response
            if "data" in data and len(data["data"]) > 0:
                import base64
                b64_image = data["data"][0].get("b64_json")
                if b64_image:
                    return base64.b64decode(b64_image)
            
            raise ImageGenerationFailed(
                detail="No image returned from generation service"
            )
            
        except httpx.TimeoutException:
            logger.error("Azure Image API timeout")
            raise AzureImageProviderError(
                detail="Image generation timed out. Please try again."
            )
        except httpx.ConnectError:
            logger.error("Azure Image API connection error")
            raise AzureImageProviderError(
                detail="Unable to connect to image generation service"
            )
    
    async def close(self):
        """Close the HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None


class MockImageClient:
    """
    Mock image generation client for testing.
    
    Generates simple placeholder images without API calls.
    """
    
    async def generate_image(
        self,
        prompt: str,
        resolution: ImageResolution = ImageResolution.STANDARD,
        seed: Optional[int] = None
    ) -> bytes:
        """
        Generate a placeholder image for testing.
        
        Creates a colored rectangle with text showing the prompt.
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            # If Pillow not available, return minimal PNG
            return self._minimal_png()
        
        # Determine size from resolution
        size_str = RESOLUTION_SIZE_MAP.get(resolution, "1024x1024")
        width, height = map(int, size_str.split("x"))
        
        # Create image with gradient background
        img = Image.new("RGB", (width, height), color=(40, 44, 52))
        draw = ImageDraw.Draw(img)
        
        # Add border
        border_color = (97, 175, 239)
        draw.rectangle([10, 10, width-10, height-10], outline=border_color, width=3)
        
        # Add text (truncated prompt)
        text = f"[MOCK] {prompt[:100]}..."
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Center text
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (width - text_width) // 2
        draw.text((text_x, height // 2), text, fill=(255, 255, 255), font=font)
        
        # Add seed info if provided
        if seed:
            draw.text((20, height - 40), f"Seed: {seed}", fill=(150, 150, 150), font=font)
        
        # Convert to bytes
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
    
    def _minimal_png(self) -> bytes:
        """Return a minimal 1x1 PNG if Pillow unavailable."""
        # Minimal valid PNG (1x1 transparent pixel)
        return bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,
            0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,
            0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
            0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,
            0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,
            0x42, 0x60, 0x82
        ])
    
    async def close(self):
        """No-op for mock client."""
        pass


def get_image_client() -> ImageProviderProtocol:
    """
    Factory function to get the appropriate image client.
    
    Returns AzureImageClient if configured, MockImageClient otherwise.
    """
    if azure_image_settings.PROVIDER == "mock":
        logger.info("Using MockImageClient")
        return MockImageClient()
    
    if azure_image_settings.is_configured:
        logger.info("Using AzureImageClient")
        return AzureImageClient()
    
    logger.warning("Azure Image not configured - falling back to MockImageClient")
    return MockImageClient()


# Default instance (lazy - use get_image_client() for proper initialization)
image_client: ImageProviderProtocol = get_image_client()
