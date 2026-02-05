"""
Celery Task Definitions.

Stub tasks that simulate work and update DB.
"""

import asyncio
import time
from asgiref.sync import async_to_sync

from app.workers.celery_app import celery
from app.services.task_service import task_service
from app.db import init_db

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
    Stub task for comic generation.
    """
    async def _process():
        # 1. Initialize DB (needed for Beanie models in worker process)
        # Note: In production, consider doing this once per worker init
        await init_db()
        
        # We get the generation by DB ID usually, but here we passed ID? 
        # Wait, generation_id is passed. task_service uses task_id (celery ID).
        # Let's align. The service updates by CELERY task_id.
        # But we also have the DB document ID `generation_id`.
        # using self.request.id gives us the Celery ID.
        
        task_id = self.request.id
        
        try:
            # Start
            await task_service.update_progress(task_id, 10)
            
            # Simulate heavy work
            # Phase 1: Planning
            time.sleep(2) 
            await task_service.update_progress(task_id, 30)
            
            # Phase 2: Generation
            time.sleep(2)
            await task_service.update_progress(task_id, 60)
            
            # Phase 3: Finalizing
            time.sleep(2)
            await task_service.update_progress(task_id, 90)
            
            # Complete
            await task_service.mark_completed(task_id)
            
        except Exception as e:
            await task_service.mark_failed(task_id, str(e))
            # Re-raise to let Celery know? Or handle gracefully?
            # If we mark failed in DB, we might strictly fail task.
            raise e

    # Run the async logic
    run_async(_process())
