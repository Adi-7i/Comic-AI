"""
Delivery Guards - Dependency injection for PDF delivery endpoints.

Provides reusable route guards for:
- Project ownership validation
- PDF asset existence checking
"""

from fastapi import Depends

from app.models.project import Project
from app.models.user import User
from app.models.pdf_asset import PdfAsset
from app.core.exceptions import AssetMissing
from app.api.v1.dependencies.permissions import get_project_or_404


async def get_pdf_asset_for_project(
    project: Project = Depends(get_project_or_404)
) -> PdfAsset:
    """
    Load PDF asset for user's project.
    
    Args:
        project: Project (validated for ownership via get_project_or_404)
        
    Returns:
        PdfAsset if exists
        
    Raises:
        AssetMissing: If PDF not generated yet
    """
    pdf_asset = await PdfAsset.find_one(
        PdfAsset.project_id == project.id
    )
    
    if not pdf_asset:
        raise AssetMissing(
            detail="PDF not generated yet. Generate PDF first."
        )
    
    return pdf_asset
