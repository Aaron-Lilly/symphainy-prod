"""
Integration Tests for JSON Processing Abstraction

Tests JSON abstraction with JSON adapter to verify Layer 1 → Layer 0 integration.

WHAT (Test Role): I verify JSON abstraction properly delegates to JSON adapter
HOW (Test Implementation): I test abstraction with adapter using State Surface mock
"""

import pytest
from symphainy_platform.foundations.public_works.adapters.json_adapter import JsonProcessingAdapter
from symphainy_platform.foundations.public_works.abstractions.json_processing_abstraction import JsonProcessingAbstraction
from symphainy_platform.foundations.public_works.protocols.file_parsing_protocol import FileParsingRequest
from tests.fixtures.mock_state_surface import MockStateSurface, mock_state_surface


@pytest.fixture
def json_adapter():
    """Create JSON adapter instance."""
    return JsonProcessingAdapter()


@pytest.fixture
def json_abstraction(json_adapter, mock_state_surface):
    """Create JSON abstraction with adapter and State Surface."""
    return JsonProcessingAbstraction(
        json_adapter=json_adapter,
        state_surface=mock_state_surface
    )


@pytest.mark.asyncio
async def test_json_abstraction_initialization(json_abstraction):
    """Test that JSON abstraction initializes correctly."""
    assert json_abstraction is not None
    assert json_abstraction.json_adapter is not None
    assert json_abstraction.state_surface is not None


@pytest.mark.asyncio
async def test_json_abstraction_requires_adapter(mock_state_surface):
    """Test that JSON abstraction fails fast when adapter is missing."""
    abstraction = JsonProcessingAbstraction(
        json_adapter=None,  # No adapter
        state_surface=mock_state_surface
    )
    
    # Store test file
    json_content = '{"name": "test", "value": 123}'
    mock_state_surface.store_file_data(
        "file:test:session:json001",
        json_content.encode('utf-8'),
        metadata={"filename": "test.json", "file_type": "json"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:json001",
        filename="test.json",
        state_surface=mock_state_surface
    )
    
    result = await abstraction.parse_file(request)
    
    assert result.success is False
    assert "JSON adapter is required" in result.error


@pytest.mark.asyncio
async def test_json_abstraction_parse_object_integration(json_abstraction, mock_state_surface):
    """Test JSON abstraction parses JSON object using adapter."""
    json_content = '{"name": "test", "value": 123, "active": true}'
    mock_state_surface.store_file_data(
        "file:test:session:json001",
        json_content.encode('utf-8'),
        metadata={"filename": "test.json", "file_type": "json"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:json001",
        filename="test.json",
        state_surface=mock_state_surface
    )
    
    result = await json_abstraction.parse_file(request)
    
    assert result.success is True
    assert result.structured_data is not None
    assert "data" in result.structured_data
    assert result.structured_data["data"]["name"] == "test"
    assert result.structured_data["data"]["value"] == 123
    assert result.metadata is not None


@pytest.mark.asyncio
async def test_json_abstraction_parse_array_integration(json_abstraction, mock_state_surface):
    """Test JSON abstraction parses JSON array using adapter."""
    json_content = '[{"id": 1, "name": "item1"}, {"id": 2, "name": "item2"}]'
    mock_state_surface.store_file_data(
        "file:test:session:json_array",
        json_content.encode('utf-8'),
        metadata={"filename": "array.json", "file_type": "json"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:json_array",
        filename="array.json",
        state_surface=mock_state_surface
    )
    
    result = await json_abstraction.parse_file(request)
    
    assert result.success is True
    assert result.structured_data is not None
    assert "data" in result.structured_data
    assert isinstance(result.structured_data["data"], list)
    assert len(result.structured_data["data"]) == 2


@pytest.mark.asyncio
async def test_json_abstraction_handles_invalid_json(json_abstraction, mock_state_surface):
    """Test JSON abstraction handles invalid JSON gracefully."""
    invalid_json = '{"invalid": json}'
    mock_state_surface.store_file_data(
        "file:test:session:invalid",
        invalid_json.encode('utf-8'),
        metadata={"filename": "invalid.json", "file_type": "json"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:invalid",
        filename="invalid.json",
        state_surface=mock_state_surface
    )
    
    result = await json_abstraction.parse_file(request)
    
    assert result.success is False
    assert "error" in result.error.lower() or "json" in result.error.lower()
