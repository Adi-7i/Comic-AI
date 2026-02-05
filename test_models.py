"""
Test suite for database models.

Validates Pydantic model instantiation, field validation, and enum constraints.
Run with: pytest test_models.py -v
"""

import pytest
from datetime import datetime
from decimal import Decimal

from app.models import (
    User, Project, Character, Scene, Generation, Payment, AuditLog,
    UserPlan, AccountStatus, ProjectStatus, GenerationStatus, 
    PaymentStatus, AuditEventType
)


class TestEnums:
    """Test enum definitions."""
    
    def test_user_plan_enum(self):
        """Test UserPlan enum values."""
        assert UserPlan.FREE == "free"
        assert UserPlan.PRO == "pro"
        assert UserPlan.CREATIVE == "creative"
    
    def test_account_status_enum(self):
        """Test AccountStatus enum values."""
        assert AccountStatus.ACTIVE == "active"
        assert AccountStatus.SUSPENDED == "suspended"
        assert AccountStatus.DELETED == "deleted"
    
    def test_project_status_enum(self):
        """Test ProjectStatus enum values."""
        assert ProjectStatus.DRAFT == "draft"
        assert ProjectStatus.GENERATING == "generating"
        assert ProjectStatus.COMPLETED == "completed"
        assert ProjectStatus.FAILED == "failed"


class TestUserModel:
    """Test User model."""
    
    def test_user_creation_minimal(self):
        """Test creating user with minimal required fields."""
        user = User(
            email="test@example.com",
            hashed_password="$2b$12$hashedpassword"
        )
        assert user.email == "test@example.com"
        assert user.plan == UserPlan.FREE  # default
        assert user.account_status == AccountStatus.ACTIVE  # default
        assert user.generation_limits["monthly_quota"] == 10
    
    def test_user_creation_full(self):
        """Test creating user with all fields."""
        user = User(
            email="pro@example.com",
            hashed_password="$2b$12$hashedpassword",
            full_name="Pro User",
            plan=UserPlan.PRO,
            account_status=AccountStatus.ACTIVE,
            generation_limits={
                "monthly_quota": 100,
                "current_usage": 25,
                "last_reset_at": datetime.utcnow().isoformat()
            }
        )
        assert user.full_name == "Pro User"
        assert user.plan == UserPlan.PRO
        assert user.generation_limits["monthly_quota"] == 100
    
    def test_user_email_validation(self):
        """Test email validation."""
        with pytest.raises(Exception):  # Pydantic validation error
            User(
                email="invalid-email",
                hashed_password="$2b$12$hashedpassword"
            )


class TestProjectModel:
    """Test Project model."""
    
    def test_project_creation(self):
        """Test creating project with required fields."""
        from beanie import PydanticObjectId
        
        project = Project(
            user_id=PydanticObjectId(),
            title="Test Comic",
            plan_snapshot=UserPlan.FREE
        )
        assert project.title == "Test Comic"
        assert project.status == ProjectStatus.DRAFT  # default
        assert project.total_pages == 1  # default
    
    def test_project_total_pages_validation(self):
        """Test total_pages field validation."""
        from beanie import PydanticObjectId
        
        # Valid page count
        project = Project(
            user_id=PydanticObjectId(),
            title="Multi-page Comic",
            total_pages=10,
            plan_snapshot=UserPlan.PRO
        )
        assert project.total_pages == 10
        
        # Invalid page count (too low)
        with pytest.raises(Exception):  # Pydantic validation error
            Project(
                user_id=PydanticObjectId(),
                title="Invalid",
                total_pages=0,
                plan_snapshot=UserPlan.FREE
            )


class TestCharacterModel:
    """Test Character model."""
    
    def test_character_creation(self):
        """Test creating character with appearance metadata."""
        from beanie import PydanticObjectId
        
        character = Character(
            project_id=PydanticObjectId(),
            name="Hero",
            appearance={
                "hair": "black",
                "eyes": "blue",
                "clothing": "cape"
            },
            consistency_seed="hero_v1"
        )
        assert character.name == "Hero"
        assert character.appearance["hair"] == "black"
        assert character.consistency_seed == "hero_v1"


class TestSceneModel:
    """Test Scene model."""
    
    def test_scene_creation(self):
        """Test creating scene with panel location."""
        from beanie import PydanticObjectId
        
        scene = Scene(
            project_id=PydanticObjectId(),
            page_no=1,
            panel_no=1,
            narrative_text={
                "dialogue": ["Hero: I'll save you!"],
                "action": "Hero flies",
                "setting": "City"
            }
        )
        assert scene.page_no == 1
        assert scene.panel_no == 1
        assert scene.language == "en"  # default
    
    def test_scene_panel_validation(self):
        """Test panel_no validation (must be 1-4)."""
        from beanie import PydanticObjectId
        
        # Valid panel number
        scene = Scene(
            project_id=PydanticObjectId(),
            page_no=1,
            panel_no=4,
            narrative_text={}
        )
        assert scene.panel_no == 4
        
        # Invalid panel number (too high)
        with pytest.raises(Exception):  # Pydantic validation error
            Scene(
                project_id=PydanticObjectId(),
                page_no=1,
                panel_no=5,  # Invalid - only 4 panels
                narrative_text={}
            )


class TestGenerationModel:
    """Test Generation model."""
    
    def test_generation_creation(self):
        """Test creating generation task."""
        from beanie import PydanticObjectId
        
        generation = Generation(
            project_id=PydanticObjectId(),
            user_id=PydanticObjectId(),
            cost_metadata={
                "llm_tokens": 1500,
                "image_count": 4
            }
        )
        assert generation.status == GenerationStatus.QUEUED  # default
        assert generation.retry_count == 0  # default
        assert generation.cost_metadata["llm_tokens"] == 1500


class TestPaymentModel:
    """Test Payment model."""
    
    def test_payment_creation(self):
        """Test creating payment transaction."""
        from beanie import PydanticObjectId
        
        payment = Payment(
            user_id=PydanticObjectId(),
            plan_purchased=UserPlan.PRO,
            amount=Decimal("9.99"),
            gateway="stripe",
            gateway_transaction_id="ch_abc123"
        )
        assert payment.plan_purchased == UserPlan.PRO
        assert payment.amount == Decimal("9.99")
        assert payment.currency == "USD"  # default
        assert payment.status == PaymentStatus.PENDING  # default


class TestAuditLogModel:
    """Test AuditLog model."""
    
    def test_audit_log_creation(self):
        """Test creating audit log entry."""
        from beanie import PydanticObjectId
        
        log = AuditLog(
            user_id=PydanticObjectId(),
            event_type=AuditEventType.USER_LOGIN,
            event_data={
                "success": True,
                "ip": "192.168.1.1"
            }
        )
        assert log.event_type == AuditEventType.USER_LOGIN
        assert log.severity == "info"  # default
        assert log.event_data["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
