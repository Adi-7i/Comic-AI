"""
Configuration management for the application.

Uses Pydantic Settings to load configuration from environment variables
with .env file support. All sensitive credentials MUST be loaded from env vars.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Environment variables take precedence over .env file values.
    All settings are type-safe and validated by Pydantic.
    """
    
    # Application
    APP_NAME: str = "Comic Generation SaaS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security - REQUIRED in production
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_USE_ENV_VAR"  # JWT signing secret
    ALGORITHM: str = "HS256"  # JWT algorithm
    
    # Token expiry
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Short-lived access token
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7     # Long-lived refresh token
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "comic_saas"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60        # Max requests per minute per user
    GENERATION_LIMIT_PER_DAY: int = 100    # Max generations per day (global)
    
    # Plan Limits (stored here for easy configuration)
    # FREE plan
    FREE_MAX_PAGES: int = 0
    FREE_ALLOW_GENERATION: bool = False
    FREE_MONTHLY_QUOTA: int = 0
    
    # PRO plan
    PRO_MAX_PAGES: int = 3
    PRO_WATERMARK_REQUIRED: bool = True
    PRO_MONTHLY_QUOTA: int = 50
    
    # CREATIVE plan
    CREATIVE_MAX_PAGES: int = 10
    CREATIVE_WATERMARK_REQUIRED: bool = False
    CREATIVE_MONTHLY_QUOTA: int = 200
    
    # CORS (for frontend integration)
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Global settings instance
# Import this in other modules: from app.core.config import settings
settings = Settings()
