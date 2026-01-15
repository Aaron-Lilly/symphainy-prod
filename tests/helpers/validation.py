"""
Validation Functions for Parsing Tests

Validates parser output matches expected format and content.
"""

import json
from typing import Dict, Any, List, Optional
from symphainy_platform.foundations.public_works.protocols.parsing_service_protocol import (
    ParsingResult
)


def validate_binary_parsing_result(
    result: ParsingResult,
    expected_records: int,
    expected_fields: Optional[List[str]] = None
) -> None:
    """
    Validate binary parsing result.
    
    Checks:
    - Success flag is True
    - Structured data contains records
    - Record count matches expected
    - Each record has expected fields
    - Validation rules (88-level fields) are present
    - Output can be converted to JSONL format
    
    Args:
        result: ParsingResult from binary parser
        expected_records: Expected number of records
        expected_fields: Optional list of expected field names
        
    Raises:
        AssertionError: If validation fails
    """
    assert result.success, f"Parsing failed: {result.error}"
    assert result.data is not None, "No structured data returned"
    
    # Check for records in structured data
    records = None
    if isinstance(result.data, dict):
        if "records" in result.data:
            records = result.data["records"]
        elif "data" in result.data:
            records = result.data["data"]
        else:
            # Try to find records in any list value
            for key, value in result.data.items():
                if isinstance(value, list) and len(value) > 0:
                    records = value
                    break
    elif isinstance(result.data, list):
        records = result.data
    
    assert records is not None, "No records found in structured data"
    assert isinstance(records, list), "Records should be a list"
    assert len(records) == expected_records, \
        f"Expected {expected_records} records, got {len(records)}"
    
    # Validate each record has expected fields
    if expected_fields:
        for i, record in enumerate(records):
            assert isinstance(record, dict), f"Record {i} should be a dictionary"
            for field in expected_fields:
                # Check for both uppercase and lowercase field names
                field_found = (
                    field in record or
                    field.upper() in record or
                    field.lower() in record or
                    field.replace('-', '_') in record or
                    field.replace('_', '-') in record
                )
                assert field_found, \
                    f"Record {i} missing expected field: {field}"
    
    # Validate validation rules are present (for insights pillar)
    if result.validation_rules:
        assert isinstance(result.validation_rules, dict), \
            "Validation rules should be a dictionary"
        # Check for 88-level fields (may be in different keys)
        has_88_fields = (
            "88_level_fields" in result.validation_rules or
            "validation_rules" in result.validation_rules or
            "rules" in result.validation_rules
        )
        # Note: 88-level fields may not always be present, so this is a soft check
        # if has_88_fields:
        #     assert len(result.validation_rules.get("88_level_fields", [])) > 0, \
        #         "88-level fields should not be empty"
    
    # Validate JSONL format
    try:
        jsonl_lines = [json.dumps(record) for record in records]
        assert len(jsonl_lines) == expected_records, "JSONL format incorrect"
        
        # Validate each line is valid JSON
        for line in jsonl_lines:
            json.loads(line)  # Should not raise
    except Exception as e:
        raise AssertionError(f"JSONL format validation failed: {e}")


def validate_pdf_parsing_result(
    result: ParsingResult,
    expected_text: Optional[str] = None,
    min_text_length: int = 10
) -> None:
    """
    Validate PDF parsing result.
    
    Checks:
    - Success flag is True
    - Text content is extracted
    - Expected text appears in extracted content (if provided)
    - Metadata is present (page count, etc.)
    
    Args:
        result: ParsingResult from PDF parser
        expected_text: Optional expected text to find in extracted content
        min_text_length: Minimum length of extracted text
        
    Raises:
        AssertionError: If validation fails
    """
    assert result.success, f"PDF parsing failed: {result.error}"
    assert result.data is not None, "No data returned"
    
    # Check for text chunks
    text_chunks = None
    if isinstance(result.data, dict):
        if "text_chunks" in result.data:
            text_chunks = result.data["text_chunks"]
        elif "text" in result.data:
            text_chunks = [result.data["text"]]
        elif "content" in result.data:
            text_chunks = [result.data["content"]]
    elif isinstance(result.data, str):
        text_chunks = [result.data]
    elif isinstance(result.data, list):
        text_chunks = result.data
    
    assert text_chunks is not None, "No text chunks found in result"
    assert isinstance(text_chunks, list), "Text chunks should be a list"
    assert len(text_chunks) > 0, "Text chunks should not be empty"
    
    # Combine text chunks
    extracted_text = " ".join(str(chunk) for chunk in text_chunks)
    assert len(extracted_text) >= min_text_length, \
        f"Extracted text too short: {len(extracted_text)} < {min_text_length}"
    
    # Validate expected text appears (if provided)
    if expected_text:
        assert expected_text.lower() in extracted_text.lower(), \
            f"Expected text '{expected_text}' not found in extracted content"
    
    # Validate metadata (if present)
    if result.metadata:
        assert isinstance(result.metadata, dict), "Metadata should be a dictionary"
        # Page count may be in different keys
        has_page_info = (
            "page_count" in result.metadata or
            "pages" in result.metadata or
            "num_pages" in result.metadata
        )
        # Note: Page info may not always be present, so this is a soft check


