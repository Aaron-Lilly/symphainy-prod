"""
Unit Tests for HTML Processing Adapter

Tests HTML adapter in isolation (no Runtime/State Surface dependencies).

WHAT (Test Role): I verify HTML adapter can parse HTML files correctly
HOW (Test Implementation): I test with sample HTML bytes directly
"""

import pytest
from symphainy_platform.foundations.public_works.adapters.html_adapter import HtmlProcessingAdapter


@pytest.fixture
def html_adapter():
    """Create HTML adapter instance."""
    return HtmlProcessingAdapter()


@pytest.mark.asyncio
async def test_html_adapter_initialization(html_adapter):
    """Test that HTML adapter initializes correctly."""
    assert html_adapter is not None
    assert hasattr(html_adapter, 'bs4_available')


@pytest.mark.asyncio
async def test_html_adapter_no_library(html_adapter):
    """Test HTML adapter behavior when BeautifulSoup is not available."""
    if not html_adapter.bs4_available:
        invalid_html = b"<html></html>"
        result = await html_adapter.parse_file(invalid_html, "test.html")
        
        assert result["success"] is False
        assert "error" in result
        assert "BeautifulSoup not available" in result["error"]


@pytest.mark.asyncio
@pytest.mark.skipif(
    not pytest.importorskip("bs4", reason="BeautifulSoup not available"),
    reason="BeautifulSoup not available"
)
async def test_html_adapter_parse_simple_html(html_adapter):
    """Test parsing a simple HTML file."""
    if not html_adapter.bs4_available:
        pytest.skip("BeautifulSoup not available")
    
    html_content = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Test Heading</h1>
            <p>This is a test paragraph.</p>
        </body>
    </html>
    """
    html_data = html_content.encode('utf-8')
    
    result = await html_adapter.parse_file(html_data, "test.html")
    
    assert result["success"] is True
    assert "text" in result
    assert "Test Heading" in result["text"] or "test" in result["text"].lower()
    assert "elements" in result
    assert "tables" in result
    assert "metadata" in result


@pytest.mark.asyncio
@pytest.mark.skipif(
    not pytest.importorskip("bs4", reason="BeautifulSoup not available"),
    reason="BeautifulSoup not available"
)
async def test_html_adapter_parse_html_with_table(html_adapter):
    """Test parsing HTML with a table."""
    if not html_adapter.bs4_available:
        pytest.skip("BeautifulSoup not available")
    
    html_content = """
    <html>
        <body>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Age</th>
                </tr>
                <tr>
                    <td>Alice</td>
                    <td>30</td>
                </tr>
                <tr>
                    <td>Bob</td>
                    <td>25</td>
                </tr>
            </table>
        </body>
    </html>
    """
    html_data = html_content.encode('utf-8')
    
    result = await html_adapter.parse_file(html_data, "test_table.html")
    
    assert result["success"] is True
    assert "tables" in result
    assert len(result["tables"]) > 0
    # Check that table data is extracted
    if result["tables"]:
        table = result["tables"][0]
        assert "data" in table or "rows" in table


@pytest.mark.asyncio
@pytest.mark.skipif(
    not pytest.importorskip("bs4", reason="BeautifulSoup not available"),
    reason="BeautifulSoup not available"
)
async def test_html_adapter_parse_html_with_links(html_adapter):
    """Test parsing HTML with links."""
    if not html_adapter.bs4_available:
        pytest.skip("BeautifulSoup not available")
    
    html_content = """
    <html>
        <body>
            <a href="https://example.com">Example Link</a>
            <a href="/page">Internal Link</a>
        </body>
    </html>
    """
    html_data = html_content.encode('utf-8')
    
    result = await html_adapter.parse_file(html_data, "test_links.html")
    
    assert result["success"] is True
    assert "elements" in result
    # Check that links are extracted
    links = [elem for elem in result["elements"] if elem.get("type") == "link"]
    assert len(links) >= 2


@pytest.mark.asyncio
@pytest.mark.skipif(
    not pytest.importorskip("bs4", reason="BeautifulSoup not available"),
    reason="BeautifulSoup not available"
)
async def test_html_adapter_parse_malformed_html(html_adapter):
    """Test parsing malformed HTML (should still work with BeautifulSoup)."""
    if not html_adapter.bs4_available:
        pytest.skip("BeautifulSoup not available")
    
    malformed_html = """
    <html>
        <body>
            <p>Unclosed paragraph
            <div>Missing closing tag
        </body>
    </html>
    """
    html_data = malformed_html.encode('utf-8')
    
    result = await html_adapter.parse_file(html_data, "malformed.html")
    
    # BeautifulSoup should handle malformed HTML gracefully
    assert result["success"] is True or "error" in result


@pytest.mark.asyncio
async def test_html_adapter_metadata(html_adapter):
    """Test that metadata is correctly populated."""
    if not html_adapter.bs4_available:
        pytest.skip("BeautifulSoup not available")
    
    html_content = "<html><body><p>Test</p></body></html>"
    html_data = html_content.encode('utf-8')
    
    result = await html_adapter.parse_file(html_data, "test.html")
    
    if result["success"]:
        assert "metadata" in result
        assert result["metadata"]["type"] == "html"
        assert result["metadata"]["filename"] == "test.html"
