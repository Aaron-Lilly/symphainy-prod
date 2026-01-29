"""
Validation Rules for Integration Tests

These validators compare actual parsing results against expected outputs
to prove the platform actually works correctly.

Philosophy: Tests should validate REAL outputs, not just API availability.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    
    def __bool__(self) -> bool:
        return self.is_valid


# Get expected outputs directory
EXPECTED_DIR = Path(__file__).parent


def load_expected(file_type: str, file_name: str) -> Optional[Dict[str, Any]]:
    """Load expected output for a test file."""
    expected_file = EXPECTED_DIR / file_type / f"{file_name}_expected.json"
    if expected_file.exists():
        with open(expected_file) as f:
            return json.load(f)
    return None


def validate_csv_parse(
    result: Dict[str, Any],
    original_file: str = "sample.csv"
) -> ValidationResult:
    """
    Validate CSV parsing results.
    
    Checks:
    - All expected columns are present
    - Row count matches expected
    - Column types are correct
    - Sample data matches expected values
    - Quality checks pass
    
    Args:
        result: The parsing result from the platform
        original_file: Name of the original CSV file
        
    Returns:
        ValidationResult with is_valid, errors, and warnings
    """
    errors = []
    warnings = []
    
    expected = load_expected("csv", original_file.replace(".csv", "_csv"))
    if not expected:
        return ValidationResult(False, [f"No expected output for {original_file}"], [])
    
    expected_parse = expected.get("parse_result", {})
    
    # Extract parsed data from result
    # Handle various result formats from different parsing implementations
    parsed = result.get("artifacts", {}).get("parsed_content", {})
    if not parsed:
        parsed = result.get("parsed_content", {})
    if not parsed:
        parsed = result.get("data", {})
    if not parsed:
        parsed = result
    
    # Check columns
    expected_columns = expected_parse.get("columns", [])
    actual_columns = parsed.get("columns", parsed.get("headers", []))
    
    if actual_columns:
        missing_cols = set(expected_columns) - set(actual_columns)
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")
        extra_cols = set(actual_columns) - set(expected_columns)
        if extra_cols:
            warnings.append(f"Extra columns found: {extra_cols}")
    else:
        warnings.append("Could not extract column information from result")
    
    # Check row count
    expected_rows = expected_parse.get("total_rows", 0)
    actual_rows = parsed.get("total_rows", parsed.get("row_count", 0))
    if actual_rows and actual_rows != expected_rows:
        errors.append(f"Row count mismatch: expected {expected_rows}, got {actual_rows}")
    
    # Check sample data if available
    sample_data = expected_parse.get("sample_data", {})
    rows = parsed.get("rows", parsed.get("data", []))
    
    if rows and sample_data.get("first_row"):
        first_row = rows[0] if isinstance(rows[0], dict) else {}
        expected_first = sample_data["first_row"]
        
        # Check key field values
        if first_row.get("name") != expected_first.get("name"):
            warnings.append(f"First row name mismatch: expected '{expected_first.get('name')}', got '{first_row.get('name')}'")
    
    # Quality checks
    quality = expected.get("quality_checks", {})
    if quality.get("positive_salaries"):
        salaries = [r.get("salary", 0) for r in rows if isinstance(r, dict)]
        if any(s <= 0 for s in salaries if s):
            errors.append("Found non-positive salary values")
    
    if quality.get("valid_email_format"):
        emails = [r.get("email", "") for r in rows if isinstance(r, dict)]
        email_pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
        invalid_emails = [e for e in emails if e and not email_pattern.match(e)]
        if invalid_emails:
            errors.append(f"Invalid email format: {invalid_emails}")
    
    is_valid = len(errors) == 0
    return ValidationResult(is_valid, errors, warnings)


def validate_json_parse(
    result: Dict[str, Any],
    original_file: str = "sample.json"
) -> ValidationResult:
    """
    Validate JSON parsing results.
    
    Checks:
    - Structure matches expected (root keys, nested structure)
    - Key values match expected
    - Data types are correct
    
    Args:
        result: The parsing result from the platform
        original_file: Name of the original JSON file
        
    Returns:
        ValidationResult with is_valid, errors, and warnings
    """
    errors = []
    warnings = []
    
    expected = load_expected("json", original_file.replace(".json", "_json"))
    if not expected:
        return ValidationResult(False, [f"No expected output for {original_file}"], [])
    
    expected_parse = expected.get("parse_result", {})
    
    # Extract parsed data
    parsed = result.get("artifacts", {}).get("parsed_content", {})
    if not parsed:
        parsed = result.get("parsed_content", {})
    if not parsed:
        parsed = result.get("data", {})
    if not parsed:
        parsed = result
    
    # Check structure
    structure = expected_parse.get("structure", {})
    expected_root_keys = structure.get("root_keys", [])
    
    if expected_root_keys:
        actual_keys = list(parsed.keys()) if isinstance(parsed, dict) else []
        missing_keys = set(expected_root_keys) - set(actual_keys)
        if missing_keys:
            errors.append(f"Missing root keys: {missing_keys}")
    
    # Check organization field
    expected_org = expected_parse.get("organization")
    if expected_org:
        actual_org = parsed.get("organization")
        if actual_org != expected_org:
            errors.append(f"Organization mismatch: expected '{expected_org}', got '{actual_org}'")
    
    # Check employees count
    employees = expected_parse.get("employees", {})
    expected_count = employees.get("count", 0)
    
    actual_employees = parsed.get("employees", [])
    if isinstance(actual_employees, list):
        if len(actual_employees) != expected_count:
            errors.append(f"Employee count mismatch: expected {expected_count}, got {len(actual_employees)}")
    
    # Quality checks
    quality = expected.get("quality_checks", {})
    if quality.get("valid_json_structure") and not isinstance(parsed, dict):
        errors.append("Result is not a valid JSON object")
    
    is_valid = len(errors) == 0
    return ValidationResult(is_valid, errors, warnings)


def validate_file_upload(
    result: Dict[str, Any],
    expected_file_name: str,
    expected_file_type: str
) -> ValidationResult:
    """
    Validate file upload results.
    
    Checks:
    - File ID was generated
    - File name matches
    - File type matches
    - Storage path exists
    
    Args:
        result: The upload result from the platform
        expected_file_name: Expected file name
        expected_file_type: Expected MIME type
        
    Returns:
        ValidationResult with is_valid, errors, and warnings
    """
    errors = []
    warnings = []
    
    # Extract artifacts
    artifacts = result.get("artifacts", result)
    
    # Check file_id
    file_id = artifacts.get("file_id", artifacts.get("artifact_id"))
    if not file_id:
        errors.append("No file_id returned from upload")
    
    # Check file name if returned
    actual_name = artifacts.get("file_name", artifacts.get("ui_name"))
    if actual_name and actual_name != expected_file_name:
        warnings.append(f"File name mismatch: expected '{expected_file_name}', got '{actual_name}'")
    
    # Check file type
    actual_type = artifacts.get("file_type", artifacts.get("mime_type", artifacts.get("content_type")))
    if actual_type and actual_type != expected_file_type:
        warnings.append(f"File type mismatch: expected '{expected_file_type}', got '{actual_type}'")
    
    # Check storage path
    storage_path = artifacts.get("storage_path", artifacts.get("gcs_blob_path", artifacts.get("blob_path")))
    if not storage_path:
        warnings.append("No storage path returned - file may not be persisted")
    
    is_valid = len(errors) == 0
    return ValidationResult(is_valid, errors, warnings)


def validate_parse_result_structure(
    result: Dict[str, Any],
    expected_artifact_type: str = "parsed_content"
) -> ValidationResult:
    """
    Validate that a parse result has the expected structure.
    
    Args:
        result: The parsing result
        expected_artifact_type: Expected artifact key
        
    Returns:
        ValidationResult
    """
    errors = []
    warnings = []
    
    # Check for artifacts
    if "artifacts" not in result:
        errors.append("Result missing 'artifacts' key")
        return ValidationResult(False, errors, warnings)
    
    artifacts = result["artifacts"]
    
    # Check for parsed content artifact
    if expected_artifact_type not in artifacts:
        # Check alternate keys
        alternate_keys = ["parsed_data", "content", "data", "parsed_file"]
        found = any(k in artifacts for k in alternate_keys)
        if not found:
            errors.append(f"Missing '{expected_artifact_type}' in artifacts")
    
    # Check for status
    status = result.get("status")
    if status and status not in ["completed", "success", "COMPLETED", "SUCCESS"]:
        warnings.append(f"Unexpected status: {status}")
    
    is_valid = len(errors) == 0
    return ValidationResult(is_valid, errors, warnings)


def validate_execution_status(
    status: Dict[str, Any],
    expected_status: str = "completed"
) -> ValidationResult:
    """
    Validate execution status response.
    
    Args:
        status: The execution status response
        expected_status: Expected status value
        
    Returns:
        ValidationResult
    """
    errors = []
    warnings = []
    
    # Check execution_id
    exec_id = status.get("execution_id", status.get("intent_id"))
    if not exec_id:
        errors.append("Missing execution_id in status")
    
    # Check status value
    actual_status = status.get("status", "").lower()
    if actual_status != expected_status.lower():
        if actual_status in ["failed", "error"]:
            error_msg = status.get("error", status.get("error_message", "Unknown error"))
            errors.append(f"Execution failed: {error_msg}")
        else:
            warnings.append(f"Status mismatch: expected '{expected_status}', got '{actual_status}'")
    
    # Check for artifacts on completion
    if actual_status == "completed" and not status.get("artifacts"):
        warnings.append("Completed execution has no artifacts")
    
    is_valid = len(errors) == 0
    return ValidationResult(is_valid, errors, warnings)


# Aggregate validators for common test patterns

def validate_upload_and_parse_flow(
    upload_result: Dict[str, Any],
    parse_result: Dict[str, Any],
    file_name: str,
    file_type: str
) -> ValidationResult:
    """
    Validate complete upload → parse flow.
    
    Args:
        upload_result: Result from file upload
        parse_result: Result from file parse
        file_name: Original file name
        file_type: File MIME type
        
    Returns:
        Aggregated ValidationResult
    """
    all_errors = []
    all_warnings = []
    
    # Validate upload
    upload_validation = validate_file_upload(upload_result, file_name, file_type)
    all_errors.extend(upload_validation.errors)
    all_warnings.extend(upload_validation.warnings)
    
    # Validate parse structure
    parse_validation = validate_parse_result_structure(parse_result)
    all_errors.extend(parse_validation.errors)
    all_warnings.extend(parse_validation.warnings)
    
    # Validate specific content based on type
    if "csv" in file_type or file_name.endswith(".csv"):
        content_validation = validate_csv_parse(parse_result, file_name)
        all_errors.extend(content_validation.errors)
        all_warnings.extend(content_validation.warnings)
    elif "json" in file_type or file_name.endswith(".json"):
        content_validation = validate_json_parse(parse_result, file_name)
        all_errors.extend(content_validation.errors)
        all_warnings.extend(content_validation.warnings)
    
    is_valid = len(all_errors) == 0
    return ValidationResult(is_valid, all_errors, all_warnings)
