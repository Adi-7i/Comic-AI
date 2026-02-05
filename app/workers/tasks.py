"""
Celery Task Definitions.

Image Generation Task:
- Validates project ownership & plan rules
- Generates images page-by-page
- Uploads to Azure Blob
- Updates progress (0-100)
- Handles FREE plan atomic update
"""

import asyncio
import logging
import random
from datetime import datetime, timezone

from beanie import PydanticObjectId

from app.workers.celery_app import celery
from app.services.task_service import task_service
from app.db import init_db


logger = logging.getLogger(__name__)


# Helper to run async code in sync Celery task
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@celery.task(bind=True, name="app.workers.tasks.generate_comic_task")
def generate_comic_task(self, generation_id: str):
    """
    Stub task for comic generation (story/text).
    Kept for backwards compatibility.
    """
    async def _process():
        await init_db()
        task_id = self.request.id
        
        try:
            await task_service.update_progress(task_id, 10)
            await asyncio.sleep(2)
            await task_service.update_progress(task_id, 50)
            await asyncio.sleep(2)
            await task_service.update_progress(task_id, 90)
            await task_service.mark_completed(task_id)
        except Exception as e:
            await task_service.mark_failed(task_id, str(e))
            raise

    run_async(_process())


@celery.task(
    bind=True, 
    name="app.workers.tasks.image_generation_task",
    autoretry_for=(ConnectionError, TimeoutError),  # Only transient errors
    retry_backoff=True,
    retry_kwargs={"max_retries": 3}
)
def image_generation_task(self, generation_id: str):
    """
    Image Generation Task - Creates comic page images.
    
    Steps:
    1. Validate project ownership & status
    2. Enforce plan rules BEFORE generation
    3. Generate images page-by-page
    4. Upload each page to Azure Blob
    5. Update task progress (0-100)
    6. Persist asset metadata
    7. Mark free_story_used atomically (Free plan)
    
    Hard fails on:
    - Plan violation
    - Invalid scene structure
    - Non-transient errors
    """
    async def _process():
        # Import here to avoid circular imports in worker
        from app.models.project import Project
        from app.models.user import User
        from app.models.generation import Generation
        from app.models.enums import UserPlan, GenerationStatus, ProjectStatus
        from app.services.comic_engine import comic_engine
        from app.services.plan_service import plan_service
        from app.core.exceptions import (
            FreeStoryAlreadyUsed,
            PlanImageAccessDenied,
            InvalidSceneStructure
        )
        
        # Initialize DB connection
        await init_db()
        
        task_id = self.request.id
        logger.info(f"Starting image generation: task_id={task_id}, gen_id={generation_id}")
        
        try:
            # 1. Load Generation record
            generation = await Generation.get(PydanticObjectId(generation_id))
            if not generation:
                raise ValueError(f"Generation {generation_id} not found")
            
            # Update with Celery task ID if not set
            if not generation.task_id:
                generation.task_id = task_id
                await generation.save()
            
            await task_service.update_progress(task_id, 5)
            
            # 2. Load Project
            project = await Project.get(generation.project_id)
            if not project:
                raise ValueError(f"Project {generation.project_id} not found")
            
            # 3. Load User
            user = await User.get(generation.user_id)
            if not user:
                raise ValueError(f"User {generation.user_id} not found")
            
            await task_service.update_progress(task_id, 10)
            
            # =====================================================
            # PLAN VALIDATION (CRITICAL - HARD FAIL ON VIOLATION)
            # =====================================================
            
            plan = project.plan_snapshot
            
            # FREE Plan: Check free_story_available
            if plan == UserPlan.FREE:
                if not user.free_story_available or user.free_story_used:
                    raise FreeStoryAlreadyUsed(
                        detail="Your free story has already been used. Upgrade to continue."
                    )
                
                # FREE plan: max 1 page
                if project.total_pages > 1:
                    raise PlanImageAccessDenied(
                        detail="Free plan allows only 1 page per story."
                    )
            
            # PRO Plan: max 3 pages
            elif plan == UserPlan.PRO:
                if project.total_pages > 3:
                    raise PlanImageAccessDenied(
                        detail=f"Pro plan allows maximum 3 pages. Project has {project.total_pages}."
                    )
            
            # CREATIVE Plan: configurable limit (default 10+)
            elif plan == UserPlan.CREATIVE:
                limits = plan_service.get_plan_limits(plan)
                max_pages = limits.get("max_pages", 10)
                if project.total_pages > max_pages:
                    raise PlanImageAccessDenied(
                        detail=f"Creative plan allows maximum {max_pages} pages."
                    )
            
            await task_service.update_progress(task_id, 15)
            
            # =====================================================
            # GENERATE PAGES
            # =====================================================
            
            total_pages = project.total_pages
            pages_completed = 0
            
            # Generate seed for consistency across all panels
            base_seed = random.randint(1, 1000000)
            
            for page_no in range(1, total_pages + 1):
                try:
                    # Calculate progress (15-90% for generation)
                    progress_per_page = 75 / total_pages
                    current_progress = 15 + int(pages_completed * progress_per_page)
                    
                    await task_service.update_progress(task_id, current_progress)
                    
                    logger.info(f"Generating page {page_no}/{total_pages}")
                    
                    # Generate the page
                    asset = await comic_engine.generate_page(
                        project=project,
                        page_no=page_no,
                        user=user,
                        seed=base_seed + page_no
                    )
                    
                    # Link asset to generation
                    asset.generation_id = generation.id
                    await asset.save()
                    
                    pages_completed += 1
                    
                except InvalidSceneStructure as e:
                    # Hard fail on invalid structure
                    logger.error(f"Invalid scene structure: {e}")
                    raise
                except Exception as e:
                    # Log but attempt to continue with other pages
                    logger.error(f"Page {page_no} failed: {e}")
                    # For strict mode, re-raise
                    raise
            
            await task_service.update_progress(task_id, 90)
            
            # =====================================================
            # FREE PLAN: ATOMIC UPDATE
            # =====================================================
            
            if plan == UserPlan.FREE and pages_completed > 0:
                # Atomic update to prevent race conditions
                await User.find_one(
                    User.id == user.id,
                    User.free_story_used == False  # Only update if not already used
                ).update({
                    "$set": {
                        "free_story_used": True,
                        "free_story_available": False,
                        "updated_at": datetime.now(timezone.utc)
                    }
                })
                logger.info(f"Marked free_story_used for user {user.id}")
            
            # =====================================================
            # COMPLETE
            # =====================================================
            
            # Update project status
            project.status = ProjectStatus.COMPLETED
            project.completed_at = datetime.now(timezone.utc)
            await project.save()
            
            await task_service.mark_completed(task_id, result={
                "pages_generated": pages_completed,
                "total_pages": total_pages
            })
            
            logger.info(f"Image generation completed: {pages_completed}/{total_pages} pages")
            
        except (FreeStoryAlreadyUsed, PlanImageAccessDenied, InvalidSceneStructure) as e:
            # Hard failures - don't retry
            logger.error(f"Plan/validation error: {e.detail}")
            await task_service.mark_failed(task_id, e.detail)
            # Don't re-raise - we've handled it
            
        except Exception as e:
            # Other errors - mark failed and potentially retry
            error_msg = str(e)
            if len(error_msg) > 500:
                error_msg = error_msg[:497] + "..."
            
            logger.error(f"Image generation failed: {error_msg}")
            await task_service.mark_failed(task_id, error_msg)
            raise  # Re-raise for Celery retry logic

    run_async(_process())
