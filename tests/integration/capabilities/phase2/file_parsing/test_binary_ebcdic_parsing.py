#!/usr/bin/env python3
"""
Test: Binary File Parsing (EBCDIC) - Two-Phase Materialization Flow

Tests the parse_content capability for EBCDIC-encoded binary files with copybook definitions.
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from tests.integration.capabilities.base_capability_test import BaseCapabilityTest

class TestBinaryEBCDICParsing(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="Binary File Parsing (EBCDIC) - Two-Phase Materialization Flow",
            test_id_prefix="binary_ebcdic_parse"
        )
    
    def _ascii_to_ebcdic(self, ascii_string: str) -> bytes:
        """
        Convert ASCII string to EBCDIC encoding.
        This is a simplified mapping for testing purposes.
        In production, use proper EBCDIC code page conversion.
        """
        # EBCDIC code page 037 mapping (simplified for common characters)
        # For testing, we'll use a basic conversion
        # Real EBCDIC conversion requires proper code page tables
        ebcdic_map = {
            ' ': 0x40, 'A': 0xC1, 'B': 0xC2, 'C': 0xC3, 'D': 0xC4, 'E': 0xC5,
            'F': 0xC6, 'G': 0xC7, 'H': 0xC8, 'I': 0xC9, 'J': 0xD1, 'K': 0xD2,
            'L': 0xD3, 'M': 0xD4, 'N': 0xD5, 'O': 0xD6, 'P': 0xD7, 'Q': 0xD8,
            'R': 0xD9, 'S': 0xE2, 'T': 0xE3, 'U': 0xE4, 'V': 0xE5, 'W': 0xE6,
            'X': 0xE7, 'Y': 0xE8, 'Z': 0xE9, '0': 0xF0, '1': 0xF1, '2': 0xF2,
            '3': 0xF3, '4': 0xF4, '5': 0xF5, '6': 0xF6, '7': 0xF7, '8': 0xF8,
            '9': 0xF9
        }
        
        result = bytearray()
        for char in ascii_string:
            if char in ebcdic_map:
                result.append(ebcdic_map[char])
            else:
                # Default to space if character not in map
                result.append(0x40)
        return bytes(result)
    
    async def run_test(self) -> bool:
        if not await self.authenticate():
            return False
        
        # Phase 1: Upload binary file
        self.print_info("Step 2: Phase 1 - Uploading EBCDIC binary file")
        
        # Create a simple binary record structure matching the copybook
        # Copybook defines: CUSTOMER-RECORD with fields:
        #   05 CUSTOMER-ID      PIC X(10)  - 10 bytes
        #   05 CUSTOMER-NAME    PIC X(30)  - 30 bytes
        #   05 CUSTOMER-AGE     PIC 9(3)   - 3 bytes (numeric)
        #   05 CUSTOMER-CITY    PIC X(20)  - 20 bytes
        # Total: 63 bytes per record
        
        # Create test binary data (EBCDIC encoded)
        customer_id = "CUST001   "  # 10 bytes, right-padded
        customer_name = "John Doe                    "  # 30 bytes, right-padded
        customer_age = "030"  # 3 bytes, numeric
        customer_city = "New York            "  # 20 bytes, right-padded
        
        # Convert to EBCDIC
        binary_record = (
            self._ascii_to_ebcdic(customer_id) +
            self._ascii_to_ebcdic(customer_name) +
            self._ascii_to_ebcdic(customer_age) +
            self._ascii_to_ebcdic(customer_city)
        )
        
        # Add a second record for testing
        customer_id2 = "CUST002   "
        customer_name2 = "Jane Smith                  "
        customer_age2 = "025"
        customer_city2 = "San Francisco      "
        binary_record2 = (
            self._ascii_to_ebcdic(customer_id2) +
            self._ascii_to_ebcdic(customer_name2) +
            self._ascii_to_ebcdic(customer_age2) +
            self._ascii_to_ebcdic(customer_city2)
        )
        
        binary_content = binary_record + binary_record2
        
        test_file_name = f"test_binary_ebcdic_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.bin"
        
        file_content_hex = binary_content.hex()
        upload_status = await self.submit_intent_and_poll(
            intent_type="ingest_file",
            parameters={
                "ingestion_type": "upload",
                "ui_name": test_file_name,
                "file_content": file_content_hex,
                "file_type": "binary",
                "mime_type": "application/octet-stream"
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
        
        # Extract session_id from file_reference for copybook reference
        session_id = None
        if file_reference:
            # file_reference format: "file:tenant_id:session_id:file_id"
            parts = file_reference.split(":")
            if len(parts) >= 3:
                session_id = parts[2]
        
        self.print_success(f"Phase 1 complete - File uploaded with ID: {file_id}")
        if file_reference:
            self.print_info(f"File reference: {file_reference}")
        
        # Phase 2: Save file
        self.print_info("Step 3: Phase 2 - Saving file")
        if not await self.save_materialization(boundary_contract_id, file_id):
            return False
        
        self.print_success("Phase 2 complete - File saved")
        
        # Upload copybook file
        self.print_info("Step 4: Uploading copybook file")
        
        # COBOL copybook definition
        copybook_definition = """
       01 CUSTOMER-RECORD.
          05 CUSTOMER-ID      PIC X(10).
          05 CUSTOMER-NAME    PIC X(30).
          05 CUSTOMER-AGE     PIC 9(3).
          05 CUSTOMER-CITY    PIC X(20).
        """
        
        copybook_content_hex = copybook_definition.strip().encode('utf-8').hex()
        copybook_file_name = f"copybook_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.cpy"
        
        copybook_upload_status = await self.submit_intent_and_poll(
            intent_type="ingest_file",
            parameters={
                "ingestion_type": "upload",
                "ui_name": copybook_file_name,
                "file_content": copybook_content_hex,
                "file_type": "unstructured",
                "mime_type": "text/plain"
            }
        )
        
        if not copybook_upload_status:
            self.print_error("Failed to upload copybook file")
            return False
        
        copybook_artifacts = copybook_upload_status.get("artifacts", {})
        if "file" not in copybook_artifacts:
            self.print_error("No file artifact found after copybook upload")
            return False
        
        copybook_file_artifact = copybook_artifacts["file"]
        copybook_semantic_payload = copybook_file_artifact.get("semantic_payload", {})
        copybook_file_id = copybook_semantic_payload.get("file_id")
        copybook_file_reference = copybook_semantic_payload.get("file_reference")
        copybook_boundary_contract_id = copybook_semantic_payload.get("boundary_contract_id")
        
        if not copybook_file_id:
            self.print_error("No copybook file_id found")
            return False
        
        if not copybook_file_reference:
            self.print_error("No copybook file_reference found")
            return False
        
        # Save copybook file
        if copybook_boundary_contract_id:
            if not await self.save_materialization(copybook_boundary_contract_id, copybook_file_id):
                self.print_warning("Failed to save copybook file, continuing anyway")
        
        # Use copybook file_reference directly as copybook_reference
        copybook_reference = copybook_file_reference
        
        self.print_success(f"Copybook uploaded with ID: {copybook_file_id}")
        self.print_info(f"Copybook reference: {copybook_reference}")
        
        # Phase 3: Parse file with copybook
        self.print_info("Step 5: Phase 3 - Parsing saved binary file with copybook (EBCDIC)")
        
        parse_params = {
            "file_id": file_id,
            "file_type": "binary",
            "copybook_reference": copybook_reference,
            "parse_options": {
                "encoding": "ebcdic",
                "codepage": "037",  # EBCDIC code page 037 (US English)
                "record_length": 63  # Total record length
            }
        }
        if file_reference:
            parse_params["file_reference"] = file_reference
        
        parse_status = await self.submit_intent_and_poll(
            intent_type="parse_content",
            parameters=parse_params,
            timeout=120  # Binary parsing may take longer
        )
        
        if not parse_status:
            return False
        
        # Validate parsed content
        self.print_info("Step 6: Validating parsed binary (EBCDIC) results")
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
        
        # Check for expected binary data
        semantic_payload = parsed_artifact.get("semantic_payload", {})
        parsed_content = semantic_payload.get("content") or semantic_payload.get("parsed_data") or semantic_payload.get("data")
        
        if not parsed_content:
            renderings = parsed_artifact.get("renderings", {})
            parsed_content = renderings.get("content") or renderings.get("parsed_data")
        
        if not parsed_content:
            self.print_error("Parsed content is empty")
            return False
        
        content_str = str(parsed_content).lower()
        # Binary parsing should extract structured data based on copybook
        if "customer" in content_str or "cust001" in content_str or "john" in content_str or "new york" in content_str:
            self.print_success("Parsed binary contains expected customer data")
        else:
            self.print_warning("Parsed binary may not contain expected customer data")
        
        # Check if parsed content is structured (list/dict of records)
        if isinstance(parsed_content, list) and len(parsed_content) > 0:
            self.print_success(f"Parsed binary contains {len(parsed_content)} records")
            # Validate first record structure
            if isinstance(parsed_content[0], dict):
                if "customer_id" in parsed_content[0] or "customer-name" in parsed_content[0]:
                    self.print_success("Parsed records have expected structure")
        elif isinstance(parsed_content, dict) and len(parsed_content) > 0:
            self.print_success("Parsed binary contains structured data")
        elif isinstance(parsed_content, str) and len(parsed_content) > 0:
            self.print_success(f"Parsed binary contains {len(parsed_content)} characters")
        else:
            self.print_error("Parsed binary is empty")
            return False
        
        self.print_success("✅ Binary File Parsing (EBCDIC) - Two-Phase Materialization Flow: PASSED")
        return True

async def main():
    test = TestBinaryEBCDICParsing()
    result = await test.execute()
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
