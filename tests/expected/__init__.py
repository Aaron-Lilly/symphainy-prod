"""
Expected outputs and validation rules for integration tests.

This module provides:
- Expected outputs for test files (CSV, JSON, PDF, etc.)
- Validation functions to compare actual vs expected results
- Quality checks to verify platform correctness

Usage:
    from tests.expected.validation_rules import validate_csv_parse, ValidationResult
    
    result = await parse_file("sample.csv")
    validation = validate_csv_parse(result, "sample.csv")
    
    assert validation.is_valid, f"Errors: {validation.errors}"
"""

from tests.expected.validation_rules import (
    ValidationResult,
    validate_csv_parse,
    validate_json_parse,
    validate_file_upload,
    validate_parse_result_structure,
    validate_execution_status,
    validate_upload_and_parse_flow,
    load_expected,
)

__all__ = [
    "ValidationResult",
    "validate_csv_parse",
    "validate_json_parse",
    "validate_file_upload",
    "validate_parse_result_structure",
    "validate_execution_status",
    "validate_upload_and_parse_flow",
    "load_expected",
]
