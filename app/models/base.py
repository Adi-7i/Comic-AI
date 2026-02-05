"""
Base document class for all MongoDB collections.

Provides:
- UUID-based public_id for external references
- Soft delete support (is_deleted, deleted_at)
- Automatic timestamps (created_at, updated_at)
- Common query methods for non-deleted records
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING


class BaseDocument(Document):
    """
    Base class for all MongoDB documents.
    
    Provides common fields and functionality:
    - public_id: UUID-based external identifier (indexed, unique)
    - Soft delete: is_deleted flag and deleted_at timestamp
    - Timestamps: created_at and updated_at
    
    Note: All models inheriting from this class will have soft delete enabled.
    DO NOT expose MongoDB ObjectIds (_id) externally - always use public_id.
    """
    
    # UUID-based public identifier for external references
    # This prevents enumeration attacks and information disclosure
    public_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="UUID-based public identifier for external API responses"
    )
    
    # Soft delete support
    is_deleted: bool = Field(
        default=False,
        description="Soft delete flag - True if record is deleted"
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when record was soft deleted"
    )
    
    # Automatic timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when record was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when record was last updated"
    )
    
    class Settings:
        """Beanie document settings."""
        # This will be overridden in child classes
        name = "base_documents"
        
        # Define indexes at base level
        indexes = [
            IndexModel([("public_id", ASCENDING)], unique=True),
            IndexModel([("is_deleted", ASCENDING)]),
            IndexModel([("created_at", ASCENDING)]),
        ]
    
    async def soft_delete(self) -> None:
        """
        Soft delete this document.
        Sets is_deleted=True and deleted_at=now.
        """
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        await self.save()
    
    async def restore(self) -> None:
        """
        Restore a soft-deleted document.
        Sets is_deleted=False and deleted_at=None.
        """
        self.is_deleted = False
        self.deleted_at = None
        await self.save()
    
    def save_changes(self, *args, **kwargs):
        """Override save to update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save_changes(*args, **kwargs)
    
    @classmethod
    async def find_active(cls, *args, **kwargs):
        """
        Find documents that are not soft-deleted.
        Convenience method that adds is_deleted=False filter.
        """
        return await cls.find({"is_deleted": False}, *args, **kwargs).to_list()
    
    @classmethod
    def find_one_active(cls, *args, **kwargs):
        """
        Find one document that is not soft-deleted.
        Convenience method that adds is_deleted=False filter.
        """
        return cls.find_one({"is_deleted": False}, *args, **kwargs)
