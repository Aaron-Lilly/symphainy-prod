# Parsing Testing Strategy

## Overview

This document outlines a comprehensive testing strategy for all parsing services that **works around GCS and Supabase permission issues** by using **in-memory State Surface** and ensures parsers actually work correctly (e.g., binary files → JSONL with copybooks, PDF text extraction, etc.).

## Goals

1. **No External Dependencies**: Tests run without GCS, Supabase, or Redis
2. **In-Memory Storage**: Use `StateSurface(use_memory=True)` for all file operations
3. **Real Functionality Validation**: Ensure parsers produce correct output formats
4. **End-to-End Testing**: Test full parsing pipeline from file upload to structured output
5. **CI/CD Ready**: Tests can run in any environment without infrastructure setup

## Architecture

### Test Infrastructure

```
tests/
├── fixtures/
│   ├── files/
│   │   ├── binary/          # Binary files with copybooks
│   │   ├── pdf/             # PDF test files
│   │   ├── excel/           # Excel test files
│   │   ├── csv/             # CSV test files
│   │   ├── json/            # JSON test files
│   │   ├── word/            # Word document test files
│   │   ├── text/            # Plain text test files
│   │   ├── image/           # Image test files (for OCR)
│   │   └── html/            # HTML test files
│   └── copybooks/           # COBOL copybook definitions
├── helpers/
│   ├── state_surface_setup.py    # In-memory State Surface fixtures
│   ├── file_fixtures.py          # File creation utilities
│   ├── validation.py             # Output validation functions
│   └── mock_services.py          # Mock services for testing
└── integration/
    ├── test_structured_parsing.py
    ├── test_unstructured_parsing.py
    ├── test_hybrid_parsing.py
    ├── test_workflow_sop_parsing.py
    └── test_mainframe_parsing.py  # Special focus on binary → JSONL
```

## Testing Strategy

### 1. In-Memory State Surface Setup

**Key Principle**: All tests use `StateSurface(use_memory=True)` to avoid GCS/Supabase dependencies.

```python
@pytest.fixture
async def in_memory_state_surface():
    """Create in-memory State Surface for testing."""
    from symphainy_platform.runtime.state_surface import StateSurface
    return StateSurface(use_memory=True)
```

### 2. File Fixture Creation

**Key Principle**: Create realistic test files programmatically (no external file dependencies).

#### Binary Files with Copybooks

- Create binary files matching COBOL copybook structures
- Include test cases for:
  - Fixed-length records
  - COMP-3 fields (packed decimal)
  - BINARY fields
  - OCCURS clauses
  - 88-level fields (for validation rules)
  - EBCDIC encoding

#### PDF Files

- Create simple PDFs with known text content
- Test cases:
  - Text extraction
  - Metadata extraction
  - Multi-page documents
  - Tables (if supported)

#### Other File Types

- Excel: Create `.xlsx` files with known data
- CSV: Create CSV files with various formats
- JSON: Create valid JSON files
- Word: Create `.docx` files with known content
- Text: Create plain text files
- Image: Create simple images for OCR testing
- HTML: Create HTML files for parsing

### 3. Validation Functions

**Key Principle**: Validate parser output matches expected format and content.

#### Binary/Mainframe Validation

```python
def validate_binary_parsing_result(result: ParsingResult, expected_records: int):
    """
    Validate binary parsing result.
    
    Checks:
    - Success flag is True
    - Structured data contains records
    - Record count matches expected
    - Each record has expected fields
    - Validation rules (88-level fields) are present
    - Output can be converted to JSONL format
    """
    assert result.success, f"Parsing failed: {result.error}"
    assert result.data is not None, "No structured data returned"
    assert "records" in result.data, "No records in structured data"
    assert len(result.data["records"]) == expected_records, \
        f"Expected {expected_records} records, got {len(result.data['records'])}"
    
    # Validate each record has expected fields
    for record in result.data["records"]:
        assert "CUSTOMER-ID" in record or "customer_id" in record, \
            "Record missing CUSTOMER-ID field"
    
    # Validate validation rules are present (for insights pillar)
    if result.validation_rules:
        assert "88_level_fields" in result.validation_rules, \
            "88-level fields not extracted"
    
    # Validate JSONL format
    import json
    jsonl_lines = [json.dumps(record) for record in result.data["records"]]
    assert len(jsonl_lines) == expected_records, "JSONL format incorrect"
```

