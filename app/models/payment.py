"""
Payment collection model.

Tracks payment transactions for plan purchases with Razorpay integration.
"""

from datetime import datetime
from typing import Optional, Dict, List
from decimal import Decimal

from beanie import PydanticObjectId
from pydantic import Field
from pymongo import IndexModel, ASCENDING

from app.models.base import BaseDocument
from app.models.enums import PaymentStatus, UserPlan


class Payment(BaseDocument):
    """
    Payment transaction model for Razorpay integration.
    
    Tracks:
    - Order creation
    - Payment capture
    - Webhook events
    - Plan upgrades
    
    Security:
    - Idempotent processing via processed_events
    - Raw webhook payload for audit trail
    - Unique Razorpay order IDs
    """
    
    # User reference
    user_id: PydanticObjectId = Field(
        ...,
        description="Reference to User who made the payment"
    )
    
    # Razorpay identifiers
    razorpay_order_id: str = Field(
        ...,
        description="Unique Razorpay order ID"
    )
    razorpay_payment_id: Optional[str] = Field(
        default=None,
        description="Razorpay payment ID (set after payment capture)"
    )
    
    # Plan purchased
    plan_purchased: UserPlan = Field(
        ...,
        description="Plan tier purchased (PRO/CREATIVE)"
    )
    
    # Amount and currency (stored in smallest unit: paise for INR)
    amount: int = Field(
        ...,
        description="Payment amount in smallest currency unit (paise for INR)"
    )
    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=3,
        description="Currency code (ISO 4217, e.g., INR, USD)"
    )
    
    # Payment status
    status: PaymentStatus = Field(
        default=PaymentStatus.CREATED,
        description="Payment transaction status"
    )
    
    # Webhook processing (idempotency & audit)
    raw_webhook_payload: Optional[Dict] = Field(
        default=None,
        description="Raw webhook JSON for audit trail"
    )
    processed_events: List[str] = Field(
        default_factory=list,
        description="List of processed webhook event IDs (prevents duplicates)"
    )
    webhook_verified_at: Optional[datetime] = Field(
        default=None,
        description="When webhook signature was verified"
    )
    payment_captured_at: Optional[datetime] = Field(
        default=None,
        description="When payment was captured (success)"
    )
    
    # Additional metadata for debugging/tracking
    metadata: Dict = Field(
        default_factory=dict,
        description="Additional data (receipt, notes, etc.)"
    )
    
    class Settings:
        name = "payments"
        
        indexes = [
            # Razorpay order lookup (unique)
            IndexModel([("razorpay_order_id", ASCENDING)], unique=True),
            
            # User's payment history
            IndexModel([("user_id", ASCENDING), ("created_at", ASCENDING)]),
            
            # Payment ID lookup (after capture)
            IndexModel([("razorpay_payment_id", ASCENDING)]),
            
            # Status filtering
            IndexModel([("status", ASCENDING)]),
        ]
    
    def __repr__(self) -> str:
        return (
            f"<Payment user={self.user_id} "
            f"order={self.razorpay_order_id} "
            f"plan={self.plan_purchased.value} "
            f"status={self.status.value}>"
        )
    
    @property
    def amount_display(self) -> str:
        """Get human-readable amount (e.g., '₹99.00')."""
        amount_major = self.amount / 100  # paise to rupees
        symbol = "₹" if self.currency == "INR" else self.currency
        return f"{symbol}{amount_major:.2f}"
    
    def is_event_processed(self, event_id: str) -> bool:
        """Check if webhook event already processed (idempotency)."""
        return event_id in self.processed_events
    
    def mark_event_processed(self, event_id: str) -> None:
        """Mark webhook event as processed."""
        if event_id not in self.processed_events:
            self.processed_events.append(event_id)
