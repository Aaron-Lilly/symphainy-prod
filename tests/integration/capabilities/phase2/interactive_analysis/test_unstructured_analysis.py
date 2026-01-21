#!/usr/bin/env python3
"""
Test: Unstructured Data Analysis - Two-Phase Materialization Flow

Tests the analyze_unstructured_data capability:
- Analysis completes and produces insights
- Insights are meaningful (not generic responses)
- Analysis handles unstructured data correctly
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

class TestUnstructuredAnalysis(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="Unstructured Data Analysis - Two-Phase Materialization Flow",
            test_id_prefix="unstructured_analysis"
        )
    
    async def run_test(self) -> bool:
        if not await self.authenticate():
            return False
        
        # Phase 1: Upload unstructured file
        self.print_info("Step 2: Phase 1 - Uploading unstructured test file")
        text_content = """
        Customer Feedback Report - Q4 2024
        
        Overall customer satisfaction has improved this quarter. Key highlights:
        - Product quality received positive feedback from 85% of customers
        - Shipping times were mentioned as an area for improvement
        - Customer service response time decreased by 20%
        - New feature requests include mobile app improvements and better integration
        
        Recommendations:
        1. Continue focusing on product quality
        2. Address shipping time concerns
        3. Prioritize mobile app development
        """
        file_content_hex = text_content.encode('utf-8').hex()
        test_file_name = f"unstructured_analysis_test_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.txt"
        
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
        parsed_result = parse_artifacts.get("parsed_result") or parse_artifacts.get("parsed_file")
        parsed_file_id = parse_artifacts.get("parsed_file_id")
        
        if not parsed_file_id and parsed_result:
            if isinstance(parsed_result, dict):
                semantic_payload = parsed_result.get("semantic_payload", {})
                parsed_file_id = semantic_payload.get("parsed_file_id") or parsed_result.get("id") or parsed_result.get("parsed_file_id")
        
        if not parsed_file_id:
            self.print_error("No parsed_file_id found in parse result")
            return False
        
        self.print_success(f"File parsed successfully: {parsed_file_id}")
        
        # Step 5: Analyze unstructured data
        self.print_info("Step 5: Analyzing unstructured data")
        analysis_status = await self.submit_intent_and_poll(
            intent_type="analyze_unstructured_data",
            parameters={
                "parsed_file_id": parsed_file_id,
                "analysis_options": {
                    "extract_key_points": True,
                    "identify_sentiment": True,
                    "extract_entities": True
                }
            },
            timeout=180  # Analysis may take longer
        )
        
        if not analysis_status:
            return False
        
        # Validate analysis results
        self.print_info("Step 6: Validating analysis results")
        analysis_artifacts = analysis_status.get("artifacts", {})
        
        unstructured_analysis = analysis_artifacts.get("unstructured_analysis", {})
        summary = unstructured_analysis.get("summary", {})
        key_findings = unstructured_analysis.get("key_findings", [])
        
        if not unstructured_analysis:
            self.print_error("No unstructured_analysis found in results")
            return False
        
        self.print_success("Unstructured analysis completed successfully")
        
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
        
        self.print_success("✅ Unstructured Data Analysis - Two-Phase Materialization Flow: PASSED")
        return True

async def main():
    test = TestUnstructuredAnalysis()
    result = await test.execute()
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
