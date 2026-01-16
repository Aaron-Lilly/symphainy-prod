"""
Integration Tests for HTML Processing Abstraction

Tests HTML abstraction with HTML adapter to verify Layer 1 → Layer 0 integration.
"""

import pytest
from symphainy_platform.foundations.public_works.adapters.html_adapter import HtmlProcessingAdapter
from symphainy_platform.foundations.public_works.abstractions.html_processing_abstraction import HtmlProcessingAbstraction
from symphainy_platform.foundations.public_works.protocols.file_parsing_protocol import FileParsingRequest
from tests.fixtures.mock_state_surface import MockStateSurface, mock_state_surface


@pytest.fixture
def html_adapter():
    """Create HTML adapter instance."""
    return HtmlProcessingAdapter()


@pytest.fixture
def html_abstraction(html_adapter, mock_state_surface):
    """Create HTML abstraction with adapter and State Surface."""
    return HtmlProcessingAbstraction(
        html_adapter=html_adapter,
        state_surface=mock_state_surface
    )


@pytest.mark.asyncio
async def test_html_abstraction_initialization(html_abstraction):
    """Test that HTML abstraction initializes correctly."""
    assert html_abstraction is not None
    assert html_abstraction.html_adapter is not None
    assert html_abstraction.state_surface is not None


@pytest.mark.asyncio
async def test_html_abstraction_requires_adapter(mock_state_surface):
    """Test that HTML abstraction fails fast when adapter is missing."""
    abstraction = HtmlProcessingAbstraction(
        html_adapter=None,
        state_surface=mock_state_surface
    )
    
    # Store test file
    mock_state_surface.store_file_data(
        "file:test:session:html001",
        b"<html></html>",
        metadata={"filename": "test.html", "file_type": "html"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:html001",
        filename="test.html",
        state_surface=mock_state_surface
    )
    
    result = await abstraction.parse_file(request)
    
    assert result.success is False
    assert "HTML adapter is required" in result.error or "adapter" in result.error.lower()


@pytest.mark.asyncio
@pytest.mark.skipif(
    not pytest.importorskip("bs4", reason="BeautifulSoup not available"),
    reason="BeautifulSoup not available"
)
async def test_html_abstraction_parse_file_integration(html_abstraction, mock_state_surface):
    """Test HTML abstraction parses file using adapter."""
    if not html_abstraction.html_adapter.bs4_available:
        pytest.skip("BeautifulSoup not available")
    
    html_content = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Test Heading</h1>
            <p>Test paragraph</p>
        </body>
    </html>
    """
    
    mock_state_surface.store_file_data(
        "file:test:session:html001",
        html_content.encode('utf-8'),
        metadata={"filename": "test.html", "file_type": "html"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:html001",
        filename="test.html",
        state_surface=mock_state_surface
    )
    
    result = await html_abstraction.parse_file(request)
    
    assert result.success is True
    assert result.text_content is not None
    assert "Test" in result.text_content or "test" in result.text_content.lower()
    assert result.structured_data is not None


@pytest.mark.asyncio
async def test_html_abstraction_handles_missing_file(html_abstraction, mock_state_surface):
    """Test HTML abstraction handles missing file gracefully."""
    request = FileParsingRequest(
        file_reference="file:test:session:missing",
        filename="missing.html",
        state_surface=mock_state_surface
    )
    
    result = await html_abstraction.parse_file(request)
    
    assert result.success is False
    assert "File not found" in result.error
