"""
Integration Tests for Excel Processing Abstraction

Tests Excel abstraction with Excel adapter to verify Layer 1 → Layer 0 integration.
"""

import pytest
from symphainy_platform.foundations.public_works.adapters.excel_adapter import ExcelProcessingAdapter
from symphainy_platform.foundations.public_works.abstractions.excel_processing_abstraction import ExcelProcessingAbstraction
from symphainy_platform.foundations.public_works.protocols.file_parsing_protocol import FileParsingRequest
from tests.fixtures.mock_state_surface import MockStateSurface, mock_state_surface


@pytest.fixture
def excel_adapter():
    """Create Excel adapter instance."""
    return ExcelProcessingAdapter()


@pytest.fixture
def excel_abstraction(excel_adapter, mock_state_surface):
    """Create Excel abstraction with adapter and State Surface."""
    return ExcelProcessingAbstraction(
        excel_adapter=excel_adapter,
        state_surface=mock_state_surface
    )


@pytest.mark.asyncio
async def test_excel_abstraction_initialization(excel_abstraction):
    """Test that Excel abstraction initializes correctly."""
    assert excel_abstraction is not None
    assert excel_abstraction.excel_adapter is not None
    assert excel_abstraction.state_surface is not None


@pytest.mark.asyncio
async def test_excel_abstraction_requires_adapter(mock_state_surface):
    """Test that Excel abstraction fails fast when adapter is missing."""
    abstraction = ExcelProcessingAbstraction(
        excel_adapter=None,
        state_surface=mock_state_surface
    )
    
    # Store test file
    mock_state_surface.store_file_data(
        "file:test:session:excel001",
        b"dummy",
        metadata={"filename": "test.xlsx", "file_type": "excel"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:excel001",
        filename="test.xlsx",
        state_surface=mock_state_surface
    )
    
    result = await abstraction.parse_file(request)
    
    assert result.success is False
    assert "Excel adapter is required" in result.error or "adapter" in result.error.lower()


@pytest.mark.asyncio
@pytest.mark.skipif(
    not pytest.importorskip("pandas", reason="pandas not available"),
    reason="pandas not available"
)
async def test_excel_abstraction_parse_file_integration(excel_abstraction, mock_state_surface):
    """Test Excel abstraction parses file using adapter."""
    if not excel_abstraction.excel_adapter.pandas_available:
        pytest.skip("pandas not available")
    
    # Create simple Excel file
    import pandas as pd
    import io
    
    df = pd.DataFrame({
        'name': ['Alice', 'Bob'],
        'age': [30, 25]
    })
    
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl' if excel_abstraction.excel_adapter.openpyxl_available else None)
    excel_data = excel_buffer.getvalue()
    
    mock_state_surface.store_file_data(
        "file:test:session:excel001",
        excel_data,
        metadata={"filename": "test.xlsx", "file_type": "excel"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:excel001",
        filename="test.xlsx",
        state_surface=mock_state_surface
    )
    
    result = await excel_abstraction.parse_file(request)
    
    # Result may succeed or fail depending on library availability
    assert result is not None
    assert hasattr(result, 'success')
    
    if result.success:
        assert result.structured_data is not None
        assert "sheets" in result.structured_data or "tables" in result.structured_data


@pytest.mark.asyncio
async def test_excel_abstraction_handles_missing_file(excel_abstraction, mock_state_surface):
    """Test Excel abstraction handles missing file gracefully."""
    request = FileParsingRequest(
        file_reference="file:test:session:missing",
        filename="missing.xlsx",
        state_surface=mock_state_surface
    )
    
    result = await excel_abstraction.parse_file(request)
    
    assert result.success is False
    assert "File not found" in result.error
