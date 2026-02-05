"""
Authentication dependencies for FastAPI routes.

Provides reusable dependencies for:
- Token validation
- User authentication
- Plan enforcement
- Rate limiting
"""

from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.models.user import User
from app.models.enums import UserPlan, AccountStatus
from app.services.auth_service import auth_service
from app.services.plan_service import plan_service
from app.core.exceptions import (
    AuthUnauthorized,
    AccountSuspended,
    PlanLimitExceeded,
)


# OAuth2 scheme for token extraction
# This will look for "Authorization: Bearer <token>" header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependency to get current authenticated user from JWT token.
    
    Extracts token from Authorization header, validates it,
    and returns the User object.
    
    Args:
        token: JWT access token from Authorization header
        
    Returns:
        User object of authenticated user
        
    Raises:
        AuthUnauthorized: If token is invalid or user not found
        AuthTokenExpired: If token has expired
        
    Usage:
        @app.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            return {"user_id": user.public_id}
    """
    user = await auth_service.get_current_user_from_token(token)
    return user


async def get_active_user(user: User = Depends(get_current_user)) -> User:
    """
    Dependency to get current user and verify account is active.
    
    Checks that user.account_status == ACTIVE.
    Use this for routes that require an active account.
    
    Args:
        user: User object from get_current_user dependency
        
    Returns:
        User object if account is active
        
    Raises:
        AccountSuspended: If account is suspended or deleted
        
    Usage:
        @app.get("/active-required")
        async def route(user: User = Depends(get_active_user)):
            return {"status": "active"}
    """
    if user.account_status != AccountStatus.ACTIVE:
        raise AccountSuspended(
            detail=f"Account is {user.account_status.value}. "
            "Please contact support."
        )
    
    return user


def plan_required(required_plan: UserPlan) -> Callable:
    """
    Dependency factory for plan enforcement.
    
    Creates a dependency that checks if user has required plan or higher.
    This is a factory function that returns a dependency function.
    
    Args:
        required_plan: Minimum plan tier required
        
    Returns:
        Dependency function that validates user plan
        
    Raises:
        PlanLimitExceeded: If user's plan is insufficient
        
    Usage:
        # Require PRO plan or higher
        @app.post("/pro-feature")
        async def pro_route(user: User = Depends(plan_required(UserPlan.PRO))):
            return {"message": "PRO feature accessed"}
            
        # Require CREATIVE plan
        @app.post("/creative-feature")
        async def creative_route(user: User = Depends(plan_required(UserPlan.CREATIVE))):
            return {"message": "CREATIVE feature accessed"}
    """
    async def check_plan(user: User = Depends(get_active_user)) -> User:
        """Inner dependency that performs the actual check."""
        plan_service.check_plan_access(user, required_plan)
        return user
    
    return check_plan


async def rate_limit_check(user: User = Depends(get_active_user)) -> User:
    """
    Dependency for basic rate limiting via generation quota.
    
    Checks that user hasn't exceeded their monthly generation quota.
    Use this before allowing generation operations.
    
    Args:
        user: User object from get_active_user dependency
        
    Returns:
        User object if quota not exceeded
        
    Raises:
        QuotaExceeded: If monthly quota is exceeded
        
    Usage:
        @app.post("/generate")
        async def generate(user: User = Depends(rate_limit_check)):
            # Proceed with generation
            pass
    """
    plan_service.check_generation_quota(user)
    return user


async def can_generate(user: User = Depends(get_active_user)) -> User:
    """
    Dependency to check if user's plan allows generation at all.
    
    FREE plan users cannot generate any comics.
    Use this as a quick check before detailed generation logic.
    
    Args:
        user: User object from get_active_user dependency
        
    Returns:
        User object if generation is allowed
        
    Raises:
        PlanLimitExceeded: If plan doesn't allow generation
        
    Usage:
        @app.post("/generate")
        async def generate(user: User = Depends(can_generate)):
            # User can generate
            pass
    """
    if not plan_service.can_generate(user):
        raise PlanLimitExceeded(
            detail=f"Your {user.plan.value} plan does not allow comic generation. "
            "Please upgrade to PRO or CREATIVE plan."
        )
    
    return user
