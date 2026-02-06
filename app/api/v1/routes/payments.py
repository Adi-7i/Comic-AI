"""
Payment API Routes.

Thin routes that delegate to payment_service.

Endpoints:
- POST /create-order - Create Razorpay payment order
- GET /orders/{order_id} - Get order status

Security:
- All endpoints require authentication
- Order creation validates plan
- Status endpoint verifies ownership
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import User
from app.models.enums import UserPlan
from app.schemas.payment import (
    CreateOrderRequest,
    CreateOrderResponse,
    OrderStatusResponse
)
from app.api.v1.dependencies.auth import get_current_user
from app.services.payment_service import payment_service
from app.core.exceptions import (
    InvalidPlanRequested,
    PaymentOrderCreateFailed
)


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/create-order",
    response_model=CreateOrderResponse,
    summary="Create Razorpay payment order",
    description="Create a Razorpay order for plan purchase"
)
async def create_payment_order(
    request: CreateOrderRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a Razorpay payment order.
    
    - **plan**: Plan to purchase (PRO or CREATIVE)
    
    Returns:
        Order details including order_id and Razorpay key for frontend
        
    Security:
        - User must be authenticated
        - Amount is backend-enforced (not from frontend)
        - Order stored in DB for webhook verification
    """
    logger.info(
        f"Create order request: user={current_user.id}, plan={request.plan.value}"
    )
    
    try:
        # Delegate to service (thin route)
        order_data = await payment_service.create_order(
            user=current_user,
            plan=request.plan
        )
        
        return CreateOrderResponse(**order_data)
        
    except InvalidPlanRequested as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )
    except PaymentOrderCreateFailed as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.detail
        )


@router.get(
    "/orders/{order_id}",
    response_model=OrderStatusResponse,
    summary="Get payment order status",
    description="Check the status of a payment order"
)
async def get_order_status(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get payment order status.
    
    - **order_id**: Razorpay order ID
    
    Returns:
        Order status and details
        
    Security:
        - User must own the order (enforced by service)
    """
    logger.info(f"Get order status: order_id={order_id}, user={current_user.id}")
    
    # Delegate to service
    payment = await payment_service.get_order_status(
        user=current_user,
        order_id=order_id
    )
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment order not found"
        )
    
    return OrderStatusResponse(
        order_id=payment.razorpay_order_id,
        payment_id=payment.razorpay_payment_id,
        status=payment.status,
        plan=payment.plan_purchased,
        amount_display=payment.amount_display,
        created_at=payment.created_at,
        payment_captured_at=payment.payment_captured_at
    )
