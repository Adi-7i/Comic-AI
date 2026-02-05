"""
Payment collection model.

Tracks payment transactions for plan purchases with gateway integration.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict

from beanie import PydanticObjectId
from pydantic import Field, condecimal
from pymongo import IndexModel, ASCENDING

from app.models.base import BaseDocument
from app.models.enums import PaymentStatus, UserPlan


class Payment(BaseDocument):
    """
    Payment transaction model.
    
    Tracks payments for plan purchases/upgrades.
    Stores gateway references for webhook verification and reconciliation.
    """
    
    # User reference
    user_id: PydanticObjectId = Field(
        description="Reference to User who made the payment"
    )
    
    # Plan purchased
    plan_purchased: UserPlan = Field(
        description="Plan tier purchased (pro/creative)"
    )
    
    # Amount and currency
    amount: condecimal(max_digits=10, decimal_places=2) = Field(  # type: ignore
        description="Payment amount (e.g., 9.99)"
    )
    currency: str = Field(
        default="USD",
        min_length=3,
        max_length=3,
        description="Currency code (ISO 4217, e.g., USD, EUR)"
    )
    
    # Payment status
    status: PaymentStatus = Field(
        default=PaymentStatus.PENDING,
        description="Payment transaction status"
    )
    
    # Gateway integration
    gateway: str = Field(
        description="Payment gateway name (stripe, paypal, etc.)"
    )
    gateway_transaction_id: str = Field(
        description="Unique transaction ID from payment gateway"
    )
    gateway_customer_id: Optional[str] = Field(
        default=None,
        description="Customer ID in payment gateway (for recurring payments)"
    )
    
    # Webhook verification
    webhook_verified_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when webhook was verified (security measure)"
    )
    
    # Additional metadata
    # Example: {
    #   "receipt_url": "https://stripe.com/receipts/...",
    #   "invoice_id": "inv_123",
    #   "webhook_payload": {...}
    # }
    metadata: Dict = Field(
        default_factory=dict,
        description="Additional payment metadata (receipts, invoices, webhook data)"
    )
    
    class Settings:
        name = "payments"
        
        indexes = [
            # User's payment history
            IndexModel([("user_id", ASCENDING)]),
            
            # User's payments ordered by date (billing history)
            IndexModel([("user_id", ASCENDING), ("created_at", ASCENDING)]),
            
            # Gateway transaction ID - must be unique for idempotency
            IndexModel([("gateway_transaction_id", ASCENDING)], unique=True),
            
            # Inherit base indexes (public_id, is_deleted, created_at)
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "plan_purchased": "pro",
                "amount": "9.99",
                "currency": "USD",
                "status": "completed",
                "gateway": "stripe",
                "gateway_transaction_id": "ch_3AbcDef123456",
                "gateway_customer_id": "cus_Xyz789",
                "webhook_verified_at": "2026-02-05T12:05:00",
                "metadata": {
                    "receipt_url": "https://stripe.com/receipts/abc123",
                    "invoice_id": "in_xyz789"
                }
            }
        }
