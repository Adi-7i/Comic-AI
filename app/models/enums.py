"""
Enum definitions for the comic generation SaaS.

All enums used across different models are defined here for:
- Centralized management
- Type safety
- Consistent validation
"""

from enum import Enum


class UserPlan(str, Enum):
    """
    Subscription plan tiers.
    
    - FREE: Basic tier with limited generation quota
    - PRO: Mid-tier with higher quota and additional features
    - CREATIVE: Premium tier with maximum quota and all features
    """
    FREE = "free"
    PRO = "pro"
    CREATIVE = "creative"


class AccountStatus(str, Enum):
    """
    User account status.
    
    - ACTIVE: Account is active and can use the platform
    - SUSPENDED: Account temporarily suspended (payment issues, violations)
    - DELETED: Account marked for deletion (soft delete)
    """
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class ProjectStatus(str, Enum):
    """
    Project lifecycle status.
    
    - DRAFT: Project created but not submitted for generation
    - GENERATING: AI generation in progress
    - COMPLETED: Generation successfully completed
    - FAILED: Generation failed (errors, quota exceeded, etc.)
    """
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerationStatus(str, Enum):
    """
    Async generation task status.
    
    - QUEUED: Task queued for processing
    - PROCESSING: Task currently being processed by worker
    - COMPLETED: Task completed successfully
    - FAILED: Task failed (API errors, timeouts, validation errors)
    """
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PaymentStatus(str, Enum):
    """
    Payment transaction status.
    
    - CREATED: Razorpay order created, awaiting payment
    - PENDING: Payment initiated but not confirmed  
    - SUCCESS: Payment captured and verified (Razorpay)
    - COMPLETED: Payment successfully processed (legacy)
    - FAILED: Payment failed (declined, insufficient funds, etc.)
    - REFUNDED: Payment refunded to customer
    """
    CREATED = "created"      # Step-8: Razorpay order created
    PENDING = "pending"
    SUCCESS = "success"      # Step-8: Razorpay payment captured
    COMPLETED = "completed"  # Legacy/generic success
    FAILED = "failed"
    REFUNDED = "refunded"


class AuditEventType(str, Enum):
    """
    Audit log event types for security and billing tracking.
    
    Security events:
    - USER_LOGIN: User logged in
    - USER_LOGOUT: User logged out
    - PASSWORD_CHANGE: Password was changed
    - EMAIL_CHANGE: Email was changed
    - ACCOUNT_SUSPENDED: Account was suspended
    - ACCOUNT_DELETED: Account was deleted
    
    Billing events:
    - PLAN_UPGRADED: User upgraded to higher tier
    - PLAN_DOWNGRADED: User downgraded to lower tier
    - PAYMENT_COMPLETED: Payment successfully processed
    - PAYMENT_FAILED: Payment attempt failed
    - REFUND_ISSUED: Refund was issued
    
    Usage events:
    - GENERATION_STARTED: Generation task started
    - GENERATION_COMPLETED: Generation task completed
    - QUOTA_EXCEEDED: User exceeded their plan quota
    """
    # Security events
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PASSWORD_CHANGE = "password_change"
    EMAIL_CHANGE = "email_change"
    ACCOUNT_SUSPENDED = "account_suspended"
    ACCOUNT_DELETED = "account_deleted"
    
    # Billing events
    PLAN_UPGRADED = "plan_upgraded"
    PLAN_DOWNGRADED = "plan_downgraded"
    PAYMENT_COMPLETED = "payment_completed"
    PAYMENT_FAILED = "payment_failed"
    REFUND_ISSUED = "refund_issued"
    
    # Usage events
    GENERATION_STARTED = "generation_started"
    GENERATION_COMPLETED = "generation_completed"
    QUOTA_EXCEEDED = "quota_exceeded"
