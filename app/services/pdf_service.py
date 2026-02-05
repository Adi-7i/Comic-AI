"""
PDF Service - PDF Compilation Orchestrator.

Business logic for:
- Validating project readiness
- Loading comic assets
- Compiling images into PDF
- Uploading to Azure Blob
- Creating PdfAsset metadata
"""

import logging
import tempfile
from pathlib import Path
from typing import List
from datetime import datetime, timezone, timedelta
import httpx

from beanie import PydanticObjectId

from app.models.project import Project
from app.models.user import User
from app.models.comic_asset import ComicAsset
from app.models.pdf_asset import PdfAsset
from app.models.enums import ProjectStatus, UserPlan
from app.core.pdf_config import pdf_settings, get_dpi_for_plan
from app.core.exceptions import (
    ProjectNotCompleted,
    AssetMissing,
    PdfAlreadyExists,
    PdfGenerationFailed,
    PlanPdfAccessDenied
)
from app.utils.pdf_builder import create_comic_pdf
from app.utils.azure_blob import azure_blob_service


logger = logging.getLogger(__name__)


class PdfService:
    """
    PDF compilation service.
    
    Orchestrates the entire PDF generation flow.
    """
    
    async def validate_compilation(
        self,
        project: Project,
        force_regenerate: bool = False
    ) -> None:
        """
        Pre-flight validation before PDF compilation.
        
        Args:
            project: Project to compile
            force_regenerate: Allow regeneration if PDF exists
            
        Raises:
            ProjectNotCompleted: If project not fully generated
            AssetMissing: If comic page images missing
            PdfAlreadyExists: If PDF exists and not forcing regeneration
        """
        # 1. Check project status
        if project.status != ProjectStatus.COMPLETED:
            raise ProjectNotCompleted(
                detail=f"Project status is {project.status}. Must be COMPLETED."
            )
        
        # 2. Check if PDF already exists
        existing_pdf = await PdfAsset.find_one(
            PdfAsset.project_id == project.id
        )
        
        if existing_pdf and not force_regenerate:
            raise PdfAlreadyExists(
                detail="PDF already generated. Use force_regenerate=true to recreate."
            )
        
        # 3. Verify all comic assets exist
        total_pages = project.total_pages
        asset_count = await ComicAsset.find(
            ComicAsset.project_id == project.id
        ).count()
        
        if asset_count != total_pages:
            raise AssetMissing(
                detail=f"Expected {total_pages} comic pages, found {asset_count}"
            )
        
        logger.info(f"Validation passed for project {project.id}")
    
    async def enforce_plan_rules(self, project: Project) -> None:
        """
        Enforce plan-based page count limits.
        
        Args:
            project: Project to check
            
        Raises:
            PlanPdfAccessDenied: If page count exceeds plan limit
        """
        plan = project.plan_snapshot
        total_pages = project.total_pages
        
        # FREE: max 1 page
        if plan == UserPlan.FREE:
            if total_pages > 1:
                raise PlanPdfAccessDenied(
                    detail="Free plan allows only 1 page per comic"
                )
        
        # PRO: max 3 pages
        elif plan == UserPlan.PRO:
            if total_pages > 3:
                raise PlanPdfAccessDenied(
                    detail=f"Pro plan allows maximum 3 pages. Project has {total_pages} pages."
                )
        
        # CREATIVE: configurable (from settings)
        elif plan == UserPlan.CREATIVE:
            from app.core.config import settings
            max_pages = settings.CREATIVE_MAX_PAGES
            if total_pages > max_pages:
                raise PlanPdfAccessDenied(
                    detail=f"Creative plan allows maximum {max_pages} pages"
                )
        
        logger.info(f"Plan rules enforced: {plan} allows {total_pages} pages")
    
    async def compile_pdf(
        self,
        project: Project,
        user: User
    ) -> PdfAsset:
        """
        Compile comic images into PDF.
        
        Main orchestration method.
        
        Args:
            project: Project to compile
            user: User requesting compilation
            
        Returns:
            PdfAsset with metadata
            
        Raises:
            PdfGenerationFailed: If compilation fails
        """
        try:
            logger.info(f"Starting PDF compilation: project={project.id}, user={user.id}")
            
            # 1. Load comic assets (ordered by page_no)
            comic_assets = await ComicAsset.find(
                ComicAsset.project_id == project.id
            ).sort(+ComicAsset.page_no).to_list()
            
            if not comic_assets:
                raise AssetMissing("No comic page images found")
            
            # 2. Download images from Azure Blob
            image_bytes_list = await self._download_images(comic_assets)
            
            # 3. Determine DPI based on plan
            dpi = get_dpi_for_plan(project.plan_snapshot)
            
            # 4. Build PDF
            pdf_bytes = await self._build_pdf(
                images=image_bytes_list,
                dpi=dpi,
                metadata={
                    "project_id": str(project.id),
                    "author": user.email,
                    "plan_snapshot": project.plan_snapshot.value,
                    "title": project.config.get("title", "Comic Book")
                }
            )
            
            # 5. Upload to Azure Blob
            blob_path = azure_blob_service.build_pdf_blob_path(str(project.id))
            await azure_blob_service.upload_pdf(pdf_bytes, blob_path)
            
            # 6. Generate signed URL
            blob_url = azure_blob_service.generate_signed_url(
                blob_path,
                expiry_hours=pdf_settings.PDF_SAS_EXPIRY_HOURS
            )
            url_expires_at = datetime.now(timezone.utc) + timedelta(
                hours=pdf_settings.PDF_SAS_EXPIRY_HOURS
            )
            
            # 7. Create or update PdfAsset
            pdf_asset = await self._upsert_pdf_asset(
                project_id=project.id,
                blob_url=blob_url,
                blob_path=blob_path,
                resolution_dpi=dpi,
                plan_snapshot=project.plan_snapshot,
                file_size_bytes=len(pdf_bytes),
                page_count=len(comic_assets),
                url_expires_at=url_expires_at
            )
            
            logger.info(f"PDF compiled: {pdf_asset.file_size_mb}MB, {pdf_asset.page_count} pages")
            return pdf_asset
            
        except (ProjectNotCompleted, AssetMissing, PlanPdfAccessDenied):
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"PDF compilation failed: {e}")
            raise PdfGenerationFailed(detail=str(e))
    
    async def _download_images(self, comic_assets: List[ComicAsset]) -> List[bytes]:
        """
        Download comic page images from Azure Blob.
        
        Args:
            comic_assets: List of ComicAsset records
            
        Returns:
            List of image bytes
        """
        image_bytes_list = []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for asset in comic_assets:
                logger.debug(f"Downloading image: page {asset.page_no}")
                
                response = await client.get(asset.blob_url)
                response.raise_for_status()
                
                image_bytes_list.append(response.content)
        
        return image_bytes_list
    
    async def _build_pdf(
        self,
        images: List[bytes],
        dpi: int,
        metadata: dict
    ) -> bytes:
        """
        Build PDF from images using pdf_builder.
        
        Args:
            images: List of image bytes
            dpi: Resolution
            metadata: PDF metadata
            
        Returns:
            PDF as bytes
        """
        # Use temporary file for PDF creation
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Create PDF
            file_size = create_comic_pdf(
                images=images,
                output_path=tmp_path,
                dpi=dpi,
                metadata=metadata
            )
            
            # Read PDF bytes
            pdf_bytes = Path(tmp_path).read_bytes()
            
            return pdf_bytes
            
        finally:
            # Cleanup temp file
            Path(tmp_path).unlink(missing_ok=True)
    
    async def _upsert_pdf_asset(
        self,
        project_id: PydanticObjectId,
        blob_url: str,
        blob_path: str,
        resolution_dpi: int,
        plan_snapshot: UserPlan,
        file_size_bytes: int,
        page_count: int,
        url_expires_at: datetime
    ) -> PdfAsset:
        """
        Create or update PdfAsset record.
        
        Args:
            project_id: Project ID
            blob_url: Signed download URL
            blob_path: Azure Blob path
            resolution_dpi: PDF resolution
            plan_snapshot: Plan at generation time
            file_size_bytes: PDF file size
            page_count: Number of pages
            url_expires_at: URL expiry time
            
        Returns:
            PdfAsset record
        """
        # Check for existing
        existing = await PdfAsset.find_one(
            PdfAsset.project_id == project_id
        )
        
        if existing:
            # Update existing
            existing.blob_url = blob_url
            existing.blob_path = blob_path
            existing.resolution_dpi = resolution_dpi
            existing.plan_snapshot = plan_snapshot
            existing.file_size_bytes = file_size_bytes
            existing.page_count = page_count
            existing.url_expires_at = url_expires_at
            existing.updated_at = datetime.now(timezone.utc)
            await existing.save()
            return existing
        
        # Create new
        pdf_asset = PdfAsset(
            project_id=project_id,
            blob_url=blob_url,
            blob_path=blob_path,
            resolution_dpi=resolution_dpi,
            plan_snapshot=plan_snapshot,
            file_size_bytes=file_size_bytes,
            page_count=page_count,
            url_expires_at=url_expires_at
        )
        await pdf_asset.save()
        return pdf_asset


# Singleton instance
pdf_service = PdfService()
