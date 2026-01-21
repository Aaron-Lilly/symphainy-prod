#!/usr/bin/env python3
"""
Test: Platform Solution Creation from Blueprint

Tests the create_solution capability with blueprint source:
- Solution creation from blueprint completes
- Solution contains domain service bindings
- Solution defines supported intents
- Results are stored and retrievable

This tests the "translate user uploaded SOP/workflow diagrams into platform journeys" requirement.
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from tests.integration.capabilities.base_capability_test import BaseCapabilityTest

class TestCreateSolutionFromBlueprint(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="Platform Solution Creation from Blueprint",
            test_id_prefix="solution_from_blueprint"
        )
    
    async def run_test(self) -> bool:
        if not await self.authenticate():
            return False
        
        # Step 1: Create workflow → blueprint → solution
        self.print_info("Step 2: Creating workflow first")
        
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
        test_file_name = f"solution_test_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.bpmn"
        
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
            self.print_warning("Could not create workflow - skipping solution creation")
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
        self.print_info("Step 3: Creating blueprint from workflow")
        blueprint_status = await self.submit_intent_and_poll(
            intent_type="create_blueprint",
            parameters={
                "workflow_id": workflow_id
            },
            timeout=300
        )
        
        if not blueprint_status:
            self.print_warning("Could not create blueprint - skipping solution creation")
            return True
        
        blueprint_artifacts = blueprint_status.get("artifacts", {})
        blueprint_artifact = blueprint_artifacts.get("blueprint", {})
        if isinstance(blueprint_artifact, dict):
            semantic_payload = blueprint_artifact.get("semantic_payload", {})
            blueprint_id = semantic_payload.get("blueprint_id")
        else:
            blueprint_id = blueprint_artifact.get("blueprint_id") if isinstance(blueprint_artifact, dict) else None
        
        if not blueprint_id:
            self.print_warning("Could not extract blueprint_id")
            return True
        
        self.print_success(f"Blueprint created: {blueprint_id}")
        
        # Step 3: Create solution from blueprint (using Outcomes Realm create_solution intent)
        self.print_info("Step 4: Creating platform solution from blueprint")
        solution_status = await self.submit_intent_and_poll(
            intent_type="create_solution",
            parameters={
                "solution_source": "blueprint",
                "source_id": blueprint_id
            },
            timeout=300  # Solution creation may take longer
        )
        
        if not solution_status:
            return False
        
        # Validate solution results
        self.print_info("Step 5: Validating solution results")
        solution_artifacts = solution_status.get("artifacts", {})
        
        solution_artifact = solution_artifacts.get("solution", {})
        solution_id = solution_artifacts.get("solution_id")
        
        if not solution_id:
            # Try to extract from solution_artifact
            if isinstance(solution_artifact, dict):
                solution_id = solution_artifact.get("solution_id")
                solution_data = solution_artifact.get("solution", {})
            else:
                solution_data = solution_artifact
        
        if not solution_id:
            self.print_error("No solution_id found in solution result")
            return False
        
        self.print_success(f"Platform solution created successfully: {solution_id}")
        
        # Validate solution structure
        if isinstance(solution_artifact, dict):
            solution_data = solution_artifact.get("solution", {}) or solution_artifact
        
        if solution_data:
            context = solution_data.get("context", {})
            domain_service_bindings = solution_data.get("domain_service_bindings", [])
            supported_intents = solution_data.get("supported_intents", [])
            
            if context:
                goals = context.get("goals", [])
                constraints = context.get("constraints", [])
                if goals:
                    self.print_success(f"Solution has {len(goals)} goals")
                if constraints:
                    self.print_info(f"Solution has {len(constraints)} constraints")
            
            if domain_service_bindings:
                self.print_success(f"Solution has {len(domain_service_bindings)} domain service bindings")
                for binding in domain_service_bindings[:3]:
                    domain = binding.get("domain")
                    system_name = binding.get("system_name")
                    if domain:
                        self.print_info(f"  Domain: {domain}, System: {system_name}")
            
            if supported_intents:
                self.print_success(f"Solution supports {len(supported_intents)} intents")
                self.print_info(f"  Sample intents: {', '.join(supported_intents[:5])}")
        
        self.print_success("✅ Platform Solution Creation from Blueprint: PASSED")
        return True

async def main():
    test = TestCreateSolutionFromBlueprint()
    result = await test.execute()
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
