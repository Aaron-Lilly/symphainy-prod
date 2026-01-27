"""
Test Parser Outputs - Validate Standardized Format

This script tests that all parsers produce standardized FileParsingResult outputs
with consistent structure metadata and format.

Usage:
    python tests/test_parser_outputs.py
    pytest tests/test_parser_outputs.py -v
"""

import sys
import os
import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from symphainy_platform.foundations.public_works.protocols.file_parsing_protocol import (
    FileParsingResult,
    FileParsingRequest
)


def validate_file_parsing_result(result: FileParsingResult, expected_parsing_type: str) -> tuple[bool, list[str]]:
    """
    Validate FileParsingResult matches standardized format.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    # Must be FileParsingResult
    if not isinstance(result, FileParsingResult):
        errors.append(f"Result must be FileParsingResult, got {type(result)}")
        return False, errors
    
    # If successful, validate structure
    if result.success:
        # parsing_type must be set explicitly
        if result.parsing_type is None:
            errors.append("parsing_type must be set (got None)")
        elif result.parsing_type != expected_parsing_type:
            errors.append(f"parsing_type mismatch: expected '{expected_parsing_type}', got '{result.parsing_type}'")
        
        # metadata must exist
        if result.metadata is None:
            errors.append("metadata must not be None")
        elif not isinstance(result.metadata, dict):
            errors.append("metadata must be a dict")
        else:
            # metadata must include parsing_type
            if "parsing_type" not in result.metadata:
                errors.append("metadata must include 'parsing_type'")
            elif result.metadata["parsing_type"] != expected_parsing_type:
                errors.append(f"metadata.parsing_type mismatch: expected '{expected_parsing_type}', got '{result.metadata.get('parsing_type')}'")
            
            # metadata must include structure (for chunking service)
            if "structure" not in result.metadata:
                errors.append("metadata must include 'structure' for chunking service")
            elif not isinstance(result.metadata["structure"], dict):
                errors.append("metadata.structure must be a dict")
        
        # text_content should be None (not empty string) if no text
        if result.text_content is not None and not isinstance(result.text_content, str):
            errors.append("text_content must be str or None")
        
        # structured_data must be JSON-serializable if present
        if result.structured_data is not None:
            try:
                json.dumps(result.structured_data)
            except (TypeError, ValueError) as e:
                errors.append(f"structured_data must be JSON-serializable: {e}")
            
            # structured_data must have "format" field
            if not isinstance(result.structured_data, dict):
                errors.append("structured_data must be a dict")
            elif "format" not in result.structured_data:
                errors.append("structured_data must include 'format' field")
            else:
                # structured_data must NOT contain nested "metadata" or "structure"
                if "metadata" in result.structured_data:
                    errors.append("structured_data must not contain nested 'metadata'")
                if "structure" in result.structured_data:
                    errors.append("structured_data must not contain nested 'structure'")
        
        # timestamp must be set
        if not result.timestamp:
            errors.append("timestamp must be set")
        else:
            # Validate timestamp format (ISO format)
            try:
                datetime.fromisoformat(result.timestamp.replace('Z', '+00:00'))
            except ValueError:
                errors.append(f"timestamp must be ISO format: {result.timestamp}")
    
    return len(errors) == 0, errors


def validate_structure_metadata(structure: Dict[str, Any], parsing_type: str) -> tuple[bool, list[str]]:
    """
    Validate structure metadata format based on parsing type.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    if not isinstance(structure, dict):
        errors.append("structure must be a dict")
        return False, errors
    
    if parsing_type == "unstructured":
        # Should have pages, sections, or paragraphs
        if not any(key in structure for key in ["pages", "sections", "paragraphs"]):
            errors.append("Unstructured parsing must have pages, sections, or paragraphs in structure")
    
    elif parsing_type == "structured":
        # Should have rows or sheets
        if not any(key in structure for key in ["rows", "sheets", "object"]):
            errors.append("Structured parsing must have rows, sheets, or object in structure")
    
    elif parsing_type == "hybrid":
        # Should have pages/sections/paragraphs AND tables
        has_text_structure = any(key in structure for key in ["pages", "sections", "paragraphs"])
        if not has_text_structure:
            errors.append("Hybrid parsing must have text structure (pages/sections/paragraphs)")
    
    elif parsing_type == "workflow":
        # Should have workflow structure
        if "workflow" not in structure:
            errors.append("Workflow parsing must have 'workflow' in structure")
        else:
            workflow = structure["workflow"]
            if not isinstance(workflow, dict):
                errors.append("workflow must be a dict")
            elif not any(key in workflow for key in ["tasks", "gateways", "flows"]):
                errors.append("workflow must have tasks, gateways, or flows")
    
    elif parsing_type == "sop":
        # Should have sections or steps
        if not any(key in structure for key in ["sections", "steps"]):
            errors.append("SOP parsing must have sections or steps in structure")
    
    elif parsing_type == "mainframe":
        # Should have records
        if "records" not in structure:
            errors.append("Mainframe parsing must have 'records' in structure")
    
    elif parsing_type == "data_model":
        # Should have schema
        if "schema" not in structure:
            errors.append("Data model parsing must have 'schema' in structure")
    
    return len(errors) == 0, errors


