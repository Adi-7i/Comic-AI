"""
Security utilities for password hashing and JWT token management.

Provides:
- Password hashing using bcrypt (secure, salt rounds=12)
- JWT token creation and validation
- Access and refresh token utilities
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    
    Args:
        password: Plain-text password to hash
        
    Returns:
        Hashed password string (bcrypt hash with salt)
        
    Example:
        hashed = hash_password("mypassword123")
        # Returns: "$2b$12$..."
    """
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.
    
    Args:
        plain_password: Plain-text password to verify
        hashed_password: Bcrypt hash to compare against
        
    Returns:
        True if password matches, False otherwise
        
    Example:
        is_valid = verify_password("mypassword123", "$2b$12$...")
    """
    # Convert to bytes
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    
    # Verify
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Access tokens are short-lived (default: 15 minutes) and used for
    authenticating API requests.
    
    Args:
        data: Payload to encode in token (e.g., {"sub": user_id})
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
        
    Security Notes:
        - Never include sensitive data (passwords, etc.) in payload
        - Only include user public_id, not MongoDB ObjectId
        - Token is signed with SECRET_KEY from environment
        
    Example:
        token = create_access_token({"sub": user.public_id})
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    # Encode and sign the token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT refresh token.
    
    Refresh tokens are long-lived (default: 7 days) and used to obtain
    new access tokens without re-authenticating.
    
    Args:
        data: Payload to encode in token (e.g., {"sub": user_id})
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
        
    Security Notes:
        - Refresh tokens should be stored securely (httpOnly cookies or secure storage)
        - Token hash should be stored in database for revocation support
        - Longer expiry than access tokens
        
    Example:
        token = create_refresh_token({"sub": user.public_id})
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    # Encode and sign the token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string to decode
        
    Returns:
        Decoded token payload as dictionary
        
    Raises:
        JWTError: If token is invalid, expired, or signature verification fails
        
    Example:
        try:
            payload = decode_token(token)
            user_id = payload["sub"]
        except JWTError:
            # Handle invalid token
            pass
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise


def verify_token_type(payload: Dict[str, Any], expected_type: str) -> bool:
    """
    Verify that a decoded token has the expected type.
    
    Args:
        payload: Decoded token payload
        expected_type: Expected token type ("access" or "refresh")
        
    Returns:
        True if token type matches, False otherwise
        
    Example:
        if verify_token_type(payload, "refresh"):
            # Process refresh token
            pass
    """
    return payload.get("type") == expected_type
