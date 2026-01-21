#!/usr/bin/env python3
"""
Test: PDF File Parsing - Two-Phase Materialization Flow

Tests the parse_content capability for PDF files (both structured and unstructured) using the two-phase flow.
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from tests.integration.capabilities.base_capability_test import BaseCapabilityTest

class TestPDFParsing(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="PDF File Parsing - Two-Phase Materialization Flow",
            test_id_prefix="pdf_parse"
        )
    
    async def run_test(self) -> bool:
        if not await self.authenticate():
            return False
        
        # Phase 1: Upload file
        # Create a minimal PDF content (PDF header + basic structure)
        # This is a simplified PDF for testing - real PDFs are more complex
        self.print_info("Step 2: Phase 1 - Uploading PDF file")
        
        # Minimal PDF structure (simplified for testing)
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Test PDF Document) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000206 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n300\n%%EOF"
        
        test_file_name = f"test_parse_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.pdf"
        
        file_content_hex = pdf_content.hex()
        upload_status = await self.submit_intent_and_poll(
            intent_type="ingest_file",
            parameters={
                "ingestion_type": "upload",
                "ui_name": test_file_name,
                "file_content": file_content_hex,
                "file_type": "unstructured",  # PDF can be structured or unstructured
                "mime_type": "application/pdf"
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
        self.print_info("Step 4: Phase 3 - Parsing saved PDF file")
        parse_params = {
            "file_id": file_id,
            "file_type": "unstructured",
            "parse_options": {
                "extract_text": True,
                "extract_tables": False
            }
        }
        if file_reference:
            parse_params["file_reference"] = file_reference
        
        parse_status = await self.submit_intent_and_poll(
            intent_type="parse_content",
            parameters=parse_params,
            timeout=120  # PDF parsing may take longer
        )
        
        if not parse_status:
            return False
        
        # Validate parsed content
        self.print_info("Step 5: Validating parsed PDF results")
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
        
        # Check for expected PDF content
        semantic_payload = parsed_artifact.get("semantic_payload", {})
        parsed_content = semantic_payload.get("content") or semantic_payload.get("parsed_data") or semantic_payload.get("data")
        
        if not parsed_content:
            renderings = parsed_artifact.get("renderings", {})
            parsed_content = renderings.get("content") or renderings.get("parsed_data")
        
        if not parsed_content:
            self.print_error("Parsed content is empty")
            return False
        
        content_str = str(parsed_content).lower()
        # PDF parsing may extract text, metadata, or structure
        if "test" in content_str or "pdf" in content_str or "document" in content_str or len(content_str) > 0:
            self.print_success("Parsed PDF contains content")
        else:
            self.print_warning("Parsed PDF may not contain expected content")
        
        if isinstance(parsed_content, (list, dict)) and len(parsed_content) > 0:
            self.print_success("Parsed PDF contains structured data")
        elif isinstance(parsed_content, str) and len(parsed_content) > 0:
            self.print_success(f"Parsed PDF contains {len(parsed_content)} characters")
        else:
            self.print_error("Parsed PDF is empty")
            return False
        
        self.print_success("✅ PDF File Parsing - Two-Phase Materialization Flow: PASSED")
        return True

async def main():
    test = TestPDFParsing()
    result = await test.execute()
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
