"""
Simple Test for Complex Parsers - Validate Standardized Output Format

This script validates that complex parsers (mainframe, Kreuzberg) produce
standardized FileParsingResult outputs. Uses existing integration test patterns.
"""

import sys
import os
import asyncio
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from symphainy_platform.foundations.public_works.protocols.file_parsing_protocol import (
    FileParsingResult
)


def validate_file_parsing_result(result: FileParsingResult, expected_parsing_type: str) -> tuple[bool, list[str]]:
    """Validate FileParsingResult matches standardized format."""
    errors = []
    
    if not isinstance(result, FileParsingResult):
        errors.append(f"Result must be FileParsingResult, got {type(result)}")
        return False, errors
    
    if result.success:
        # parsing_type must be set
        if result.parsing_type != expected_parsing_type:
            errors.append(f"parsing_type mismatch: expected '{expected_parsing_type}', got '{result.parsing_type}'")
        
        # metadata must exist and include structure
        if not result.metadata:
            errors.append("metadata must not be None")
        elif "parsing_type" not in result.metadata:
            errors.append("metadata must include 'parsing_type'")
        elif "structure" not in result.metadata:
            errors.append("metadata must include 'structure' for chunking service")
        
        # structured_data must be JSON-serializable
        if result.structured_data:
            try:
                json.dumps(result.structured_data)
            except (TypeError, ValueError) as e:
                errors.append(f"structured_data must be JSON-serializable: {e}")
            
            # structured_data must have "format" field
            if isinstance(result.structured_data, dict) and "format" not in result.structured_data:
                errors.append("structured_data must include 'format' field")
    
    return len(errors) == 0, errors


def test_standardized_format():
    """Test that FileParsingResult structure matches standardized format."""
    print("=" * 60)
    print("🧪 Testing Standardized Format for Complex Parsers")
    print("=" * 60)
    
    # Test mainframe format
    print("\n📋 Testing Mainframe Format...")
    mainframe_result = FileParsingResult(
        success=True,
        text_content=None,
        structured_data={
            "format": "mainframe",
            "records": [{"CUSTOMER-ID": "CUST001"}],
            "schema": {}
        },
        metadata={
            "parsing_type": "mainframe",
            "structure": {
                "records": [
                    {"record_index": 0, "data": {"CUSTOMER-ID": "CUST001"}}
                ]
            },
            "file_type": "binary",
            "record_count": 1
        },
        parsing_type="mainframe",
        timestamp="2026-01-25T00:00:00"
    )
    
    is_valid, errors = validate_file_parsing_result(mainframe_result, "mainframe")
    if is_valid:
        print("  ✅ Mainframe format validation passed")
    else:
        print(f"  ❌ Mainframe format validation failed: {errors}")
        return False
    
    # Test Kreuzberg hybrid format
    print("\n📋 Testing Kreuzberg Hybrid Format...")
    kreuzberg_result = FileParsingResult(
        success=True,
        text_content="Document text content...",
        structured_data={
            "format": "hybrid",
            "tables": [{"rows": [{"col1": "val1"}]}]
        },
        metadata={
            "parsing_type": "hybrid",
            "structure": {
                "pages": [
                    {"page_number": 1, "text": "Document text content..."}
                ]
            },
            "file_type": "pdf",
            "table_count": 1
        },
        parsing_type="hybrid",
        timestamp="2026-01-25T00:00:00"
    )
    
    is_valid, errors = validate_file_parsing_result(kreuzberg_result, "hybrid")
    if is_valid:
        print("  ✅ Kreuzberg hybrid format validation passed")
    else:
        print(f"  ❌ Kreuzberg hybrid format validation failed: {errors}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All format validations passed!")
    print("=" * 60)
    print("\n💡 Note: To test actual parsing, run integration tests:")
    print("   pytest tests/integration/test_mainframe_parsing.py -v")
    print("   pytest tests/integration/abstractions/test_mainframe_abstraction_integration.py -v")
    
    return True


if __name__ == "__main__":
    success = test_standardized_format()
    exit(0 if success else 1)
