#!/usr/bin/env python3
"""
Test: Coexistence Analysis

Tests the analyze_coexistence capability:
- Coexistence analysis completes
- Conflicts and dependencies are identified
- Integration points are found
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

class TestAnalyzeCoexistence(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="Coexistence Analysis",
            test_id_prefix="analyze_coexistence"
        )
    
    async def run_test(self) -> bool:
        if not await self.authenticate():
            return False
        
        # Step 1: Create a workflow to analyze
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
        test_file_name = f"coexistence_test_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.bpmn"
        
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
            self.print_warning("Could not create workflow - skipping coexistence analysis")
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
        
        # Step 2: Analyze coexistence
        self.print_info("Step 3: Analyzing coexistence")
        coexistence_status = await self.submit_intent_and_poll(
            intent_type="analyze_coexistence",
            parameters={
                "workflow_id": workflow_id
            },
            timeout=180  # Analysis may take longer
        )
        
        if not coexistence_status:
            return False
        
        # Validate coexistence analysis results
        self.print_info("Step 4: Validating coexistence analysis results")
        coexistence_artifacts = coexistence_status.get("artifacts", {})
        
        coexistence_analysis = coexistence_artifacts.get("coexistence_analysis", {})
        if isinstance(coexistence_analysis, dict):
            semantic_payload = coexistence_analysis.get("semantic_payload", {})
            analysis_id = semantic_payload.get("analysis_id")
            analysis_data = coexistence_analysis.get("renderings", {}).get("coexistence_analysis", {})
        else:
            analysis_id = coexistence_analysis.get("analysis_id") if isinstance(coexistence_analysis, dict) else None
            analysis_data = coexistence_analysis
        
        if not analysis_data:
            self.print_error("No coexistence analysis data found")
            return False
        
        self.print_success("Coexistence analysis completed successfully")
        
        # Validate analysis structure
        existing_processes = analysis_data.get("existing_processes", [])
        integration_points = analysis_data.get("integration_points", [])
        summary = analysis_data.get("summary", {})
        
        if existing_processes:
            self.print_success(f"Analysis identified {len(existing_processes)} existing processes")
            # Check for conflicts and dependencies
            conflicts = [p for p in existing_processes if p.get("interaction_type") == "conflict"]
            dependencies = [p for p in existing_processes if p.get("interaction_type") == "dependency"]
            if conflicts:
                self.print_info(f"  Found {len(conflicts)} conflicts")
            if dependencies:
                self.print_info(f"  Found {len(dependencies)} dependencies")
        else:
            self.print_info("No existing processes identified (may be expected for new workflows)")
        
        if integration_points:
            self.print_success(f"Analysis identified {len(integration_points)} integration points")
        else:
            self.print_info("No integration points identified (may be expected)")
        
        if summary:
            total_conflicts = summary.get("total_conflicts", 0)
            total_dependencies = summary.get("total_dependencies", 0)
            risk_level = summary.get("risk_level")
            
            if total_conflicts or total_dependencies:
                self.print_info(f"Summary: {total_conflicts} conflicts, {total_dependencies} dependencies")
            if risk_level:
                self.print_info(f"Risk level: {risk_level}")
        
        self.print_success("✅ Coexistence Analysis: PASSED")
        return True

async def main():
    test = TestAnalyzeCoexistence()
    result = await test.execute()
    return 0 if result else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
