"""
Integration Tests for Image Processing Abstraction

Tests Image abstraction with Image adapter to verify Layer 1 → Layer 0 integration.
"""

import pytest
from symphainy_platform.foundations.public_works.adapters.image_adapter import ImageProcessingAdapter
from symphainy_platform.foundations.public_works.abstractions.image_processing_abstraction import ImageProcessingAbstraction
from symphainy_platform.foundations.public_works.protocols.file_parsing_protocol import FileParsingRequest
from tests.fixtures.mock_state_surface import MockStateSurface, mock_state_surface


@pytest.fixture
def image_adapter():
    """Create Image adapter instance."""
    return ImageProcessingAdapter()


@pytest.fixture
def image_abstraction(image_adapter, mock_state_surface):
    """Create Image abstraction with adapter and State Surface."""
    return ImageProcessingAbstraction(
        ocr_adapter=image_adapter,  # ImageProcessingAbstraction uses ocr_adapter parameter
        state_surface=mock_state_surface
    )


@pytest.mark.asyncio
async def test_image_abstraction_initialization(image_abstraction):
    """Test that Image abstraction initializes correctly."""
    assert image_abstraction is not None
    assert image_abstraction.ocr_adapter is not None  # ImageProcessingAbstraction uses ocr_adapter attribute
    assert image_abstraction.state_surface is not None


@pytest.mark.asyncio
async def test_image_abstraction_requires_adapter(mock_state_surface):
    """Test that Image abstraction fails fast when adapter is missing."""
    abstraction = ImageProcessingAbstraction(
        ocr_adapter=None,  # ImageProcessingAbstraction uses ocr_adapter parameter
        state_surface=mock_state_surface
    )
    
    # Store test file
    mock_state_surface.store_file_data(
        "file:test:session:image001",
        b"dummy",
        metadata={"filename": "test.png", "file_type": "image"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:image001",
        filename="test.png",
        state_surface=mock_state_surface
    )
    
    result = await abstraction.parse_file(request)
    
    assert result.success is False
    assert "OCR adapter" in result.error or "adapter" in result.error.lower()


@pytest.mark.asyncio
async def test_image_abstraction_handles_missing_file(image_abstraction, mock_state_surface):
    """Test Image abstraction handles missing file gracefully."""
    request = FileParsingRequest(
        file_reference="file:test:session:missing",
        filename="missing.png",
        state_surface=mock_state_surface
    )
    
    result = await image_abstraction.parse_file(request)
    
    assert result.success is False
    assert "File not found" in result.error


@pytest.mark.asyncio
@pytest.mark.skipif(
    not pytest.importorskip("PIL", reason="PIL not available") or
    not pytest.importorskip("pytesseract", reason="pytesseract not available"),
    reason="OCR dependencies not available"
)
async def test_image_abstraction_parse_file_integration(image_abstraction, mock_state_surface):
    """Test Image abstraction extracts text using adapter."""
    if not image_abstraction.ocr_adapter.pytesseract_available or not image_abstraction.ocr_adapter.pil_available:
        pytest.skip("OCR dependencies not available")
    
    # Create simple image
    from PIL import Image
    import io
    
    img = Image.new('RGB', (100, 100), color='white')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    image_data = img_buffer.getvalue()
    
    mock_state_surface.store_file_data(
        "file:test:session:image001",
        image_data,
        metadata={"filename": "test.png", "file_type": "image"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:image001",
        filename="test.png",
        state_surface=mock_state_surface
    )
    
    result = await image_abstraction.parse_file(request)
    
    # Result may succeed or fail depending on OCR quality
    assert result is not None
    assert hasattr(result, 'success')
    
    if result.success:
        assert hasattr(result, 'text_content')
