"""
Azure Blob Storage utilities.

Handles:
- Image upload to Azure Blob (private container)
- Time-limited SAS URL generation
- Blob path management

SECURITY: Connection strings are never logged.
"""

import logging
from typing import Optional
from datetime import datetime, timedelta, timezone
from io import BytesIO

from app.core.azure_image_config import azure_blob_settings


logger = logging.getLogger(__name__)


class AzureBlobService:
    """
    Azure Blob Storage service for comic asset management.
    
    All images are stored in private containers with SAS-based access.
    """
    
    def __init__(self):
        self._client = None
        self._container_client = None
    
    def _get_container_client(self):
        """
        Lazy-initialize the blob container client.
        """
        if self._container_client is None:
            if not azure_blob_settings.is_configured:
                logger.warning("Azure Blob Storage not configured - using mock mode")
                return None
            
            try:
                from azure.storage.blob import BlobServiceClient
                
                connection_string = azure_blob_settings.CONNECTION_STRING.get_secret_value()
                self._client = BlobServiceClient.from_connection_string(connection_string)
                self._container_client = self._client.get_container_client(
                    azure_blob_settings.CONTAINER_NAME
                )
                
                # Create container if it doesn't exist
                if not self._container_client.exists():
                    self._container_client.create_container()
                    logger.info(f"Created container: {azure_blob_settings.CONTAINER_NAME}")
                    
            except ImportError:
                logger.error("azure-storage-blob package not installed")
                return None
            except Exception as e:
                logger.error(f"Failed to initialize Azure Blob client: {type(e).__name__}")
                return None
                
        return self._container_client
    
    async def upload_image(
        self,
        image_bytes: bytes,
        blob_path: str,
        content_type: str = "image/png"
    ) -> Optional[str]:
        """
        Upload image to Azure Blob Storage.
        
        Args:
            image_bytes: Image data as bytes
            blob_path: Path within container (e.g., "projects/123/pages/1.png")
            content_type: MIME type of the image
            
        Returns:
            Blob path if successful, None if failed
            
        Note: Uses sync Azure SDK - wrap in executor for true async in production
        """
        container = self._get_container_client()
        
        if container is None:
            # Mock mode - return fake path
            logger.warning("Azure Blob not configured - mock upload")
            return blob_path
        
        try:
            from azure.storage.blob import ContentSettings
            
            blob_client = container.get_blob_client(blob_path)
            blob_client.upload_blob(
                BytesIO(image_bytes),
                overwrite=True,
                content_settings=ContentSettings(content_type=content_type)
            )
            
            logger.info(f"Uploaded blob: {blob_path}")
            return blob_path
            
        except Exception as e:
            logger.error(f"Blob upload failed: {type(e).__name__}")
            return None
    
    def generate_signed_url(
        self,
        blob_path: str,
        expiry_hours: Optional[int] = None
    ) -> str:
        """
        Generate a time-limited SAS URL for blob access.
        
        Args:
            blob_path: Path to the blob within container
            expiry_hours: Hours until URL expires (default from config)
            
        Returns:
            Signed URL string
        """
        if expiry_hours is None:
            expiry_hours = azure_blob_settings.SAS_EXPIRY_HOURS
        
        container = self._get_container_client()
        
        if container is None:
            # Mock mode - return placeholder URL
            return f"https://mock-storage.blob.core.windows.net/{azure_blob_settings.CONTAINER_NAME}/{blob_path}"
        
        try:
            from azure.storage.blob import generate_blob_sas, BlobSasPermissions
            
            blob_client = container.get_blob_client(blob_path)
            
            # Generate SAS token
            sas_token = generate_blob_sas(
                account_name=self._client.account_name,
                container_name=azure_blob_settings.CONTAINER_NAME,
                blob_name=blob_path,
                account_key=self._client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.now(timezone.utc) + timedelta(hours=expiry_hours)
            )
            
            return f"{blob_client.url}?{sas_token}"
            
        except Exception as e:
            logger.error(f"SAS URL generation failed: {type(e).__name__}")
            # Fallback to direct URL (won't work without SAS)
            return f"https://storage.blob.core.windows.net/{azure_blob_settings.CONTAINER_NAME}/{blob_path}"
    
    def get_url_expiry(self, hours: Optional[int] = None) -> datetime:
        """
        Calculate URL expiry timestamp.
        """
        if hours is None:
            hours = azure_blob_settings.SAS_EXPIRY_HOURS
        return datetime.now(timezone.utc) + timedelta(hours=hours)
    
    @staticmethod
    def build_blob_path(project_id: str, page_no: int) -> str:
        """
        Build standard blob path for a comic page.
        
        Format: projects/{project_id}/pages/{page_no}.png
        """
        return f"projects/{project_id}/pages/{page_no}.png"
    
    # ========================================================================
    # PDF-SPECIFIC METHODS (Step-7)
    # ========================================================================
    
    async def upload_pdf(
        self,
        pdf_bytes: bytes,
        blob_path: str
    ) -> Optional[str]:
        """
        Upload PDF to Azure Blob Storage.
        
        Args:
            pdf_bytes: PDF data as bytes
            blob_path: Path within container (e.g., "pdfs/{project_id}/comic.pdf")
            
        Returns:
            Blob path if successful, None if failed
        """
        return await self.upload_image(
            image_bytes=pdf_bytes,
            blob_path=blob_path,
            content_type="application/pdf"
        )
    
    @staticmethod
    def build_pdf_blob_path(project_id: str) -> str:
        """
        Build standard blob path for a project PDF.
        
        Format: pdfs/{project_id}/comic.pdf
        """
        return f"pdfs/{project_id}/comic.pdf"


# Singleton instance
azure_blob_service = AzureBlobService()
