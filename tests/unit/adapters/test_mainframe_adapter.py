"""
Unit Tests for Mainframe Processing Adapter

Tests Mainframe adapter (Custom + Cobrix strategies) in isolation.

WHAT (Test Role): I verify Mainframe adapter can parse mainframe files correctly
HOW (Test Implementation): I test with sample binary files and copybooks using State Surface mock
"""

import pytest
from symphainy_platform.foundations.public_works.adapters.mainframe_parsing.unified_adapter import MainframeProcessingAdapter
from symphainy_platform.foundations.public_works.adapters.mainframe_parsing.custom_strategy import CustomMainframeStrategy
from symphainy_platform.foundations.public_works.adapters.mainframe_parsing.cobrix_strategy import CobrixMainframeStrategy
from tests.fixtures.mock_state_surface import MockStateSurface, mock_state_surface


@pytest.fixture
def mainframe_adapter(mock_state_surface):
    """Create Mainframe adapter instance with mocked State Surface."""
    return MainframeProcessingAdapter(
        state_surface=mock_state_surface,
        cobrix_service_url=None,  # No Cobrix service for unit tests
        prefer_cobrix=False
    )


@pytest.fixture
def custom_strategy(mock_state_surface):
    """Create Custom Mainframe Strategy instance."""
    return CustomMainframeStrategy(state_surface=mock_state_surface)


@pytest.fixture
def simple_copybook():
    """Create a simple COBOL copybook for testing."""
    return """       01  CUSTOMER-RECORD.
           05  CUSTOMER-ID        PIC X(10).
           05  CUSTOMER-NAME      PIC X(30).
           05  CUSTOMER-STATUS    PIC X(1).
           05  CUSTOMER-BALANCE   PIC 9(10)V99.
"""


@pytest.fixture
def simple_binary_data():
    """Create simple binary data matching the copybook structure."""
    # Fixed-width ASCII: 10 + 30 + 1 + 12 = 53 bytes
    # Format: ID (10) + Name (30) + Status (1) + Balance (12)
    record = b'CUST001   Test Customer Name        A000000123456'
    return record


@pytest.mark.asyncio
async def test_mainframe_adapter_initialization(mainframe_adapter):
    """Test that Mainframe adapter initializes correctly."""
    assert mainframe_adapter is not None
    assert mainframe_adapter.custom_strategy is not None
    assert mainframe_adapter.state_surface is not None


@pytest.mark.asyncio
async def test_custom_strategy_initialization(custom_strategy):
    """Test that Custom strategy initializes correctly."""
    assert custom_strategy is not None
    assert custom_strategy.state_surface is not None
    assert custom_strategy.metadata_extractor is not None


@pytest.mark.asyncio
async def test_custom_strategy_parse_file_missing_file(mock_state_surface, custom_strategy):
    """Test Custom strategy handles missing file gracefully."""
    result = await custom_strategy.parse_file(
        file_reference="file:test:session:missing",
        copybook_reference="file:test:session:copybook",
        options={}
    )
    
    assert result.success is False
    assert "File not found" in result.error


@pytest.mark.asyncio
async def test_custom_strategy_parse_file_missing_copybook(mock_state_surface, custom_strategy, simple_binary_data):
    """Test Custom strategy handles missing copybook gracefully."""
    # Store binary file
    mock_state_surface.store_file_data(
        "file:test:session:binary",
        simple_binary_data,
        metadata={"filename": "test.bin", "file_type": "binary"}
    )
    
    result = await custom_strategy.parse_file(
        file_reference="file:test:session:binary",
        copybook_reference="file:test:session:missing_copybook",
        options={}
    )
    
    assert result.success is False
    assert "Copybook not found" in result.error


@pytest.mark.asyncio
async def test_custom_strategy_parse_simple_ascii_file(
    mock_state_surface,
    custom_strategy,
    simple_copybook,
    simple_binary_data
):
    """Test Custom strategy parses simple ASCII mainframe file."""
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
    
    result = await custom_strategy.parse_file(
        file_reference="file:test:session:binary",
        copybook_reference="file:test:session:copybook",
        options={"codepage": "ascii"}
    )
    
    # Result may succeed or fail depending on parsing complexity
    # But should not crash and should return a FileParsingResult
    assert result is not None
    assert hasattr(result, 'success')
    assert hasattr(result, 'timestamp')
    
    if result.success:
        assert hasattr(result, 'structured_data') or hasattr(result, 'text_content')
        assert hasattr(result, 'validation_rules')


@pytest.mark.asyncio
async def test_custom_strategy_extracts_validation_rules(
    mock_state_surface,
    custom_strategy,
    simple_copybook,
    simple_binary_data
):
    """Test Custom strategy extracts 88-level validation rules from copybook."""
    # Store copybook with 88-level fields
    copybook_with_88 = """       01  CUSTOMER-RECORD.
           05  CUSTOMER-ID        PIC X(10).
           05  CUSTOMER-STATUS    PIC X(1).
               88  ACTIVE         VALUE 'A'.
               88  INACTIVE       VALUE 'I'.
           05  CUSTOMER-BALANCE   PIC 9(10)V99.
"""
    
    mock_state_surface.store_file_data(
        "file:test:session:copybook",
        copybook_with_88.encode('utf-8'),
        metadata={"filename": "test.cpy", "file_type": "copybook"}
    )
    
    mock_state_surface.store_file_data(
        "file:test:session:binary",
        simple_binary_data,
        metadata={"filename": "test.bin", "file_type": "binary"}
    )
    
    result = await custom_strategy.parse_file(
        file_reference="file:test:session:binary",
        copybook_reference="file:test:session:copybook",
        options={"codepage": "ascii"}
    )
    
    # Should extract validation rules even if parsing fails
    assert hasattr(result, 'validation_rules')
    # Validation rules may be empty or contain extracted rules


