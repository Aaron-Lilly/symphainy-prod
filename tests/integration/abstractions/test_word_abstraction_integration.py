"""
Integration Tests for Word Processing Abstraction

Tests Word abstraction with Word adapter to verify Layer 1 → Layer 0 integration.
"""

import pytest
from symphainy_platform.foundations.public_works.adapters.word_adapter import WordProcessingAdapter
from symphainy_platform.foundations.public_works.abstractions.word_processing_abstraction import WordProcessingAbstraction
from symphainy_platform.foundations.public_works.protocols.file_parsing_protocol import FileParsingRequest
from tests.fixtures.mock_state_surface import MockStateSurface, mock_state_surface


@pytest.fixture
def word_adapter():
    """Create Word adapter instance."""
    return WordProcessingAdapter()


@pytest.fixture
def word_abstraction(word_adapter, mock_state_surface):
    """Create Word abstraction with adapter and State Surface."""
    return WordProcessingAbstraction(
        word_adapter=word_adapter,
        state_surface=mock_state_surface
    )


@pytest.mark.asyncio
async def test_word_abstraction_initialization(word_abstraction):
    """Test that Word abstraction initializes correctly."""
    assert word_abstraction is not None
    assert word_abstraction.word_adapter is not None
    assert word_abstraction.state_surface is not None


@pytest.mark.asyncio
async def test_word_abstraction_requires_adapter(mock_state_surface):
    """Test that Word abstraction fails fast when adapter is missing."""
    abstraction = WordProcessingAbstraction(
        word_adapter=None,
        state_surface=mock_state_surface
    )
    
    # Store test file
    mock_state_surface.store_file_data(
        "file:test:session:word001",
        b"dummy",
        metadata={"filename": "test.docx", "file_type": "word"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:word001",
        filename="test.docx",
        state_surface=mock_state_surface
    )
    
    result = await abstraction.parse_file(request)
    
    assert result.success is False
    assert "Word adapter is required" in result.error or "adapter" in result.error.lower()


@pytest.mark.asyncio
@pytest.mark.skipif(
    not pytest.importorskip("docx", reason="python-docx not available"),
    reason="python-docx not available"
)
async def test_word_abstraction_parse_file_integration(word_abstraction, mock_state_surface):
    """Test Word abstraction parses file using adapter."""
    if not word_abstraction.word_adapter.docx_available:
        pytest.skip("python-docx not available")
    
    # Create simple Word document
    from docx import Document
    import io
    
    doc = Document()
    doc.add_paragraph("Test paragraph")
    
    docx_buffer = io.BytesIO()
    doc.save(docx_buffer)
    docx_data = docx_buffer.getvalue()
    
    mock_state_surface.store_file_data(
        "file:test:session:word001",
        docx_data,
        metadata={"filename": "test.docx", "file_type": "word"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:word001",
        filename="test.docx",
        state_surface=mock_state_surface
    )
    
    result = await word_abstraction.parse_file(request)
    
    assert result.success is True
    assert result.text_content is not None
    assert "Test" in result.text_content or "test" in result.text_content.lower()
    assert result.structured_data is not None


@pytest.mark.asyncio
async def test_word_abstraction_handles_missing_file(word_abstraction, mock_state_surface):
    """Test Word abstraction handles missing file gracefully."""
    request = FileParsingRequest(
        file_reference="file:test:session:missing",
        filename="missing.docx",
        state_surface=mock_state_surface
    )
    
    result = await word_abstraction.parse_file(request)
    
    assert result.success is False
    assert "File not found" in result.error
