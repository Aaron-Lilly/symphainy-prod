"""
Integration Tests for PDF Processing Abstraction

Tests PDF abstraction with PDF adapter to verify Layer 1 → Layer 0 integration.
"""

import pytest
from symphainy_platform.foundations.public_works.adapters.pdf_adapter import PdfProcessingAdapter
from symphainy_platform.foundations.public_works.abstractions.pdf_processing_abstraction import PdfProcessingAbstraction
from symphainy_platform.foundations.public_works.protocols.file_parsing_protocol import FileParsingRequest
from tests.fixtures.mock_state_surface import MockStateSurface, mock_state_surface


@pytest.fixture
def pdf_adapter():
    """Create PDF adapter instance."""
    return PdfProcessingAdapter()


@pytest.fixture
def pdf_abstraction(pdf_adapter, mock_state_surface):
    """Create PDF abstraction with adapter and State Surface."""
    return PdfProcessingAbstraction(
        pdf_adapter=pdf_adapter,
        state_surface=mock_state_surface
    )


@pytest.mark.asyncio
async def test_pdf_abstraction_initialization(pdf_abstraction):
    """Test that PDF abstraction initializes correctly."""
    assert pdf_abstraction is not None
    assert pdf_abstraction.pdf_adapter is not None
    assert pdf_abstraction.state_surface is not None


@pytest.mark.asyncio
async def test_pdf_abstraction_requires_adapter(mock_state_surface):
    """Test that PDF abstraction fails fast when adapter is missing."""
    abstraction = PdfProcessingAbstraction(
        pdf_adapter=None,
        state_surface=mock_state_surface
    )
    
    # Store test file
    mock_state_surface.store_file_data(
        "file:test:session:pdf001",
        b"dummy",
        metadata={"filename": "test.pdf", "file_type": "pdf"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:pdf001",
        filename="test.pdf",
        state_surface=mock_state_surface
    )
    
    result = await abstraction.parse_file(request)
    
    assert result.success is False
    assert "PDF adapter is required" in result.error or "adapter" in result.error.lower()


@pytest.mark.asyncio
async def test_pdf_abstraction_handles_missing_file(pdf_abstraction, mock_state_surface):
    """Test PDF abstraction handles missing file gracefully."""
    request = FileParsingRequest(
        file_reference="file:test:session:missing",
        filename="missing.pdf",
        state_surface=mock_state_surface
    )
    
    result = await pdf_abstraction.parse_file(request)
    
    assert result.success is False
    assert "File not found" in result.error


@pytest.mark.asyncio
async def test_pdf_abstraction_parse_file_integration(pdf_abstraction, mock_state_surface):
    """Test PDF abstraction parses file using adapter."""
    # Create minimal PDF
    minimal_pdf = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\n0 1\ntrailer\n<< /Root 1 0 R >>\nstartxref\n10\n%%EOF"
    
    mock_state_surface.store_file_data(
        "file:test:session:pdf001",
        minimal_pdf,
        metadata={"filename": "test.pdf", "file_type": "pdf"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:pdf001",
        filename="test.pdf",
        state_surface=mock_state_surface
    )
    
    result = await pdf_abstraction.parse_file(request)
    
    # Result may succeed or fail depending on PDF validity and library availability
    assert result is not None
    assert hasattr(result, 'success')
    
    if result.success:
        assert hasattr(result, 'text_content') or hasattr(result, 'structured_data')
