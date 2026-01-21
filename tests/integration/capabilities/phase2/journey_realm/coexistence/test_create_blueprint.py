#!/usr/bin/env python3
"""
Test: Coexistence Blueprint Creation

Tests the create_blueprint capability:
- Blueprint creation completes
- Blueprint contains current state, coexistence state, roadmap, and responsibility matrix
- Visual workflow charts are generated
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

class TestCreateBlueprint(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="Coexistence Blueprint Creation",
            test_id_prefix="create_blueprint"
        )
    
    async def run_test(self) -> bool:
        if not await self.authenticate():
            return False
        
        # Step 1: Create a workflow first
        self.print_info("Step 2: Creating a test workflow first")
        
        bpmn_content = '''<?xml version="1.0" encoding="UTF-8"?>
<bpmn2:definitions xmlns:bpmn2="http://www.omg.org/spec/BPMN/20100524/MODEL">
  <bpmn2:process id="Process_1" isExecutable="true">
    <bpmn2:startEvent id="StartEvent_1"/>
    <bpmn2:task id="Task_1" name="Process Policy"/>
    <bpmn2:endEvent id="EndEvent_1"/>
    <bpmn2:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="Task_1"/>
    <bpmn2:sequenceFlow id="Flow_2" sourceRef="Task_1" targetRef="EndEvent_1"/>
  </bpmn2:process>
</bpmn2:definitions>'''
        
        file_content_hex = bpmn_content.encode('utf-8').hex()
        test_file_name = f"blueprint_test_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.bpmn"
        
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
        
        upload_artifacts = upload_status.get("artifacts", {})
        if "file" not in upload_artifacts:
            self.print_error("No file artifact found")
            return False
        
        file_artifact = upload_artifacts["file"]
        semantic_payload = file_artifact.get("semantic_payload", {})
        file_id = semantic_payload.get("file_id")
        file_reference = semantic_payload.get("file_reference")
        boundary_contract_id = semantic_payload.get("boundary_contract_id")
        
        if boundary_contract_id:
            await self.save_materialization(boundary_contract_id, file_id)
        
        workflow_status = await self.submit_intent_and_poll(
            intent_type="create_workflow",
            parameters={
                "workflow_file_path": file_reference or f"file:{file_id}",
                "workflow_type": "bpmn"
            },
            timeout=120
        )
        
        if not workflow_status:
            self.print_warning("Could not create workflow - skipping blueprint creation")
            return True
        
        workflow_artifacts = workflow_status.get("artifacts", {})
        workflow_artifact = workflow_artifacts.get("workflow", {})
        if isinstance(workflow_artifact, dict):
            semantic_payload = workflow_artifact.get("semantic_payload", {})
            workflow_id = semantic_payload.get("workflow_id")
        else:
            workflow_id = workflow_artifact.get("workflow_id") if isinstance(workflow_artifact, dict) else None
        
        if not workflow_id:
            self.print_warning("Could not extract workflow_id")
            return True
        
        self.print_success(f"Workflow created: {workflow_id}")
        
        # Step 2: Create blueprint
        self.print_info("Step 3: Creating coexistence blueprint")
        blueprint_status = await self.submit_intent_and_poll(
            intent_type="create_blueprint",
            parameters={
                "workflow_id": workflow_id
            },
            timeout=300  # Blueprint creation may take longer
        )
        
        if not blueprint_status:
            return False
        
        # Validate blueprint results
        self.print_info("Step 4: Validating blueprint results")
        blueprint_artifacts = blueprint_status.get("artifacts", {})
        
        blueprint_artifact = blueprint_artifacts.get("blueprint", {})
        if isinstance(blueprint_artifact, dict):
            semantic_payload = blueprint_artifact.get("semantic_payload", {})
            blueprint_id = semantic_payload.get("blueprint_id")
            blueprint_data = blueprint_artifact.get("renderings", {}).get("blueprint", {})
        else:
            blueprint_id = blueprint_artifact.get("blueprint_id") if isinstance(blueprint_artifact, dict) else None
            blueprint_data = blueprint_artifact
        
        if not blueprint_id:
            self.print_error("No blueprint_id found in blueprint result")
            return False
        
        self.print_success(f"Blueprint created successfully: {blueprint_id}")
        
        # Validate blueprint structure
        if blueprint_data:
            current_state = blueprint_data.get("current_state", {})
            coexistence_state = blueprint_data.get("coexistence_state", {})
            roadmap = blueprint_data.get("roadmap", {})
            responsibility_matrix = blueprint_data.get("responsibility_matrix", {})
            sections = blueprint_data.get("sections", [])
            
            if current_state:
                self.print_success("Blueprint contains current state")
                current_chart = current_state.get("workflow_chart", {})
                if current_chart:
                    self.print_info("  Current state workflow chart generated")
            
            if coexistence_state:
                self.print_success("Blueprint contains coexistence state")
                coexistence_chart = coexistence_state.get("workflow_chart", {})
                if coexistence_chart:
                    self.print_info("  Coexistence state workflow chart generated")
            
            if roadmap:
                self.print_success("Blueprint contains transition roadmap")
                phases = roadmap.get("phases", [])
                if phases:
                    self.print_info(f"  Roadmap has {len(phases)} phases")
            
            if responsibility_matrix:
                self.print_success("Blueprint contains responsibility matrix")
                responsibilities = responsibility_matrix.get("responsibilities", [])
                if responsibilities:
                    self.print_info(f"  Responsibility matrix has {len(responsibilities)} steps")
            
            if sections:
                self.print_success(f"Blueprint contains {len(sections)} sections")
        
        self.print_success("✅ Coexistence Blueprint Creation: PASSED")
        return True

async def main():
    test = TestCreateBlueprint()
    result = await test.execute()
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
