"""
PDF Asset Model - Metadata for generated PDFs.

Stores:
- Azure Blob URL for download
- Resolution (DPI) based on plan
- Plan snapshot at generation time
- File size and page count

Binary PDF data stored in Azure Blob Storage, NOT in MongoDB.
"""

from datetime import datetime, timezone
from typing import Optional

from beanie import PydanticObjectId
from pydantic import Field

from app.models.base import BaseDocument
from app.models.enums import UserPlan


class PdfAsset(BaseDocument):
    """
    PDF asset metadata.
    
    One PDF per project (unique constraint on project_id).
    """
    
    # Identity
    project_id: PydanticObjectId = Field(
        ...,
        description="Reference to Project"
    )
    
    # Storage
    blob_url: str = Field(
        ...,
        description="Signed download URL from Azure Blob"
    )
    blob_path: str = Field(
        ...,
        description="Azure Blob path (e.g., pdfs/{project_id}/comic.pdf)"
    )
    
    # Quality metadata
    resolution_dpi: int = Field(
        ...,
        description="PDF resolution in DPI (72/150/300)"
    )
    plan_snapshot: UserPlan = Field(
        ...,
        description="User plan at time of generation"
    )
    
    # File metadata
    file_size_bytes: int = Field(
        ...,
        description="PDF file size in bytes"
    )
    page_count: int = Field(
        ...,
        description="Number of pages in PDF"
    )
    
    # URL expiry
    url_expires_at: Optional[datetime] = Field(
        default=None,
        description="When the signed URL expires"
    )
    
    # Optional download tracking
    download_count: int = Field(
        default=0,
        description="Number of times downloaded (optional tracking)"
    )
    
    # Link to generation task
    generation_id: Optional[PydanticObjectId] = Field(
        default=None,
        description="Reference to Generation task that created this PDF"
    )
    
    class Settings:
        name = "pdf_assets"
        indexes = [
            "project_id",  # Unique lookup
            "created_at",  # For cleanup jobs
        ]
    
    def __repr__(self) -> str:
        return f"<PdfAsset project={self.project_id} dpi={self.resolution_dpi} pages={self.page_count}>"
    
    def is_url_expired(self) -> bool:
        """Check if signed URL has expired."""
        if not self.url_expires_at:
            return True
        return datetime.now(timezone.utc) >= self.url_expires_at
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes."""
        return round(self.file_size_bytes / (1024 * 1024), 2)
