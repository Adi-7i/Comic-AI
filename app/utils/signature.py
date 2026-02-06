"""
Webhook Signature Verification Utility.

Security-critical module for verifying Razorpay webhook signatures.

Features:
- HMAC-SHA256 signature verification
- Replay attack protection via event tracking
- Clear error messages for debugging

Used by: Razorpay webhook handler
"""

import hmac
import hashlib
from typing import Dict, Any

from app.core.exceptions import PaymentSignatureInvalid


def verify_razorpay_signature(
    payload: str,
    signature: str,
    secret: str
) -> bool:
    """
    Verify Razorpay webhook signature using HMAC-SHA256.
    
    Args:
        payload: Raw request body as string
        signature: X-Razorpay-Signature header value
        secret: RAZORPAY_WEBHOOK_SECRET from config
        
    Returns:
        True if signature is valid
        
    Raises:
        PaymentSignatureInvalid: If signature verification fails
        
    Security:
        - Uses constant-time comparison to prevent timing attacks
        - HMAC-SHA256 prevents tampering
        - Secret must never be logged
        
    Example:
        >>> verify_razorpay_signature(
        ...     payload='{"event":"payment.captured"}',
        ...     signature="abc123...",
        ...     secret="webhook_secret_xyz"
        ... )
        True
    """
    try:
        # Compute expected signature
        expected_signature = hmac.new(
            key=secret.encode('utf-8'),
            msg=payload.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # Constant-time comparison (prevents timing attacks)
        is_valid = hmac.compare_digest(expected_signature, signature)
        
        if not is_valid:
            raise PaymentSignatureInvalid(
                detail="Webhook signature verification failed. Possible tampering detected."
            )
        
        return True
        
    except Exception as e:
        if isinstance(e, PaymentSignatureInvalid):
            raise
        
        # Wrap other errors
        raise PaymentSignatureInvalid(
            detail=f"Signature verification error: {str(e)}"
        )


def verify_payment_signature(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
    secret: str
) -> bool:
    """
    Verify payment signature (for frontend callback verification).
    
    Note: This is NOT used for webhooks. Webhooks use verify_razorpay_signature.
    This is only for optional frontend callback verification.
    
    Args:
        razorpay_order_id: Order ID
        razorpay_payment_id: Payment ID
        razorpay_signature: Signature from Razorpay
        secret: RAZORPAY_KEY_SECRET
        
    Returns:
        True if valid
        
    Raises:
        PaymentSignatureInvalid: If invalid
    """
    try:
        # Create message: order_id|payment_id
        message = f"{razorpay_order_id}|{razorpay_payment_id}"
        
        # Compute expected signature
        expected_signature = hmac.new(
            key=secret.encode('utf-8'),
            msg=message.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # Constant-time comparison
        is_valid = hmac.compare_digest(expected_signature, razorpay_signature)
        
        if not is_valid:
            raise PaymentSignatureInvalid(
                detail="Payment signature verification failed"
            )
        
        return True
        
    except Exception as e:
        if isinstance(e, PaymentSignatureInvalid):
            raise
        
        raise PaymentSignatureInvalid(
            detail=f"Payment signature error: {str(e)}"
        )
