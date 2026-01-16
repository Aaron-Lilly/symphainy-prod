"""
Integration Tests for CSV Processing Abstraction

Tests CSV abstraction with CSV adapter to verify Layer 1 → Layer 0 integration.

WHAT (Test Role): I verify CSV abstraction properly delegates to CSV adapter
HOW (Test Implementation): I test abstraction with adapter using State Surface mock
"""

import pytest
from symphainy_platform.foundations.public_works.adapters.csv_adapter import CsvProcessingAdapter
from symphainy_platform.foundations.public_works.abstractions.csv_processing_abstraction import CsvProcessingAbstraction
from symphainy_platform.foundations.public_works.protocols.file_parsing_protocol import FileParsingRequest
from tests.fixtures.mock_state_surface import MockStateSurface, mock_state_surface


@pytest.fixture
def csv_adapter():
    """Create CSV adapter instance."""
    return CsvProcessingAdapter()


@pytest.fixture
def csv_abstraction(csv_adapter, mock_state_surface):
    """Create CSV abstraction with adapter and State Surface."""
    return CsvProcessingAbstraction(
        csv_adapter=csv_adapter,
        state_surface=mock_state_surface
    )


@pytest.mark.asyncio
async def test_csv_abstraction_initialization(csv_abstraction):
    """Test that CSV abstraction initializes correctly."""
    assert csv_abstraction is not None
    assert csv_abstraction.csv_adapter is not None
    assert csv_abstraction.state_surface is not None


@pytest.mark.asyncio
async def test_csv_abstraction_requires_adapter(mock_state_surface):
    """Test that CSV abstraction fails fast when adapter is missing."""
    abstraction = CsvProcessingAbstraction(
        csv_adapter=None,  # No adapter
        state_surface=mock_state_surface
    )
    
    # Store test file
    csv_content = "name,age\nAlice,30\n"
    mock_state_surface.store_file_data(
        "file:test:session:csv001",
        csv_content.encode('utf-8'),
        metadata={"filename": "test.csv", "file_type": "csv"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:csv001",
        filename="test.csv",
        state_surface=mock_state_surface
    )
    
    result = await abstraction.parse_file(request)
    
    assert result.success is False
    assert "CSV adapter is required" in result.error


@pytest.mark.asyncio
async def test_csv_abstraction_parse_file_integration(csv_abstraction, mock_state_surface):
    """Test CSV abstraction parses file using adapter."""
    # Store test CSV file
    csv_content = "name,age,city\nAlice,30,New York\nBob,25,San Francisco\n"
    mock_state_surface.store_file_data(
        "file:test:session:csv001",
        csv_content.encode('utf-8'),
        metadata={"filename": "test.csv", "file_type": "csv"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:csv001",
        filename="test.csv",
        state_surface=mock_state_surface
    )
    
    result = await csv_abstraction.parse_file(request)
    
    assert result.success is True
    assert result.structured_data is not None
    assert "rows" in result.structured_data
    assert "columns" in result.structured_data
    assert len(result.structured_data["rows"]) == 2
    assert result.structured_data["columns"] == ["name", "age", "city"]
    assert result.metadata is not None


@pytest.mark.asyncio
async def test_csv_abstraction_handles_missing_file(csv_abstraction, mock_state_surface):
    """Test CSV abstraction handles missing file gracefully."""
    request = FileParsingRequest(
        file_reference="file:test:session:missing",
        filename="missing.csv",
        state_surface=mock_state_surface
    )
    
    result = await csv_abstraction.parse_file(request)
    
    assert result.success is False
    assert "File not found" in result.error


@pytest.mark.asyncio
async def test_csv_abstraction_handles_invalid_csv(csv_abstraction, mock_state_surface):
    """Test CSV abstraction handles invalid CSV gracefully."""
    # Store invalid CSV
    invalid_csv = "This is not valid CSV content"
    mock_state_surface.store_file_data(
        "file:test:session:invalid",
        invalid_csv.encode('utf-8'),
        metadata={"filename": "invalid.csv", "file_type": "csv"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:invalid",
        filename="invalid.csv",
        state_surface=mock_state_surface
    )
    
    result = await csv_abstraction.parse_file(request)
    
    # Adapter may succeed or fail, but abstraction should handle it
    assert result is not None
    assert hasattr(result, 'success')


@pytest.mark.asyncio
async def test_csv_abstraction_uses_state_surface_from_request(csv_adapter):
    """Test CSV abstraction uses State Surface from request if not in __init__."""
    abstraction = CsvProcessingAbstraction(
        csv_adapter=csv_adapter,
        state_surface=None  # Not provided in __init__
    )
    
    # Create State Surface for request
    state_surface = MockStateSurface()
    csv_content = "name,age\nAlice,30\n"
    state_surface.store_file_data(
        "file:test:session:csv001",
        csv_content.encode('utf-8'),
        metadata={"filename": "test.csv", "file_type": "csv"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:csv001",
        filename="test.csv",
        state_surface=state_surface  # Provided in request
    )
    
    result = await abstraction.parse_file(request)
    
    assert result.success is True
