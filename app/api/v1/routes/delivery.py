"""
Delivery API Routes - PDF Compilation and Download Endpoints.

Endpoints:
- POST /projects/{project_id}/pdf - Trigger PDF compilation
- GET /projects/{project_id}/pdf/status - Check compilation status
- GET /projects/{project_id}/download - Get signed download URL
"""

import logging
from uuid import UUID
from fastapi import APIRouter, Depends, Body

from app.models.project import Project
from app.models.user import User
from app.models.generation import Generation, GenerationStatus
from app.models.pdf_asset import PdfAsset
from app.schemas.pdf import (
    PdfCompilationRequest,
    PdfCompilationResponse,
    PdfCompilationStatus,
    DownloadUrlResponse,
    PdfAssetResponse
)
from app.core.exceptions import PdfAlreadyExists, AssetMissing
from app.services.pdf_service import pdf_service
from app.services.delivery_service import delivery_service
from app.api.v1.dependencies.auth import get_current_user
from app.api.v1.dependencies.permissions import get_project_or_404
from app.api.v1.dependencies.delivery_guards import get_pdf_asset_for_project
from app.workers.celery_app import celery


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/{project_id}/pdf",
    response_model=PdfCompilationResponse,
    summary="Trigger PDF compilation",
    description="Start async PDF compilation task for completed project"
)
async def trigger_pdf_compilation(
    project_id: UUID,
    force_regenerate: bool = Body(False, embed=True),
    project: Project = Depends(get_project_or_404),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger PDF compilation for a completed project.
    
    - **project_id**: Project to compile
    - **force_regenerate**: Regenerate even if PDF exists
    
    Returns:
        Task ID for status polling
    """
    logger.info(f"PDF compilation requested: project={project_id}, user={current_user.id}")
    
    # Validate compilation readiness
    await pdf_service.validate_compilation(
        project=project,
        force_regenerate=force_regenerate
    )
    
    # Enforce plan rules
    await pdf_service.enforce_plan_rules(project)
    
    # Create Generation record for tracking
    generation = Generation(
        task_type="pdf",
        project_id=project.id,
        user_id=current_user.id,
        status=GenerationStatus.PENDING,
        progress=0
    )
    await generation.save()
    
    # Generate unique task ID
    task_id = str(generation.id)
    generation.task_id = task_id
    await generation.save()
    
    # Dispatch Celery task
    from app.workers.tasks import pdf_compilation_task
    pdf_compilation_task.apply_async(
        args=[str(project.id), str(current_user.id)],
        task_id=task_id
    )
    
    logger.info(f"PDF compilation task dispatched: task_id={task_id}")
    
    return PdfCompilationResponse(
        task_id=task_id,
        status="pending",
        message=f"PDF compilation started. Check status at /projects/{project_id}/pdf/status"
    )


@router.get(
    "/{project_id}/pdf/status",
    response_model=PdfCompilationStatus,
    summary="Get PDF compilation status",
    description="Check the status of a PDF compilation task"
)
async def get_pdf_status(
    project_id: UUID,
    project: Project = Depends(get_project_or_404),
    current_user: User = Depends(get_current_user)
):
    """
    Get PDF compilation task status.
    
    Returns:
        Task status with progress and result
    """
    # Find most recent PDF generation task
    generation = await Generation.find_one(
        Generation.project_id == project.id,
        Generation.task_type == "pdf"
    ).sort(-Generation.created_at)
    
    if not generation:
        raise AssetMissing(detail="No PDF compilation task found")
    
    # Check if PDF asset exists (completed)
    pdf_asset = None
    if generation.status == GenerationStatus.COMPLETED:
        pdf_asset_doc = await PdfAsset.find_one(
            PdfAsset.project_id == project.id
        )
        if pdf_asset_doc:
            pdf_asset = PdfAssetResponse(
                id=str(pdf_asset_doc.id),
                project_id=str(pdf_asset_doc.project_id),
                download_url=pdf_asset_doc.blob_url,
                expires_at=pdf_asset_doc.url_expires_at,
                resolution_dpi=pdf_asset_doc.resolution_dpi,
                file_size_mb=pdf_asset_doc.file_size_mb,
                page_count=pdf_asset_doc.page_count,
                created_at=pdf_asset_doc.created_at
            )
    
    return PdfCompilationStatus(
        task_id=generation.task_id,
        status=generation.status.value,
        progress=generation.progress,
        pdf_asset=pdf_asset,
        error=generation.error_message if generation.status == GenerationStatus.FAILED else None
    )


@router.get(
    "/{project_id}/download",
    response_model=DownloadUrlResponse,
    summary="Get PDF download URL",
    description="Get a time-limited signed URL for PDF download"
)
async def get_download_url(
    project_id: UUID,
    project: Project = Depends(get_project_or_404),
    current_user: User = Depends(get_current_user)
):
    """
    Get signed download URL for project PDF.
    
    - URL is time-limited (default 24 hours)
    - Auto-refreshes if expired
    
    Returns:
        Signed download URL
    """
    logger.info(f"Download URL requested: project={project_id}, user={current_user.id}")
    
    # Get PDF asset with fresh URL
    pdf_asset = await delivery_service.get_download_url(
        project=project,
        user=current_user
    )
    
    return DownloadUrlResponse(
        download_url=pdf_asset.blob_url,
        expires_at=pdf_asset.url_expires_at,
        file_size_mb=pdf_asset.file_size_mb,
        page_count=pdf_asset.page_count
    )
