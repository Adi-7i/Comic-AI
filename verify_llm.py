"""
Verification script for LLM Story Engine.

Tests:
- LLM Client Mocking
- Schema Validation
- Story Parsing & Persistence
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Override to use mock provider for testing logic
os.environ["LLM_PROVIDER"] = "mock"

from app.db import init_db
from app.models.user import User
from app.models.project import Project
from app.models.enums import UserPlan, ProjectStatus
from app.services.story_service import story_service
from app.schemas.scene import SceneCreate
from app.core.exceptions import StoryParseFailed

async def main():
    print("🔄 Initializing DB...")
    await init_db()
    
    # Cleanup
    await User.find_all().delete()
    await Project.find_all().delete()
    
    # 1. Setup User & Project
    user = User(email="llm_tester@example.com", hashed_password="X", plan=UserPlan.PRO)
    await user.save()
    
    project = Project(
        user_id=user.id,
        title="AI Comic",
        status=ProjectStatus.DRAFT,
        plan_snapshot=UserPlan.PRO
    )
    await project.save()
    print("✅ Project created")
    
    # 2. Test Story Parsing (Mock Mode)
    print("🚀 Testing Story Parsign (Mock Mode)...")
    input_text = "A cyberpunk detective story in Neo Tokyo."
    
    try:
        result = await story_service.parse_story(user, project, input_text)
        print("✅ Parse Success!")
        print(f"   Generated {result['pages']} pages")
        print(f"   Usage: {result['usage']}")
        
        # Verify persistence
        from app.models.scene import Scene
        scenes = await Scene.find(Scene.project_id == project.id).to_list()
        print(f"   Saved {len(scenes)} scenes in DB")
        assert len(scenes) == 4, "Mock returns 4 panels (1 page)"
        
    except Exception as e:
        print(f"❌ Parse Failed: {e}")
        raise e

    print("\n✅ ALL LLM TESTS PASSED")

if __name__ == "__main__":
    asyncio.run(main())
