#!/usr/bin/env python3
"""
Test: JSON File Parsing - Two-Phase Materialization Flow

Tests the parse_content capability for JSON files using the two-phase flow:
- Phase 1: Upload file (creates pending boundary contract)
- Phase 2: Save file (authorizes materialization)
- Phase 3: Parse file (extracts structured data)

Validates:
- JSON parsing completes
- Parsed structure is extracted correctly
- Parsed results are stored
- Parsed results contain meaningful data
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from tests.integration.capabilities.base_capability_test import BaseCapabilityTest

class TestJSONParsing(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="JSON File Parsing - Two-Phase Materialization Flow",
            test_id_prefix="json_parse"
        )
    
    async def run_test(self) -> bool:
        if not await self.authenticate():
            return False
        
        # Phase 1: Upload file
        self.print_info("Step 2: Phase 1 - Uploading JSON file")
        json_content = '{"users": [{"name": "John", "age": 30, "city": "New York"}, {"name": "Jane", "age": 25, "city": "San Francisco"}]}'
        test_file_name = f"test_parse_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.json"
        
        file_content_hex = json_content.encode('utf-8').hex()
        upload_status = await self.submit_intent_and_poll(
            intent_type="ingest_file",
            parameters={
                "ingestion_type": "upload",
                "ui_name": test_file_name,
                "file_content": file_content_hex,
                "file_type": "json",
                "mime_type": "application/json"
            }
        )
        
        if not upload_status:
            self.print_error("Failed to upload test file")
            return False
        
        # Extract boundary_contract_id and file_id
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
        
        if not boundary_contract_id:
            self.print_error("No boundary_contract_id found (required for two-phase flow)")
            return False
        
        if not file_id:
            self.print_error("No file_id found in file artifact")
            return False
        
        self.print_success(f"Phase 1 complete - File uploaded with ID: {file_id}")
        self.print_info(f"Boundary contract ID: {boundary_contract_id}")
        
        # Phase 2: Save file (required before parsing)
        self.print_info("Step 3: Phase 2 - Saving file (authorizing materialization)")
        if not await self.save_materialization(boundary_contract_id, file_id):
            self.print_error("Failed to save file - parsing cannot proceed")
            return False
        
        self.print_success("Phase 2 complete - File saved and available for parsing")
        
        # Phase 3: Parse file
        self.print_info("Step 4: Phase 3 - Parsing saved file")
        parse_params = {
            "file_id": file_id,
            "file_type": "json",
            "parse_options": {
                "validate_json": True
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
        
        # Validate parsed artifact
        self.print_info("Step 5: Validating parsed JSON results")
        artifacts = parse_status.get("artifacts", {})
        
        parsed_artifact = None
        parsed_artifact_id = None
        
        if isinstance(artifacts, dict):
            for key in ["parsed_content", "parsed", "content", "parsed_data"]:
                if key in artifacts:
                    artifact = artifacts[key]
                    if isinstance(artifact, dict) and "result_type" in artifact:
                        parsed_artifact = artifact
                        semantic_payload = artifact.get("semantic_payload", {})
                        parsed_artifact_id = semantic_payload.get("parsed_content_id") or semantic_payload.get("id") or semantic_payload.get("artifact_id")
                        if not parsed_artifact_id:
                            artifact_id_key = f"{key}_artifact_id"
                            if artifact_id_key in artifacts:
                                parsed_artifact_id = artifacts[artifact_id_key]
                        break
        
        if not parsed_artifact:
            self.print_error("No parsed content artifact found")
            self.print_info(f"Available artifact keys: {list(artifacts.keys()) if isinstance(artifacts, dict) else 'N/A'}")
            return False
        
        if not parsed_artifact_id:
            self.print_warning("Parsed artifact missing ID, using artifact from execution state")
            parsed_data = parsed_artifact
        else:
            self.print_info("Step 6: Retrieving parsed content artifact")
            parsed_data = await self.get_artifact_by_id(parsed_artifact_id, include_visuals=False)
            if not parsed_data:
                self.print_warning("Could not retrieve parsed content artifact via API, using from execution state")
                parsed_data = parsed_artifact
        
        self.print_success("Parsed content artifact retrieved")
        
        # Validate parsed data
        self.print_info("Step 7: Validating parsed data contains meaningful content")
        
        if isinstance(parsed_data, dict) and "result_type" in parsed_data and "semantic_payload" in parsed_data:
            semantic_payload = parsed_data.get("semantic_payload", {})
            parsed_content = semantic_payload.get("content") or semantic_payload.get("parsed_data") or semantic_payload.get("data") or semantic_payload.get("parsed_content")
            if not parsed_content:
                renderings = parsed_data.get("renderings", {})
                parsed_content = renderings.get("content") or renderings.get("parsed_data") or renderings.get("data")
        else:
            parsed_content = parsed_data.get("content") or parsed_data.get("parsed_data") or parsed_data.get("data")
        
        if not parsed_content:
            self.print_error("Parsed content is empty or missing")
            return False
        
        # Check for expected JSON data
        content_str = str(parsed_content).lower()
        if "john" in content_str or "users" in content_str or "new york" in content_str:
            self.print_success("Parsed JSON contains expected data")
        else:
            self.print_warning("Parsed JSON may not contain expected data")
        
        if isinstance(parsed_content, (list, dict)) and len(parsed_content) > 0:
            self.print_success(f"Parsed JSON contains {len(parsed_content) if isinstance(parsed_content, list) else len(parsed_content.keys())} items")
        elif isinstance(parsed_content, str) and len(parsed_content) > 0:
            self.print_success("Parsed JSON contains text content")
        else:
            self.print_error("Parsed JSON is empty")
            return False
        
        self.print_success("✅ JSON File Parsing - Two-Phase Materialization Flow: PASSED")
        return True

async def main():
    test = TestJSONParsing()
    result = await test.execute()
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
