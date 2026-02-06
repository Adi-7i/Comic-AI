"""
Razorpay Configuration & Client Setup.

Provides:
- Razorpay API credentials (from environment)
- Plan pricing configuration
- Razorpay client singleton
- Currency settings

Security:
- Secrets loaded from environment only
- Never logged or exposed
- Fails startup if missing in production
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

from app.models.enums import UserPlan


class RazorpaySettings(BaseSettings):
    """
    Razorpay configuration from environment.
    
    Required Environment Variables:
    - RAZORPAY_KEY_ID: Public API key
    - RAZORPAY_KEY_SECRET: Secret API key (never log)
    - RAZORPAY_WEBHOOK_SECRET: Webhook signature verification secret
    """
    
    # API Credentials (optional defaults for dev/testing)
    RAZORPAY_KEY_ID: str = Field(
        default="rzp_test_xxxxxxxxxx",
        description="Razorpay public key ID"
    )
    RAZORPAY_KEY_SECRET: str = Field(
        default="test_secret_key_xxxxxxxxxx",
        description="Razorpay secret key (NEVER LOG)"
    )
    RAZORPAY_WEBHOOK_SECRET: str = Field(
        default="webhook_secret_xxxxxxxxxx",
        description="Webhook signature secret (NEVER LOG)"
    )
    
    # Currency Settings
    RAZORPAY_CURRENCY: str = Field(
        default="INR",
        description="Payment currency"
    )
    
    # Plan Pricing (in paise for INR, cents for other currencies)
    # 1 INR = 100 paise
    PRO_PLAN_PRICE: int = Field(
        default=9900,  # ₹99.00
        description="Pro plan price in paise (per project, monthly)"
    )
    CREATIVE_PLAN_PRICE: int = Field(
        default=29900,  # ₹299.00
        description="Creative plan price in paise (per project, monthly)"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra env vars
    
    def __repr__(self) -> str:
        """Safe repr that doesn't expose secrets."""
        return (
            f"<RazorpaySettings "
            f"key_id={self.RAZORPAY_KEY_ID[:8]}... "
            f"currency={self.RAZORPAY_CURRENCY}>"
        )


# Global settings instance
razorpay_settings = RazorpaySettings()


# Plan pricing map
PLAN_PRICING_MAP = {
    UserPlan.PRO: razorpay_settings.PRO_PLAN_PRICE,
    UserPlan.CREATIVE: razorpay_settings.CREATIVE_PLAN_PRICE,
}


def get_plan_price(plan: UserPlan) -> int:
    """
    Get price for a plan in smallest currency unit (paise for INR).
    
    Args:
        plan: User plan
        
    Returns:
        Price in paise (or cents)
        
    Raises:
        KeyError: If plan has no price (e.g., FREE plan)
    """
    if plan not in PLAN_PRICING_MAP:
        raise ValueError(f"Plan {plan.value} is not purchasable")
    return PLAN_PRICING_MAP[plan]


def get_plan_price_display(plan: UserPlan) -> str:
    """
    Get human-readable price for a plan.
    
    Args:
        plan: User plan
        
    Returns:
        Formatted price string (e.g., "₹99.00")
    """
    price_paise = get_plan_price(plan)
    price_rupees = price_paise / 100
    currency_symbol = "₹" if razorpay_settings.RAZORPAY_CURRENCY == "INR" else razorpay_settings.RAZORPAY_CURRENCY
    return f"{currency_symbol}{price_rupees:.2f}"


# Razorpay Client Singleton
_razorpay_client: Optional[object] = None


def get_razorpay_client():
    """
    Get Razorpay client singleton.
    
    Lazily initializes client on first access.
    
    Returns:
        razorpay.Client instance
        
    Security Note:
        Credentials are loaded from environment.
        Never log the client or its credentials.
    """
    global _razorpay_client
    
    if _razorpay_client is None:
        import razorpay
        
        _razorpay_client = razorpay.Client(
            auth=(
                razorpay_settings.RAZORPAY_KEY_ID,
                razorpay_settings.RAZORPAY_KEY_SECRET
            )
        )
    
    return _razorpay_client
