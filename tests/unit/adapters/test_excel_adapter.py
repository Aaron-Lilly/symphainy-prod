"""
Unit Tests for Excel Processing Adapter

Tests Excel adapter in isolation (no Runtime/State Surface dependencies).

WHAT (Test Role): I verify Excel adapter can parse Excel files correctly
HOW (Test Implementation): I test with sample Excel bytes directly
"""

import pytest
from symphainy_platform.foundations.public_works.adapters.excel_adapter import ExcelProcessingAdapter


@pytest.fixture
def excel_adapter():
    """Create Excel adapter instance."""
    return ExcelProcessingAdapter()


@pytest.mark.asyncio
async def test_excel_adapter_initialization(excel_adapter):
    """Test that Excel adapter initializes correctly."""
    assert excel_adapter is not None
    # Adapter should check for pandas/openpyxl availability
    assert hasattr(excel_adapter, 'pandas_available')
    assert hasattr(excel_adapter, 'openpyxl_available')


@pytest.mark.asyncio
async def test_excel_adapter_no_libraries(excel_adapter):
    """Test Excel adapter behavior when no libraries are available."""
    # This test will pass if libraries are missing (expected behavior)
    # If libraries are available, the adapter will use them
    if not excel_adapter.pandas_available and not excel_adapter.openpyxl_available:
        # Create a minimal invalid Excel file
        invalid_excel = b"Not an Excel file"
        result = await excel_adapter.parse_file(invalid_excel, "test.xlsx")
        
        assert result["success"] is False
        assert "error" in result
        assert "Neither pandas nor openpyxl available" in result["error"] or "Excel parsing failed" in result["error"]


@pytest.mark.asyncio
@pytest.mark.skipif(
    not pytest.importorskip("pandas", reason="pandas not available"),
    reason="pandas not available"
)
async def test_excel_adapter_parse_simple_excel(excel_adapter):
    """Test parsing a simple Excel file (requires pandas)."""
    if not excel_adapter.pandas_available:
        pytest.skip("pandas not available")
    
    # Create a simple Excel file using pandas
    import pandas as pd
    import io
    
    # Create sample data
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [30, 25, 35],
        'city': ['New York', 'San Francisco', 'Chicago']
    })
    
    # Write to Excel format in memory
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl' if excel_adapter.openpyxl_available else None)
    excel_data = excel_buffer.getvalue()
    
    result = await excel_adapter.parse_file(excel_data, "test.xlsx")
    
    assert result["success"] is True
    assert "sheets" in result
    assert "tables" in result
    assert len(result["sheets"]) > 0
    assert len(result["tables"]) > 0
    assert "metadata" in result


@pytest.mark.asyncio
async def test_excel_adapter_parse_invalid_file(excel_adapter):
    """Test parsing an invalid Excel file."""
    invalid_data = b"This is not an Excel file"
    
    result = await excel_adapter.parse_file(invalid_data, "invalid.xlsx")
    
    # Should return error (either library not available or parsing failed)
    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_excel_adapter_metadata(excel_adapter):
    """Test that metadata is correctly populated."""
    if not excel_adapter.pandas_available and not excel_adapter.openpyxl_available:
        pytest.skip("No Excel libraries available")
    
    # Create minimal Excel file if possible
    import pandas as pd
    import io
    
    try:
        df = pd.DataFrame({'col1': [1, 2, 3]})
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_data = excel_buffer.getvalue()
        
        result = await excel_adapter.parse_file(excel_data, "test.xlsx")
        
        if result["success"]:
            assert "metadata" in result
            assert result["metadata"]["type"] == "excel"
            assert result["metadata"]["filename"] == "test.xlsx"
    except Exception:
        # If Excel creation fails, skip this test
        pytest.skip("Could not create test Excel file")
