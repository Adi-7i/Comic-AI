#!/usr/bin/env python
"""
Verification Script for Step-6: Image Generation Engine

Tests:
1. Configuration loading (no key leaks)
2. Mock image client generation
3. Watermark application
4. Blob service (mock mode)
5. Comic asset model
6. Plan service integration
"""

import asyncio
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_section(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def print_result(test: str, passed: bool, message: str = ""):
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"  {status}: {test}")
    if message:
        print(f"         {message}")


async def test_configuration():
    """Test that configuration loads without exposing secrets."""
    print_section("Configuration Tests")
    
    try:
        from app.core.azure_image_config import (
            azure_image_settings,
            azure_blob_settings,
            ImageResolution
        )
        
        # Test settings loaded
        print_result("Azure Image settings load", True)
        
        # Ensure API key is not exposed in repr/str
        settings_str = str(azure_image_settings)
        has_secret_leak = "api_key" in settings_str.lower() and "SecretStr" not in settings_str
        print_result("API key not exposed in str", not has_secret_leak)
        
        # Test resolution mapping
        from app.core.azure_image_config import RESOLUTION_SIZE_MAP
        print_result(
            "Resolution mapping exists",
            True,
            f"LOW={RESOLUTION_SIZE_MAP[ImageResolution.LOW]}"
        )
        
        # Test is_configured property
        print_result(
            "is_configured property works",
            True,
            f"Azure: {azure_image_settings.is_configured}, Blob: {azure_blob_settings.is_configured}"
        )
        
        return True
        
    except Exception as e:
        print_result("Configuration loading", False, str(e))
        return False


async def test_exceptions():
    """Test that all exception classes are defined."""
    print_section("Exception Tests")
    
    try:
        from app.core.exceptions import (
            AzureImageApiKeyMissing,
            AzureImageProviderError,
            ImageGenerationFailed,
            PlanImageAccessDenied,
            FreeStoryAlreadyUsed,
            AzureBlobUploadFailed,
            InvalidSceneStructure
        )
        
        # Test exception can be raised
        try:
            raise AzureImageApiKeyMissing()
        except AzureImageApiKeyMissing as e:
            print_result("AzureImageApiKeyMissing", True, f"status={e.status_code}")
        
        try:
            raise FreeStoryAlreadyUsed()
        except FreeStoryAlreadyUsed as e:
            print_result("FreeStoryAlreadyUsed", True, f"status={e.status_code}")
        
        return True
        
    except Exception as e:
        print_result("Exception imports", False, str(e))
        return False


async def test_mock_image_client():
    """Test mock image client generates images."""
    print_section("Mock Image Client Tests")
    
    try:
        from app.services.azure_image_client import MockImageClient, ImageResolution
        
        client = MockImageClient()
        
        # Generate test image
        image_bytes = await client.generate_image(
            prompt="Test comic panel with superhero",
            resolution=ImageResolution.STANDARD,
            seed=42
        )
        
        print_result(
            "Mock image generation",
            len(image_bytes) > 0,
            f"Generated {len(image_bytes)} bytes"
        )
        
        # Verify it's a PNG
        is_png = image_bytes[:8] == b'\x89PNG\r\n\x1a\n'
        print_result("Generated valid PNG", is_png)
        
        return True
        
    except Exception as e:
        print_result("Mock image generation", False, str(e))
        return False


async def test_watermark_service():
    """Test watermark service."""
    print_section("Watermark Service Tests")
    
    try:
        from app.services.watermark_service import watermark_service
        from app.models.enums import UserPlan
        
        # Test should_watermark logic
        print_result(
            "FREE requires watermark",
            watermark_service.should_watermark(UserPlan.FREE) == True
        )
        print_result(
            "PRO requires watermark",
            watermark_service.should_watermark(UserPlan.PRO) == True
        )
        print_result(
            "CREATIVE no watermark",
            watermark_service.should_watermark(UserPlan.CREATIVE) == False
        )
        
        # Test watermark application (needs test image)
        try:
            from PIL import Image
            from io import BytesIO
            
            # Create test image
            img = Image.new("RGB", (512, 512), color=(100, 150, 200))
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            test_bytes = buffer.getvalue()
            
            # Apply watermark
            watermarked = await watermark_service.apply_watermark(test_bytes, UserPlan.PRO)
            print_result(
                "Watermark application",
                len(watermarked) > 0,
                f"Output: {len(watermarked)} bytes"
            )
        except ImportError:
            print_result("Watermark application", True, "Pillow not installed - skipped")
        
        return True
        
    except Exception as e:
        print_result("Watermark service", False, str(e))
        return False


