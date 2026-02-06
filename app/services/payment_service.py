"""
Payment Service - Razorpay Order Creation & Verification.

Responsibilities:
- Create Razorpay orders
- Process webhook events
- Verify payment signatures
- Update payment records

Security:
- Never trust frontend callbacks
- All verification via webhooks
- Signature verification mandatory
- Idempotent processing
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from app.models.payment import Payment
from app.models.user import User
from app.models.enums import UserPlan, PaymentStatus
from app.core.razorpay_config import (
    get_razorpay_client,
    get_plan_price,
    razorpay_settings
)
from app.core.exceptions import (
    PaymentOrderCreateFailed,
    InvalidPlanRequested,
    PaymentAlreadyProcessed,
    PaymentFailed
)
from app.utils.signature import verify_razorpay_signature
from app.services.audit_service import audit_service

logger = logging.getLogger(__name__)


class PaymentService:
    """
    Razorpay payment orchestration service.
    
    Handles:
    - Order creation
    - Webhook processing
    - Payment verification
    """
    
    async def create_order(
        self,
        user: User,
        plan: UserPlan
    ) -> Dict[str, Any]:
        """
        Create a Razorpay payment order.
        
        Args:
            user: Authenticated user
            plan: Plan to purchase (PRO or CREATIVE)
            
        Returns:
            Dict with:
            - order_id: Razorpay order ID
            - amount: Amount in paise
            - currency: Currency code
            - razorpay_key: Public key for frontend
            - plan: Plan name
            
        Raises:
            InvalidPlanRequested: If plan not purchasable
            PaymentOrderCreateFailed: If Razorpay API fails
            
        Security:
            - User already authenticated (auth guard)
            - Amount comes from backend config (not frontend)
            - Order stored in DB for verification
        """
        logger.info(f"Creating payment order: user={user.id}, plan={plan.value}")
        
        # Validate plan is purchasable
        if plan not in [UserPlan.PRO, UserPlan.CREATIVE]:
            raise InvalidPlanRequested(
                detail=f"Plan {plan.value} is not available for purchase"
            )
        
        try:
            # Get plan price from config (backend-enforced)
            amount_paise = get_plan_price(plan)
            
            # Create Razorpay order
            razorpay_client = get_razorpay_client()
            
            # Generate unique receipt ID for tracking
            receipt_id = f"rcpt_{user.id}_{plan.value}_{int(datetime.now(timezone.utc).timestamp())}"
            
            razorpay_order = razorpay_client.order.create({
                "amount": amount_paise,
                "currency": razorpay_settings.RAZORPAY_CURRENCY,
                "receipt": receipt_id,
                "notes": {
                    "user_id": str(user.id),
                    "plan": plan.value,
                    "email": user.email
                }
            })
            
            logger.info(f"Razorpay order created: {razorpay_order['id']}")
            
            # Store payment record (status=CREATED)
            payment = Payment(
                user_id=user.id,
                razorpay_order_id=razorpay_order['id'],
                plan_purchased=plan,
                amount=amount_paise,
                currency=razorpay_settings.RAZORPAY_CURRENCY,
                status=PaymentStatus.CREATED,
                metadata={
                    "receipt_id": receipt_id,
                    "razorpay_order": razorpay_order  # Full order response
                }
            )
            await payment.save()
            
            # Audit log
            await audit_service.log_payment_created(
                user_id=user.id,
                order_id=razorpay_order['id'],
                plan=plan,
                amount=amount_paise
            )
            
            # Return data for frontend
            return {
                "order_id": razorpay_order['id'],
                "amount": amount_paise,
                "currency": razorpay_settings.RAZORPAY_CURRENCY,
                "razorpay_key": razorpay_settings.RAZORPAY_KEY_ID,
                "plan": plan.value
            }
            
        except Exception as e:
            logger.error(f"Failed to create Razorpay order: {e}")
            
            # Don't expose internal errors
            raise PaymentOrderCreateFailed(
                detail="Failed to create payment order. Please try again."
            )
    
    async def process_webhook_event(
        self,
        raw_payload: str,
        signature: str
    ) -> None:
        """
        Process Razorpay webhook event.
        
        Args:
            raw_payload: Raw request body (string)
            signature: X-Razorpay-Signature header
            
        Raises:
            PaymentSignatureInvalid: If signature verification fails
            PaymentAlreadyProcessed: If event already processed (idempotency)
            
        Security:
            - Signature verification MANDATORY
            - Event deduplication via event_id
            - Never trusts frontend callbacks
            
        Supported Events:
            - payment.captured → Mark success, upgrade plan
            - payment.failed → Mark failed, audit log
        """
        logger.info("Processing Razorpay webhook event")
        
        # Step 1: Verify signature (CRITICAL SECURITY)
        verify_razorpay_signature(
            payload=raw_payload,
            signature=signature,
            secret=razorpay_settings.RAZORPAY_WEBHOOK_SECRET
        )
        
        logger.info("Webhook signature verified ✓")
        
        # Step 2: Parse payload
        import json
        payload_dict = json.loads(raw_payload)
        
        event_type = payload_dict.get("event")
        event_id = payload_dict.get("payload", {}).get("payment", {}).get("entity", {}).get("id")
        
        if not event_id:
            logger.warning("Webhook missing event_id, skipping")
            return
        
        logger.info(f"Event: {event_type}, ID: {event_id}")
        
        # Step 3: Extract payment data
        payment_entity = payload_dict.get("payload", {}).get("payment", {}).get("entity", {})
        
        order_id = payment_entity.get("order_id")
        payment_id = payment_entity.get("id")
        status = payment_entity.get("status")
        
        if not order_id:
            logger.warning("Webhook missing order_id, skipping")
            return
        
        # Step 4: Load payment record
        payment = await Payment.find_one(Payment.razorpay_order_id == order_id)
        
        if not payment:
            logger.error(f"Payment not found for order {order_id}")
            return
        
        # Step 5: Idempotency check
        if payment.is_event_processed(event_id):
            logger.warning(f"Event {event_id} already processed")
            raise PaymentAlreadyProcessed(
                detail=f"Event {event_id} was already processed"
            )
        
        # Step 6: Process based on event type
        if event_type == "payment.captured":
            await self._handle_payment_captured(payment, payment_id, payload_dict, event_id)
        
        elif event_type == "payment.failed":
            await self._handle_payment_failed(payment, payload_dict, event_id)
        
        else:
            logger.info(f"Ignoring event type: {event_type}")
    
    async def _handle_payment_captured(
        self,
        payment: Payment,
        payment_id: str,
        webhook_payload: Dict,
        event_id: str
    ) -> None:
        """
        Handle payment.captured event.
        
        Actions:
        1. Update payment status to SUCCESS
        2. Store payment_id
        3. Store raw webhook
        4. Mark event as processed
        5. Trigger plan upgrade
        """
        logger.info(f"Payment captured: {payment_id}")
        
        # Update payment record
        payment.status = PaymentStatus.SUCCESS
        payment.razorpay_payment_id = payment_id
        payment.raw_webhook_payload = webhook_payload
        payment.webhook_verified_at = datetime.now(timezone.utc)
        payment.payment_captured_at = datetime.now(timezone.utc)
        payment.mark_event_processed(event_id)
        
        await payment.save()
        
        # Audit log
        await audit_service.log_payment_success(
            user_id=payment.user_id,
            order_id=payment.razorpay_order_id,
            payment_id=payment_id,
            plan=payment.plan_purchased,
            amount=payment.amount
        )
        
        # Trigger plan upgrade
        from app.services.plan_upgrade_service import plan_upgrade_service
        await plan_upgrade_service.upgrade_user_plan(
            user_id=payment.user_id,
            purchased_plan=payment.plan_purchased,
            payment=payment
        )
        
        logger.info(f"Payment processed successfully: {payment_id}")
    
    async def _handle_payment_failed(
        self,
        payment: Payment,
        webhook_payload: Dict,
        event_id: str
    ) -> None:
        """
        Handle payment.failed event.
        
        Actions:
        1. Update payment status to FAILED
        2. Store raw webhook
        3. Mark event as processed
        4. Audit log
        """
        logger.warning(f"Payment failed: {payment.razorpay_order_id}")
        
        # Update payment record
        payment.status = PaymentStatus.FAILED
        payment.raw_webhook_payload = webhook_payload
        payment.webhook_verified_at = datetime.now(timezone.utc)
        payment.mark_event_processed(event_id)
        
        await payment.save()
        
        # Audit log
        await audit_service.log_payment_failed(
            user_id=payment.user_id,
            order_id=payment.razorpay_order_id,
            plan=payment.plan_purchased,
            reason=webhook_payload.get("payload", {}).get("payment", {}).get("entity", {}).get("error_description", "Unknown")
        )
        
        logger.info(f"Payment failure logged: {payment.razorpay_order_id}")
    
    async def get_order_status(
        self,
        user: User,
        order_id: str
    ) -> Optional[Payment]:
        """
        Get payment status for an order.
        
        Args:
            user: Authenticated user
            order_id: Razorpay order ID
            
        Returns:
            Payment record if found and owned by user
            
        Security:
            - Ownership verification (user_id match)
        """
        payment = await Payment.find_one(
            Payment.razorpay_order_id == order_id,
            Payment.user_id == user.id
        )
        
        return payment


# Singleton instance
payment_service = PaymentService()
