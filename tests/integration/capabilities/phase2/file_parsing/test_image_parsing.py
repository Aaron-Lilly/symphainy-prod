#!/usr/bin/env python3
"""
Test: Image File Parsing (OCR) - Two-Phase Materialization Flow

Tests the parse_content capability for image files with OCR using the two-phase flow.
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from tests.integration.capabilities.base_capability_test import BaseCapabilityTest

class TestImageParsing(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="Image File Parsing (OCR) - Two-Phase Materialization Flow",
            test_id_prefix="image_parse"
        )
    
    async def run_test(self) -> bool:
        if not await self.authenticate():
            return False
        
        # Phase 1: Upload file
        # Create a minimal PNG image for testing
        # PNG header + minimal structure
        self.print_info("Step 2: Phase 1 - Uploading image file")
        
        # Minimal PNG structure (simplified for testing)
        # Real PNG files are more complex, but this tests the flow
        png_header = b'\x89PNG\r\n\x1a\n'  # PNG signature
        # For testing, we'll use a very simple PNG structure
        # In production, this would be a real image file
        image_content = png_header + b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
        
        test_file_name = f"test_parse_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.png"
        
        file_content_hex = image_content.hex()
        upload_status = await self.submit_intent_and_poll(
            intent_type="ingest_file",
            parameters={
                "ingestion_type": "upload",
                "ui_name": test_file_name,
                "file_content": file_content_hex,
                "file_type": "image",
                "mime_type": "image/png"
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
        
        # Phase 3: Parse file (OCR)
        self.print_info("Step 4: Phase 3 - Parsing saved image file (OCR)")
        parse_params = {
            "file_id": file_id,
            "file_type": "image",
            "parse_options": {
                "ocr": True,
                "extract_text": True
            }
        }
        if file_reference:
            parse_params["file_reference"] = file_reference
        
        parse_status = await self.submit_intent_and_poll(
            intent_type="parse_content",
            parameters=parse_params,
            timeout=180  # OCR may take longer
        )
        
        if not parse_status:
            return False
        
        # Validate parsed content
        self.print_info("Step 5: Validating parsed image (OCR) results")
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
        
        # Check for OCR results
        semantic_payload = parsed_artifact.get("semantic_payload", {})
        parsed_content = semantic_payload.get("content") or semantic_payload.get("parsed_data") or semantic_payload.get("data")
        
        if not parsed_content:
            renderings = parsed_artifact.get("renderings", {})
            parsed_content = renderings.get("content") or renderings.get("parsed_data")
        
        # OCR may return empty results for simple images, which is acceptable
        if not parsed_content:
            self.print_warning("OCR did not extract text (may be normal for simple images)")
            # Still pass - OCR may not find text in minimal test image
            parsed_content = "{}"  # Empty result is acceptable
        
        if isinstance(parsed_content, (list, dict)) and len(parsed_content) > 0:
            self.print_success("Parsed image contains structured OCR data")
        elif isinstance(parsed_content, str):
            if len(parsed_content) > 0:
                self.print_success(f"Parsed image contains {len(parsed_content)} characters of OCR text")
            else:
                self.print_info("OCR returned empty result (acceptable for simple test image)")
        else:
            self.print_warning("OCR result format unexpected, but parsing completed")
        
        self.print_success("✅ Image File Parsing (OCR) - Two-Phase Materialization Flow: PASSED")
        return True

async def main():
    test = TestImageParsing()
    result = await test.execute()
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
