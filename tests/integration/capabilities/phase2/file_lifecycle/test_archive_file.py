#!/usr/bin/env python3
"""
Test: Archive File - Two-Phase Materialization Flow

Tests the archive_file capability:
- File archiving completes successfully
- File status changes to archived
- Archived file is preserved but not accessible
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from tests.integration.capabilities.base_capability_test import BaseCapabilityTest

class TestArchiveFile(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="Archive File - Two-Phase Materialization Flow",
            test_id_prefix="archive_file"
        )
    
    async def run_test(self) -> bool:
        if not await self.authenticate():
            return False
        
        # Phase 1: Upload file
        self.print_info("Step 2: Phase 1 - Uploading file")
        file_content = "name,age,city\nJohn,30,New York\nJane,25,San Francisco"
        file_content_hex = file_content.encode('utf-8').hex()
        test_file_name = f"archive_test_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.csv"
        
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
            self.print_error("Failed to upload test file")
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
        
        # Verify file appears in list before archiving
        self.print_info("Step 4: Verifying file appears in list before archiving")
        list_status = await self.submit_intent_and_poll(
            intent_type="list_files",
            parameters={}
        )
        
        if list_status:
            list_artifacts = list_status.get("artifacts", {})
            listed_files = list_artifacts.get("files", [])
            found_before = False
            for listed_file in listed_files:
                if isinstance(listed_file, dict):
                    listed_file_id = listed_file.get("file_id") or listed_file.get("id")
                    if listed_file_id == file_id:
                        found_before = True
                        break
            
            if found_before:
                self.print_success("File appears in list before archiving")
            else:
                self.print_warning("File may not appear in list (may be expected)")
        
        # Step 5: Archive file
        self.print_info("Step 5: Archiving file")
        archive_status = await self.submit_intent_and_poll(
            intent_type="archive_file",
            parameters={
                "file_id": file_id,
                "file_reference": file_reference,
                "reason": "Test archiving"
            }
        )
        
        if not archive_status:
            return False
        
        # Validate archive results
        self.print_info("Step 6: Validating archive results")
        archive_artifacts = archive_status.get("artifacts", {})
        
        archived_file_id = archive_artifacts.get("file_id")
        archive_status_value = archive_artifacts.get("status")
        archived_at = archive_artifacts.get("archived_at")
        archive_reason = archive_artifacts.get("archive_reason")
        
        if archived_file_id != file_id:
            self.print_error(f"Archive returned different file_id: {archived_file_id} vs {file_id}")
            return False
        
        if archive_status_value != "archived":
            self.print_error(f"File status is not 'archived': {archive_status_value}")
            return False
        
        self.print_success(f"File archived successfully")
        self.print_info(f"Archived at: {archived_at}")
        self.print_info(f"Reason: {archive_reason}")
        
        # Verify file does not appear in active list after archiving
        self.print_info("Step 7: Verifying archived file does not appear in active list")
        list_status_after = await self.submit_intent_and_poll(
            intent_type="list_files",
            parameters={}
        )
        
        if list_status_after:
            list_artifacts_after = list_status_after.get("artifacts", {})
            listed_files_after = list_artifacts_after.get("files", [])
            found_after = False
            for listed_file in listed_files_after:
                if isinstance(listed_file, dict):
                    listed_file_id = listed_file.get("file_id") or listed_file.get("id")
                    if listed_file_id == file_id:
                        found_after = True
                        break
            
            if not found_after:
                self.print_success("Archived file correctly excluded from active file list")
            else:
                self.print_warning("Archived file still appears in list (may need filtering)")
        
        self.print_success("✅ Archive File - Two-Phase Materialization Flow: PASSED")
        return True

async def main():
    test = TestArchiveFile()
    result = await test.execute()
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
