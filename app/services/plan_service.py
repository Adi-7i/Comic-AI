"""
Plan enforcement service - Plan tier validation and quota management.

Provides plan-level access control and quota checking.
NO business logic - pure validation and rule enforcement.
"""

from typing import Dict, Any

from app.core.config import settings
from app.core.exceptions import PlanLimitExceeded, QuotaExceeded
from app.models.user import User
from app.models.enums import UserPlan


class PlanService:
    """
    Plan enforcement service class.
    
    Validates user plan tier and enforces plan-specific limits.
    All rules are configured in settings (app.core.config).
    """
    
    @staticmethod
    def check_plan_access(user: User, required_plan: UserPlan) -> None:
        """
        Verify user has the required plan tier or higher.
        
        Args:
            user: User object to check
            required_plan: Minimum required plan tier
            
        Raises:
            PlanLimitExceeded: If user's plan is insufficient
            
        Plan Hierarchy:
            FREE < PRO < CREATIVE
            
        Example:
            check_plan_access(user, UserPlan.PRO)
            # Allows PRO and CREATIVE users, blocks FREE users
        """
        # Define plan hierarchy (higher number = higher tier)
        plan_hierarchy = {
            UserPlan.FREE: 0,
            UserPlan.PRO: 1,
            UserPlan.CREATIVE: 2,
        }
        
        user_level = plan_hierarchy.get(user.plan, 0)
        required_level = plan_hierarchy.get(required_plan, 999)
        
        if user_level < required_level:
            raise PlanLimitExceeded(
                detail=f"This feature requires {required_plan.value} plan or higher. "
                f"Your current plan: {user.plan.value}"
            )
    
    @staticmethod
    def get_plan_limits(plan: UserPlan) -> Dict[str, Any]:
        """
        Get plan-specific limits and features.
        
        Args:
            plan: User plan tier
            
        Returns:
            Dictionary with plan limits
            
        Plan Limits:
            FREE:
                - max_pages: 0 (no generation allowed)
                - allow_generation: False
                - monthly_quota: 0
                - watermark_required: N/A
                
            PRO:
                - max_pages: 3
                - allow_generation: True
                - monthly_quota: 50
                - watermark_required: True
                
            CREATIVE:
                - max_pages: 10
                - allow_generation: True
                - monthly_quota: 200
                - watermark_required: False
        """
        if plan == UserPlan.FREE:
            return {
                "max_pages": settings.FREE_MAX_PAGES,
                "allow_generation": settings.FREE_ALLOW_GENERATION,
                "monthly_quota": settings.FREE_MONTHLY_QUOTA,
                "watermark_required": True,  # N/A for FREE (no generation)
            }
        elif plan == UserPlan.PRO:
            return {
                "max_pages": settings.PRO_MAX_PAGES,
                "allow_generation": True,
                "monthly_quota": settings.PRO_MONTHLY_QUOTA,
                "watermark_required": settings.PRO_WATERMARK_REQUIRED,
            }
        elif plan == UserPlan.CREATIVE:
            return {
                "max_pages": settings.CREATIVE_MAX_PAGES,
                "allow_generation": True,
                "monthly_quota": settings.CREATIVE_MONTHLY_QUOTA,
                "watermark_required": settings.CREATIVE_WATERMARK_REQUIRED,
            }
        else:
            # Default to most restrictive (FREE) for unknown plans
            return {
                "max_pages": 0,
                "allow_generation": False,
                "monthly_quota": 0,
                "watermark_required": True,
            }
    
    @staticmethod
    def check_generation_quota(user: User) -> None:
        """
        Verify user hasn't exceeded monthly generation quota.
        
        Args:
            user: User object to check
            
        Raises:
            QuotaExceeded: If user has exceeded their monthly quota
            
        Quota Logic:
            - Compares current_usage vs monthly_quota in generation_limits
            - FREE plan has 0 quota (always exceeds)
            - PRO plan has 50 generations/month
            - CREATIVE plan has 200 generations/month
        """
        limits = user.generation_limits
        current_usage = limits.get("current_usage", 0)
        monthly_quota = limits.get("monthly_quota", 0)
        
        if current_usage >= monthly_quota:
            raise QuotaExceeded(
                detail=f"Monthly generation quota exceeded. "
                f"Used: {current_usage}/{monthly_quota}. "
                f"Upgrade your plan for higher quota."
            )
    
    @staticmethod
    def check_page_limit(user: User, requested_pages: int) -> None:
        """
        Verify requested page count doesn't exceed plan limit.
        
        Args:
            user: User object to check
            requested_pages: Number of pages user wants to create
            
        Raises:
            PlanLimitExceeded: If requested pages exceed plan limit
            
        Page Limits:
            - FREE: 0 pages (no generation)
            - PRO: 3 pages max
            - CREATIVE: 10 pages max
        """
        plan_limits = PlanService.get_plan_limits(user.plan)
        max_pages = plan_limits["max_pages"]
        
        if requested_pages > max_pages:
            raise PlanLimitExceeded(
                detail=f"Your {user.plan.value} plan allows maximum {max_pages} pages. "
                f"Requested: {requested_pages}. "
                f"Upgrade your plan for more pages."
            )
    
    @staticmethod
    def can_generate(user: User) -> bool:
        """
        Check if user's plan allows generation at all.
        
        Args:
            user: User object to check
            
        Returns:
            True if generation is allowed, False otherwise
            
        Note:
            FREE plan does not allow any generation.
            Use this for quick checks before detailed validation.
        """
        plan_limits = PlanService.get_plan_limits(user.plan)
        return plan_limits["allow_generation"]
    
    @staticmethod
    def requires_watermark(user: User) -> bool:
        """
        Check if user's plan requires watermark on generated images.
        
        Args:
            user: User object to check
            
        Returns:
            True if watermark is required, False otherwise
            
        Watermark Rules:
            - FREE: N/A (no generation)
            - PRO: Watermark required
            - CREATIVE: No watermark
        """
        plan_limits = PlanService.get_plan_limits(user.plan)
        return plan_limits["watermark_required"]


# Singleton instance
plan_service = PlanService()
