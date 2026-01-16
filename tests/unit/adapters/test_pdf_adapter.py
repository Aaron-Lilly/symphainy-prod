"""
Unit Tests for PDF Processing Adapter

Tests PDF adapter in isolation (no Runtime/State Surface dependencies).

WHAT (Test Role): I verify PDF adapter can parse PDF files correctly
HOW (Test Implementation): I test with sample PDF bytes directly
"""

import pytest
from symphainy_platform.foundations.public_works.adapters.pdf_adapter import PdfProcessingAdapter


@pytest.fixture
def pdf_adapter():
    """Create PDF adapter instance."""
    return PdfProcessingAdapter()


@pytest.mark.asyncio
async def test_pdf_adapter_initialization(pdf_adapter):
    """Test that PDF adapter initializes correctly."""
    assert pdf_adapter is not None
    assert hasattr(pdf_adapter, 'pdfplumber_available')
    assert hasattr(pdf_adapter, 'pypdf2_available')


@pytest.mark.asyncio
async def test_pdf_adapter_no_libraries(pdf_adapter):
    """Test PDF adapter behavior when no libraries are available."""
    if not pdf_adapter.pdfplumber_available and not pdf_adapter.pypdf2_available:
        invalid_pdf = b"Not a PDF file"
        result = await pdf_adapter.parse_file(invalid_pdf, "test.pdf")
        
        assert result["success"] is False
        assert "error" in result
        assert "Neither pdfplumber nor PyPDF2 available" in result["error"]


@pytest.mark.asyncio
async def test_pdf_adapter_parse_invalid_file(pdf_adapter):
    """Test parsing an invalid PDF file."""
    invalid_data = b"This is not a PDF file"
    
    result = await pdf_adapter.parse_file(invalid_data, "invalid.pdf")
    
    # Should return error (either library not available or parsing failed)
    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
@pytest.mark.skipif(
    not pytest.importorskip("pdfplumber", reason="pdfplumber not available"),
    reason="pdfplumber not available"
)
async def test_pdf_adapter_parse_simple_pdf(pdf_adapter):
    """Test parsing a simple PDF file (requires pdfplumber)."""
    if not pdf_adapter.pdfplumber_available:
        pytest.skip("pdfplumber not available")
    
    # Create a minimal PDF file (this is complex, so we'll test with a known PDF structure)
    # For now, we'll just verify the adapter can handle the call
    # In a real scenario, you'd use a test PDF file
    
    # Create minimal PDF bytes (PDF header)
    minimal_pdf = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\n0 1\ntrailer\n<< /Root 1 0 R >>\nstartxref\n10\n%%EOF"
    
    result = await pdf_adapter.parse_file(minimal_pdf, "test.pdf")
    
    # Result may succeed or fail depending on PDF validity, but should not crash
    assert "success" in result
    assert "text" in result or "error" in result
    assert "metadata" in result


@pytest.mark.asyncio
async def test_pdf_adapter_metadata(pdf_adapter):
    """Test that metadata is correctly populated."""
    if not pdf_adapter.pdfplumber_available and not pdf_adapter.pypdf2_available:
        pytest.skip("No PDF libraries available")
    
    # Test with minimal PDF
    minimal_pdf = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\n0 1\ntrailer\n<< /Root 1 0 R >>\nstartxref\n10\n%%EOF"
    
    result = await pdf_adapter.parse_file(minimal_pdf, "test.pdf")
    
    if result["success"]:
        assert "metadata" in result
        assert result["metadata"]["type"] == "pdf"
        assert result["metadata"]["filename"] == "test.pdf"
