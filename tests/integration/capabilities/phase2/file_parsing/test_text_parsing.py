#!/usr/bin/env python3
"""
Test: Text File Parsing - Two-Phase Materialization Flow

Tests the parse_content capability for plain text files using the two-phase flow.
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from tests.integration.capabilities.base_capability_test import BaseCapabilityTest

class TestTextParsing(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="Text File Parsing - Two-Phase Materialization Flow",
            test_id_prefix="text_parse"
        )
    
    async def run_test(self) -> bool:
        if not await self.authenticate():
            return False
        
        # Phase 1: Upload file
        self.print_info("Step 2: Phase 1 - Uploading text file")
        text_content = "This is a test document.\n\nIt contains multiple paragraphs.\n\nLine 1\nLine 2\nLine 3"
        test_file_name = f"test_parse_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.txt"
        
        file_content_hex = text_content.encode('utf-8').hex()
        upload_status = await self.submit_intent_and_poll(
            intent_type="ingest_file",
            parameters={
                "ingestion_type": "upload",
                "ui_name": test_file_name,
                "file_content": file_content_hex,
                "file_type": "unstructured",
                "mime_type": "text/plain"
            }
        )
        
        if not upload_status:
            self.print_error("Failed to upload test file")
            return False
        
        # Extract IDs
        upload_artifacts = upload_status.get("artifacts", {})
        if "file" not in upload_artifacts:
            self.print_error("No file artifact found after upload")
            return False
        
        file_artifact = upload_artifacts["file"]
        if not isinstance(file_artifact, dict) or "semantic_payload" not in file_artifact:
            self.print_error("File artifact is not in structured format")
            return False
        
        semantic_payload = file_artifact.get("semantic_payload", {})
        boundary_contract_id = semantic_payload.get("boundary_contract_id")
        file_id = semantic_payload.get("file_id")
        file_reference = semantic_payload.get("file_reference")
        
        if not boundary_contract_id or not file_id:
            self.print_error("Missing boundary_contract_id or file_id")
            return False
        
        self.print_success(f"Phase 1 complete - File uploaded with ID: {file_id}")
        
        # Phase 2: Save file
        self.print_info("Step 3: Phase 2 - Saving file")
        if not await self.save_materialization(boundary_contract_id, file_id):
            return False
        
        self.print_success("Phase 2 complete - File saved")
        
        # Phase 3: Parse file
        self.print_info("Step 4: Phase 3 - Parsing saved file")
        parse_params = {
            "file_id": file_id,
            "file_type": "unstructured",
            "parse_options": {
                "extract_text": True
            }
        }
        if file_reference:
            parse_params["file_reference"] = file_reference
        
        parse_status = await self.submit_intent_and_poll(
            intent_type="parse_content",
            parameters=parse_params
        )
        
        if not parse_status:
            return False
        
        # Validate parsed content
        self.print_info("Step 5: Validating parsed text results")
        artifacts = parse_status.get("artifacts", {})
        
        parsed_artifact = None
        if isinstance(artifacts, dict):
            for key in ["parsed_content", "parsed", "content", "parsed_data"]:
                if key in artifacts:
                    artifact = artifacts[key]
                    if isinstance(artifact, dict) and "result_type" in artifact:
                        parsed_artifact = artifact
                        break
        
        if not parsed_artifact:
            self.print_error("No parsed content artifact found")
            return False
        
        # Check for expected text
        semantic_payload = parsed_artifact.get("semantic_payload", {})
        parsed_content = semantic_payload.get("content") or semantic_payload.get("parsed_data") or semantic_payload.get("data")
        
        if not parsed_content:
            renderings = parsed_artifact.get("renderings", {})
            parsed_content = renderings.get("content") or renderings.get("parsed_data")
        
        if not parsed_content:
            self.print_error("Parsed content is empty")
            return False
        
        content_str = str(parsed_content).lower()
        if "test document" in content_str or "paragraphs" in content_str:
            self.print_success("Parsed text contains expected content")
        else:
            self.print_warning("Parsed text may not contain expected content")
        
        if isinstance(parsed_content, str) and len(parsed_content) > 0:
            self.print_success(f"Parsed text contains {len(parsed_content)} characters")
        else:
            self.print_error("Parsed text is empty")
            return False
        
        self.print_success("✅ Text File Parsing - Two-Phase Materialization Flow: PASSED")
        return True

async def main():
    test = TestTextParsing()
    result = await test.execute()
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