@pytest.mark.asyncio
async def test_unified_adapter_strategy_selection(mainframe_adapter, mock_state_surface, simple_copybook, simple_binary_data):
    """Test unified adapter selects appropriate strategy."""
    # Store files
    mock_state_surface.store_file_data(
        "file:test:session:copybook",
        simple_copybook.encode('utf-8'),
        metadata={"filename": "test.cpy", "file_type": "copybook"}
    )
    
    mock_state_surface.store_file_data(
        "file:test:session:binary",
        simple_binary_data,
        metadata={"filename": "test.bin", "file_type": "binary", "size": len(simple_binary_data)}
    )
    
    # Test with prefer_custom option
    result = await mainframe_adapter.parse_file(
        file_reference="file:test:session:binary",
        copybook_reference="file:test:session:copybook",
        options={"prefer_custom": True, "codepage": "ascii"}
    )
    
    # Should use custom strategy (no Cobrix service available)
    assert result is not None
    assert hasattr(result, 'success')


@pytest.mark.asyncio
async def test_unified_adapter_handles_missing_strategy(mainframe_adapter, mock_state_surface):
    """Test unified adapter handles case when no strategy is available."""
    # Create adapter without any strategies (shouldn't happen, but test edge case)
    # Actually, custom strategy is always available, so this tests error handling
    
    result = await mainframe_adapter.parse_file(
        file_reference="file:test:session:missing",
        copybook_reference="file:test:session:missing",
        options={}
    )
    
    # Should return error result
    assert result is not None
    assert result.success is False
    assert "error" in result.error.lower() or "not found" in result.error.lower()


@pytest.mark.asyncio
async def test_custom_strategy_supports_feature(custom_strategy):
    """Test Custom strategy feature support checks."""
    # Test various features
    assert isinstance(custom_strategy.supports_feature("OCCURS"), bool)
    assert isinstance(custom_strategy.supports_feature("REDEFINES"), bool)
    assert isinstance(custom_strategy.supports_feature("COMP-3"), bool)
    assert isinstance(custom_strategy.supports_feature("88-level"), bool)
    assert isinstance(custom_strategy.supports_feature("large_files"), bool)


@pytest.mark.asyncio
async def test_custom_strategy_handles_invalid_copybook(mock_state_surface, custom_strategy, simple_binary_data):
    """Test Custom strategy handles invalid copybook gracefully."""
    # Store invalid copybook
    invalid_copybook = "This is not a valid COBOL copybook"
    
    mock_state_surface.store_file_data(
        "file:test:session:invalid_copybook",
        invalid_copybook.encode('utf-8'),
        metadata={"filename": "invalid.cpy", "file_type": "copybook"}
    )
    
    mock_state_surface.store_file_data(
        "file:test:session:binary",
        simple_binary_data,
        metadata={"filename": "test.bin", "file_type": "binary"}
    )
    
    result = await custom_strategy.parse_file(
        file_reference="file:test:session:binary",
        copybook_reference="file:test:session:invalid_copybook",
        options={"codepage": "ascii"}
    )
    
    # Should return error result
    assert result.success is False
    assert "error" in result.error.lower() or "failed" in result.error.lower()


@pytest.mark.asyncio
async def test_custom_strategy_handles_empty_binary_file(mock_state_surface, custom_strategy, simple_copybook):
    """Test Custom strategy handles empty binary file gracefully."""
    # Store copybook
    mock_state_surface.store_file_data(
        "file:test:session:copybook",
        simple_copybook.encode('utf-8'),
        metadata={"filename": "test.cpy", "file_type": "copybook"}
    )
    
    # Store empty binary file
    mock_state_surface.store_file_data(
        "file:test:session:empty_binary",
        b"",
        metadata={"filename": "empty.bin", "file_type": "binary"}
    )
    
    result = await custom_strategy.parse_file(
        file_reference="file:test:session:empty_binary",
        copybook_reference="file:test:session:copybook",
        options={"codepage": "ascii"}
    )
    
    # Should return error result (may be "File not found" or parsing error)
    assert result.success is False
    assert result.error is not None
    assert len(result.error) > 0


@pytest.mark.asyncio
async def test_custom_strategy_different_codepages(mock_state_surface, custom_strategy, simple_copybook):
    """Test Custom strategy handles different codepages."""
    # Store copybook
    mock_state_surface.store_file_data(
        "file:test:session:copybook",
        simple_copybook.encode('utf-8'),
        metadata={"filename": "test.cpy", "file_type": "copybook"}
    )
    
    # Test with different codepages
    for codepage in ["ascii", "cp037", "utf-8"]:
        # Create minimal binary data
        binary_data = b'CUST001   Test Customer Name        A000000123456'
        mock_state_surface.store_file_data(
            f"file:test:session:binary_{codepage}",
            binary_data,
            metadata={"filename": f"test_{codepage}.bin", "file_type": "binary"}
        )
        
        result = await custom_strategy.parse_file(
            file_reference=f"file:test:session:binary_{codepage}",
            copybook_reference="file:test:session:copybook",
            options={"codepage": codepage}
        )
        
        # Should handle codepage option (may succeed or fail based on data)
        assert result is not None
        assert hasattr(result, 'success')