#### PDF Validation

```python
def validate_pdf_parsing_result(result: ParsingResult, expected_text: str):
    """
    Validate PDF parsing result.
    
    Checks:
    - Success flag is True
    - Text content is extracted
    - Expected text appears in extracted content
    - Metadata is present (page count, etc.)
    """
    assert result.success, f"PDF parsing failed: {result.error}"
    assert result.data is not None, "No data returned"
    assert "text_chunks" in result.data, "No text chunks in result"
    
    # Combine text chunks
    extracted_text = " ".join(result.data["text_chunks"])
    assert expected_text.lower() in extracted_text.lower(), \
        f"Expected text '{expected_text}' not found in extracted content"
    
    # Validate metadata
    if result.metadata:
        assert "page_count" in result.metadata or "pages" in result.metadata, \
            "Page count not in metadata"
```

#### Other File Type Validations

- **Excel**: Validate table structure, cell values, sheet names
- **CSV**: Validate row count, column names, data types
- **JSON**: Validate JSON structure, key presence, data types
- **Word**: Validate text extraction, formatting metadata
- **Text**: Validate exact text match
- **Image**: Validate OCR text extraction
- **HTML**: Validate text extraction, link extraction

### 4. Test Structure

#### Integration Test Template

```python
@pytest.mark.integration
@pytest.mark.parsing
class TestStructuredParsing:
    """Integration tests for Structured Parsing Service."""
    
    @pytest.fixture
    async def setup(self, in_memory_state_surface):
        """Set up test environment."""
        # Create State Surface
        state_surface = in_memory_state_surface
        
        # Create Public Works Foundation (with in-memory State Surface)
        from symphainy_platform.foundations.public_works.foundation_service import (
            PublicWorksFoundationService
        )
        public_works = PublicWorksFoundationService(config={})
        await public_works.initialize()
        public_works.set_state_surface(state_surface)
        
        # Create Platform Gateway
        from symphainy_platform.runtime.platform_gateway import PlatformGateway
        from symphainy_platform.foundations.curator.foundation_service import (
            CuratorFoundationService
        )
        curator = CuratorFoundationService(public_works_foundation=public_works)
        await curator.initialize()
        platform_gateway = PlatformGateway(
            public_works_foundation=public_works,
            curator=curator
        )
        
        # Create Structured Parsing Service
        from symphainy_platform.realms.content.services.structured_parsing_service.structured_parsing_service import (
            StructuredParsingService
        )
        # ... initialize service modules ...
        service = StructuredParsingService(
            state_surface=state_surface,
            platform_gateway=platform_gateway,
            excel_parser=excel_parser,
            csv_parser=csv_parser,
            json_parser=json_parser,
            binary_parser=binary_parser
        )
        
        return {
            "state_surface": state_surface,
            "service": service,
            "platform_gateway": platform_gateway
        }
    
    @pytest.mark.asyncio
    async def test_binary_parsing_with_copybook(self, setup):
        """Test binary file parsing with copybook → JSONL."""
        # 1. Create test binary file and copybook
        binary_data, copybook_data = create_test_binary_file_with_copybook()
        
        # 2. Store files in State Surface
        file_ref = await setup["state_surface"].store_file(
            session_id="test_session",
            tenant_id="test_tenant",
            file_data=binary_data,
            filename="test_file.bin"
        )
        copybook_ref = await setup["state_surface"].store_file(
            session_id="test_session",
            tenant_id="test_tenant",
            file_data=copybook_data.encode('utf-8'),
            filename="test_copybook.cpy"
        )
        
        # 3. Create parsing request
        from symphainy_platform.foundations.public_works.protocols.parsing_service_protocol import (
            ParsingRequest
        )
        request = ParsingRequest(
            file_reference=file_ref,
            filename="test_file.bin",
            options={"copybook_reference": copybook_ref}
        )
        
        # 4. Parse file
        result = await setup["service"].parse_structured_file(request)
        
        # 5. Validate result
        validate_binary_parsing_result(result, expected_records=3)
        
        # 6. Validate JSONL format
        import json
        jsonl_output = "\n".join([
            json.dumps(record) for record in result.data["records"]
        ])
        assert len(jsonl_output.split("\n")) == 3, "JSONL should have 3 lines"
        
        # 7. Validate validation rules (88-level fields)
        assert result.validation_rules is not None, "Validation rules missing"
        assert "88_level_fields" in result.validation_rules, \
            "88-level fields not extracted"
```

