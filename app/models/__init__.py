"""
Database models package.

Exports all Beanie document models and enums for easy importing.
"""

from app.models.base import BaseDocument
from app.models.enums import (
    UserPlan,
    AccountStatus,
    ProjectStatus,
    GenerationStatus,
    PaymentStatus,
    AuditEventType,
)
from app.models.user import User
from app.models.project import Project
from app.models.character import Character
from app.models.scene import Scene
from app.models.generation import Generation
from app.models.payment import Payment
from app.models.audit_log import AuditLog

__all__ = [
    # Base
    "BaseDocument",
    
    # Enums
    "UserPlan",
    "AccountStatus",
    "ProjectStatus",
    "GenerationStatus",
    "PaymentStatus",
    "AuditEventType",
    
    # Models
    "User",
    "Project",
    "Character",
    "Scene",
    "Generation",
    "Payment",
    "AuditLog",
]
