"""
User collection model.

Manages user accounts, authentication, subscription plans, and usage quotas.
"""

from datetime import datetime
from typing import Optional, Dict

from beanie import Indexed
from pydantic import EmailStr, Field
from pymongo import IndexModel, ASCENDING

from app.models.base import BaseDocument
from app.models.enums import UserPlan, AccountStatus


class User(BaseDocument):
    """
    User account model.
    
    Stores user authentication, profile, plan, and usage tracking.
    No business logic - pure data model with validation only.
    """
    
    # Authentication
    email: Indexed(EmailStr, unique=True) = Field(
        description="User email address - unique identifier for login"
    )
    hashed_password: str = Field(
        description="Bcrypt/Argon2 hashed password - NEVER store plain text"
    )
    
    # Profile
    full_name: Optional[str] = Field(
        default=None,
        description="User's full name (optional)"
    )
    
    # Plan and Status
    plan: UserPlan = Field(
        default=UserPlan.FREE,
        description="Current subscription plan tier"
    )
    account_status: AccountStatus = Field(
        default=AccountStatus.ACTIVE,
        description="Account status (active/suspended/deleted)"
    )
    
    # Generation limits and tracking
    generation_limits: Dict = Field(
        default_factory=lambda: {
            "monthly_quota": 10,  # Free tier default
            "current_usage": 0,
            "last_reset_at": datetime.utcnow().isoformat(),
        },
        description="Monthly generation quota and usage tracking"
    )
    
    # Activity tracking
    last_login_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp of last successful login"
    )
    
    class Settings:
        name = "users"
        
        indexes = [
            # Unique email for authentication
            IndexModel([("email", ASCENDING)], unique=True),
            
            # Plan-based queries (e.g., find all pro users)
            IndexModel([("plan", ASCENDING)]),
            
            # Account status filtering (e.g., find all active users)
            IndexModel([("account_status", ASCENDING)]),
            
            # Inherit base indexes (public_id, is_deleted, created_at)
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "hashed_password": "$2b$12$...",
                "full_name": "John Doe",
                "plan": "free",
                "account_status": "active",
                "generation_limits": {
                    "monthly_quota": 10,
                    "current_usage": 3,
                    "last_reset_at": "2026-02-01T00:00:00",
                },
            }
        }
