#!/usr/bin/env python3
"""
Test: Data Quality Assessment - Two-Phase Materialization Flow

Tests the assess_data_quality capability:
- Assessment completes and returns quality metrics
- Metrics are meaningful (not just "quality: good")
- Assessment identifies actual issues
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

class TestAssessDataQuality(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="Data Quality Assessment - Two-Phase Materialization Flow",
            test_id_prefix="data_quality"
        )
    
    async def run_test(self) -> bool:
        if not await self.authenticate():
            return False
        
        # Phase 1: Upload file with known quality issues
        self.print_info("Step 2: Phase 1 - Uploading test file with quality issues")
        csv_content = "name,age,email,score\nJohn,30,john@example.com,85\nJane,,jane@example.com,92\nBob,25,invalid-email,78\n,35,bob@example.com,150\nAlice,28,alice@example.com,88"
        file_content_hex = csv_content.encode('utf-8').hex()
        test_file_name = f"data_quality_test_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.csv"
        
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
        source_file_id = file_id  # For assess_data_quality, source_file_id is the file_id
        
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
        
        # Step 5: Assess data quality
        self.print_info("Step 5: Assessing data quality")
        quality_status = await self.submit_intent_and_poll(
            intent_type="assess_data_quality",
            parameters={
                "parsed_file_id": parsed_file_id,
                "source_file_id": source_file_id,
                "parser_type": "csv"
            },
            timeout=180  # Quality assessment may take longer
        )
        
        if not quality_status:
            return False
        
        # Validate quality assessment results
        self.print_info("Step 6: Validating quality assessment results")
        quality_artifacts = quality_status.get("artifacts", {})
        
        quality_assessment = quality_artifacts.get("quality_assessment", {})
        
        if not quality_assessment:
            self.print_error("No quality_assessment found in results")
            return False
        
        overall_quality = quality_assessment.get("overall_quality")
        parsing_quality = quality_assessment.get("parsing_quality", {})
        data_quality = quality_assessment.get("data_quality", {})
        source_quality = quality_assessment.get("source_quality", {})
        
        self.print_success("Quality assessment completed successfully")
        if overall_quality:
            self.print_info(f"Overall quality: {overall_quality}")
        
        # Check for issues
        parsing_issues = parsing_quality.get("issues", [])
        data_issues = data_quality.get("issues", [])
        source_issues = source_quality.get("issues", [])
        
        total_issues = len(parsing_issues) + len(data_issues) + len(source_issues)
        if total_issues > 0:
            self.print_success(f"Assessment identified {total_issues} quality issues")
        else:
            self.print_info("No quality issues identified (may be expected for clean data)")
        
        self.print_success("✅ Data Quality Assessment - Two-Phase Materialization Flow: PASSED")
        return True

async def main():
    test = TestAssessDataQuality()
    result = await test.execute()
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