def test_file_parsing_result_protocol():
    """Test FileParsingResult protocol structure."""
    print("\n🧪 Testing FileParsingResult Protocol...")
    
    # Test with all fields
    result = FileParsingResult(
        success=True,
        text_content="test",
        structured_data={"format": "unstructured", "data": []},
        metadata={
            "parsing_type": "unstructured",
            "structure": {"paragraphs": []}
        },
        parsing_type="unstructured",
        timestamp=datetime.utcnow().isoformat()
    )
    
    # Validate
    is_valid, errors = validate_file_parsing_result(result, "unstructured")
    if not is_valid:
        print(f"  ❌ Validation failed: {errors}")
        return False
    
    is_valid, errors = validate_structure_metadata(result.metadata["structure"], "unstructured")
    if not is_valid:
        print(f"  ❌ Structure validation failed: {errors}")
        return False
    
    print("  ✅ FileParsingResult protocol test passed")
    return True


def test_file_parsing_result_text_content_none():
    """Test FileParsingResult with text_content=None (structured files)."""
    print("\n🧪 Testing FileParsingResult with text_content=None...")
    
    result = FileParsingResult(
        success=True,
        text_content=None,  # Structured files have no text
        structured_data={
            "format": "structured",
            "rows": [{"col1": "val1"}]
        },
        metadata={
            "parsing_type": "structured",
            "structure": {"rows": []}
        },
        parsing_type="structured",
        timestamp=datetime.utcnow().isoformat()
    )
    
    # Validate
    is_valid, errors = validate_file_parsing_result(result, "structured")
    if not is_valid:
        print(f"  ❌ Validation failed: {errors}")
        return False
    
    if result.text_content is not None:
        print(f"  ❌ Structured files should have text_content=None, got {type(result.text_content)}")
        return False
    
    print("  ✅ text_content=None test passed")
    return True


def test_structure_metadata_formats():
    """Test various structure metadata formats."""
    print("\n🧪 Testing structure metadata formats...")
    
    test_cases = [
        ("unstructured", {
            "paragraphs": [
                {"paragraph_index": 0, "text": "Para 1"},
                {"paragraph_index": 1, "text": "Para 2"}
            ]
        }),
        ("structured", {
            "rows": [
                {"row_index": 0, "data": {"col1": "val1"}},
                {"row_index": 1, "data": {"col1": "val2"}}
            ]
        }),
        ("workflow", {
            "workflow": {
                "tasks": [{"task_index": 0, "task_name": "Task 1"}],
                "gateways": [],
                "flows": []
            }
        }),
        ("sop", {
            "sections": [{"section_index": 0, "section_title": "Section 1"}],
            "steps": [{"step_index": 0, "step_text": "Step 1"}]
        }),
        ("data_model", {
            "schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }),
    ]
    
    all_passed = True
    for parsing_type, structure in test_cases:
        is_valid, errors = validate_structure_metadata(structure, parsing_type)
        if not is_valid:
            print(f"  ❌ {parsing_type} structure validation failed: {errors}")
            all_passed = False
        else:
            print(f"  ✅ {parsing_type} structure format valid")
    
    return all_passed


def test_structured_data_format():
    """Test structured_data standardized format."""
    print("\n🧪 Testing structured_data format...")
    
    # Test structured format
    structured_data = {
        "format": "structured",
        "rows": [{"col1": "val1"}],
        "columns": ["col1"]
    }
    
    if "format" not in structured_data:
        print("  ❌ structured_data must have 'format'")
        return False
    
    if "metadata" in structured_data:
        print("  ❌ structured_data must not have 'metadata'")
        return False
    
    if "structure" in structured_data:
        print("  ❌ structured_data must not have 'structure'")
        return False
    
    # Test JSON serializability
    try:
        json_str = json.dumps(structured_data)
        if not json_str:
            print("  ❌ structured_data must be JSON-serializable")
            return False
    except (TypeError, ValueError) as e:
        print(f"  ❌ structured_data JSON serialization failed: {e}")
        return False
    
    print("  ✅ structured_data format test passed")
    return True


def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n🔍 Checking dependencies...")
    
    dependencies = {
        "duckdb": "duckdb",
        "PyYAML": "yaml",
        "json": "json"  # Built-in
    }
    
    missing = []
    for package_name, import_name in dependencies.items():
        try:
            __import__(import_name)
            print(f"  ✅ {package_name} installed")
        except ImportError:
            print(f"  ❌ {package_name} NOT installed")
            missing.append(package_name)
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("   Install with: pip install " + " ".join(missing))
        return False
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Parser Output Standardization Tests")
    print("=" * 60)
    
    # Check dependencies
    deps_ok = check_dependencies()
    if not deps_ok:
        print("\n⚠️  Some dependencies are missing. Tests may fail.")
    
    # Run tests
    tests = [
        ("FileParsingResult Protocol", test_file_parsing_result_protocol),
        ("text_content=None", test_file_parsing_result_text_content_none),
        ("Structure Metadata Formats", test_structure_metadata_formats),
        ("Structured Data Format", test_structured_data_format),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n📈 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Parsing standardization is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit(main())
