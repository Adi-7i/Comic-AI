"""
Comic Engine - Page Generation Orchestrator.

Handles:
- Loading scenes for a page
- Building image prompts from narrative
- Controlling image generation flow
- Layout composition (4-panel grid)
- Watermark application
- Asset creation
"""

import logging
from typing import List, Optional
from datetime import datetime, timezone
from io import BytesIO

from beanie import PydanticObjectId

from app.models.project import Project
from app.models.scene import Scene
from app.models.user import User
from app.models.comic_asset import ComicAsset
from app.models.enums import UserPlan
from app.core.azure_image_config import (
    azure_image_settings,
    ImageResolution
)
from app.core.exceptions import InvalidSceneStructure
from app.services.azure_image_client import get_image_client, ImageProviderProtocol
from app.services.watermark_service import watermark_service
from app.utils.azure_blob import azure_blob_service


logger = logging.getLogger(__name__)


class ComicEngine:
    """
    Comic page generation orchestrator.
    
    Coordinates image generation, layout, watermarking, and storage.
    """
    
    # Plan to resolution mapping
    PLAN_RESOLUTION_MAP = {
        UserPlan.FREE: ImageResolution.LOW,
        UserPlan.PRO: ImageResolution.STANDARD,
        UserPlan.CREATIVE: ImageResolution.HIGH,
    }
    
    def __init__(self, image_client: Optional[ImageProviderProtocol] = None):
        """
        Initialize comic engine.
        
        Args:
            image_client: Optional image client override (for testing)
        """
        self._image_client = image_client
    
    def _get_image_client(self) -> ImageProviderProtocol:
        """Get or create image client."""
        if self._image_client is None:
            self._image_client = get_image_client()
        return self._image_client
    
    async def generate_page(
        self,
        project: Project,
        page_no: int,
        user: User,
        seed: Optional[int] = None
    ) -> ComicAsset:
        """
        Generate a complete comic page with all 4 panels.
        
        Args:
            project: Project being generated
            page_no: Page number to generate
            user: User requesting generation
            seed: Random seed for reproducibility
            
        Returns:
            ComicAsset with storage metadata
            
        Raises:
            InvalidSceneStructure: If page doesn't have exactly 4 panels
        """
        plan = project.plan_snapshot
        resolution = self.PLAN_RESOLUTION_MAP.get(plan, ImageResolution.STANDARD)
        
        # 1. Load scenes for this page
        scenes = await self._load_page_scenes(project.id, page_no)
        
        if len(scenes) != azure_image_settings.PANELS_PER_PAGE:
            raise InvalidSceneStructure(
                detail=f"Page {page_no} requires exactly 4 panels, found {len(scenes)}"
            )
        
        # 2. Generate panels
        logger.info(f"Generating page {page_no} for project {project.id}")
        panel_images = []
        
        image_client = self._get_image_client()
        
        for scene in scenes:
            prompt = self._build_panel_prompt(scene, project.config)
            
            try:
                panel_bytes = await image_client.generate_image(
                    prompt=prompt,
                    resolution=resolution,
                    seed=seed
                )
                panel_images.append(panel_bytes)
                
                # Update scene with prompt used
                scene.prompt_used = prompt
                await scene.save()
                
            except Exception as e:
                logger.error(f"Panel {scene.panel_no} generation failed: {e}")
                raise
        
        # 3. Compose page layout
        page_image = await self._compose_page_layout(panel_images)
        
        # 4. Apply watermark if required
        if watermark_service.should_watermark(plan):
            page_image = await watermark_service.apply_watermark(
                page_image,
                plan
            )
            watermarked = True
        else:
            watermarked = False
        
        # 5. Upload to blob storage
        blob_path = azure_blob_service.build_blob_path(str(project.id), page_no)
        await azure_blob_service.upload_image(page_image, blob_path)
        
        # 6. Generate signed URL
        blob_url = azure_blob_service.generate_signed_url(blob_path)
        url_expires_at = azure_blob_service.get_url_expiry()
        
        # 7. Create/update asset record
        asset = await self._upsert_asset(
            project_id=project.id,
            page_no=page_no,
            blob_url=blob_url,
            blob_path=blob_path,
            resolution=resolution.value,
            plan_snapshot=plan,
            watermarked=watermarked,
            seed=seed,
            url_expires_at=url_expires_at
        )
        
        logger.info(f"Page {page_no} generated: {blob_path}")
        return asset
    
    async def _load_page_scenes(
        self,
        project_id: PydanticObjectId,
        page_no: int
    ) -> List[Scene]:
        """
        Load all scenes for a page, sorted by panel number.
        """
        scenes = await Scene.find(
            Scene.project_id == project_id,
            Scene.page_no == page_no,
        ).sort(+Scene.panel_no).to_list()
        
        return scenes
    
    def _build_panel_prompt(
        self,
        scene: Scene,
        project_config: dict
    ) -> str:
        """
        Build image generation prompt from scene narrative.
        
        Combines:
        - Scene action/setting
        - Character descriptions
        - Project style preferences
        """
        narrative = scene.narrative_text
        
        # Extract narrative components
        action = narrative.get("action", "")
        setting = narrative.get("setting", "")
        dialogue = narrative.get("dialogue", [])
        
        # Build base prompt
        parts = []
        
        # Add style prefix from project config
        style = project_config.get("style", "manga")
        parts.append(f"Comic panel in {style} style.")
        
        # Add setting
        if setting:
            parts.append(f"Setting: {setting}.")
        
        # Add action
        if action:
            parts.append(f"Action: {action}.")
        
        # Note about dialogue (not rendered in image, just context)
        if dialogue:
            # We could add visual hints about who's speaking
            parts.append("Leave space for speech bubbles.")
        
        # Add quality modifiers
        parts.append("High quality, detailed, dynamic composition.")
        
        # Combine into single prompt
        prompt = " ".join(parts)
        
        # Ensure reasonable length
        if len(prompt) > 1000:
            prompt = prompt[:997] + "..."
        
        return prompt
    
    async def _compose_page_layout(
        self,
        panel_images: List[bytes]
    ) -> bytes:
        """
        Compose 4 panels into a single page with fixed grid layout.
        
        Layout:
        +-----+-----+
        |  1  |  2  |
        +-----+-----+
        |  3  |  4  |
        +-----+-----+
        
        With safe margins for text bubbles.
        """
        try:
            from PIL import Image
        except ImportError:
            logger.warning("Pillow not installed - returning first panel as page")
            return panel_images[0] if panel_images else b""
        
        page_width = azure_image_settings.PAGE_WIDTH_PX
        page_height = azure_image_settings.PAGE_HEIGHT_PX
        spacing = azure_image_settings.PANEL_SPACING_PX
        margin = azure_image_settings.SAFE_MARGIN_PX
        
        # Calculate panel dimensions
        panel_width = (page_width - 2 * margin - spacing) // 2
        panel_height = (page_height - 2 * margin - spacing) // 2
        
        # Create blank page
        page = Image.new("RGB", (page_width, page_height), color=(255, 255, 255))
        
        # Panel positions (2x2 grid)
        positions = [
            (margin, margin),                                    # Top-left
            (margin + panel_width + spacing, margin),           # Top-right
            (margin, margin + panel_height + spacing),          # Bottom-left
            (margin + panel_width + spacing, margin + panel_height + spacing),  # Bottom-right
        ]
        
        # Place each panel
        for idx, (panel_bytes, pos) in enumerate(zip(panel_images, positions)):
            try:
                panel_img = Image.open(BytesIO(panel_bytes))
                
                # Resize to fit panel space
                panel_img = panel_img.resize(
                    (panel_width, panel_height),
                    Image.Resampling.LANCZOS
                )
                
                # Paste onto page
                page.paste(panel_img, pos)
                
            except Exception as e:
                logger.error(f"Failed to place panel {idx + 1}: {e}")
                # Draw placeholder rectangle
                from PIL import ImageDraw
                draw = ImageDraw.Draw(page)
                draw.rectangle(
                    [pos, (pos[0] + panel_width, pos[1] + panel_height)],
                    outline=(200, 200, 200),
                    width=2
                )
        
        # Add panel borders
        from PIL import ImageDraw
        draw = ImageDraw.Draw(page)
        for pos in positions:
            draw.rectangle(
                [pos, (pos[0] + panel_width, pos[1] + panel_height)],
                outline=(0, 0, 0),
                width=3
            )
        
        # Convert to bytes
        buffer = BytesIO()
        page.save(buffer, format="PNG")
        return buffer.getvalue()
    
    async def _upsert_asset(
        self,
        project_id: PydanticObjectId,
        page_no: int,
        blob_url: str,
        blob_path: str,
        resolution: str,
        plan_snapshot: UserPlan,
        watermarked: bool,
        seed: Optional[int],
        url_expires_at: datetime
    ) -> ComicAsset:
        """
        Create or update comic asset record.
        """
        # Check for existing asset
        existing = await ComicAsset.find_one(
            ComicAsset.project_id == project_id,
            ComicAsset.page_no == page_no
        )
        
        if existing:
            existing.blob_url = blob_url
            existing.blob_path = blob_path
            existing.resolution = resolution
            existing.plan_snapshot = plan_snapshot
            existing.watermarked = watermarked
            existing.seed = seed
            existing.url_expires_at = url_expires_at
            existing.updated_at = datetime.now(timezone.utc)
            await existing.save()
            return existing
        
        # Create new asset
        asset = ComicAsset(
            project_id=project_id,
            page_no=page_no,
            blob_url=blob_url,
            blob_path=blob_path,
            resolution=resolution,
            plan_snapshot=plan_snapshot,
            watermarked=watermarked,
            seed=seed,
            url_expires_at=url_expires_at
        )
        await asset.save()
        return asset


# Singleton instance
comic_engine = ComicEngine()
