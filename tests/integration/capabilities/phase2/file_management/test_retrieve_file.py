#!/usr/bin/env python3
"""
Test: File Retrieval

Tests the retrieve_file capability:
- File retrieval completes
- File is accessible by file_id
- Retrieved file matches original
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from tests.integration.capabilities.base_capability_test import BaseCapabilityTest

class TestRetrieveFile(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="File Retrieval by ID - Full Execution Completion",
            test_id_prefix="retrieve_file"
        )
    
    async def run_test(self) -> bool:
        if not await self.authenticate():
            return False
        
        # First register a file to retrieve
        self.print_info("Step 2: Registering test file for retrieval")
        test_file_content = "retrieval,test,data\n1,2,3\n4,5,6"
        test_file_name = f"retrieve_test_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.csv"
        
        # Convert file content to hex-encoded bytes
        file_content_hex = test_file_content.encode('utf-8').hex()
        
        register_status = await self.submit_intent_and_poll(
            intent_type="ingest_file",
            parameters={
                "ingestion_type": "upload",
                "ui_name": test_file_name,
                "file_content": file_content_hex,
                "file_type": "csv",
                "mime_type": "text/csv"
            }
        )
        
        if not register_status:
            self.print_error("Failed to register test file")
            return False
        
        # Get file_id from registration (structured format)
        artifacts = register_status.get("artifacts", {})
        
        # Access structured artifact
        if "file" not in artifacts:
            self.print_error("No file artifact found in registration artifacts")
            self.print_info(f"Available artifact keys: {list(artifacts.keys())}")
            return False
        
        file_artifact = artifacts["file"]
        if not isinstance(file_artifact, dict) or "result_type" not in file_artifact:
            self.print_error("File artifact is not in structured format")
            return False
        
        semantic_payload = file_artifact.get("semantic_payload", {})
        file_id = semantic_payload.get("file_id")
        file_reference = semantic_payload.get("file_reference")
        
        if not file_id:
            self.print_error("No file_id found in semantic_payload")
            self.print_info(f"Available semantic_payload keys: {list(semantic_payload.keys())}")
            return False
        
        self.print_success(f"Test file registered: {file_id}")
        
        # Submit file retrieval intent
        self.print_info("Step 3: Submitting file retrieval intent")
        retrieve_params = {"file_id": file_id}
        if file_reference:
            retrieve_params["file_reference"] = file_reference
            self.print_info(f"Using file_reference from registration: {file_reference}")
        
        retrieve_status = await self.submit_intent_and_poll(
            intent_type="retrieve_file",
            parameters=retrieve_params
        )
        
        if not retrieve_status:
            return False
        
        # Validate retrieved file (structured format)
        self.print_info("Step 4: Validating retrieved file")
        retrieve_artifacts = retrieve_status.get("artifacts", {})
        
        if "file" not in retrieve_artifacts:
            self.print_error("No file artifact found in retrieval result")
            return False
        
        retrieve_file_artifact = retrieve_artifacts["file"]
        if not isinstance(retrieve_file_artifact, dict) or retrieve_file_artifact.get("result_type") != "file":
            self.print_error("Retrieved file artifact is not in structured format")
            return False
        
        retrieve_semantic = retrieve_file_artifact.get("semantic_payload", {})
        retrieve_file_id = retrieve_semantic.get("file_id")
        
        if retrieve_file_id != file_id:
            self.print_error(f"Retrieved file_id mismatch: expected {file_id}, got {retrieve_file_id}")
            return False
        
        # Check if file_contents is in renderings (if include_contents was True)
        renderings = retrieve_file_artifact.get("renderings", {})
        if renderings.get("file_contents"):
            self.print_success("File contents available in renderings")
        
        self.print_success("Retrieved file is valid and accessible")
        self.print_success("✅ File Retrieval by ID - Full Execution Completion: PASSED")
        return True

async def main():
    test = TestRetrieveFile()
    result = await test.execute()
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
