"""
Token-related Pydantic schemas.

Defines request and response models for token operations.
"""

from typing import Optional
from pydantic import BaseModel, Field


class Token(BaseModel):
    """
    JWT token response schema.
    
    Returned after successful login or token refresh.
    Contains both access and refresh tokens.
    """
    access_token: str = Field(
        description="JWT access token (short-lived, 15 min)"
    )
    refresh_token: str = Field(
        description="JWT refresh token (long-lived, 7 days)"
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer' for JWT)"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }


class AccessToken(BaseModel):
    """
    Access token only response schema.
    
    Returned after refreshing tokens (no new refresh token).
    """
    access_token: str = Field(
        description="JWT access token (short-lived, 15 min)"
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer' for JWT)"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }


class RefreshRequest(BaseModel):
    """
    Refresh token request schema.
    
    Contains the refresh token to validate and exchange for new access token.
    """
    refresh_token: str = Field(
        description="JWT refresh token received during login"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    }


class TokenData(BaseModel):
    """
    Decoded token payload schema.
    
    Internal use only - represents validated token data.
    """
    user_id: str = Field(
        description="User public_id from token subject"
    )
    token_type: str = Field(
        description="Token type (access or refresh)"
    )
    scopes: Optional[list] = Field(
        default=None,
        description="Optional permission scopes (for future use)"
    )
