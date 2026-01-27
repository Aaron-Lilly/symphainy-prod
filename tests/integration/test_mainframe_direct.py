"""
Direct Mainframe Parsing Test

Tests mainframe parsing directly with the abstraction to validate
standardized output format for Insurance use case.
"""

import sys
import os
import asyncio
import json
import uuid

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from symphainy_platform.foundations.public_works.protocols.file_parsing_protocol import (
    FileParsingResult,
    FileParsingRequest
)
from symphainy_platform.foundations.public_works.foundation_service import PublicWorksFoundationService
from symphainy_platform.foundations.public_works.abstractions.file_storage_abstraction import FileStorageAbstraction
from tests.fixtures.file_fixtures import create_test_binary_file_with_copybook


class InMemoryFileStorage:
    """Simple in-memory file storage for testing."""
    
    def __init__(self):
        self._files = {}
    
    async def upload_file(self, file_data: bytes, storage_path: str, metadata: dict = None) -> bool:
        """Store file in memory."""
        self._files[storage_path] = {
            "data": file_data,
            "metadata": metadata or {}
        }
        return True
    
    async def download_file(self, storage_path: str) -> bytes:
        """Retrieve file from memory."""
        if storage_path in self._files:
            return self._files[storage_path]["data"]
        return None
    
    async def delete_file(self, storage_path: str) -> bool:
        """Delete file from memory."""
        if storage_path in self._files:
            del self._files[storage_path]
            return True
        return False


def validate_standardized_output(result: FileParsingResult, expected_type: str) -> tuple[bool, list[str]]:
    """Validate FileParsingResult matches standardized format."""
    errors = []
    
    if not result.success:
        errors.append(f"Parsing failed: {result.error}")
        return False, errors
    
    # Check parsing_type
    if result.parsing_type != expected_type:
        errors.append(f"parsing_type: expected '{expected_type}', got '{result.parsing_type}'")
    
    # Check metadata
    if not result.metadata:
        errors.append("metadata is None")
    else:
        if result.metadata.get("parsing_type") != expected_type:
            errors.append(f"metadata.parsing_type: expected '{expected_type}', got '{result.metadata.get('parsing_type')}'")
        
        if "structure" not in result.metadata:
            errors.append("metadata.structure is missing")
        elif not isinstance(result.metadata["structure"], dict):
            errors.append("metadata.structure must be a dict")
    
    # Check structured_data
    if result.structured_data:
        if not isinstance(result.structured_data, dict):
            errors.append("structured_data must be a dict")
        elif "format" not in result.structured_data:
            errors.append("structured_data.format is missing")
        elif result.structured_data["format"] != expected_type:
            errors.append(f"structured_data.format: expected '{expected_type}', got '{result.structured_data['format']}'")
    
    return len(errors) == 0, errors


