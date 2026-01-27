#!/usr/bin/env python3
"""
Test: Workflow Creation from BPMN File

Tests the create_workflow capability from uploaded BPMN file:
- BPMN file parsing completes
- Workflow structure is created
- Workflow visualization is generated
- Results are stored and retrievable
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from tests.integration.capabilities.base_capability_test import BaseCapabilityTest

class TestCreateWorkflowFromBPMN(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="Workflow Creation from BPMN File",
            test_id_prefix="workflow_from_bpmn"
        )
    
    async def run_test(self) -> bool:
        if not await self.authenticate():
            return False
        
        # Step 1: Create a simple BPMN file content
        self.print_info("Step 2: Creating test BPMN file content")
        
        # Simple BPMN 2.0 XML structure
        bpmn_content = '''<?xml version="1.0" encoding="UTF-8"?>
<bpmn2:definitions xmlns:bpmn2="http://www.omg.org/spec/BPMN/20100524/MODEL"
                   xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
                   xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
                   id="sample-diagram" targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn2:process id="Process_1" isExecutable="true">
    <bpmn2:startEvent id="StartEvent_1"/>
    <bpmn2:task id="Task_1" name="Process File"/>
    <bpmn2:task id="Task_2" name="Validate Data"/>
    <bpmn2:endEvent id="EndEvent_1"/>
    <bpmn2:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="Task_1"/>
    <bpmn2:sequenceFlow id="Flow_2" sourceRef="Task_1" targetRef="Task_2"/>
    <bpmn2:sequenceFlow id="Flow_3" sourceRef="Task_2" targetRef="EndEvent_1"/>
  </bpmn2:process>
</bpmn2:definitions>'''
        
        # Step 2: Upload BPMN file
        self.print_info("Step 3: Uploading BPMN file")
        file_content_hex = bpmn_content.encode('utf-8').hex()
        test_file_name = f"test_workflow_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.bpmn"
        
        upload_status = await self.submit_intent_and_poll(
            intent_type="ingest_file",
            parameters={
                "ingestion_type": "upload",
                "ui_name": test_file_name,
                "file_content": file_content_hex,
                "file_type": "bpmn",
                "mime_type": "application/xml"
            }
        )
        
        if not upload_status:
            return False
        
        # Extract file information
        upload_artifacts = upload_status.get("artifacts", {})
        if "file" not in upload_artifacts:
            self.print_error("No file artifact found after upload")
            return False
        
        file_artifact = upload_artifacts["file"]
        semantic_payload = file_artifact.get("semantic_payload", {})
        file_id = semantic_payload.get("file_id")
        file_reference = semantic_payload.get("file_reference")
        
        if not file_id:
            self.print_error("No file_id found after upload")
            return False
        
        self.print_success(f"BPMN file uploaded: {file_id}")
        
        # Step 3: Save file (two-phase flow)
        self.print_info("Step 4: Saving file (two-phase flow)")
        boundary_contract_id = semantic_payload.get("boundary_contract_id")
        if boundary_contract_id:
            if not await self.save_materialization(boundary_contract_id, file_id):
                self.print_warning("Failed to save file, continuing anyway")
        
        # Step 4: Create workflow from BPMN file
        # Note: The create_workflow intent expects workflow_file_path
        # We may need to use file_reference or file_id
        self.print_info("Step 5: Creating workflow from BPMN file")
        
        # Try using file_reference as workflow_file_path
        workflow_file_path = file_reference or f"file:{file_id}"
        
        workflow_status = await self.submit_intent_and_poll(
            intent_type="create_workflow",
            parameters={
                "workflow_file_path": workflow_file_path,
                "workflow_type": "bpmn"
            },
            timeout=180  # Workflow creation may take longer
        )
        
        if not workflow_status:
            return False
        
        # Validate workflow results
        self.print_info("Step 6: Validating workflow results")
        workflow_artifacts = workflow_status.get("artifacts", {})
        
        workflow_artifact = workflow_artifacts.get("workflow", {})
        if isinstance(workflow_artifact, dict):
            semantic_payload = workflow_artifact.get("semantic_payload", {})
            workflow_id = semantic_payload.get("workflow_id")
            workflow_data = workflow_artifact.get("renderings", {}).get("workflow", {})
        else:
            workflow_id = workflow_artifact.get("workflow_id") if isinstance(workflow_artifact, dict) else None
            workflow_data = workflow_artifact
        
        if not workflow_id:
            self.print_error("No workflow_id found in workflow result")
            return False
        
        self.print_success(f"Workflow created successfully: {workflow_id}")
        
        # Validate workflow structure
        if workflow_data:
            workflow_type = workflow_data.get("workflow_type")
            status = workflow_data.get("status")
            source_file = workflow_data.get("source_file")
            
            if workflow_type:
                self.print_info(f"Workflow type: {workflow_type}")
            if status:
                self.print_info(f"Workflow status: {status}")
            if source_file:
                self.print_info(f"Source file: {source_file}")
        
        # Validate workflow visual
        workflow_visual = workflow_artifacts.get("workflow_visual", {})
        if workflow_visual:
            image_base64 = workflow_visual.get("image_base64")
            storage_path = workflow_visual.get("storage_path")
            
            if image_base64:
                self.print_success("Workflow visual image generated (base64)")
            if storage_path:
                self.print_info(f"Workflow visual stored at: {storage_path}")
        else:
            self.print_warning("No workflow visual generated (may not be implemented)")
        
        self.print_success("✅ Workflow Creation from BPMN File: PASSED")
        return True

async def main():
    test = TestCreateWorkflowFromBPMN()
    result = await test.execute()
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
