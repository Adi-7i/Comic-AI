"""
PDF Builder Utility - Low-level PDF construction.

Uses reportlab to create PDFs from comic page images.
Handles:
- One page per comic image
- Aspect ratio preservation
- Metadata embedding
- Deterministic output
"""

import logging
from pathlib import Path
from typing import List, Dict
from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

from app.core.pdf_config import pdf_settings


logger = logging.getLogger(__name__)


def create_comic_pdf(
    images: List[bytes],
    output_path: str,
    dpi: int,
    metadata: dict
) -> int:
    """
    Create PDF from comic page images.
    
    Args:
        images: List of image bytes (one per page)
        output_path: Where to save PDF
        dpi: Resolution (72/150/300)
        metadata: {project_id, author, plan_snapshot, title}
    
    Returns:
        File size in bytes
        
    Raises:
        Exception: If PDF creation fails
    """
    try:
        # Calculate page size in points (72 points = 1 inch)
        page_width_pts = pdf_settings.PAGE_WIDTH_INCHES * 72
        page_height_pts = pdf_settings.PAGE_HEIGHT_INCHES * 72
        margin_pts = pdf_settings.MARGIN_INCHES * 72
        
        # Create PDF canvas
        c = canvas.Canvas(
            output_path,
            pagesize=(page_width_pts, page_height_pts)
        )
        
        # Embed metadata
        _set_pdf_metadata(c, metadata)
        
        # Add each image as a page
        for idx, image_bytes in enumerate(images):
            logger.debug(f"Adding page {idx + 1}/{len(images)}")
            
            # Load image
            img = Image.open(BytesIO(image_bytes))
            
            # Calculate image dimensions to fit page with margins
            available_width = page_width_pts - (2 * margin_pts)
            available_height = page_height_pts - (2 * margin_pts)
            
            # Preserve aspect ratio
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height
            
            if aspect_ratio > (available_width / available_height):
                # Width is constraining dimension
                final_width = available_width
                final_height = final_width / aspect_ratio
            else:
                # Height is constraining dimension
                final_height = available_height
                final_width = final_height * aspect_ratio
            
            # Center image on page
            x = (page_width_pts - final_width) / 2
            y = (page_height_pts - final_height) / 2
            
            # Draw image using ImageReader for better quality
            img_reader = ImageReader(BytesIO(image_bytes))
            c.drawImage(
                img_reader,
                x, y,
                width=final_width,
                height=final_height,
                preserveAspectRatio=True
            )
            
            # Add page number footer (small, centered)
            _add_page_number(c, idx + 1, len(images), page_width_pts, margin_pts)
            
            # Finish page
            c.showPage()
        
        # Save PDF
        c.save()
        
        # Get file size
        file_size = Path(output_path).stat().st_size
        logger.info(f"PDF created: {file_size} bytes, {len(images)} pages, {dpi} DPI")
        
        return file_size
        
    except Exception as e:
        logger.error(f"PDF creation failed: {e}")
        raise


def _set_pdf_metadata(c: canvas.Canvas, metadata: dict):
    """
    Embed metadata into PDF.
    
    Args:
        c: ReportLab canvas
        metadata: Metadata dictionary
    """
    c.setAuthor(metadata.get("author", "Comic AI"))
    c.setTitle(metadata.get("title", "Comic Book"))
    c.setSubject(f"Comic Project {metadata.get('project_id', 'Unknown')}")
    c.setKeywords([
        "comic",
        "ai-generated",
        metadata.get("plan_snapshot", "")
    ])
    c.setCreator("Comic AI Platform")
    c.setProducer("Comic AI - reportlab")


def _add_page_number(
    c: canvas.Canvas,
    page_num: int,
    total_pages: int,
    page_width_pts: float,
    margin_pts: float
):
    """
    Add page number to bottom center of page.
    
    Args:
        c: ReportLab canvas
        page_num: Current page number (1-indexed)
        total_pages: Total number of pages
        page_width_pts: Page width in points
        margin_pts: Margin in points
    """
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(0.5, 0.5, 0.5)  # Gray color
    text = f"{page_num} of {total_pages}"
    text_width = c.stringWidth(text, "Helvetica", 8)
    c.drawString(
        (page_width_pts - text_width) / 2,
        margin_pts / 2,
        text
    )


def estimate_pdf_size(page_count: int, avg_image_size_bytes: int) -> int:
    """
    Estimate PDF file size.
    
    Args:
        page_count: Number of pages
        avg_image_size_bytes: Average image size
    
    Returns:
        Estimated file size in bytes
    """
    # PDF overhead + compressed images
    overhead = 10000  # ~10KB overhead
    compression_ratio = 0.9  # Slight compression
    
    estimated = overhead + (page_count * avg_image_size_bytes * compression_ratio)
    return int(estimated)