async def test_mainframe_parsing_direct():
    """Test mainframe parsing directly."""
    print("\n" + "=" * 70)
    print("🧪 MAINFRAME PARSING DIRECT TEST")
    print("=" * 70)
    
    # Create in-memory file storage
    file_storage = InMemoryFileStorage()
    
    # Create State Surface with file storage
    from symphainy_platform.runtime.state_surface import StateSurface
    state_surface = StateSurface(use_memory=True, file_storage=file_storage)
    
    # Create Public Works Foundation
    print("\n📦 Initializing Public Works Foundation...")
    public_works = PublicWorksFoundationService(config={})
    await public_works.initialize()
    public_works.set_state_surface(state_surface)
    
    # Get mainframe processing abstraction
    mainframe_abstraction = public_works.get_mainframe_processing_abstraction()
    if not mainframe_abstraction:
        print("  ❌ Mainframe processing abstraction not available")
        return False
    
    print("  ✅ Mainframe processing abstraction available")
    
    # Create test files
    print("\n📁 Creating test files...")
    binary_data, copybook_content = create_test_binary_file_with_copybook()
    print(f"  ✅ Binary file: {len(binary_data)} bytes (3 records)")
    print(f"  ✅ Copybook: {len(copybook_content)} characters")
    
    # Store files in file storage and create references
    tenant_id = "test_tenant"
    session_id = "test_session"
    
    print("\n💾 Storing files...")
    # Store binary file
    binary_storage_path = f"test/{tenant_id}/{session_id}/test_file.bin"
    await file_storage.upload_file(binary_data, binary_storage_path)
    binary_file_ref = f"file:{tenant_id}:{session_id}:{uuid.uuid4().hex[:8]}"
    await state_surface.store_file_reference(
        session_id=session_id,
        tenant_id=tenant_id,
        file_reference=binary_file_ref,
        storage_location=binary_storage_path,
        filename="test_file.bin"
    )
    print(f"  ✅ Binary file stored: {binary_file_ref}")
    
    # Store copybook
    copybook_storage_path = f"test/{tenant_id}/{session_id}/copybook.cpy"
    await file_storage.upload_file(copybook_content.encode('utf-8'), copybook_storage_path)
    copybook_file_ref = f"file:{tenant_id}:{session_id}:{uuid.uuid4().hex[:8]}"
    await state_surface.store_file_reference(
        session_id=session_id,
        tenant_id=tenant_id,
        file_reference=copybook_file_ref,
        storage_location=copybook_storage_path,
        filename="copybook.cpy"
    )
    print(f"  ✅ Copybook stored: {copybook_file_ref}")
    
    # Create parsing request
    print("\n🔄 Parsing mainframe file...")
    request = FileParsingRequest(
        file_reference=binary_file_ref,
        copybook_reference=copybook_file_ref,
        filename="test_file.bin",
        state_surface=state_surface
    )
    
    # Parse file
    try:
        result = await mainframe_abstraction.parse_file(request)
        
        if not result.success:
            print(f"  ❌ Parsing failed: {result.error}")
            return False
        
        print("  ✅ Parsing succeeded!")
        
        # Validate standardized format
        print("\n🔍 Validating standardized output format...")
        is_valid, errors = validate_standardized_output(result, "mainframe")
        
        if not is_valid:
            print("  ❌ Format validation failed:")
            for error in errors:
                print(f"     - {error}")
            return False
        
        print("  ✅ Format validation passed!")
        
        # Show results
        print("\n📊 Parsing Results:")
        print(f"  - parsing_type: {result.parsing_type}")
        print(f"  - text_content: {type(result.text_content).__name__} ({len(result.text_content) if result.text_content else 0} chars)")
        print(f"  - structured_data.format: {result.structured_data.get('format') if result.structured_data else None}")
        
        # Check structure metadata
        structure = result.metadata.get("structure", {})
        records = structure.get("records", [])
        print(f"  - metadata.structure.records: {len(records)} records")
        
        # Check structured_data
        if result.structured_data:
            parsed_records = result.structured_data.get("records", [])
            print(f"  - structured_data.records: {len(parsed_records)} records")
            
            # Show first record
            if parsed_records:
                first_record = parsed_records[0]
                print(f"\n  📋 First Record Sample:")
                record_str = json.dumps(first_record, indent=6)
                print(f"     {record_str[:300]}...")
        
        # Check validation_rules (88-level fields)
        if result.validation_rules:
            print(f"\n  ✅ Validation rules extracted: {len(result.validation_rules)} rules")
        
        print("\n" + "=" * 70)
        print("✅ MAINFRAME PARSING TEST PASSED")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"  ❌ Exception during parsing: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run test."""
    print("=" * 70)
    print("🚀 MAINFRAME PARSING DIRECT INTEGRATION TEST")
    print("=" * 70)
    print("\nTesting mainframe parsing for Insurance use case")
    
    try:
        result = await test_mainframe_parsing_direct()
        if result:
            print("\n🎉 Test passed! Foundation is validated for Insurance use case.")
            return 0
        else:
            print("\n⚠️  Test failed.")
            return 1
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