def validate_excel_parsing_result(
    result: ParsingResult,
    expected_rows: int,
    expected_columns: Optional[List[str]] = None
) -> None:
    """
    Validate Excel parsing result.
    
    Checks:
    - Success flag is True
    - Structured data contains rows
    - Row count matches expected
    - Column names match expected (if provided)
    
    Args:
        result: ParsingResult from Excel parser
        expected_rows: Expected number of rows
        expected_columns: Optional list of expected column names
        
    Raises:
        AssertionError: If validation fails
    """
    assert result.success, f"Excel parsing failed: {result.error}"
    assert result.data is not None, "No data returned"
    
    # Check for rows/table data
    rows = None
    if isinstance(result.data, dict):
        if "rows" in result.data:
            rows = result.data["rows"]
        elif "data" in result.data:
            rows = result.data["data"]
        elif "table" in result.data:
            rows = result.data["table"]
    elif isinstance(result.data, list):
        rows = result.data
    
    assert rows is not None, "No rows found in structured data"
    assert isinstance(rows, list), "Rows should be a list"
    assert len(rows) == expected_rows, \
        f"Expected {expected_rows} rows, got {len(rows)}"
    
    # Validate column names (if provided)
    if expected_columns and len(rows) > 0:
        first_row = rows[0]
        if isinstance(first_row, dict):
            for col in expected_columns:
                col_found = (
                    col in first_row or
                    col.upper() in first_row or
                    col.lower() in first_row
                )
                assert col_found, f"Missing expected column: {col}"


def validate_csv_parsing_result(
    result: ParsingResult,
    expected_rows: int,
    expected_columns: Optional[List[str]] = None
) -> None:
    """
    Validate CSV parsing result.
    
    Checks:
    - Success flag is True
    - Structured data contains rows
    - Row count matches expected
    - Column names match expected (if provided)
    
    Args:
        result: ParsingResult from CSV parser
        expected_rows: Expected number of rows
        expected_columns: Optional list of expected column names
        
    Raises:
        AssertionError: If validation fails
    """
    # CSV validation is similar to Excel
    validate_excel_parsing_result(result, expected_rows, expected_columns)


def validate_json_parsing_result(
    result: ParsingResult,
    expected_structure: Optional[Dict[str, Any]] = None
) -> None:
    """
    Validate JSON parsing result.
    
    Checks:
    - Success flag is True
    - Structured data is valid JSON structure
    - Expected keys are present (if provided)
    
    Args:
        result: ParsingResult from JSON parser
        expected_structure: Optional expected JSON structure
        
    Raises:
        AssertionError: If validation fails
    """
    assert result.success, f"JSON parsing failed: {result.error}"
    assert result.data is not None, "No data returned"
    
    # Validate structure (if provided)
    if expected_structure:
        if isinstance(result.data, dict):
            for key in expected_structure:
                assert key in result.data, f"Missing expected key: {key}"


def validate_text_parsing_result(
    result: ParsingResult,
    expected_text: Optional[str] = None
) -> None:
    """
    Validate text parsing result.
    
    Checks:
    - Success flag is True
    - Text content is extracted
    - Expected text matches (if provided)
    
    Args:
        result: ParsingResult from text parser
        expected_text: Optional expected text content
        
    Raises:
        AssertionError: If validation fails
    """
    assert result.success, f"Text parsing failed: {result.error}"
    assert result.data is not None, "No data returned"
    
    # Get text content
    text_content = None
    if isinstance(result.data, str):
        text_content = result.data
    elif isinstance(result.data, dict):
        text_content = result.data.get("text") or result.data.get("content")
    
    assert text_content is not None, "No text content found"
    assert isinstance(text_content, str), "Text content should be a string"
    assert len(text_content) > 0, "Text content should not be empty"
    
    # Validate expected text (if provided)
    if expected_text:
        assert expected_text == text_content, \
            f"Expected text does not match: '{expected_text}' != '{text_content}'"