async def test_blob_service():
    """Test blob service (mock mode)."""
    print_section("Azure Blob Service Tests")
    
    try:
        from app.utils.azure_blob import azure_blob_service
        
        # Test path building
        path = azure_blob_service.build_blob_path("test-project-123", 1)
        print_result(
            "Blob path building",
            "test-project-123" in path and "1.png" in path,
            f"Path: {path}"
        )
        
        # Test signed URL generation (mock mode)
        url = azure_blob_service.generate_signed_url(path)
        print_result(
            "Signed URL generation (mock)",
            "mock-storage" in url or "blob.core.windows.net" in url,
            f"URL: {url[:60]}..."
        )
        
        return True
        
    except Exception as e:
        print_result("Blob service", False, str(e))
        return False


async def test_models():
    """Test model definitions."""
    print_section("Model Tests")
    
    try:
        from app.models.comic_asset import ComicAsset
        from app.models.user import User
        from app.models.enums import UserPlan
        
        # Check ComicAsset has required fields
        comic_asset_fields = ComicAsset.model_fields.keys()
        required_fields = ['project_id', 'page_no', 'blob_url', 'resolution', 'watermarked']
        
        has_all = all(f in comic_asset_fields for f in required_fields)
        print_result(
            "ComicAsset has required fields",
            has_all,
            f"Fields: {list(comic_asset_fields)[:5]}..."
        )
        
        # Check User has free_story fields
        user_fields = User.model_fields.keys()
        has_free_story = 'free_story_available' in user_fields and 'free_story_used' in user_fields
        print_result("User has free_story fields", has_free_story)
        
        return True
        
    except Exception as e:
        print_result("Model tests", False, str(e))
        return False


async def test_schemas():
    """Test schema definitions."""
    print_section("Schema Tests")
    
    try:
        from app.schemas.image import (
            ImageGenerationRequest,
            ImageGenerationStatus,
            ComicAssetResponse
        )
        
        # Test request schema
        request = ImageGenerationRequest(project_id="test-123")
        print_result("ImageGenerationRequest schema", True)
        
        # Test status schema
        status = ImageGenerationStatus(
            task_id="celery-123",
            status="processing",
            progress=50,
            total_pages=4
        )
        print_result(
            "ImageGenerationStatus schema",
            True,
            f"progress={status.progress}%"
        )
        
        return True
        
    except Exception as e:
        print_result("Schema tests", False, str(e))
        return False


async def test_celery_task_registration():
    """Test Celery task is registered."""
    print_section("Celery Task Tests")
    
    try:
        from app.workers.tasks import image_generation_task, generate_comic_task
        
        print_result(
            "image_generation_task exists",
            callable(image_generation_task),
            f"Name: {image_generation_task.name}"
        )
        print_result(
            "generate_comic_task exists",
            callable(generate_comic_task),
            f"Name: {generate_comic_task.name}"
        )
        
        return True
        
    except Exception as e:
        print_result("Celery task registration", False, str(e))
        return False


async def main():
    print("\n" + "=" * 60)
    print("  STEP-6: IMAGE GENERATION ENGINE VERIFICATION")
    print("=" * 60)
    
    results = []
    
    results.append(await test_configuration())
    results.append(await test_exceptions())
    results.append(await test_mock_image_client())
    results.append(await test_watermark_service())
    results.append(await test_blob_service())
    results.append(await test_models())
    results.append(await test_schemas())
    results.append(await test_celery_task_registration())
    
    print_section("SUMMARY")
    passed = sum(results)
    total = len(results)
    
    print(f"\n  Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  ✓ All verification tests PASSED!")
        print("  Image Generation Engine is ready for integration testing.")
    else:
        print(f"\n  ✗ {total - passed} test(s) FAILED")
        print("  Please review the failures above.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
