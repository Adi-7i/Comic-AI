"""
Payment Request/Response Schemas.

Defines API contracts for:
- Order creation
- Payment status
- Webhook payloads
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.enums import UserPlan, PaymentStatus


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class CreateOrderRequest(BaseModel):
    """
    Request to create a Razorpay payment order.
    
    Used by: POST /api/v1/payments/create-order
    """
    plan: UserPlan = Field(
        ...,
        description="Plan to purchase (PRO or CREATIVE)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "plan": "PRO"
            }
        }


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class CreateOrderResponse(BaseModel):
    """
    Response after creating Razorpay order.
    
    Frontend uses this data to initialize Razorpay checkout.
    """
    order_id: str = Field(
        ...,
        description="Razorpay order ID (pass to frontend)"
    )
    amount: int = Field(
        ...,
        description="Amount in paise (smallest currency unit)"
    )
    currency: str = Field(
        ...,
        description="Currency code (e.g., INR)"
    )
    razorpay_key: str = Field(
        ...,
        description="Razorpay public key ID (for frontend SDK)"
    )
    plan: str = Field(
        ...,
        description="Plan being purchased"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "order_L0Q7xKz3xxxxxxxxxxx",
                "amount": 9900,
                "currency": "INR",
                "razorpay_key": "rzp_test_xxxxxxxxxx",
                "plan": "PRO"
            }
        }


class OrderStatusResponse(BaseModel):
    """
    Payment order status response.
    
    Used by: GET /api/v1/payments/orders/{order_id}
    """
    order_id: str = Field(..., description="Razorpay order ID")
    payment_id: Optional[str] = Field(None, description="Payment ID (if captured)")
    status: PaymentStatus = Field(..., description="Current payment status")
    plan: UserPlan = Field(..., description="Plan purchased")
    amount_display: str = Field(..., description="Human-readable amount (e.g., '₹99.00')")
    created_at: datetime = Field(..., description="Order creation time")
    payment_captured_at: Optional[datetime] = Field(None, description="Payment capture time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "order_L0Q7xKz3xxxxxxxxxxx",
                "payment_id": "pay_L0Q8xxxxxxxxxxxxxxx",
                "status": "SUCCESS",
                "plan": "PRO",
                "amount_display": "₹99.00",
                "created_at": "2026-02-06T15:30:00Z",
                "payment_captured_at": "2026-02-06T15:31:25Z"
            }
        }


# ============================================================================
# WEBHOOK SCHEMAS
# ============================================================================

class RazorpayWebhookPayload(BaseModel):
    """
    Razorpay webhook event structure.
    
    Simplified schema - actual payload has more fields.
    We store the raw payload in Payment.raw_webhook_payload for audit.
    """
    event: str = Field(
        ...,
        description="Event type (e.g., 'payment.captured', 'payment.failed')"
    )
    account_id: str = Field(
        ...,
        description="Razorpay account ID"
    )
    contains: list = Field(
        default_factory=list,
        description="Entities included (e.g., ['payment', 'order'])"
    )
    created_at: int = Field(
        ...,
        description="Timestamp (Unix epoch)"
    )
    
    # Nested entity data
    payload: dict = Field(
        ...,
        description="Event payload with payment/order details"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "event": "payment.captured",
                "account_id": "acc_xxxxxxxxxx",
                "contains": ["payment"],
                "created_at": 1675320000,
                "payload": {
                    "payment": {
                        "entity": {
                            "id": "pay_xxxxxxxx",
                            "amount": 9900,
                            "currency": "INR",
                            "status": "captured",
                            "order_id": "order_xxxxxxxx"
                        }
                    }
                }
            }
        }
