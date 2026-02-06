"""
Razorpay Webhook Handler.

CRITICAL SECURITY ENDPOINT

This endpoint:
1. Receives webhook events from Razorpay
2. Verifies signature (MANDATORY)
3. Processes payment events
4. Triggers plan upgrades

Security:
- NO authentication (Razorpay doesn't auth)
- Signature verification is the auth
- Idempotent processing
- No trust in frontend callbacks

Events Handled:
- payment.captured → Success, upgrade plan
- payment.failed → Mark failed, audit log
"""

import logging
from fastapi import APIRouter, Request, HTTPException, status

from app.services.payment_service import payment_service
from app.core.exceptions import (
    PaymentSignatureInvalid,
    PaymentAlreadyProcessed
)


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/webhook",
    summary="Razorpay webhook handler",
    description="Receive and process Razorpay webhook events",
    include_in_schema=False  # Hide from public API docs
)
async def razorpay_webhook(request: Request):
    """
    Razorpay webhook endpoint.
    
    **CRITICAL SECURITY**: This endpoint has NO authentication.
    Security is enforced via HMAC signature verification.
    
    Flow:
    1. Read raw body + signature header
    2. Verify signature (MANDATORY)
    3. Process event (idempotent)
    4. Return 200 OK
    
    If signature invalid: 403 Forbidden
    If event already processed: 409 Conflict (but still 200 to Razorpay)
    
    Razorpay retries failed webhooks, so we return 200 even for duplicates.
    """
    logger.info("Received Razorpay webhook")
    
    try:
        # Step 1: Read raw body (needed for signature verification)
        raw_body = await request.body()
        raw_payload = raw_body.decode('utf-8')
        
        # Step 2: Get signature from header
        signature = request.headers.get("X-Razorpay-Signature")
        
        if not signature:
            logger.error("Missing X-Razorpay-Signature header")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Missing signature header"
            )
        
        logger.debug(f"Signature: {signature[:20]}...")
        
        # Step 3: Process webhook (service handles signature verification)
        await payment_service.process_webhook_event(
            raw_payload=raw_payload,
            signature=signature
        )
        
        logger.info("Webhook processed successfully ✓")
        
        # Return 200 OK to Razorpay
        return {
            "status": "ok",
            "message": "Webhook processed"
        }
        
    except PaymentSignatureInvalid as e:
        # Signature verification failed - CRITICAL
        logger.error(f"Webhook signature invalid: {e.detail}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid signature"
        )
    
    except PaymentAlreadyProcessed as e:
        # Duplicate event - log but return 200 (idempotency)
        logger.warning(f"Duplicate webhook: {e.detail}")
        
        # Return 200 to prevent Razorpay retries
        return {
            "status": "ok",
            "message": "Event already processed"
        }
    
    except Exception as e:
        # Unexpected error - log and return 500
        logger.error(f"Webhook processing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )
