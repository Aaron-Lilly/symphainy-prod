# Task: Port Full Custom Mainframe Parsing Strategy

## Status: READY FOR IMPLEMENTATION

## Overview

Port the complete custom mainframe parsing implementation from the legacy codebase to the new architectural pattern. The current implementation is a placeholder that returns an error. This task requires implementing the full COBOL copybook parsing and binary record parsing logic.

## Context

The custom mainframe strategy is one of two strategies available in the `MainframeProcessingAdapter`:
1. **Custom Strategy** (this task) - Pure Python implementation
2. **Cobrix Strategy** - HTTP service-based implementation (already working)

The custom strategy provides a self-contained Python solution that doesn't require external services, making it ideal for MVP and development environments.

## Current State

**Location**: `/home/founders/demoversion/symphainy_source_code/symphainy_platform/foundations/public_works/adapters/mainframe_parsing/custom_strategy.py`

**Current Implementation**: Placeholder that returns:
```python
return FileParsingResult(
    success=False,
    error="Custom mainframe parsing not yet fully implemented. Use Cobrix strategy for now.",
    validation_rules=validation_rules,
    timestamp=datetime.utcnow().isoformat()
)
```

## Source Material

**Legacy Implementation**: `/home/founders/demoversion/symphainy_source/symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/mainframe_processing_adapter.py`

**Key Methods to Port**:
1. `_parse_copybook_from_string()` - Parse COBOL copybook from string content
2. `_clean_cobol()` - Clean COBOL lines, handle continuation lines
3. `_parse_field_definition()` - Parse individual field definitions
4. `_parse_pic_clause()` - Parse PIC clauses to extract field information
5. `_handle_occurs()` - Denormalize OCCURS clauses
6. `_denormalize_cobol()` - Flatten OCCURS clauses
7. `_get_subgroup()` - Get fields within a parent level
8. `_rename_filler_fields()` - Rename FILLER fields to avoid duplicates
9. `_parse_binary_records()` - Parse binary records using field definitions
10. `_normalize_ascii_file()` - Normalize ASCII files (remove newlines, find data start)
11. `_find_ascii_data_start_extensible()` - Find where data starts in ASCII files
12. `_detect_and_strip_prefix_extensible()` - Detect and strip record prefixes
13. `_strip_record_prefixes_extensible()` - Strip prefixes from all records
14. `_validate_field_against_copybook()` - Validate field data against copybook
15. `_parse_field_value()` - Parse individual field values
16. `_get_len_for_comp_binary()` - Calculate byte length for COMP/BINARY fields
17. `_ebcdic_to_decimal()` - Convert EBCDIC-encoded bytes to decimal
18. `_unpack_hex_array()` - Unpack binary/COMP fields
19. `_unpack_comp3_number()` - Unpack COMP-3 (packed decimal) numbers
20. `_custom_encoder()` - Clean EBCDIC strings (remove @ symbols, control chars)
21. `_records_to_text()` - Convert records to text representation

## Architecture Requirements

### New Architecture Pattern

The new implementation must follow the **5-Layer Architecture**:

1. **Layer 0 (Adapter)**: `CustomMainframeStrategy` - Raw technology client
2. **Layer 1 (Abstraction)**: `MainframeProcessingAbstraction` - Lightweight coordination
3. **Layer 2 (Protocol)**: `FileParsingProtocol` - Interface contract
4. **Layer 3 (Runtime)**: `StateSurface` - File retrieval via Runtime
5. **Layer 4 (Foundation)**: `PublicWorksFoundationService` - Orchestration

### Key Differences from Legacy

1. **File Retrieval**: Uses `StateSurface.get_file()` instead of file paths
2. **Bytes-Based**: Works with `bytes` directly, not file paths
3. **Async/Await**: All methods are async
4. **Return Type**: Returns `FileParsingResult` (from protocol), not raw dicts
5. **State Surface**: Receives `StateSurface` instance in `__init__`, uses it for file retrieval

### Current Structure

```python
class CustomMainframeStrategy:
    def __init__(self, state_surface: Any):
        self.state_surface = state_surface
        self.logger = logger
        self.metadata_extractor = MetadataExtractor()
    
    async def parse_file(
        self,
        file_reference: str,
        copybook_reference: str,
        options: Dict[str, Any]
    ) -> FileParsingResult:
        # TODO: Implement full parsing logic
```

## Implementation Steps

### Step 1: Port Copybook Parsing

1. Port `_parse_copybook_from_string()` method
2. Port `_clean_cobol()` method
3. Port `_parse_field_definition()` method
4. Port `_parse_pic_clause()` method
5. Port `_handle_occurs()` method
6. Port `_denormalize_cobol()` method
7. Port `_get_subgroup()` method
8. Port `_rename_filler_fields()` method

**Key Requirements**:
- Handle COBOL continuation lines (columns 6-72)
- Support OCCURS clauses (with recursive expansion)
- Support REDEFINES (remove redefined fields)
- Support FILLER fields (rename to FILLER_1, FILLER_2, etc.)
- Extract PIC clauses and parse them
- Detect COMP, COMP-3, BINARY modifiers
- Handle level numbers (01, 02, etc.)

### Step 2: Port Binary Record Parsing

1. Port `_parse_binary_records()` method
2. Port `_parse_field_value()` method
3. Port `_get_len_for_comp_binary()` method
4. Port `_ebcdic_to_decimal()` method
5. Port `_unpack_hex_array()` method
6. Port `_unpack_comp3_number()` method
7. Port `_custom_encoder()` method

**Key Requirements**:
- Calculate record length from field definitions
- Adjust field lengths for COMP-3 (packed decimal): `math.ceil((digit_count + 1) / 2)`
- Adjust field lengths for COMP/BINARY: Use `_get_len_for_comp_binary()`
- Read fields sequentially (trust copybook as source of truth)
- **Field-Type-Aware Normalization**: 
  - Text fields: Apply EBCDIC→ASCII/Unicode conversion using code page
  - Numeric fields (COMP-3, COMP, BINARY): NO character translation (decode as binary)
  - Display format numeric: Apply encoding conversion, then parse as number
- **Code Page/CCSID Handling**:
  - Support multiple EBCDIC code pages (cp037, cp1047, etc.)
  - Detect or allow configuration of code page via options
  - Default to cp037 (IBM-037) if not specified
  - Log code page used for debugging
- Handle ASCII vs EBCDIC encoding (detect automatically, allow override)
- Parse COMP-3 (packed decimal) fields
- Parse COMP/BINARY (binary integer) fields
- Parse display format (ASCII/EBCDIC) fields
- Handle record alignment and misalignment detection
- Skip comment/metadata records (extensible pattern detection)

### Step 3: Port ASCII File Normalization

1. Port `_normalize_ascii_file()` method
2. Port `_find_ascii_data_start_extensible()` method
3. Port `_detect_and_strip_prefix_extensible()` method
4. Port `_strip_record_prefixes_extensible()` method

**Key Requirements**:
- Remove newlines between records (fixed-width records should not have newlines)
- Find first valid data record (skip headers/comments using extensible patterns)
- Detect and strip record prefixes (e.g., "POL001", "POL002") using spacing detection
- Use extensible pattern matching (not file-specific)
- **Best Practice**: Only normalize ASCII files (detect encoding first, skip normalization for EBCDIC)
- **Best Practice**: Preserve field boundaries - don't remove newlines that are part of field data (rare but possible)
- **Best Practice**: Validate normalization results - ensure record length matches copybook after normalization

**ASCII Normalization Best Practices** (Based on Industry Standards):
- **When Required**: ASCII fixed-width files that have newlines between records or header/comment sections
- **When NOT Required**: 
  - Pure binary/EBCDIC files (no character translation needed)
  - Already-normalized ASCII files (no newlines, no headers)
  - Files where copybook indicates variable-length records (different handling)
- **Encoding Detection**: Detect ASCII vs EBCDIC before normalization (>80% printable ASCII = ASCII file)
- **Header Detection**: Use extensible patterns (comment markers, field name matching, type validation)
- **Prefix Detection**: Use spacing-based detection (find patterns, calculate spacing, infer prefix length)
- **Validation**: After normalization, verify first few records match copybook structure

### Step 4: Port Field Validation

1. Port `_validate_field_against_copybook()` method

**Key Requirements**:
- Validate field length matches copybook
- Validate data type (numeric vs string)
- Detect copybook/file mismatches
- Report data quality issues (don't try to "fix" them)

### Step 5: Port Utility Methods

1. Port `_records_to_text()` method
2. Ensure all helper methods are ported

**Helper Methods Checklist**:
- ✅ `_get_len_for_comp_binary()` - Calculate byte length for COMP/BINARY fields
- ✅ `_ebcdic_to_decimal()` - Convert EBCDIC-encoded bytes to decimal
- ✅ `_unpack_hex_array()` - Unpack binary/COMP fields
- ✅ `_unpack_comp3_number()` - Unpack COMP-3 (packed decimal) numbers
- ✅ `_custom_encoder()` - Clean EBCDIC strings (remove @ symbols, control chars)
- ✅ `_records_to_text()` - Convert records to text representation
- ✅ `_validate_record_length()` - Validate record length matches copybook (if present in legacy)

### Step 6: Integrate with Metadata Extractor

The `MetadataExtractor` is already initialized and used. Ensure validation rules are extracted BEFORE parsing and included in the result.

### Step 7: Map Return Format to FileParsingResult

**CRITICAL**: The legacy implementation returns a dict, but we must return `FileParsingResult`.

**Return Format Mapping**:

```python
# Legacy format
{
    "success": True,
    "text": text_content,
    "tables": [{"data": records, "columns": [...], "row_count": N}],
    "records": [...],
    "data": pd.DataFrame(...),  # Optional
    "metadata": {...},
    "validation_rules": {...}
}

# FileParsingResult format
FileParsingResult(
    success=True,
    text_content=text_content,  # From "text"
    structured_data={
        "tables": tables,  # From "tables" (list of table dicts)
        "records": records,  # From "records" (list of record dicts)
        "dataframe": data  # From "data" (if pandas DataFrame available)
    },
    metadata=metadata,  # From "metadata"
    validation_rules=validation_rules  # From "validation_rules"
)
```

**Key Mapping Rules**:
- `text` → `text_content` (string)
- `tables` → `structured_data["tables"]` (list of table dicts)
- `records` → `structured_data["records"]` (list of record dicts)
- `data` (DataFrame) → `structured_data["dataframe"]` (if available)
- `metadata` → `metadata` (dict)
- `validation_rules` → `validation_rules` (dict)

## Critical Implementation Details

### Code Page/CCSID Handling

**Best Practice**: Support multiple EBCDIC code pages and allow configuration.

```python
# Default code page (from options or default)
codepage = options.get("codepage", "cp037")  # IBM-037 (US English)

# Supported code pages:
# - cp037 (IBM-037, US English) - DEFAULT
# - cp1047 (IBM-1047, Latin-1)
# - cp500 (IBM-500, EBCDIC International)
# - cp1140 (IBM-1140, Euro symbol)

# Use codecs.decode() for EBCDIC→Unicode conversion
try:
    decoded_text = codecs.decode(ebcdic_bytes, codepage, errors='ignore')
except LookupError:
    self.logger.warning(f"Unknown code page {codepage}, falling back to cp037")
    decoded_text = codecs.decode(ebcdic_bytes, "cp037", errors='ignore')
```

**Important**: 
- Only apply code page conversion to TEXT fields (PIC X, PIC A)
- Do NOT apply to numeric fields (COMP-3, COMP, BINARY) - these are binary
- Display format numeric fields (PIC 9) may need conversion for parsing

### Field-Type-Aware Normalization

**Critical**: Different field types require different handling:

1. **Text Fields (PIC X, PIC A)**:
   - Apply EBCDIC→ASCII/Unicode conversion using code page
   - Clean control characters, @ symbols, etc.
   - Preserve field boundaries (don't collapse spaces in fixed-width)

2. **Numeric Fields - Binary (COMP, COMP-3, BINARY)**:
   - NO character translation (these are binary representations)
   - Decode using binary unpacking methods
   - Handle endianness (typically big-endian for mainframe)

3. **Numeric Fields - Display Format (PIC 9)**:
   - Apply encoding conversion (EBCDIC→ASCII) if needed
   - Parse as integer/float after conversion
   - Handle EBCDIC digit encoding (0xF0-0xF9)

### COMP-3 (Packed Decimal) Handling

```python
# For COMP-3, count only digits (9s), not sign character (S) or V
expanded_pic = pic_info.get('expanded_pic', '')
digit_count = len([c for c in expanded_pic if c in '9Z'])
if digit_count > 0:
    field_length = int(math.ceil((digit_count + 1) / 2))
```

### COMP/BINARY Handling

```python
# For COMP/BINARY, count only digits (9s), not sign character (S)
expanded_pic = pic_info.get('expanded_pic', '')
digit_count = len([c for c in expanded_pic if c in '9Z'])
if digit_count > 0:
    field_length = self._get_len_for_comp_binary(digit_count)
```

### ASCII vs EBCDIC Detection

```python
# Detect ASCII files
if len(binary_data) > 100:
    ascii_bytes = sum(1 for b in binary_data[:100] if 0x20 <= b <= 0x7E)
    if ascii_bytes / 100 > 0.8:  # >80% ASCII printable
        is_ascii_file = True
```

### Record Alignment

- Trust the copybook as the source of truth
- Read fields sequentially
- Handle misalignment gracefully (log warnings, don't crash)
- For EBCDIC files, use actual bytes_read as record length if misaligned
- For ASCII files, use normalization to handle prefixes/newlines

### ASCII Normalization Complexity Review

**Assessment**: The ASCII normalization logic is **required and appropriate** for ASCII fixed-width mainframe files, but can be **simplified and improved**.

**Current Approach** (from legacy):
1. Remove all newlines (simple replace)
2. Find data start using pattern matching and heuristics
3. Detect and strip record prefixes using spacing detection

**Issues Identified**:
1. **Newline Removal**: Too aggressive - removes ALL newlines. Should only remove newlines at record boundaries.
2. **Prefix Detection**: Uses file-specific patterns (POL, REC) - not truly extensible.
3. **Header Detection**: Complex heuristics that may be over-engineered.

**Recommended Improvements**:
1. **Smarter Newline Removal**: 
   - Only remove newlines that appear at record boundaries (every N bytes where N = record_length)
   - Preserve newlines that are part of field data (rare but possible)
   - Validate after removal that record structure is intact

2. **More Extensible Prefix Detection**:
   - Use spacing detection (find repeated patterns, calculate spacing)
   - Don't hard-code "POL" or "REC" patterns
   - Use first field value patterns to detect prefixes

3. **Simplified Header Detection**:
   - Use comment markers (#, *, /, //, REM, etc.)
   - Match copybook field names in header rows
   - Validate data records by checking field types match expected patterns

4. **Performance Optimization**:
   - Only normalize if file is detected as ASCII (>80% printable)
   - Skip normalization if file is already clean (no newlines, no headers)
   - Use streaming/chunked processing for large files

**Best Practice**: 
- Normalization should be **optional** and **detected automatically**
- If file is already clean (no newlines, proper record boundaries), skip normalization
- Log normalization steps for debugging
- Validate normalization results (first few records match copybook)

## Testing Requirements

### Unit Tests

Create tests for:
1. Copybook parsing (simple and complex with OCCURS)
2. Field definition parsing (PIC clauses, COMP, COMP-3, BINARY)
3. Binary record parsing (COMP-3, COMP, BINARY, display format)
4. ASCII file normalization (with and without newlines, headers, prefixes)
5. EBCDIC encoding handling (multiple code pages: cp037, cp1047)
6. Field validation (length mismatches, type mismatches)
7. Code page conversion (EBCDIC→ASCII/Unicode)
8. Field-type-aware normalization (text vs binary fields)
9. Return format mapping (legacy dict → FileParsingResult)

### Integration Tests

Test with:
1. Simple binary file with copybook
2. Binary file with OCCURS clauses
3. ASCII fixed-width file (with newlines, headers, prefixes)
4. ASCII fixed-width file (already clean, no normalization needed)
5. EBCDIC file (cp037)
6. EBCDIC file (cp1047)
7. File with COMP-3 fields
8. File with COMP/BINARY fields
9. File with mixed field types (text, numeric, binary)
10. File with record length mismatches (validation)
11. File with unknown code page (fallback behavior)

### Negative Tests

Test edge cases:
1. Invalid copybook (malformed COBOL)
2. File doesn't match copybook (length mismatches)
3. Unknown code page (fallback to cp037)
4. Invalid characters in text fields (non-printable)
5. Misaligned records (graceful handling)
6. Empty file
7. File with only headers/comments (no data records)

### Test Files

Reference test files from:
- `/home/founders/demoversion/symphainy_source_code/tests/integration/test_complex_parsing_flows.py`
- Legacy test files (if available)

**Test Data Requirements**:
- Known EBCDIC layout + copybook + expected ASCII output
- ASCII files with various normalization needs (newlines, headers, prefixes)
- Files with different code pages (cp037, cp1047)
- Files with edge cases (misalignment, invalid characters, etc.)

## Acceptance Criteria

1. ✅ `CustomMainframeStrategy.parse_file()` successfully parses binary files with copybooks
2. ✅ Supports OCCURS clauses (with recursive expansion)
3. ✅ Supports REDEFINES (removes redefined fields)
4. ✅ Supports COMP-3 (packed decimal) fields
5. ✅ Supports COMP/BINARY fields
6. ✅ Handles ASCII fixed-width files (with normalization)
7. ✅ Handles EBCDIC files (with proper encoding)
8. ✅ Extracts validation rules (88-level fields) via MetadataExtractor
9. ✅ Returns `FileParsingResult` with structured data
10. ✅ All tests pass (unit and integration)
11. ✅ No regressions in existing functionality
12. ✅ Follows new architecture patterns (State Surface, async/await, FileParsingResult)

## Dependencies

- `symphainy_platform.foundations.public_works.protocols.file_parsing_protocol.FileParsingResult`
- `symphainy_platform.foundations.public_works.adapters.file_parsing.metadata_extractor.MetadataExtractor`
- `symphainy_platform.runtime.state_surface.StateSurface`
- Python standard library: `re`, `math`, `codecs`, `io`, `array`
- Optional: `pandas` (for DataFrame support in structured_data, if available)

## Notes

1. **Performance**: The legacy code includes performance warnings for large OCCURS expansions (>1000 fields). Preserve these warnings.

2. **Error Handling**: The legacy code includes extensive error handling and logging. Preserve this for debugging.

3. **Extensibility**: The legacy code uses "extensible" patterns (not file-specific). Preserve this approach.

4. **Validation**: The legacy code validates fields but doesn't try to "fix" data. Preserve this approach (report issues, don't auto-correct).

5. **Encoding**: Support both ASCII and EBCDIC (cp037, cp1047, cp500, cp1140). The legacy code includes encoding detection logic. Allow code page configuration via options.

6. **Record Alignment**: The legacy code handles misalignment gracefully. Preserve this (log warnings, continue parsing).

7. **Code Page Management**: 
   - Support multiple EBCDIC code pages (cp037 default, cp1047, cp500, cp1140)
   - Allow code page specification via options: `options.get("codepage", "cp037")`
   - Detect code page from file metadata if available
   - Log code page used for debugging
   - Fallback to cp037 if unknown code page specified

8. **Field-Type-Aware Normalization**:
   - Text fields (PIC X, PIC A): Apply EBCDIC→ASCII/Unicode conversion
   - Binary fields (COMP, COMP-3, BINARY): NO character translation (decode as binary)
   - Display format numeric (PIC 9): Apply encoding conversion, then parse as number
   - This ensures correctness - mistreating packed decimal as text will corrupt data

9. **ASCII Normalization Improvements**:
   - Only normalize ASCII files (detect encoding first)
   - Smarter newline removal (only at record boundaries)
   - More extensible prefix detection (spacing-based, not file-specific)
   - Simplified header detection (comment markers, field name matching)
   - Skip normalization if file is already clean
   - Validate normalization results (first few records match copybook)

10. **Return Format**: Map legacy dict format to `FileParsingResult` protocol (see Step 7).

## Related Files

- **Current Implementation**: `symphainy_platform/foundations/public_works/adapters/mainframe_parsing/custom_strategy.py`
- **Legacy Source**: `symphainy_source/symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/mainframe_processing_adapter.py`
- **Abstraction**: `symphainy_platform/foundations/public_works/abstractions/mainframe_processing_abstraction.py`
- **Protocol**: `symphainy_platform/foundations/public_works/protocols/file_parsing_protocol.py`
- **Base Class**: `symphainy_platform/foundations/public_works/adapters/mainframe_parsing/base.py`
- **Metadata Extractor**: `symphainy_platform/foundations/public_works/adapters/file_parsing/metadata_extractor.py`

## Questions?

If you encounter issues or need clarification:
1. Review the legacy implementation for reference
2. Check the existing Cobrix strategy for architecture patterns
3. Review the test files for expected behavior
4. Check the `FileParsingResult` protocol for return format

## Estimated Complexity

**High** - This is a complex porting task involving:
- ~2400+ lines of legacy code
- Complex COBOL parsing logic
- Binary data manipulation
- Encoding handling (ASCII/EBCDIC)
- Record alignment logic
- Field validation

**Estimated Time**: 4-8 hours depending on familiarity with COBOL and binary parsing.

## Success Metrics

- All parsing tests pass
- Can parse real-world mainframe files
- Performance is acceptable (< 1 second per 1000 records for typical files)
- Error messages are clear and actionable
- Code follows new architecture patterns

## Summary of Improvements Made to Task Plan

This task plan has been enhanced with the following improvements:

1. **Return Format Mapping** (Step 7): Added explicit mapping from legacy dict format to `FileParsingResult` protocol to ensure correct return structure.

2. **Code Page/CCSID Handling**: Added support for multiple EBCDIC code pages (cp037, cp1047, cp500, cp1140) with configuration via options and automatic fallback.

3. **Field-Type-Aware Normalization**: Clarified that different field types require different handling:
   - Text fields: Apply EBCDIC→ASCII/Unicode conversion
   - Binary fields (COMP, COMP-3, BINARY): NO character translation
   - Display format numeric: Apply encoding conversion, then parse

4. **ASCII Normalization Review**: 
   - Assessed that normalization is required and appropriate
   - Identified improvements: smarter newline removal, more extensible prefix detection, simplified header detection
   - Added best practices: only normalize when needed, validate results, skip if already clean

5. **Helper Methods Checklist**: Added complete checklist of all helper methods to ensure nothing is missed.

6. **Enhanced Testing Requirements**: 
   - Added negative tests for edge cases
   - Added tests for code page handling
   - Added tests for field-type-aware normalization
   - Added tests for return format mapping

7. **Implementation Details**: Added detailed sections on:
   - Code page handling with examples
   - Field-type-aware normalization
   - ASCII normalization complexity review with recommendations

These improvements ensure the implementation will be robust, maintainable, and correctly handle real-world mainframe files with proper encoding, normalization, and field-type awareness.
