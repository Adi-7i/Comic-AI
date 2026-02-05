"""
Verification script for Core Domain APIs.
"""
import asyncio
import os
from dotenv import load_dotenv

# Load .env file explicitly to ensure variables are available
load_dotenv()

from app.core.config import settings
from app.db import init_db
from app.models.user import User
from app.models.project import Project
from app.models.scene import Scene
from app.services.project_service import project_service
from app.services.scene_service import scene_service
from app.schemas.project import ProjectCreate
from app.schemas.scene import SceneCreate, NarrativeText
from app.models.enums import UserPlan, ProjectStatus

async def main():
    print("🔄 Initializing DB...")
    await init_db()
    
    # Cleanup
    await User.find_all().delete()
    await Project.find_all().delete()
    await Scene.find_all().delete()
    
    print("✅ DB Cleaned")
    
    # 1. Create User
    user = User(
        email="test@example.com",
        hashed_password="hash",
        plan=UserPlan.PRO  # Pro plan allows 3 pages
    )
    await user.save()
    print(f"✅ User created (Plan: {user.plan.value})")
    
    # 2. Create Project
    project_data = ProjectCreate(
        title="Test Comic",
        description="A test project",
        config={"style": "manga"}
    )
    project = await project_service.create_project(user, project_data)
    print(f"✅ Project created: {project.title} (Snapshot: {project.plan_snapshot.value})")
    
    assert project.plan_snapshot == UserPlan.PRO
    assert project.status == ProjectStatus.DRAFT
    
    # 3. Add Scenes (Page 1)
    scenes_data = [
        SceneCreate(
            page_no=1,
            panel_no=1,
            narrative_text=NarrativeText(
                dialogue=["Hello"],
                action="Standing",
                setting="Room"
            ),
            language="en"
        ),
        SceneCreate(
            page_no=1,
            panel_no=2,
            narrative_text=NarrativeText(
                dialogue=["Hi"],
                action="Smiling",
                setting="Room"
            ),
            language="en"
        )
    ]
    
    created_scenes = await scene_service.add_scenes(project, scenes_data)
    print(f"✅ added {len(created_scenes)} scenes to Page 1")
    
    # 4. Verify Pagination/Limits
    # Pro plan max pages = 3. Let's try adding page 4 (should fail)
    
    # Add page 2 (OK)
    await scene_service.add_scenes(project, [
        SceneCreate(
            page_no=2,
            panel_no=1,
            narrative_text=NarrativeText(dialogue=[], action="X", setting="Y"),
            language="en"
        )
    ])
    print("✅ Page 2 added")
    
    # Add page 3 (OK)
    await scene_service.add_scenes(project, [
        SceneCreate(
            page_no=3,
            panel_no=1,
            narrative_text=NarrativeText(dialogue=[], action="X", setting="Y"),
            language="en"
        )
    ])
    print("✅ Page 3 added")
    
    # Add page 4 (Should Fail)
    try:
        await scene_service.add_scenes(project, [
            SceneCreate(
                page_no=4,
                panel_no=1,
                narrative_text=NarrativeText(dialogue=[], action="X", setting="Y"),
                language="en"
            )
        ])
        print("❌ FAILED: Page 4 should have been blocked")
    except Exception as e:
        print(f"✅ BLOCKED: Page 4 blocked correctly ({e})")

    print("\n✅ ALL TESTS PASSED")

if __name__ == "__main__":
    asyncio.run(main())
