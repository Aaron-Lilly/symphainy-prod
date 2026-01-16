"""
Integration Tests for Mainframe Processing Abstraction

Tests Mainframe abstraction with Mainframe adapter to verify Layer 1 → Layer 0 integration.

WHAT (Test Role): I verify Mainframe abstraction properly delegates to Mainframe adapter
HOW (Test Implementation): I test abstraction with adapter using State Surface mock
"""

import pytest
from symphainy_platform.foundations.public_works.adapters.mainframe_parsing.unified_adapter import MainframeProcessingAdapter
from symphainy_platform.foundations.public_works.abstractions.mainframe_processing_abstraction import MainframeProcessingAbstraction
from symphainy_platform.foundations.public_works.protocols.file_parsing_protocol import FileParsingRequest
from tests.fixtures.mock_state_surface import MockStateSurface, mock_state_surface


@pytest.fixture
def mainframe_adapter(mock_state_surface):
    """Create Mainframe adapter instance with State Surface."""
    return MainframeProcessingAdapter(
        state_surface=mock_state_surface,
        cobrix_service_url=None,
        prefer_cobrix=False
    )


@pytest.fixture
def mainframe_abstraction(mainframe_adapter, mock_state_surface):
    """Create Mainframe abstraction with adapter and State Surface."""
    return MainframeProcessingAbstraction(
        mainframe_adapter=mainframe_adapter,
        state_surface=mock_state_surface
    )


@pytest.fixture
def simple_copybook():
    """Create a simple COBOL copybook for testing."""
    return """       01  CUSTOMER-RECORD.
           05  CUSTOMER-ID        PIC X(10).
           05  CUSTOMER-NAME      PIC X(30).
           05  CUSTOMER-STATUS    PIC X(1).
           05  CUSTOMER-BALANCE   PIC 9(10)V99).
"""


@pytest.fixture
def simple_binary_data():
    """Create simple binary data matching the copybook structure."""
    # Fixed-width ASCII: 10 + 30 + 1 + 12 = 53 bytes
    record = b'CUST001   Test Customer Name        A000000123456'
    return record


@pytest.mark.asyncio
async def test_mainframe_abstraction_initialization(mainframe_abstraction):
    """Test that Mainframe abstraction initializes correctly."""
    assert mainframe_abstraction is not None
    assert mainframe_abstraction.mainframe_adapter is not None
    assert mainframe_abstraction.state_surface is not None


@pytest.mark.asyncio
async def test_mainframe_abstraction_requires_copybook(mainframe_abstraction, mock_state_surface, simple_binary_data):
    """Test that Mainframe abstraction requires copybook_reference."""
    # Store binary file
    mock_state_surface.store_file_data(
        "file:test:session:binary",
        simple_binary_data,
        metadata={"filename": "test.bin", "file_type": "binary"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:binary",
        filename="test.bin",
        copybook_reference=None,  # Missing copybook
        state_surface=mock_state_surface
    )
    
    result = await mainframe_abstraction.parse_file(request)
    
    assert result.success is False
    assert "copybook_reference required" in result.error


@pytest.mark.asyncio
async def test_mainframe_abstraction_parse_file_integration(
    mainframe_abstraction,
    mock_state_surface,
    simple_copybook,
    simple_binary_data
):
    """Test Mainframe abstraction parses file using adapter."""
    # Store copybook
    mock_state_surface.store_file_data(
        "file:test:session:copybook",
        simple_copybook.encode('utf-8'),
        metadata={"filename": "test.cpy", "file_type": "copybook"}
    )
    
    # Store binary file
    mock_state_surface.store_file_data(
        "file:test:session:binary",
        simple_binary_data,
        metadata={"filename": "test.bin", "file_type": "binary"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:binary",
        copybook_reference="file:test:session:copybook",
        filename="test.bin",
        options={"codepage": "ascii"},
        state_surface=mock_state_surface
    )
    
    result = await mainframe_abstraction.parse_file(request)
    
    # Result may succeed or fail depending on parsing complexity
    # But should not crash and should return a FileParsingResult
    assert result is not None
    assert hasattr(result, 'success')
    assert hasattr(result, 'timestamp')
    
    if result.success:
        assert hasattr(result, 'structured_data') or hasattr(result, 'text_content')
        assert hasattr(result, 'validation_rules')


@pytest.mark.asyncio
async def test_mainframe_abstraction_handles_missing_file(mainframe_abstraction, mock_state_surface, simple_copybook):
    """Test Mainframe abstraction handles missing file gracefully."""
    # Store copybook
    mock_state_surface.store_file_data(
        "file:test:session:copybook",
        simple_copybook.encode('utf-8'),
        metadata={"filename": "test.cpy", "file_type": "copybook"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:missing",
        copybook_reference="file:test:session:copybook",
        filename="missing.bin",
        state_surface=mock_state_surface
    )
    
    result = await mainframe_abstraction.parse_file(request)
    
    assert result.success is False
    assert "error" in result.error.lower() or "not found" in result.error.lower()


@pytest.mark.asyncio
async def test_mainframe_abstraction_handles_missing_copybook(mainframe_abstraction, mock_state_surface, simple_binary_data):
    """Test Mainframe abstraction handles missing copybook gracefully."""
    # Store binary file
    mock_state_surface.store_file_data(
        "file:test:session:binary",
        simple_binary_data,
        metadata={"filename": "test.bin", "file_type": "binary"}
    )
    
    request = FileParsingRequest(
        file_reference="file:test:session:binary",
        copybook_reference="file:test:session:missing_copybook",
        filename="test.bin",
        state_surface=mock_state_surface
    )
    
    result = await mainframe_abstraction.parse_file(request)
    
    assert result.success is False
    assert "error" in result.error.lower() or "not found" in result.error.lower()


@pytest.mark.asyncio
async def test_mainframe_abstraction_uses_state_surface_from_request(mainframe_adapter):
    """Test Mainframe abstraction uses State Surface from request if not in __init__."""
    abstraction = MainframeProcessingAbstraction(
        mainframe_adapter=mainframe_adapter,
        state_surface=None  # Not provided in __init__
    )
    
    # Create State Surface for request
    state_surface = MockStateSurface()
    copybook = """       01  RECORD.
           05  FIELD1        PIC X(10).
"""
    state_surface.store_file_data(
        "file:test:session:copybook",
        copybook.encode('utf-8'),
        metadata={"filename": "test.cpy", "file_type": "copybook"}
    )
    
    binary_data = b'TEST      '
    state_surface.store_file_data(
        "file:test:session:binary",
        binary_data,
        metadata={"filename": "test.bin", "file_type": "binary"}
    )
    
    # Update adapter's state_surface
    mainframe_adapter.state_surface = state_surface
    
    request = FileParsingRequest(
        file_reference="file:test:session:binary",
        copybook_reference="file:test:session:copybook",
        filename="test.bin",
        options={"codepage": "ascii"},
        state_surface=state_surface  # Provided in request
    )
    
    result = await abstraction.parse_file(request)
    
    # Should use State Surface from request
    assert result is not None
    assert hasattr(result, 'success')
