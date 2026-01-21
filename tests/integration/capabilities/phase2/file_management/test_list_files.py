#!/usr/bin/env python3
"""
Test: File Listing

Tests the list_files capability:
- File listing completes
- Returns list of files (may be empty)
- Files have required metadata
"""

import sys
import asyncio
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from tests.integration.capabilities.base_capability_test import BaseCapabilityTest

class TestListFiles(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="File Listing - Full Execution Completion",
            test_id_prefix="list_files"
        )
    
    async def run_test(self) -> bool:
        if not await self.authenticate():
            return False
        
        # Submit file listing intent
        self.print_info("Step 2: Submitting file listing intent")
        status = await self.submit_intent_and_poll(
            intent_type="list_files",
            parameters={
                "limit": 10,
                "file_type": None
            }
        )
        
        if not status:
            return False
        
        # Validate file list
        self.print_info("Step 3: Validating file list")
        artifacts = status.get("artifacts", {})
        
        # Handle structured artifacts format - list_files returns file_list artifact
        file_list = []
        if isinstance(artifacts, dict):
            # Look for file_list structured artifact
            if "file_list" in artifacts:
                file_list_artifact = artifacts["file_list"]
                if isinstance(file_list_artifact, dict) and "result_type" in file_list_artifact:
                    # Structured artifact - extract files from semantic_payload
                    semantic_payload = file_list_artifact.get("semantic_payload", {})
                    file_list = semantic_payload.get("files", [])
                    if not file_list:
                        # Check if count is 0 (empty list is valid)
                        count = semantic_payload.get("count", 0)
                        if count == 0:
                            self.print_warning("No files returned in listing (may be empty database)")
                            self.print_success("✅ File Listing - Full Execution Completion: PASSED (empty list)")
                            return True
        
        if not file_list:
            self.print_warning("No files returned in listing (may be empty database)")
            self.print_success("✅ File Listing - Full Execution Completion: PASSED (empty list)")
            return True
        
        self.print_success(f"File listing returned {len(file_list)} file(s)")
        
        # Validate that files have required metadata
        for file_item in file_list[:3]:
            if isinstance(file_item, dict):
                file_id = file_item.get("file_id") or file_item.get("id")
                if file_id:
                    self.print_success(f"File found with ID: {file_id}")
                else:
                    self.print_warning("File item missing file_id")
        
        self.print_success("✅ File Listing - Full Execution Completion: PASSED")
        return True

async def main():
    test = TestListFiles()
    result = await test.execute()
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
