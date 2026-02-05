"""
Custom exception classes for the application.

Provides a clear error taxonomy for different failure scenarios.
All exceptions include appropriate HTTP status codes for FastAPI.
"""

from fastapi import HTTPException, status


class AuthInvalidCredentials(HTTPException):
    """
    Raised when user provides invalid email/password combination.
    HTTP 401 Unauthorized.
    """
    def __init__(self, detail: str = "Invalid email or password"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthTokenExpired(HTTPException):
    """
    Raised when JWT token has expired.
    HTTP 401 Unauthorized.
    """
    def __init__(self, detail: str = "Token has expired"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthUnauthorized(HTTPException):
    """
    Raised when authentication is missing or invalid.
    HTTP 401 Unauthorized.
    """
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class PlanLimitExceeded(HTTPException):
    """
    Raised when user's plan tier is insufficient for requested feature.
    HTTP 403 Forbidden.
    """
    def __init__(self, detail: str = "Your current plan does not allow this feature"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class QuotaExceeded(HTTPException):
    """
    Raised when user has exceeded their monthly generation quota.
    HTTP 429 Too Many Requests.
    """
    def __init__(self, detail: str = "Monthly generation quota exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
        )


class AccountSuspended(HTTPException):
    """
    Raised when user account is suspended or deleted.
    HTTP 403 Forbidden.
    """
    def __init__(self, detail: str = "Account is suspended or deleted"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )



class EmailAlreadyExists(HTTPException):
    """
    Raised when attempting to register with an email that already exists.
    HTTP 400 Bad Request.
    """
    def __init__(self, detail: str = "Email already registered"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class ProjectNotFound(HTTPException):
    """
    Raised when a requested project is not found.
    HTTP 404 Not Found.
    """
    def __init__(self, detail: str = "Project not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class ProjectAccessDenied(HTTPException):
    """
    Raised when user tries to access a project they don't own.
    HTTP 403 Forbidden.
    """
    def __init__(self, detail: str = "You do not have access to this project"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class ProjectInvalidStatus(HTTPException):
    """
    Raised when an operation is invalid for current project status.
    HTTP 400 Bad Request.
    """
    def __init__(self, detail: str = "Operation invalid for current project status"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )



class ScenePanelRuleViolation(HTTPException):
    """
    Raised when scene configuration violates fixed-panel rules.
    HTTP 400 Bad Request.
    """
    def __init__(self, detail: str = "Panel rule violation"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class LLMApiKeyMissing(HTTPException):
    """
    Raised when LLM API key is not configured.
    HTTP 500 Internal Server Error (Server Misconfiguration).
    """
    def __init__(self, detail: str = "LLM API Key is missing"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class LLMProviderError(HTTPException):
    """
    Raised when the upstream LLM provider fails (network, 5xx).
    HTTP 502 Bad Gateway.
    """
    def __init__(self, detail: str = "LLM Provider Error"):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
        )


class StoryParseFailed(HTTPException):
    """
    Raised when LLM output cannot be parsed into valid JSON schema after retries.
    HTTP 422 Unprocessable Entity.
    """
    def __init__(self, detail: str = "Failed to generate valid story structure"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class ContentBlocked(HTTPException):
    """
    Raised when input violates moderation policy.
    HTTP 400 Bad Request.
    """
    def __init__(self, detail: str = "Content blocked by moderation policy"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class TaskAlreadyRunning(HTTPException):
    """
    Raised when a project already has an active task.
    HTTP 409 Conflict.
    """
    def __init__(self, detail: str = "Task already running"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


# ============================================================================
# Image Generation Exceptions (Step-6)
# ============================================================================

class AzureImageApiKeyMissing(HTTPException):
    """
    Raised when Azure Image API key is not configured.
    HTTP 500 Internal Server Error (Server Misconfiguration).
    """
    def __init__(self, detail: str = "Azure Image API key is not configured"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class AzureImageProviderError(HTTPException):
    """
    Raised when the Azure Image API returns an error (network, 5xx, rate limit).
    HTTP 502 Bad Gateway.
    """
    def __init__(self, detail: str = "Azure Image generation service error"):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
        )


class ImageGenerationFailed(HTTPException):
    """
    Raised when image generation fails after retries.
    HTTP 500 Internal Server Error.
    """
    def __init__(self, detail: str = "Image generation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class PlanImageAccessDenied(HTTPException):
    """
    Raised when user's plan doesn't allow image generation.
    HTTP 403 Forbidden.
    """
    def __init__(self, detail: str = "Your plan does not allow image generation"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class FreeStoryAlreadyUsed(HTTPException):
    """
    Raised when FREE plan user has already used their one-time story.
    HTTP 403 Forbidden.
    """
    def __init__(self, detail: str = "Your free story has already been used"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class AzureBlobUploadFailed(HTTPException):
    """
    Raised when image upload to Azure Blob Storage fails.
    HTTP 500 Internal Server Error.
    """
    def __init__(self, detail: str = "Failed to upload image to storage"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class InvalidSceneStructure(HTTPException):
    """
    Raised when scene data doesn't match expected structure for generation.
    HTTP 400 Bad Request.
    """
    def __init__(self, detail: str = "Invalid scene structure for image generation"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
