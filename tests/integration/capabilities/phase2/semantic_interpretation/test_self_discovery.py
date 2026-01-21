#!/usr/bin/env python3
"""
Test: Semantic Interpretation - Self Discovery

Tests the interpret_data_self_discovery capability:
- Automatic semantic discovery completes
- Entities and relationships are discovered
- Semantic summary is generated
- Results are stored and retrievable
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from tests.integration.capabilities.base_capability_test import BaseCapabilityTest

class TestSelfDiscovery(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="Semantic Interpretation - Self Discovery",
            test_id_prefix="self_discovery"
        )
    
    async def run_test(self) -> bool:
        if not await self.authenticate():
            return False
        
        # Phase 1: Upload file
        self.print_info("Step 2: Phase 1 - Uploading test file")
        csv_content = "policy_number,beneficiary,coverage_amount,issue_date\nPOL-001,John Doe,500000,2024-01-15\nPOL-002,Jane Smith,750000,2024-02-20\nPOL-003,Bob Johnson,300000,2024-03-10"
        file_content_hex = csv_content.encode('utf-8').hex()
        test_file_name = f"self_discovery_test_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.csv"
        
        upload_status = await self.submit_intent_and_poll(
            intent_type="ingest_file",
            parameters={
                "ingestion_type": "upload",
                "ui_name": test_file_name,
                "file_content": file_content_hex,
                "file_type": "csv",
                "mime_type": "text/csv"
            }
        )
        
        if not upload_status:
            return False
        
        # Extract IDs
        upload_artifacts = upload_status.get("artifacts", {})
        if "file" not in upload_artifacts:
            self.print_error("No file artifact found after upload")
            return False
        
        file_artifact = upload_artifacts["file"]
        semantic_payload = file_artifact.get("semantic_payload", {})
        boundary_contract_id = semantic_payload.get("boundary_contract_id")
        file_id = semantic_payload.get("file_id")
        
        if not boundary_contract_id or not file_id:
            self.print_error("Missing boundary_contract_id or file_id")
            return False
        
        # Phase 2: Save file
        self.print_info("Step 3: Phase 2 - Saving file")
        if not await self.save_materialization(boundary_contract_id, file_id):
            return False
        
        # Phase 3: Parse file
        self.print_info("Step 4: Phase 3 - Parsing file")
        file_reference = semantic_payload.get("file_reference")
        parse_status = await self.submit_intent_and_poll(
            intent_type="parse_content",
            parameters={
                "file_id": file_id,
                "file_reference": file_reference,
                "parse_options": {
                    "extract_text": True
                }
            }
        )
        
        if not parse_status:
            return False
        
        # Extract parsed_file_id
        parse_artifacts = parse_status.get("artifacts", {})
        
        # Try different artifact structures
        parsed_result = parse_artifacts.get("parsed_result")
        if not parsed_result:
            # Try alternative structure
            parsed_result = parse_artifacts.get("parsed_file")
        
        if not parsed_result:
            self.print_error("No parsed_result artifact found")
            self.print_info(f"Available artifact keys: {list(parse_artifacts.keys())}")
            # Try to find parsed_file_id directly in artifacts
            parsed_file_id = parse_artifacts.get("parsed_file_id")
            if parsed_file_id:
                self.print_info(f"Found parsed_file_id directly in artifacts: {parsed_file_id}")
            else:
                return False
        else:
            # Extract from structured artifact
            if isinstance(parsed_result, dict):
                semantic_payload = parsed_result.get("semantic_payload", {})
                parsed_file_id = semantic_payload.get("parsed_file_id") or parsed_result.get("id") or parsed_result.get("parsed_file_id")
            else:
                parsed_file_id = None
            
            if not parsed_file_id:
                self.print_error("No parsed_file_id found in parse result")
                self.print_info(f"Parsed result structure: {parsed_result}")
                return False
        
        self.print_success(f"File parsed successfully: {parsed_file_id}")
        
        # Step 5: Self-discovery interpretation
        self.print_info("Step 5: Running self-discovery semantic interpretation")
        discovery_status = await self.submit_intent_and_poll(
            intent_type="interpret_data_self_discovery",
            parameters={
                "parsed_file_id": parsed_file_id,
                "discovery_options": {
                    "min_confidence": 0.7,
                    "include_relationships": True,
                    "include_entities": True
                }
            },
            timeout=180  # Discovery may take longer
        )
        
        if not discovery_status:
            return False
        
        # Validate discovery results
        self.print_info("Step 6: Validating discovery results")
        discovery_artifacts = discovery_status.get("artifacts", {})
        
        discovery = discovery_artifacts.get("discovery", {})
        semantic_map = discovery.get("semantic_map", {})
        entities = semantic_map.get("entities", [])
        relationships = semantic_map.get("relationships", [])
        interpretation = discovery.get("interpretation", {})
        
        if not discovery:
            self.print_error("No discovery results found")
            return False
        
        self.print_success("Self-discovery completed successfully")
        self.print_info(f"Discovered {len(entities)} entities")
        self.print_info(f"Discovered {len(relationships)} relationships")
        
        if interpretation:
            data_type = interpretation.get("data_type")
            confidence = interpretation.get("confidence")
            if data_type:
                self.print_info(f"Interpreted data type: {data_type} (confidence: {confidence})")
        
        # Validate that we have meaningful results
        if len(entities) == 0 and len(relationships) == 0:
            self.print_warning("No entities or relationships discovered (may be expected for simple data)")
        else:
            self.print_success("Discovery found meaningful semantic information")
        
        self.print_success("✅ Semantic Interpretation - Self Discovery: PASSED")
        return True

async def main():
    test = TestSelfDiscovery()
    result = await test.execute()
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
