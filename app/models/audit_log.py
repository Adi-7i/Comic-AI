"""
Audit Log collection model.

Immutable audit trail for security and billing events.
"""

from datetime import datetime
from typing import Optional, Dict

from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel, ASCENDING

from app.models.enums import AuditEventType


class AuditLog(Document):
    """
    Audit log model for security and billing events.
    
    CRITICAL DIFFERENCES FROM OTHER MODELS:
    - Does NOT inherit from BaseDocument (no soft delete)
    - Immutable - no update operations allowed
    - Never deleted - permanent audit trail
    - No public_id field (internal use only)
    
    Tracks security events (login, password changes) and billing events
    (plan upgrades, payments) for compliance and debugging.
    """
    
    # User reference
    user_id: PydanticObjectId = Field(
        description="Reference to User who triggered the event"
    )
    
    # Event details
    event_type: AuditEventType = Field(
        description="Type of event being logged"
    )
    
    # Immutable event data
    # Example for login: {
    #   "success": true,
    #   "login_method": "email",
    #   "ip_address": "192.168.1.1"
    # }
    # Example for payment: {
    #   "plan": "pro",
    #   "amount": 9.99,
    #   "gateway": "stripe"
    # }
    event_data: Dict = Field(
        description="Immutable event-specific data (varies by event_type)"
    )
    
    # Request metadata
    ip_address: Optional[str] = Field(
        default=None,
        description="IP address of request (for security events)"
    )
    user_agent: Optional[str] = Field(
        default=None,
        description="User agent string (for security events)"
    )
    
    # Severity/priority
    severity: str = Field(
        default="info",
        description="Event severity: info, warning, critical"
    )
    
    # Timestamp (not from BaseDocument)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when event occurred"
    )
    
    class Settings:
        name = "audit_logs"
        
        indexes = [
            # User's audit trail
            IndexModel([("user_id", ASCENDING)]),
            
            # Event type filtering (e.g., all login attempts)
            IndexModel([("event_type", ASCENDING), ("created_at", ASCENDING)]),
            
            # Time-based queries (recent events)
            IndexModel([("created_at", ASCENDING)]),
            
            # Severity filtering (critical events only)
            IndexModel([("severity", ASCENDING)]),
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "event_type": "user_login",
                "event_data": {
                    "success": True,
                    "login_method": "email",
                    "session_id": "sess_abc123"
                },
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0...",
                "severity": "info",
                "created_at": "2026-02-05T12:00:00"
            }
        }
    
    # Prevent updates to maintain immutability
    async def save(self, *args, **kwargs):
        """
        Override save to prevent updates.
        Only allow insert operations (when _id is None).
        """
        if self.id is not None:
            raise ValueError("AuditLog records are immutable and cannot be updated")
        return await super().save(*args, **kwargs)
    
    async def delete(self, *args, **kwargs):
        """
        Override delete to prevent deletion.
        Audit logs must never be deleted.
        """
        raise ValueError("AuditLog records cannot be deleted")
