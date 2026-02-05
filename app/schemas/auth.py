"""
Authentication-related Pydantic schemas.

Defines request and response models for authentication endpoints.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.enums import UserPlan, AccountStatus


class UserRegister(BaseModel):
    """
    User registration request schema.
    
    Required fields for creating a new user account.
    """
    email: EmailStr = Field(
        description="User email address (must be unique)"
    )
    password: str = Field(
        min_length=8,
        max_length=100,
        description="Password (minimum 8 characters)"
    )
    full_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="User's full name (optional)"
    )
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password meets minimum security requirements.
        
        Requirements:
        - At least 8 characters (enforced by min_length)
        - At least one letter (optional, can be added)
        - At least one number (optional, can be added)
        """
        # Basic validation - can be extended with regex for complexity
        if len(v.strip()) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "securepass123",
                "full_name": "John Doe"
            }
        }
    }


class UserLogin(BaseModel):
    """
    User login request schema.
    
    Credentials for authentication.
    """
    email: EmailStr = Field(
        description="User email address"
    )
    password: str = Field(
        description="User password"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "securepass123"
            }
        }
    }


class UserResponse(BaseModel):
    """
    User information response schema.
    
    Returns user data without sensitive fields (no password).
    Uses public_id instead of MongoDB ObjectId.
    """
    public_id: str = Field(
        description="Public user identifier"
    )
    email: EmailStr = Field(
        description="User email address"
    )
    full_name: Optional[str] = Field(
        default=None,
        description="User's full name"
    )
    plan: UserPlan = Field(
        description="Current subscription plan"
    )
    account_status: AccountStatus = Field(
        description="Account status"
    )
    generation_limits: dict = Field(
        description="Generation quota and usage tracking"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "public_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "full_name": "John Doe",
                "plan": "free",
                "account_status": "active",
                "generation_limits": {
                    "monthly_quota": 10,
                    "current_usage": 3,
                    "last_reset_at": "2026-02-01T00:00:00"
                }
            }
        }
    }
