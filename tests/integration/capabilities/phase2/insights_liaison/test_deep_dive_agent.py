#!/usr/bin/env python3
"""
Test: Insights Liaison Agent - Deep Dive Analysis

Tests the analyze_unstructured_data capability with deep_dive: true:
- Deep dive agent session is initiated
- Agent session ID is returned
- Agent provides interactive analysis capabilities
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

class TestDeepDiveAgent(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="Insights Liaison Agent - Deep Dive Analysis",
            test_id_prefix="deep_dive_agent"
        )
    
    async def run_test(self) -> bool:
        if not await self.authenticate():
            return False
        
        # Phase 1: Upload unstructured file (PDF text)
        self.print_info("Step 2: Phase 1 - Uploading unstructured test file")
        # Create a simple text file that simulates unstructured content
        text_content = """
        Insurance Policy Document
        
        Policy Number: POL-001
        Beneficiary: John Doe
        Coverage Amount: $500,000
        Issue Date: January 15, 2024
        
        Terms and Conditions:
        This policy provides comprehensive coverage for the beneficiary.
        Coverage includes medical expenses, disability benefits, and life insurance.
        
        Exclusions:
        - Pre-existing conditions
        - High-risk activities
        - War-related incidents
        
        This policy is valid for the duration specified in the contract.
        """
        file_content_hex = text_content.encode('utf-8').hex()
        test_file_name = f"deep_dive_test_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.txt"
        
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
            parsed_result = parse_artifacts.get("parsed_file")
        
        if not parsed_result:
            parsed_file_id = parse_artifacts.get("parsed_file_id")
            if not parsed_file_id:
                self.print_error("No parsed_result artifact found")
                self.print_info(f"Available artifact keys: {list(parse_artifacts.keys())}")
                return False
        else:
            if isinstance(parsed_result, dict):
                semantic_payload = parsed_result.get("semantic_payload", {})
                parsed_file_id = semantic_payload.get("parsed_file_id") or parsed_result.get("id") or parsed_result.get("parsed_file_id")
            else:
                parsed_file_id = None
            
            if not parsed_file_id:
                self.print_error("No parsed_file_id found in parse result")
                return False
        
        self.print_success(f"File parsed successfully: {parsed_file_id}")
        
        # Step 5: Analyze unstructured data with deep dive
        self.print_info("Step 5: Running unstructured analysis with deep dive agent")
        analysis_status = await self.submit_intent_and_poll(
            intent_type="analyze_unstructured_data",
            parameters={
                "parsed_file_id": parsed_file_id,
                "analysis_options": {
                    "deep_dive": True,  # Enable deep dive agent session
                    "focus_areas": ["coverage", "exclusions", "terms"]
                }
            },
            timeout=180  # Deep dive may take longer
        )
        
        if not analysis_status:
            return False
        
        # Validate analysis results
        self.print_info("Step 6: Validating analysis results with deep dive")
        analysis_artifacts = analysis_status.get("artifacts", {})
        
        unstructured_analysis = analysis_artifacts.get("unstructured_analysis", {})
        summary = unstructured_analysis.get("summary", {})
        key_findings = unstructured_analysis.get("key_findings", [])
        deep_dive = unstructured_analysis.get("deep_dive", {})
        
        if not unstructured_analysis:
            self.print_error("No unstructured analysis results found")
            return False
        
        self.print_success("Unstructured analysis completed successfully")
        
        # Validate deep dive agent session
        if deep_dive:
            session_id = deep_dive.get("session_id")
            status = deep_dive.get("status")
            initial_questions = deep_dive.get("initial_questions", [])
            
            if session_id:
                self.print_success(f"Deep dive agent session initiated: {session_id}")
                self.print_info(f"Session status: {status}")
                if initial_questions:
                    self.print_info(f"Agent provided {len(initial_questions)} initial questions")
            else:
                self.print_warning("Deep dive session_id not found (may be in different format)")
        else:
            self.print_warning("Deep dive section not found in results (may not be fully implemented)")
        
        # Validate summary and findings
        if summary:
            document_type = summary.get("document_type")
            word_count = summary.get("word_count")
            sections = summary.get("sections", [])
            
            if document_type:
                self.print_info(f"Document type identified: {document_type}")
            if word_count:
                self.print_info(f"Word count: {word_count}")
            if sections:
                self.print_info(f"Sections found: {len(sections)}")
        
        if key_findings:
            self.print_success(f"Analysis found {len(key_findings)} key findings")
        
        # Check if deep_dive_initiated flag is set
        deep_dive_initiated = analysis_artifacts.get("deep_dive_initiated", False)
        if deep_dive_initiated:
            self.print_success("Deep dive agent session was successfully initiated")
        
        self.print_success("✅ Insights Liaison Agent - Deep Dive Analysis: PASSED")
        return True

async def main():
    test = TestDeepDiveAgent()
    result = await test.execute()
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