### 5. Test Execution

#### Running Tests

```bash
# Run all parsing tests
pytest tests/integration/test_*_parsing.py -v

# Run specific test
pytest tests/integration/test_mainframe_parsing.py::TestMainframeParsing::test_binary_to_jsonl -v

# Run with coverage
pytest tests/integration/test_*_parsing.py --cov=symphainy_platform/realms/content --cov-report=html
```

#### Test Categories

- `@pytest.mark.integration`: Integration tests (full pipeline)
- `@pytest.mark.parsing`: Parsing-related tests
- `@pytest.mark.mainframe`: Mainframe/binary parsing tests
- `@pytest.mark.pdf`: PDF parsing tests
- `@pytest.mark.fast`: Fast-running tests (< 1 second)
- `@pytest.mark.slow`: Slow-running tests (> 5 seconds)

## Test Coverage Requirements

### Binary/Mainframe Parsing

- ✅ Fixed-length records
- ✅ COMP-3 fields (packed decimal)
- ✅ BINARY fields
- ✅ OCCURS clauses (array fields)
- ✅ REDEFINES clauses
- ✅ 88-level fields (validation rules)
- ✅ EBCDIC encoding
- ✅ ASCII encoding
- ✅ Multiple records in file
- ✅ JSONL output format
- ✅ Validation rules extraction

### PDF Parsing

- ✅ Text extraction
- ✅ Metadata extraction (page count, author, etc.)
- ✅ Multi-page documents
- ✅ Tables (if supported)
- ✅ Images (OCR if applicable)

### Other File Types

- ✅ Excel: Multiple sheets, formulas, formatting
- ✅ CSV: Various delimiters, quoted fields, headers
- ✅ JSON: Nested structures, arrays, types
- ✅ Word: Text, formatting, tables
- ✅ Text: Plain text, encoding detection
- ✅ Image: OCR text extraction
- ✅ HTML: Text, links, structure

## Success Criteria

### Binary → JSONL

1. **Input**: Binary file + copybook
2. **Output**: JSONL format with one JSON object per record
3. **Validation**:
   - Each record has all fields from copybook
   - Field values are correctly parsed (COMP-3, BINARY, etc.)
   - Validation rules (88-level fields) are extracted
   - Output can be written to `.jsonl` file

### PDF → Text

1. **Input**: PDF file
2. **Output**: Extracted text content
3. **Validation**:
   - Text is extracted correctly
   - Metadata is present (page count, etc.)
   - Text chunks are properly formatted

### Other Formats

1. **Input**: File of specific type
2. **Output**: Structured data or text content
3. **Validation**: Output matches expected format and content

## Implementation Plan

1. ✅ Create testing strategy document (this document)
2. ⏳ Create test fixtures for all file types
3. ⏳ Create test helper utilities (State Surface setup, validation functions)
4. ⏳ Create integration tests for each parsing service
5. ⏳ Create specific tests for mainframe parsing (binary → JSONL)
6. ⏳ Create specific tests for PDF parsing
7. ⏳ Run tests and validate all parsers work correctly
8. ⏳ Document test results and any issues found

## Notes

- **No External Dependencies**: All tests use in-memory storage
- **Realistic Test Data**: Test files are created programmatically to match real-world scenarios
- **Comprehensive Validation**: Tests validate both structure and content of parser output
- **CI/CD Ready**: Tests can run in any environment without infrastructure setup
