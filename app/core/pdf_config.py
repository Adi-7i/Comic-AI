"""
PDF Generation Configuration.

Plan-based DPI rules:
- FREE: 72 DPI (screen quality, watermarked)
- PRO: 150 DPI (good quality, watermarked)  
- CREATIVE: 300 DPI (print-ready, no watermark)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from app.models.enums import UserPlan


class PdfSettings(BaseSettings):
    """PDF generation configuration."""
    
    # Resolution settings (DPI - Dots Per Inch)
    LOW_DPI: int = 72       # FREE plan - screen quality
    STANDARD_DPI: int = 150 # PRO plan - good quality
    HIGH_DPI: int = 300     # CREATIVE plan - print-ready
    
    # Page dimensions (inches) - standard comic book size
    PAGE_WIDTH_INCHES: float = 6.625   # Standard comic width
    PAGE_HEIGHT_INCHES: float = 10.25  # Standard comic height
    MARGIN_INCHES: float = 0.5         # Safe margin for printing
    
    # Azure Blob Storage settings for PDFs
    PDF_CONTAINER_NAME: str = "comic-pdfs"
    PDF_SAS_EXPIRY_HOURS: int = 24
    
    # Compression
    ENABLE_PDF_COMPRESSION: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Singleton instance
pdf_settings = PdfSettings()


# Plan to DPI mapping
PLAN_DPI_MAP = {
    UserPlan.FREE: pdf_settings.LOW_DPI,
    UserPlan.PRO: pdf_settings.STANDARD_DPI,
    UserPlan.CREATIVE: pdf_settings.HIGH_DPI,
}


def get_dpi_for_plan(plan: UserPlan) -> int:
    """
    Get DPI resolution for user plan.
    
    Args:
        plan: User's subscription plan
        
    Returns:
        DPI value (72/150/300)
    """
    return PLAN_DPI_MAP.get(plan, pdf_settings.STANDARD_DPI)
