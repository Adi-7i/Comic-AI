"""
Audit Service - Payment Event Logging.

Provides audit logging for payment-related events.
This is a simple implementation. Can be extended with:
- Separate audit logs table
- External audit logging service
- Compliance tracking
"""

import logging
from typing import Optional
from datetime import datetime, timezone

from beanie import PydanticObjectId

from app.models.enums import UserPlan
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """
    Simple audit logging service for payments.
    
    Logs to:
    1. Application logs (via logger)
    2. AuditLog collection (database)
    """
    
    async def log_payment_created(
        self,
        user_id: PydanticObjectId,
        order_id: str,
        plan: UserPlan,
        amount: int
    ) -> None:
        """Log payment order creation."""
        logger.info(
            f"AUDIT: Payment created - "
            f"user={user_id}, order={order_id}, plan={plan.value}, amount={amount}"
        )
        
        await self._write_audit_log(
            user_id=user_id,
            action="payment_created",
            details={
                "order_id": order_id,
                "plan": plan.value,
                "amount": amount
            }
        )
    
    async def log_payment_success(
        self,
        user_id: PydanticObjectId,
        order_id: str,
        payment_id: str,
        plan: UserPlan,
        amount: int
    ) -> None:
        """Log successful payment."""
        logger.info(
            f"AUDIT: Payment success - "
            f"user={user_id}, order={order_id}, payment={payment_id}, "
            f"plan={plan.value}, amount={amount}"
        )
        
        await self._write_audit_log(
            user_id=user_id,
            action="payment_success",
            details={
                "order_id": order_id,
                "payment_id": payment_id,
                "plan": plan.value,
                "amount": amount
            }
        )
    
    async def log_payment_failed(
        self,
        user_id: PydanticObjectId,
        order_id: str,
        plan: UserPlan,
        reason: str
    ) -> None:
        """Log failed payment."""
        logger.warning(
            f"AUDIT: Payment failed - "
            f"user={user_id}, order={order_id}, plan={plan.value}, reason={reason}"
        )
        
        await self._write_audit_log(
            user_id=user_id,
            action="payment_failed",
            details={
                "order_id": order_id,
                "plan": plan.value,
                "reason": reason
            }
        )
    
    async def log_plan_upgrade(
        self,
        user_id: PydanticObjectId,
        old_plan: UserPlan,
        new_plan: UserPlan,
        payment_id: str,
        order_id: str
    ) -> None:
        """Log plan upgrade."""
        logger.info(
            f"AUDIT: Plan upgraded - "
            f"user={user_id}, {old_plan.value} → {new_plan.value}, "
            f"payment={payment_id}"
        )
        
        await self._write_audit_log(
            user_id=user_id,
            action="plan_upgraded",
            details={
                "old_plan": old_plan.value,
                "new_plan": new_plan.value,
                "payment_id": payment_id,
                "order_id": order_id
            }
        )
    
    async def _write_audit_log(
        self,
        user_id: PydanticObjectId,
        action: str,
        details: dict
    ) -> None:
        """
        Write to AuditLog collection.
        
        Args:
            user_id: User performing action
            action: Action name
            details: Additional data
        """
        try:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                details=details,
                timestamp=datetime.now(timezone.utc)
            )
            await audit_log.save()
        except Exception as e:
            # Don't fail the main operation if audit logging fails
            logger.error(f"Failed to write audit log: {e}")


# Singleton instance
audit_service = AuditService()
