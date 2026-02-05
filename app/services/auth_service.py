"""
Authentication service - Core authentication business logic.

Handles user registration, login, token management, and logout.
NO route logic here - pure business logic only.
"""

from datetime import datetime
from typing import Optional

from jose import JWTError

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type,
)
from app.core.exceptions import (
    AuthInvalidCredentials,
    AuthTokenExpired,
    AuthUnauthorized,
    EmailAlreadyExists,
    AccountSuspended,
)
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.enums import UserPlan, AccountStatus, AuditEventType
from app.schemas.token import Token, AccessToken


class AuthService:
    """
    Authentication service class.
    
    Provides methods for user authentication workflows.
    All methods are async and work with Beanie ODM.
    """
    
    @staticmethod
    async def register_user(email: str, password: str, full_name: Optional[str] = None) -> User:
        """
        Register a new user account.
        
        Args:
            email: User's email address (must be unique)
            password: Plain-text password (will be hashed)
            full_name: Optional user's full name
            
        Returns:
            Created User object
            
        Raises:
            EmailAlreadyExists: If email is already registered
            
        Business Logic:
            1. Check if email already exists
            2. Hash password securely
            3. Create user with FREE plan by default
            4. Set generation limits based on FREE plan
            5. Log audit event
        """
        # Check if email already exists
        existing_user = await User.find_one(User.email == email)
        if existing_user:
            raise EmailAlreadyExists()
        
        # Hash password
        hashed_pwd = hash_password(password)
        
        # Create user with default FREE plan
        user = User(
            email=email,
            hashed_password=hashed_pwd,
            full_name=full_name,
            plan=UserPlan.FREE,
            account_status=AccountStatus.ACTIVE,
            generation_limits={
                "monthly_quota": 0,  # FREE plan has no generation quota
                "current_usage": 0,
                "last_reset_at": datetime.utcnow().isoformat(),
            }
        )
        
        await user.save()
        
        # Log audit event (user registration)
        audit_log = AuditLog(
            user_id=user.id,
            event_type=AuditEventType.USER_LOGIN,  # Using LOGIN for registration
            event_data={
                "action": "user_registered",
                "email": email,
                "plan": user.plan.value,
            },
            severity="info"
        )
        await audit_log.save()
        
        return user
    
    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User's email address
            password: Plain-text password to verify
            
        Returns:
            User object if authentication succeeds, None otherwise
            
        Raises:
            AuthInvalidCredentials: If email/password is invalid
            AccountSuspended: If account is not active
            
        Business Logic:
            1. Find user by email
            2. Verify password hash
            3. Check account status is ACTIVE
            4. Update last_login_at timestamp
            5. Return user or raise exception
        """
        # Find user by email
        user = await User.find_one(User.email == email, User.is_deleted == False)
        
        if not user:
            raise AuthInvalidCredentials()
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            raise AuthInvalidCredentials()
        
        # Check account status
        if user.account_status != AccountStatus.ACTIVE:
            raise AccountSuspended(
                detail=f"Account is {user.account_status.value}"
            )
        
        # Update last login timestamp
        user.last_login_at = datetime.utcnow()
        await user.save()
        
        # Log audit event (successful login)
        audit_log = AuditLog(
            user_id=user.id,
            event_type=AuditEventType.USER_LOGIN,
            event_data={
                "action": "login_success",
                "email": email,
            },
            severity="info"
        )
        await audit_log.save()
        
        return user
    
    @staticmethod
    async def create_tokens_for_user(user: User) -> Token:
        """
        Create access and refresh tokens for authenticated user.
        
        Args:
            user: Authenticated User object
            
        Returns:
            Token schema with access_token and refresh_token
            
        Security Notes:
            - Only user public_id is stored in token (not MongoDB ObjectId)
            - Tokens are signed with SECRET_KEY
            - Access token expires in 15 minutes
            - Refresh token expires in 7 days
        """
        # Create token payload with user public_id
        token_data = {"sub": user.public_id}
        
        # Generate tokens
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    @staticmethod
    async def refresh_access_token(refresh_token: str) -> AccessToken:
        """
        Validate refresh token and issue new access token.
        
        Args:
            refresh_token: JWT refresh token
            
        Returns:
            AccessToken schema with new access_token
            
        Raises:
            AuthUnauthorized: If refresh token is invalid
            AuthTokenExpired: If refresh token has expired
            
        Business Logic:
            1. Decode refresh token
            2. Verify token type is "refresh"
            3. Find user by public_id
            4. Generate new access token
            5. Return new access token only (no new refresh token)
        """
        try:
            # Decode token
            payload = decode_token(refresh_token)
            
            # Verify it's a refresh token
            if not verify_token_type(payload, "refresh"):
                raise AuthUnauthorized(detail="Invalid token type")
            
            # Extract user public_id
            user_public_id: str = payload.get("sub")
            if not user_public_id:
                raise AuthUnauthorized()
            
            # Find user
            user = await User.find_one(
                User.public_id == user_public_id,
                User.is_deleted == False
            )
            
            if not user:
                raise AuthUnauthorized()
            
            # Check account status
            if user.account_status != AccountStatus.ACTIVE:
                raise AccountSuspended()
            
            # Create new access token
            token_data = {"sub": user.public_id}
            access_token = create_access_token(token_data)
            
            return AccessToken(
                access_token=access_token,
                token_type="bearer"
            )
            
        except JWTError:
            raise AuthTokenExpired()
    
    @staticmethod
    async def get_current_user_from_token(token: str) -> User:
        """
        Get current user from JWT access token.
        
        Args:
            token: JWT access token
            
        Returns:
            User object
            
        Raises:
            AuthUnauthorized: If token is invalid or user not found
            AuthTokenExpired: If token has expired
            
        Used by: get_current_user dependency
        """
        try:
            # Decode token
            payload = decode_token(token)
            
            # Verify it's an access token
            if not verify_token_type(payload, "access"):
                raise AuthUnauthorized(detail="Invalid token type")
            
            # Extract user public_id
            user_public_id: str = payload.get("sub")
            if not user_public_id:
                raise AuthUnauthorized()
            
            # Find user
            user = await User.find_one(
                User.public_id == user_public_id,
                User.is_deleted == False
            )
            
            if not user:
                raise AuthUnauthorized()
            
            return user
            
        except JWTError:
            raise AuthTokenExpired()


# Singleton instance
auth_service = AuthService()
