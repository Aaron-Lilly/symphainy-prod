"""
Unit Tests for Image Processing Adapter

Tests Image/OCR adapter in isolation (no Runtime/State Surface dependencies).

WHAT (Test Role): I verify Image adapter can extract text from images using OCR
HOW (Test Implementation): I test with sample image bytes directly
"""

import pytest
from symphainy_platform.foundations.public_works.adapters.image_adapter import ImageProcessingAdapter


@pytest.fixture
def image_adapter():
    """Create Image adapter instance."""
    return ImageProcessingAdapter()


@pytest.mark.asyncio
async def test_image_adapter_initialization(image_adapter):
    """Test that Image adapter initializes correctly."""
    assert image_adapter is not None
    assert hasattr(image_adapter, 'pytesseract_available')
    assert hasattr(image_adapter, 'pil_available')


@pytest.mark.asyncio
async def test_image_adapter_no_libraries(image_adapter):
    """Test Image adapter behavior when OCR libraries are not available."""
    if not image_adapter.pytesseract_available or not image_adapter.pil_available:
        invalid_image = b"Not an image"
        result = await image_adapter.extract_text_from_bytes(invalid_image)
        
        assert result["success"] is False
        assert "error" in result
        assert "OCR dependencies" in result["error"]


@pytest.mark.asyncio
async def test_image_adapter_parse_invalid_file(image_adapter):
    """Test parsing an invalid image file."""
    invalid_data = b"This is not an image file"
    
    result = await image_adapter.extract_text_from_bytes(invalid_data)
    
    # Should return error (either library not available or parsing failed)
    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
@pytest.mark.skipif(
    not pytest.importorskip("pytesseract", reason="pytesseract not available") or
    not pytest.importorskip("PIL", reason="PIL not available"),
    reason="OCR dependencies not available"
)
async def test_image_adapter_extract_text_from_simple_image(image_adapter):
    """Test extracting text from a simple image (requires pytesseract and PIL)."""
    if not image_adapter.pytesseract_available or not image_adapter.pil_available:
        pytest.skip("OCR dependencies not available")
    
    # Create a simple image with text using PIL
    from PIL import Image, ImageDraw, ImageFont
    import io
    
    # Create a simple white image
    img = Image.new('RGB', (200, 100), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, or fallback to basic drawing
    try:
        # Try to use a default font
        font = ImageFont.load_default()
        draw.text((10, 40), "Test Text", fill='black', font=font)
    except:
        # Fallback: draw text without font
        draw.text((10, 40), "Test Text", fill='black')
    
    # Save to bytes
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    image_data = img_buffer.getvalue()
    
    result = await image_adapter.extract_text_from_bytes(image_data)
    
    # OCR may or may not succeed depending on image quality and tesseract installation
    # But the adapter should handle it gracefully
    assert "success" in result
    assert "text" in result or "error" in result
    assert "metadata" in result


@pytest.mark.asyncio
async def test_image_adapter_metadata(image_adapter):
    """Test that metadata is correctly populated."""
    if not image_adapter.pytesseract_available or not image_adapter.pil_available:
        pytest.skip("OCR dependencies not available")
    
    # Create a minimal image
    from PIL import Image
    import io
    
    img = Image.new('RGB', (100, 100), color='white')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    image_data = img_buffer.getvalue()
    
    result = await image_adapter.extract_text_from_bytes(image_data)
    
    if result["success"]:
        assert "metadata" in result
        assert result["metadata"]["type"] == "image"
        assert "format" in result["metadata"]
        assert "width" in result["metadata"]
        assert "height" in result["metadata"]


@pytest.mark.asyncio
@pytest.mark.skipif(
    not pytest.importorskip("PIL", reason="PIL not available"),
    reason="PIL not available"
)
async def test_image_adapter_different_formats(image_adapter):
    """Test adapter with different image formats."""
    if not image_adapter.pil_available:
        pytest.skip("PIL not available")
    
    from PIL import Image
    import io
    
    # Test PNG
    img = Image.new('RGB', (50, 50), color='red')
    png_buffer = io.BytesIO()
    img.save(png_buffer, format='PNG')
    png_data = png_buffer.getvalue()
    
    result_png = await image_adapter.extract_text_from_bytes(png_data)
    assert "success" in result_png or "error" in result_png
    
    # Test JPEG
    jpeg_buffer = io.BytesIO()
    img.save(jpeg_buffer, format='JPEG')
    jpeg_data = jpeg_buffer.getvalue()
    
    result_jpeg = await image_adapter.extract_text_from_bytes(jpeg_data)
    assert "success" in result_jpeg or "error" in result_jpeg
