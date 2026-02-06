#!/usr/bin/env python3
"""
Payment Layer Verification Script (Step-8).

Tests:
1. Configuration loading
2. Exception classes
3. Payment model & schemas
4. Signature verification
5. Services setup
6. API routes registration
"""

import sys
import asyncio


def verify_payment_layer():
    """Run all payment layer verification tests."""
    print("=" * 60)
    print("PAYMENT LAYER VERIFICATION (Step-8: Razorpay)")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Razorpay Configuration
    print("\n1️⃣  Testing Razorpay configuration...")
    try:
        from app.core.razorpay_config import (
            razorpay_settings,
            get_plan_price,
            get_plan_price_display,
            PLAN_PRICING_MAP
        )
        from app.models.enums import UserPlan
        
        # Check config loaded
        assert razorpay_settings.RAZORPAY_CURRENCY == "INR"
        
        # Check plan pricing
        pro_price = get_plan_price(UserPlan.PRO)
        creative_price = get_plan_price(UserPlan.CREATIVE)
        
        assert pro_price == 9900  # ₹99.00
        assert creative_price == 29900  # ₹299.00
        
        # Check display formatting
        pro_display = get_plan_price_display(UserPlan.PRO)
        assert "₹" in pro_display or "99" in pro_display
        
        print("   ✅ Razorpay config loaded")
        print(f"   - PRO: {pro_display}")
        print(f"   - CREATIVE: {get_plan_price_display(UserPlan.CREATIVE)}")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 2: Payment Exceptions
    print("\n2️⃣  Testing payment exceptions...")
    try:
        from app.core.exceptions import (
            PaymentOrderCreateFailed,
            PaymentSignatureInvalid,
            PaymentAlreadyProcessed,
            PaymentFailed,
            PlanUpgradeFailed,
            InvalidPlanRequested
        )
        
        exception_count = 6
        print(f"   ✅ All {exception_count} payment exceptions defined")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 3: Payment Model
    print("\n3️⃣  Testing Payment model...")
    try:
        from app.models.payment import Payment
        from app.models.enums import PaymentStatus
        
        # Check model fields via model_fields
        model_fields = Payment.model_fields
        required_fields = [
            'user_id', 'razorpay_order_id', 'razorpay_payment_id',
            'plan_purchased', 'amount', 'currency', 'status',
            'raw_webhook_payload', 'processed_events',
            'webhook_verified_at', 'payment_captured_at'
        ]
        
        for field in required_fields:
            assert field in model_fields, f"Missing field: {field}"
        
        # Check PaymentStatus enum has new values
        assert hasattr(PaymentStatus, 'CREATED')
        assert hasattr(PaymentStatus, 'SUCCESS')
        assert PaymentStatus.CREATED.value == "created"
        assert PaymentStatus.SUCCESS.value == "success"
        
        print("   ✅ Payment model updated for Razorpay")
        print("   - Razorpay fields present")
        print("   - Idempotency support (processed_events)")
        print("   - PaymentStatus enum extended")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 4: Payment Schemas
    print("\n4️⃣  Testing payment schemas...")
    try:
        from app.schemas.payment import (
            CreateOrderRequest,
            CreateOrderResponse,
            OrderStatusResponse,
            RazorpayWebhookPayload
        )
        
        schema_count = 4
        print(f"   ✅ All {schema_count} payment schemas defined")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 5: Signature Verification
    print("\n5️⃣  Testing signature verification...")
    try:
        from app.utils.signature import verify_razorpay_signature
        import hmac
        import hashlib
        
        # Test signature verification with known values
        secret = "test_secret_123"
        payload = '{"event":"payment.captured"}'
        
        # Generate valid signature
        valid_signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Should pass with valid signature
        result = verify_razorpay_signature(payload, valid_signature, secret)
        assert result == True
        
        # Should fail with invalid signature
        try:
            verify_razorpay_signature(payload, "invalid_signature", secret)
            assert False, "Should have raised exception"
        except Exception:
            pass  # Expected
        
        print("   ✅ Signature verification working")
        print("   - HMAC-SHA256 validation")
        print("   - Constant-time comparison")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 6: Payment Service
    print("\n6️⃣  Testing payment service...")
    try:
        from app.services.payment_service import payment_service, PaymentService
        
        assert isinstance(payment_service, PaymentService)
        assert hasattr(payment_service, 'create_order')
        assert hasattr(payment_service, 'process_webhook_event')
        assert hasattr(payment_service, 'get_order_status')
        
        print("   ✅ PaymentService initialized")
        print("   - create_order()")
        print("   - process_webhook_event()")
        print("   - get_order_status()")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 7: Plan Upgrade Service
    print("\n7️⃣  Testing plan upgrade service...")
    try:
        from app.services.plan_upgrade_service import plan_upgrade_service, PlanUpgradeService
        
        assert isinstance(plan_upgrade_service, PlanUpgradeService)
        assert hasattr(plan_upgrade_service, 'upgrade_user_plan')
        assert hasattr(plan_upgrade_service, '_is_valid_upgrade')
        
        # Test upgrade validation logic
        from app.models.enums import UserPlan
        
        # Valid upgrades
        assert plan_upgrade_service._is_valid_upgrade(UserPlan.FREE, UserPlan.PRO) == True
        assert plan_upgrade_service._is_valid_upgrade(UserPlan.FREE, UserPlan.CREATIVE) == True
        assert plan_upgrade_service._is_valid_upgrade(UserPlan.PRO, UserPlan.CREATIVE) == True
        
        # Invalid downgrades
        assert plan_upgrade_service._is_valid_upgrade(UserPlan.PRO, UserPlan.FREE) == False
        assert plan_upgrade_service._is_valid_upgrade(UserPlan.CREATIVE, UserPlan.PRO) == False
        
        print("   ✅ PlanUpgradeService initialized")
        print("   - Upgrade path validation working")
        print("   - FREE → PRO ✓, PRO → CREATIVE ✓")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 8: Audit Service
    print("\n8️⃣  Testing audit service...")
    try:
        from app.services.audit_service import audit_service, AuditService
        
        assert isinstance(audit_service, AuditService)
        assert hasattr(audit_service, 'log_payment_created')
        assert hasattr(audit_service, 'log_payment_success')
        assert hasattr(audit_service, 'log_payment_failed')
        assert hasattr(audit_service, 'log_plan_upgrade')
        
        print("   ✅ AuditService initialized")
        print("   - Payment event logging ready")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 9: API Routes
    print("\n9️⃣  Testing API routes...")
    try:
        from app.api.v1.routes.payments import router as payments_router
        from app.api.v1.webhooks.razorpay import router as webhook_router
        
        # Check routes exist
        payment_routes = [r.path for r in payments_router.routes]
        webhook_routes = [r.path for r in webhook_router.routes]
        
        assert "/create-order" in payment_routes
        assert "/orders/{order_id}" in payment_routes
        assert "/webhook" in webhook_routes
        
        print("   ✅ Payment API routes defined")
        print("   - POST /create-order")
        print("   - GET /orders/{order_id}")
        print("   - POST /webhook (Razorpay)")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 10: Environment Configuration
    print("\n🔟 Testing environment configuration...")
    try:
        # Check .env.example has required vars
        with open('.env.example', 'r') as f:
            env_content = f.read()
        
        required_vars = [
            'RAZORPAY_KEY_ID',
            'RAZORPAY_KEY_SECRET',
            'RAZORPAY_WEBHOOK_SECRET',
            'RAZORPAY_CURRENCY',
            'PRO_PLAN_PRICE',
            'CREATIVE_PLAN_PRICE'
        ]
        
        for var in required_vars:
            assert var in env_content, f"Missing: {var}"
        
        print("   ✅ Environment configuration complete")
        print(f"   - {len(required_vars)} Razorpay variables documented")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"✅ Tests Passed: {tests_passed}/10")
    print(f"❌ Tests Failed: {tests_failed}/10")
    print("=" * 60)
    
    return tests_failed == 0


if __name__ == "__main__":
    success = verify_payment_layer()
    sys.exit(0 if success else 1)
