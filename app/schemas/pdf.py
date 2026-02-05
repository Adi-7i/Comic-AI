"""
PDF Compilation & Delivery Schemas.

Request/response schemas for PDF generation API endpoints.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PdfCompilationRequest(BaseModel):
    """Request to compile project images into PDF."""
    
    project_id: str = Field(
        ...,
        description="Project ID to generate PDF for"
    )
    force_regenerate: bool = Field(
        default=False,
        description="Force regeneration even if PDF exists"
    )


class PdfAssetResponse(BaseModel):
    """Response containing PDF asset metadata."""
    
    id: str = Field(..., description="PDF asset ID")
    project_id: str = Field(..., description="Project ID")
    download_url: str = Field(..., description="Signed download URL")
    expires_at: datetime = Field(..., description="URL expiration time")
    resolution_dpi: int = Field(..., description="PDF resolution (72/150/300)")
    file_size_mb: float = Field(..., description="File size in MB")
    page_count: int = Field(..., description="Number of pages")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "project_id": "507f1f77bcf86cd799439012",
                "download_url": "https://cynerza.blob.core.windows.net/comic-pdfs/...",
                "expires_at": "2026-02-06T23:00:00Z",
                "resolution_dpi": 150,
                "file_size_mb": 2.5,
                "page_count": 3,
                "created_at": "2026-02-05T23:00:00Z"
            }
        }


class PdfCompilationStatus(BaseModel):
    """Status of PDF compilation task."""
    
    task_id: str = Field(..., description="Celery task ID")
    status: str = Field(..., description="Task status (pending/processing/completed/failed)")
    progress: int = Field(default=0, description="Progress percentage (0-100)")
    pdf_asset: Optional[PdfAssetResponse] = Field(
        default=None,
        description="PDF asset metadata (only if completed)"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message (only if failed)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "abc123-def456-ghi789",
                "status": "completed",
                "progress": 100,
                "pdf_asset": {
                    "id": "507f1f77bcf86cd799439011",
                    "project_id": "507f1f77bcf86cd799439012",
                    "download_url": "https://...",
                    "expires_at": "2026-02-06T23:00:00Z",
                    "resolution_dpi": 150,
                    "file_size_mb": 2.5,
                    "page_count": 3,
                    "created_at": "2026-02-05T23:00:00Z"
                },
                "error": None
            }
        }


class PdfCompilationResponse(BaseModel):
    """Response when triggering PDF compilation."""
    
    task_id: str = Field(..., description="Celery task ID for tracking")
    status: str = Field(..., description="Initial status (pending/processing)")
    message: str = Field(..., description="Human-readable message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "abc123-def456-ghi789",
                "status": "pending",
                "message": "PDF compilation started. Check status at /projects/{id}/pdf/status"
            }
        }


class DownloadUrlResponse(BaseModel):
    """Response containing signed download URL."""
    
    download_url: str = Field(..., description="Time-limited signed URL")
    expires_at: datetime = Field(..., description="URL expiration time")
    file_size_mb: float = Field(..., description="File size in MB")
    page_count: int = Field(..., description="Number of pages")
    
    class Config:
        json_schema_extra = {
            "example": {
                "download_url": "https://cynerza.blob.core.windows.net/comic-pdfs/...?sig=...",
                "expires_at": "2026-02-06T23:00:00Z",
                "file_size_mb": 2.5,
                "page_count": 3
            }
        }
