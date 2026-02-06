"""
Plan Upgrade Service - User Plan Management.

Responsibilities:
- Upgrade user plans after successful payment
- Enforce upgrade rules
- Audit plan changes
- Handle edge cases

Security:
- Only called after webhook verification
- Never called from frontend
- Full audit trail
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from beanie import PydanticObjectId

from app.models.user import User
from app.models.payment import Payment
from app.models.enums import UserPlan, PaymentStatus
from app.core.exceptions import PlanUpgradeFailed
from app.services.audit_service import audit_service

logger = logging.getLogger(__name__)


class PlanUpgradeService:
    """
    Handles user plan upgrades after successful payments.
    
    Rules:
    - FREE → PRO: Allowed
    - FREE → CREATIVE: Allowed
    - PRO → CREATIVE: Allowed
    - Downgrades: Not supported (manual CS intervention)
    """
    
    async def upgrade_user_plan(
        self,
        user_id: PydanticObjectId,
        purchased_plan: UserPlan,
        payment: Payment
    ) -> User:
        """
        Upgrade user's plan after successful payment.
        
        Args:
            user_id: User to upgrade
            purchased_plan: New plan (PRO or CREATIVE)
            payment: Associated payment record
            
        Returns:
            Updated User object
            
        Raises:
            PlanUpgradeFailed: If upgrade fails
            
        Security:
            - Only called after webhook verification
            - Validates payment is SUCCESS
            - Idempotent (safe to call multiple times)
            
        Side Effects:
            - Updates user.plan
            - Sets user.plan_upgraded_at
            - Emits audit log
        """
        logger.info(f"Upgrading plan: user={user_id}, plan={purchased_plan.value}")
        
        try:
            # Load user
            user = await User.get(user_id)
            if not user:
                raise PlanUpgradeFailed(
                    detail=f"User {user_id} not found"
                )
            
            # Validate payment is successful
            if payment.status not in [PaymentStatus.SUCCESS, PaymentStatus.COMPLETED]:
                raise PlanUpgradeFailed(
                    detail="Cannot upgrade plan: payment not successful"
                )
            
            # Check if already upgraded (idempotency)
            if user.plan == purchased_plan:
                logger.info(f"User {user_id} already on plan {purchased_plan.value}, skipping")
                return user
            
            # Validate upgrade path
            current_plan = user.plan
            if not self._is_valid_upgrade(current_plan, purchased_plan):
                logger.warning(
                    f"Invalid upgrade: {current_plan.value} → {purchased_plan.value}"
                )
                # Don't fail - just log warning (payment already successful)
                # CS can handle edge cases
            
            # Store old plan for audit
            old_plan = user.plan
            
            # Upgrade plan
            user.plan = purchased_plan
            user.plan_upgraded_at = datetime.now(timezone.utc)
            
            await user.save()
            
            logger.info(
                f"Plan upgraded: user={user_id}, "
                f"{old_plan.value} → {purchased_plan.value}"
            )
            
            # Audit log
            await audit_service.log_plan_upgrade(
                user_id=user_id,
                old_plan=old_plan,
                new_plan=purchased_plan,
                payment_id=str(payment.id),
                order_id=payment.razorpay_order_id
            )
            
            return user
            
        except Exception as e:
            logger.error(f"Plan upgrade failed: {e}")
            
            # Re-raise known exceptions
            if isinstance(e, PlanUpgradeFailed):
                raise
            
            # Wrap unknown errors
            raise PlanUpgradeFailed(
                detail=f"Failed to upgrade plan: {str(e)}"
            )
    
    def _is_valid_upgrade(
        self,
        current_plan: UserPlan,
        new_plan: UserPlan
    ) -> bool:
        """
        Check if upgrade path is valid.
        
        Valid upgrades:
        - FREE → PRO ✓
        - FREE → CREATIVE ✓
        - PRO → CREATIVE ✓
        
        Invalid:
        - CREATIVE → PRO ✗ (downgrade)
        - PRO → FREE ✗ (downgrade)
        - CREATIVE → FREE ✗ (downgrade)
        
        Args:
            current_plan: Current user plan
            new_plan: Requested new plan
            
        Returns:
            True if valid upgrade path
        """
        # Define plan hierarchy (higher = better)
        plan_hierarchy = {
            UserPlan.FREE: 0,
            UserPlan.PRO: 1,
            UserPlan.CREATIVE: 2
        }
        
        current_level = plan_hierarchy.get(current_plan, 0)
        new_level = plan_hierarchy.get(new_plan, 0)
        
        # Upgrade = moving to higher tier
        return new_level > current_level
    
    async def get_user_plan_info(
        self,
        user_id: PydanticObjectId
    ) -> dict:
        """
        Get user's current plan information.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with plan details
        """
        user = await User.get(user_id)
        if not user:
            return {}
        
        return {
            "current_plan": user.plan.value,
            "upgraded_at": user.plan_upgraded_at,
            "can_upgrade_to": self._get_available_upgrades(user.plan)
        }
    
    def _get_available_upgrades(
        self,
        current_plan: UserPlan
    ) -> list[str]:
        """
        Get list of plans user can upgrade to.
        
        Args:
            current_plan: User's current plan
            
        Returns:
            List of plan names (e.g., ["PRO", "CREATIVE"])
        """
        if current_plan == UserPlan.FREE:
            return ["PRO", "CREATIVE"]
        elif current_plan == UserPlan.PRO:
            return ["CREATIVE"]
        else:
            return []  # Already on highest tier


# Singleton instance
plan_upgrade_service = PlanUpgradeService()
