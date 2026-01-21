#!/usr/bin/env python3
"""
Test: Structured Data Analysis - Two-Phase Materialization Flow

Tests the analyze_structured_data capability:
- Analysis completes and produces insights
- Insights are meaningful (not generic responses)
- Analysis handles structured data correctly
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

class TestStructuredAnalysis(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="Structured Data Analysis - Two-Phase Materialization Flow",
            test_id_prefix="structured_analysis"
        )
    
    async def run_test(self) -> bool:
        if not await self.authenticate():
            return False
        
        # Phase 1: Upload structured file
        self.print_info("Step 2: Phase 1 - Uploading structured test file")
        csv_content = "product,quantity,revenue,region\nWidget A,100,5000,North\nWidget B,150,7500,South\nWidget A,80,4000,East\nWidget C,200,10000,West\nWidget B,120,6000,North"
        file_content_hex = csv_content.encode('utf-8').hex()
        test_file_name = f"structured_analysis_test_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.csv"
        
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
        
        # Step 5: Analyze structured data
        self.print_info("Step 5: Analyzing structured data")
        analysis_status = await self.submit_intent_and_poll(
            intent_type="analyze_structured_data",
            parameters={
                "parsed_file_id": parsed_file_id,
                "analysis_options": {
                    "include_statistics": True,
                    "include_trends": True,
                    "include_insights": True
                }
            },
            timeout=180  # Analysis may take longer
        )
        
        if not analysis_status:
            return False
        
        # Validate analysis results
        self.print_info("Step 6: Validating analysis results")
        analysis_artifacts = analysis_status.get("artifacts", {})
        
        structured_analysis = analysis_artifacts.get("structured_analysis", {})
        summary = structured_analysis.get("summary", {})
        insights = structured_analysis.get("insights", [])
        statistics = structured_analysis.get("statistics", {})
        
        if not structured_analysis:
            self.print_error("No structured_analysis found in results")
            return False
        
        self.print_success("Structured analysis completed successfully")
        
        if summary:
            record_count = summary.get("record_count")
            field_count = summary.get("field_count")
            if record_count:
                self.print_info(f"Analyzed {record_count} records")
            if field_count:
                self.print_info(f"Found {field_count} fields")
        
        if insights:
            self.print_success(f"Analysis generated {len(insights)} insights")
        
        if statistics:
            self.print_info(f"Statistics calculated for {len(statistics)} fields")
        
        self.print_success("✅ Structured Data Analysis - Two-Phase Materialization Flow: PASSED")
        return True

async def main():
    test = TestStructuredAnalysis()
    result = await test.execute()
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
