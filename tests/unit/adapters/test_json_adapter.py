"""
Unit Tests for JSON Processing Adapter

Tests JSON adapter in isolation (no Runtime/State Surface dependencies).

WHAT (Test Role): I verify JSON adapter can parse JSON files correctly
HOW (Test Implementation): I test with sample JSON bytes directly
"""

import pytest
from symphainy_platform.foundations.public_works.adapters.json_adapter import JsonProcessingAdapter


@pytest.fixture
def json_adapter():
    """Create JSON adapter instance."""
    return JsonProcessingAdapter()


@pytest.mark.asyncio
async def test_json_adapter_parse_object(json_adapter):
    """Test parsing a JSON object."""
    json_content = '{"name": "test", "value": 123, "active": true}'
    file_data = json_content.encode('utf-8')
    
    result = await json_adapter.parse_file(file_data, "test.json")
    
    assert result["success"] is True
    assert "data" in result
    assert result["data"]["name"] == "test"
    assert result["data"]["value"] == 123
    assert result["data"]["active"] is True


@pytest.mark.asyncio
async def test_json_adapter_parse_array(json_adapter):
    """Test parsing a JSON array."""
    json_content = '[{"id": 1, "name": "item1"}, {"id": 2, "name": "item2"}]'
    file_data = json_content.encode('utf-8')
    
    result = await json_adapter.parse_file(file_data, "array.json")
    
    assert result["success"] is True
    assert "data" in result
    assert isinstance(result["data"], list)
    assert len(result["data"]) == 2
    assert result["data"][0]["id"] == 1
    assert result["data"][1]["name"] == "item2"


@pytest.mark.asyncio
async def test_json_adapter_parse_nested(json_adapter):
    """Test parsing nested JSON structures."""
    json_content = '{"user": {"name": "Alice", "settings": {"theme": "dark"}}}'
    file_data = json_content.encode('utf-8')
    
    result = await json_adapter.parse_file(file_data, "nested.json")
    
    assert result["success"] is True
    assert result["data"]["user"]["name"] == "Alice"
    assert result["data"]["user"]["settings"]["theme"] == "dark"


@pytest.mark.asyncio
async def test_json_adapter_invalid_json(json_adapter):
    """Test parsing invalid JSON."""
    json_content = '{"invalid": json}'
    file_data = json_content.encode('utf-8')
    
    result = await json_adapter.parse_file(file_data, "invalid.json")
    
    assert result["success"] is False
    assert "error" in result
    assert "JSON parsing failed" in result["error"]


@pytest.mark.asyncio
async def test_json_adapter_metadata(json_adapter):
    """Test that metadata is correctly populated."""
    json_content = '{"test": "data"}'
    file_data = json_content.encode('utf-8')
    
    result = await json_adapter.parse_file(file_data, "test.json")
    
    assert result["success"] is True
    assert "metadata" in result
    assert result["metadata"]["type"] == "json"
    assert result["metadata"]["is_object"] is True
    assert result["metadata"]["is_array"] is False
    assert result["metadata"]["filename"] == "test.json"
    assert result["metadata"]["size"] == len(file_data)
