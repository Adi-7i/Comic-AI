"""
Authentication routes - Thin route handlers.

All routes delegate to services for business logic.
Routes are responsible for:
- Request validation (via Pydantic schemas)
- Calling appropriate service methods
- Returning responses
- Error handling

NO business logic in routes.
"""

from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import UserRegister, UserLogin, UserResponse
from app.schemas.token import Token, AccessToken, RefreshRequest
from app.services.auth_service import auth_service
from app.models.user import User
from app.api.v1.dependencies.auth import get_current_user, get_active_user


# Create router for auth endpoints
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Dict, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Register a new user account.
    
    Creates a new user with FREE plan by default.
    Returns user info and authentication tokens.
    
    Args:
        user_data: UserRegister schema with email, password, full_name
        
    Returns:
        Dictionary with user info and tokens
        
    Raises:
        400: Email already exists
        422: Validation error (invalid email, weak password, etc.)
    """
    # Delegate to service
    user = await auth_service.register_user(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name
    )
    
    # Generate tokens
    tokens = await auth_service.create_tokens_for_user(user)
    
    # Return user info and tokens
    return {
        "user": {
            "public_id": user.public_id,
            "email": user.email,
            "full_name": user.full_name,
            "plan": user.plan.value,
            "account_status": user.account_status.value,
        },
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
        "token_type": tokens.token_type,
    }


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Login with email and password.
    
    Authenticates user and returns JWT tokens.
    
    Args:
        credentials: UserLogin schema with email and password
        
    Returns:
        Token schema with access_token and refresh_token
        
    Raises:
        401: Invalid credentials
        403: Account suspended or deleted
    """
    # Authenticate user
    user = await auth_service.authenticate_user(
        email=credentials.email,
        password=credentials.password
    )
    
    # Generate tokens
    tokens = await auth_service.create_tokens_for_user(user)
    
    return tokens


@router.post("/login/form", response_model=Token)
async def login_form(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login with OAuth2 password flow (for Swagger UI compatibility).
    
    This endpoint uses OAuth2PasswordRequestForm which expects:
    - username (we use email)
    - password
    
    Args:
        form_data: OAuth2 form data (username=email, password)
        
    Returns:
        Token schema with access_token and refresh_token
        
    Raises:
        401: Invalid credentials
        403: Account suspended or deleted
    """
    # Authenticate user (username field contains email)
    user = await auth_service.authenticate_user(
        email=form_data.username,  # OAuth2 uses 'username' field
        password=form_data.password
    )
    
    # Generate tokens
    tokens = await auth_service.create_tokens_for_user(user)
    
    return tokens


@router.post("/refresh", response_model=AccessToken)
async def refresh_token(refresh_data: RefreshRequest):
    """
    Refresh access token using refresh token.
    
    Validates refresh token and issues new access token.
    Does NOT issue a new refresh token.
    
    Args:
        refresh_data: RefreshRequest schema with refresh_token
        
    Returns:
        AccessToken schema with new access_token
        
    Raises:
        401: Invalid or expired refresh token
        403: Account suspended or deleted
    """
    # Refresh token via service
    new_token = await auth_service.refresh_access_token(
        refresh_token=refresh_data.refresh_token
    )
    
    return new_token


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: User = Depends(get_active_user)):
    """
    Get current authenticated user information.
    
    Requires valid access token in Authorization header.
    Returns user profile without sensitive data.
    
    Args:
        user: Current user from get_active_user dependency
        
    Returns:
        UserResponse schema with user profile
        
    Raises:
        401: Invalid or missing token
        403: Account not active
    """
    return UserResponse(
        public_id=user.public_id,
        email=user.email,
        full_name=user.full_name,
        plan=user.plan,
        account_status=user.account_status,
        generation_limits=user.generation_limits,
    )


@router.post("/logout", response_model=Dict)
async def logout(user: User = Depends(get_current_user)):
    """
    Logout user (invalidate tokens).
    
    Note: With JWT, true logout requires token blacklisting or
    storing refresh tokens in DB for revocation.
    This endpoint is a placeholder that confirms logout.
    
    In production, you would:
    1. Store refresh token hash in DB during login
    2. Mark it as revoked during logout
    3. Check revocation status during token refresh
    
    Args:
        user: Current user from get_current_user dependency
        
    Returns:
        Success message
    """
    # In production: invalidate refresh token in database
    # For now, just return success
    
    return {
        "message": "Logged out successfully",
        "detail": "Please discard your tokens on the client side"
    }


@router.get("/health", response_model=Dict)
async def health_check():
    """
    Health check endpoint for auth service.
    
    Public endpoint (no authentication required).
    Used for monitoring and load balancer health checks.
    
    Returns:
        Status message
    """
    return {
        "status": "healthy",
        "service": "authentication"
    }
