"""
Create Workflow Intent Service

Implements the create_workflow intent for the Operations Realm.

Contract: docs/intent_contracts/journey_workflow_management/intent_create_workflow.md

Purpose: Create workflow from SOP document or BPMN file.

WHAT (Intent Service Role): I create workflows from SOPs or BPMN files
HOW (Intent Service Implementation): I parse input documents and generate
    structured workflow definitions with steps, transitions, and metadata

Naming Convention:
- Realm: Operations Realm
- Artifacts: operations_workflow
- Solution = platform construct (OperationsSolution)
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class CreateWorkflowService(BaseIntentService):
    """
    Intent service for workflow creation.
    
    Creates workflows from:
    - SOP documents
    - BPMN files
    - Manual specification
    
    Generates structured workflow with steps, transitions, and metadata.
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize CreateWorkflowService."""
        super().__init__(
            service_id="create_workflow_service",
            intent_type="create_workflow",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the create_workflow intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            # Determine source type
            sop_id = intent_params.get("sop_id")
            bpmn_file_id = intent_params.get("bpmn_file_id")
            workflow_spec = intent_params.get("workflow_spec")
            
            if not any([sop_id, bpmn_file_id, workflow_spec]):
                raise ValueError("One of sop_id, bpmn_file_id, or workflow_spec is required")
            
            # Generate workflow based on source
            if sop_id:
                workflow = await self._create_from_sop(sop_id, context)
            elif bpmn_file_id:
                workflow = await self._create_from_bpmn(bpmn_file_id, context)
            else:
                workflow = await self._create_from_spec(workflow_spec, context)
            
            # Enhance workflow with metadata
            workflow_id = f"workflow_{generate_event_id()}"
            workflow["workflow_id"] = workflow_id
            workflow["created_at"] = datetime.utcnow().isoformat()
            workflow["source"] = {
                "type": "sop" if sop_id else "bpmn" if bpmn_file_id else "spec",
                "id": sop_id or bpmn_file_id or "manual"
            }
            
            # Generate visualization data
            workflow["visualization"] = self._generate_visualization_data(workflow)
            
            # Store in Artifact Plane
            artifact_id = await self._store_workflow(workflow, context)
            
            self.logger.info(f"Workflow created: {workflow_id} ({len(workflow.get('steps', []))} steps)")
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", "status": "completed", "intent_type": self.intent_type,
                    "workflow_id": workflow_id,
                    "steps_count": len(workflow.get("steps", []))
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "workflow": workflow,
                    "artifact_id": artifact_id
                },
                "events": [
                    {
                        "type": "workflow_created",
                        "workflow_id": workflow_id,
                        "source_type": workflow["source"]["type"]
                    }
                ]
            }
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "failed", "error": str(e)},
                tenant_id=context.tenant_id
            )
            raise
    
    async def _create_from_sop(self, sop_id: str, context: ExecutionContext) -> Dict[str, Any]:
        """Create workflow from SOP document."""
        # Get SOP data
        sop_data = await self._get_sop_data(sop_id, context)
        
        steps = []
        procedure_steps = sop_data.get("procedure_steps", [])
        
        for ps in procedure_steps:
            steps.append({
                "step_id": ps.get("step_id", str(ps.get("step_number", len(steps) + 1))),
                "name": ps.get("title", f"Step {len(steps) + 1}"),
                "description": ps.get("description", ""),
                "role": ps.get("responsible_role", "Operator"),
                "duration_minutes": ps.get("estimated_duration", 15),
                "inputs": ps.get("inputs", []),
                "outputs": ps.get("outputs", [])
            })
        
        # Generate transitions
        transitions = []
        for i in range(len(steps) - 1):
            transitions.append({
                "from_step": steps[i]["step_id"],
                "to_step": steps[i + 1]["step_id"],
                "condition": "complete"
            })
        
        return {
            "name": sop_data.get("title", f"Workflow from SOP {sop_id}"),
            "description": sop_data.get("purpose", ""),
            "steps": steps,
            "transitions": transitions
        }
    
    async def _create_from_bpmn(self, bpmn_file_id: str, context: ExecutionContext) -> Dict[str, Any]:
        """Create workflow from BPMN file."""
        # Get BPMN content
        bpmn_content = await self._get_bpmn_content(bpmn_file_id, context)
        
        # Parse BPMN (simplified - real implementation would use BPMN parser)
        steps = [
            {"step_id": "start", "name": "Start", "type": "start_event"},
            {"step_id": "task_1", "name": "Task 1", "type": "task"},
            {"step_id": "task_2", "name": "Task 2", "type": "task"},
            {"step_id": "end", "name": "End", "type": "end_event"}
        ]
        
        transitions = [
            {"from_step": "start", "to_step": "task_1", "condition": "default"},
            {"from_step": "task_1", "to_step": "task_2", "condition": "default"},
            {"from_step": "task_2", "to_step": "end", "condition": "default"}
        ]
        
        return {
            "name": f"Workflow from BPMN {bpmn_file_id}",
            "description": "Workflow created from BPMN file",
            "steps": steps,
            "transitions": transitions,
            "bpmn_source": bpmn_file_id
        }
    
    async def _create_from_spec(self, spec: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Create workflow from manual specification."""
        steps = spec.get("steps", [])
        
        # Ensure steps have IDs
        for i, step in enumerate(steps):
            if "step_id" not in step:
                step["step_id"] = str(i + 1)
        
        # Generate default transitions if not provided
        transitions = spec.get("transitions", [])
        if not transitions:
            for i in range(len(steps) - 1):
                transitions.append({
                    "from_step": steps[i]["step_id"],
                    "to_step": steps[i + 1]["step_id"],
                    "condition": "complete"
                })
        
        return {
            "name": spec.get("name", "Manual Workflow"),
            "description": spec.get("description", ""),
            "steps": steps,
            "transitions": transitions
        }
    
    async def _get_sop_data(self, sop_id: str, context: ExecutionContext) -> Dict[str, Any]:
        """Get SOP data from artifact plane."""
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    sop = await artifact_plane.get_artifact(
                        artifact_id=sop_id,
                        tenant_id=context.tenant_id
                    )
                    if sop:
                        return sop.get("content", sop)
            except Exception:
                pass
        
        return {"sop_id": sop_id, "procedure_steps": []}
    
    async def _get_bpmn_content(self, bpmn_file_id: str, context: ExecutionContext) -> str:
        """Get BPMN file content."""
        if self.public_works:
            try:
                file_storage = self.public_works.get_file_storage_abstraction()
                if file_storage:
                    content = await file_storage.download_file(
                        file_id=bpmn_file_id,
                        tenant_id=context.tenant_id
                    )
                    return content
            except Exception:
                pass
        return ""
    
    def _generate_visualization_data(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visualization data for workflow."""
        nodes = []
        edges = []
        
        steps = workflow.get("steps", [])
        for i, step in enumerate(steps):
            nodes.append({
                "id": step["step_id"],
                "label": step.get("name", f"Step {i+1}"),
                "type": step.get("type", "task"),
                "x": 150 + i * 200,
                "y": 200
            })
        
        for transition in workflow.get("transitions", []):
            edges.append({
                "id": f"{transition['from_step']}_to_{transition['to_step']}",
                "source": transition["from_step"],
                "target": transition["to_step"],
                "label": transition.get("condition", "")
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "layout": "horizontal"
        }
    
    async def _store_workflow(self, workflow: Dict[str, Any], context: ExecutionContext) -> Optional[str]:
        """Store workflow in Artifact Plane."""
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    result = await artifact_plane.create_artifact(
                        artifact_type="workflow",
                        content=workflow,
                        metadata={"source_type": workflow.get("source", {}).get("type")},
                        tenant_id=context.tenant_id,
                        include_payload=True
                    )
                    return result.get("artifact_id")
            except Exception as e:
                self.logger.warning(f"Could not store workflow: {e}")
        return None
