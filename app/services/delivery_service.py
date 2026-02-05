"""
Delivery Service - Download URL Management.

Handles:
- Generating signed download URLs
- URL expiry checking
- URL refresh
- Access control
"""

import logging
from datetime import datetime, timezone, timedelta

from app.models.project import Project
from app.models.user import User
from app.models.pdf_asset import PdfAsset
from app.core.pdf_config import pdf_settings
from app.core.exceptions import AssetMissing, DownloadNotAllowed
from app.utils.azure_blob import azure_blob_service


logger = logging.getLogger(__name__)


class DeliveryService:
    """
    Delivery service for PDF downloads.
    
    Manages signed URLs and access control.
    """
    
    async def get_download_url(
        self,
        project: Project,
        user: User
    ) -> PdfAsset:
        """
        Get signed download URL for project PDF.
        
        Args:
            project: Project to download
            user: User requesting download
            
        Returns:
            PdfAsset with fresh download URL
            
        Raises:
            AssetMissing: If PDF not generated yet
            DownloadNotAllowed: If user doesn't have access
        """
        # 1. Verify ownership
        if project.user_id != user.id:
            raise DownloadNotAllowed(
                detail="You don't have permission to download this PDF"
            )
        
        # 2. Load PDF asset
        pdf_asset = await PdfAsset.find_one(
            PdfAsset.project_id == project.id
        )
        
        if not pdf_asset:
            raise AssetMissing(
                detail="PDF not generated yet. Generate PDF first."
            )
        
        # 3. Check if URL expired, refresh if needed
        if pdf_asset.is_url_expired():
            logger.info(f"Refreshing expired URL for PDF {pdf_asset.id}")
            pdf_asset = await self.refresh_download_url(pdf_asset)
        
        # 4. Optional: Track download count (for analytics)
        pdf_asset.download_count += 1
        await pdf_asset.save()
        
        logger.info(f"Download URL provided: project={project.id}, user={user.id}")
        return pdf_asset
    
    async def refresh_download_url(
        self,
        pdf_asset: PdfAsset
    ) -> PdfAsset:
        """
        Regenerate signed URL for PDF.
        
        Args:
            pdf_asset: PDF asset to refresh
            
        Returns:
            Updated PdfAsset with new URL
        """
        # Generate new signed URL
        new_url = azure_blob_service.generate_signed_url(
            pdf_asset.blob_path,
            expiry_hours=pdf_settings.PDF_SAS_EXPIRY_HOURS
        )
        
        new_expiry = datetime.now(timezone.utc) + timedelta(
            hours=pdf_settings.PDF_SAS_EXPIRY_HOURS
        )
        
        # Update record
        pdf_asset.blob_url = new_url
        pdf_asset.url_expires_at = new_expiry
        pdf_asset.updated_at = datetime.now(timezone.utc)
        await pdf_asset.save()
        
        logger.info(f"URL refreshed: expires at {new_expiry}")
        return pdf_asset
    
    async def check_download_eligibility(
        self,
        project: Project,
        user: User
    ) -> bool:
        """
        Check if user can download PDF.
        
        Args:
            project: Project to check
            user: User to check
            
        Returns:
            True if download allowed
        """
        # Basic ownership check
        if project.user_id != user.id:
            return False
        
        # Check if PDF exists
        pdf_asset = await PdfAsset.find_one(
            PdfAsset.project_id == project.id
        )
        
        if not pdf_asset:
            return False
        
        # Future: Add plan-specific download limits here if needed
        # For now, all plans allow unlimited downloads
        
        return True


# Singleton instance
delivery_service = DeliveryService()
