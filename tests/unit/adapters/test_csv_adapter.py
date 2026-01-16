"""
Unit Tests for CSV Processing Adapter

Tests CSV adapter in isolation (no Runtime/State Surface dependencies).

WHAT (Test Role): I verify CSV adapter can parse CSV files correctly
HOW (Test Implementation): I test with sample CSV bytes directly
"""

import pytest
from symphainy_platform.foundations.public_works.adapters.csv_adapter import CsvProcessingAdapter


@pytest.fixture
def csv_adapter():
    """Create CSV adapter instance."""
    return CsvProcessingAdapter()


@pytest.mark.asyncio
async def test_csv_adapter_parse_simple_csv(csv_adapter):
    """Test parsing a simple CSV file."""
    csv_content = "name,age,city\nAlice,30,New York\nBob,25,San Francisco\n"
    file_data = csv_content.encode('utf-8')
    
    result = await csv_adapter.parse_file(file_data, "test.csv")
    
    assert result["success"] is True
    assert "rows" in result
    assert "columns" in result
    assert len(result["rows"]) == 2
    assert result["columns"] == ["name", "age", "city"]
    assert result["rows"][0]["name"] == "Alice"
    assert result["rows"][0]["age"] == "30"
    assert result["rows"][1]["name"] == "Bob"
    assert result["rows"][1]["age"] == "25"


@pytest.mark.asyncio
async def test_csv_adapter_parse_empty_csv(csv_adapter):
    """Test parsing an empty CSV file."""
    csv_content = ""
    file_data = csv_content.encode('utf-8')
    
    result = await csv_adapter.parse_file(file_data, "empty.csv")
    
    assert result["success"] is True
    assert len(result["rows"]) == 0
    assert len(result["columns"]) == 0


@pytest.mark.asyncio
async def test_csv_adapter_parse_csv_with_special_chars(csv_adapter):
    """Test parsing CSV with special characters."""
    csv_content = 'name,description\n"Test, Name","Contains, commas"\n'
    file_data = csv_content.encode('utf-8')
    
    result = await csv_adapter.parse_file(file_data, "special.csv")
    
    assert result["success"] is True
    assert len(result["rows"]) == 1
    assert result["rows"][0]["name"] == "Test, Name"
    assert result["rows"][0]["description"] == "Contains, commas"


@pytest.mark.asyncio
async def test_csv_adapter_parse_latin1_encoding(csv_adapter):
    """Test parsing CSV with Latin-1 encoding."""
    csv_content = "name,value\nTesté,123\n"
    file_data = csv_content.encode('latin-1')
    
    result = await csv_adapter.parse_file(file_data, "latin1.csv")
    
    assert result["success"] is True
    assert len(result["rows"]) == 1
    assert result["rows"][0]["name"] == "Testé"


@pytest.mark.asyncio
async def test_csv_adapter_metadata(csv_adapter):
    """Test that metadata is correctly populated."""
    csv_content = "col1,col2,col3\nval1,val2,val3\n"
    file_data = csv_content.encode('utf-8')
    
    result = await csv_adapter.parse_file(file_data, "test.csv")
    
    assert result["success"] is True
    assert "metadata" in result
    assert result["metadata"]["type"] == "csv"
    assert result["metadata"]["row_count"] == 1
    assert result["metadata"]["column_count"] == 3
    assert result["metadata"]["filename"] == "test.csv"
    assert result["metadata"]["size"] == len(file_data)
