"""
Watermark Service.

Applies non-removable watermarks to comic images.

Rules by Plan:
- FREE: Strong watermark (mandatory)
- PRO: Standard watermark (required)
- CREATIVE: No watermark
"""

import logging
from typing import Optional
from io import BytesIO

from app.models.enums import UserPlan


logger = logging.getLogger(__name__)


class WatermarkService:
    """
    Service for applying watermarks to comic images.
    
    Watermarks are burned into the image (non-removable).
    Placement is deterministic for consistency.
    """
    
    # Watermark text for branding
    WATERMARK_TEXT = "Comic AI"
    
    # Watermark settings by strength
    WATERMARK_OPACITY = {
        "strong": 180,   # FREE plan - very visible
        "standard": 120, # PRO plan - visible but less intrusive
    }
    
    async def apply_watermark(
        self,
        image_bytes: bytes,
        plan: UserPlan,
        strength: Optional[str] = None
    ) -> bytes:
        """
        Apply watermark to image based on plan.
        
        Args:
            image_bytes: Original image bytes
            plan: User's plan tier
            strength: Override strength ("strong" or "standard")
            
        Returns:
            Watermarked image bytes (or original if CREATIVE)
        """
        # CREATIVE plan gets no watermark
        if plan == UserPlan.CREATIVE:
            logger.debug("Skipping watermark for CREATIVE plan")
            return image_bytes
        
        # Determine strength from plan
        if strength is None:
            strength = "strong" if plan == UserPlan.FREE else "standard"
        
        try:
            return await self._apply_text_watermark(image_bytes, strength)
        except Exception as e:
            logger.error(f"Watermark failed: {type(e).__name__} - returning original")
            # Return original rather than fail the entire generation
            return image_bytes
    
    async def _apply_text_watermark(
        self,
        image_bytes: bytes,
        strength: str
    ) -> bytes:
        """
        Apply text watermark with specified strength.
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            logger.warning("Pillow not installed - watermark skipped")
            return image_bytes
        
        # Load image
        img = Image.open(BytesIO(image_bytes))
        
        # Ensure RGBA for alpha compositing
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        
        # Create watermark overlay
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Get opacity from strength
        opacity = self.WATERMARK_OPACITY.get(strength, 120)
        
        # Calculate font size based on image dimensions
        font_size = max(20, min(img.width, img.height) // 15)
        
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                font_size
            )
        except:
            font = ImageFont.load_default()
        
        # Calculate text size and position (bottom-right corner)
        text = self.WATERMARK_TEXT
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Deterministic placement: bottom-right with padding
        padding = 20
        x = img.width - text_width - padding
        y = img.height - text_height - padding
        
        # Draw shadow for visibility on any background
        shadow_offset = 2
        draw.text(
            (x + shadow_offset, y + shadow_offset),
            text,
            font=font,
            fill=(0, 0, 0, opacity)
        )
        
        # Draw main watermark text
        draw.text(
            (x, y),
            text,
            font=font,
            fill=(255, 255, 255, opacity)
        )
        
        # Add diagonal watermark for strong mode (FREE plan)
        if strength == "strong":
            self._add_diagonal_watermark(draw, img.size, font_size // 2, opacity // 2)
        
        # Composite overlay onto image
        watermarked = Image.alpha_composite(img, overlay)
        
        # Convert back to RGB for PNG/JPEG output
        if watermarked.mode == "RGBA":
            # Create white background for JPEG compatibility
            background = Image.new("RGB", watermarked.size, (255, 255, 255))
            background.paste(watermarked, mask=watermarked.split()[3])
            watermarked = background
        
        # Save to bytes
        buffer = BytesIO()
        watermarked.save(buffer, format="PNG")
        return buffer.getvalue()
    
    def _add_diagonal_watermark(
        self,
        draw: "ImageDraw.Draw",
        size: tuple,
        font_size: int,
        opacity: int
    ):
        """
        Add repeating diagonal watermark pattern for FREE plan.
        """
        try:
            from PIL import ImageFont
            try:
                font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    font_size
                )
            except:
                font = ImageFont.load_default()
        except ImportError:
            return
        
        width, height = size
        text = "Comic AI Demo"
        
        # Calculate spacing
        spacing_x = 300
        spacing_y = 200
        
        # Draw diagonal pattern
        for y in range(-height, height, spacing_y):
            for x in range(-width, width, spacing_x):
                # Offset every other row
                offset = (y // spacing_y) % 2 * (spacing_x // 2)
                draw.text(
                    (x + offset, y),
                    text,
                    font=font,
                    fill=(128, 128, 128, opacity)
                )
    
    def should_watermark(self, plan: UserPlan) -> bool:
        """
        Check if plan requires watermark.
        """
        return plan != UserPlan.CREATIVE


# Singleton instance
watermark_service = WatermarkService()
