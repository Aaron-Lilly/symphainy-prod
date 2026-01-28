"""
Generate SOP Intent Service

Implements the generate_sop intent for the Operations Realm.

Contract: docs/intent_contracts/journey_sop_management/intent_generate_sop.md

Purpose: Generate Standard Operating Procedure (SOP) document from workflow.

WHAT (Intent Service Role): I generate SOP documents from workflows
HOW (Intent Service Implementation): I analyze workflows and generate
    structured SOP documents with procedures, roles, and checklists

Naming Convention:
- Realm: Operations Realm
- Artifacts: operations_sop
- Solution = platform construct (OperationsSolution)
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class GenerateSOPService(BaseIntentService):
    """
    Intent service for SOP generation.
    
    Generates SOP documents with:
    - Procedure steps
    - Roles and responsibilities
    - Checklists
    - Prerequisites and outputs
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize GenerateSOPService."""
        super().__init__(
            service_id="generate_sop_service",
            intent_type="generate_sop",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the generate_sop intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            workflow_id = intent_params.get("workflow_id")
            if not workflow_id:
                raise ValueError("workflow_id is required for SOP generation")
            
            sop_options = intent_params.get("sop_options", {})
            
            # Get workflow data
            workflow_data = await self._get_workflow_data(workflow_id, context)
            
            # Generate SOP structure
            sop_structure = await self._generate_sop_structure(workflow_data, sop_options)
            
            # Generate procedure steps
            procedure_steps = await self._generate_procedure_steps(workflow_data)
            
            # Generate roles and responsibilities
            roles = await self._generate_roles(workflow_data)
            
            # Generate checklists
            checklists = await self._generate_checklists(procedure_steps)
            
            # Build SOP document
            sop_id = f"sop_{generate_event_id()}"
            
            sop = {
                "sop_id": sop_id,
                "workflow_id": workflow_id,
                "title": sop_structure.get("title", f"SOP for {workflow_id}"),
                "version": "1.0",
                "structure": sop_structure,
                "procedure_steps": procedure_steps,
                "roles": roles,
                "checklists": checklists,
                "prerequisites": sop_structure.get("prerequisites", []),
                "outputs": sop_structure.get("outputs", []),
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in Artifact Plane
            artifact_id = await self._store_sop(sop, context)
            
            self.logger.info(f"SOP generated: {sop_id} ({len(procedure_steps)} steps)")
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", "status": "completed", "intent_type": self.intent_type,
                    "sop_id": sop_id,
                    "steps_count": len(procedure_steps)
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "sop": sop,
                    "artifact_id": artifact_id
                },
                "events": [
                    {
                        "type": "sop_generated",
                        "sop_id": sop_id,
                        "workflow_id": workflow_id
                    }
                ]
            }
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "failed", "error": str(e)},
                tenant_id=context.tenant_id
            )
            raise
    
    async def _get_workflow_data(self, workflow_id: str, context: ExecutionContext) -> Dict[str, Any]:
        """Get workflow data."""
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    workflow = await artifact_plane.get_artifact(
                        artifact_id=workflow_id,
                        tenant_id=context.tenant_id
                    )
                    if workflow:
                        return workflow.get("content", workflow)
            except Exception:
                pass
        
        return {
            "workflow_id": workflow_id,
            "name": f"Workflow {workflow_id}",
            "steps": [
                {"step_id": "1", "name": "Initiate Process", "description": "Start the process"},
                {"step_id": "2", "name": "Execute Steps", "description": "Execute main steps"},
                {"step_id": "3", "name": "Complete Process", "description": "Finish and document"}
            ]
        }
    
    async def _generate_sop_structure(
        self,
        workflow_data: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate SOP document structure."""
        workflow_name = workflow_data.get("name", "Process")
        
        return {
            "title": f"Standard Operating Procedure: {workflow_name}",
            "purpose": f"This SOP describes the standard operating procedure for {workflow_name}",
            "scope": "All team members involved in this process",
            "prerequisites": [
                "Access to required systems",
                "Necessary permissions and approvals",
                "Required training completed"
            ],
            "outputs": [
                "Completed process documentation",
                "Updated status in system",
                "Notification to stakeholders"
            ],
            "revision_history": [
                {
                    "version": "1.0",
                    "date": datetime.utcnow().strftime("%Y-%m-%d"),
                    "description": "Initial version generated from workflow"
                }
            ]
        }
    
    async def _generate_procedure_steps(self, workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate procedure steps from workflow."""
        procedure_steps = []
        workflow_steps = workflow_data.get("steps", [])
        
        for i, step in enumerate(workflow_steps, 1):
            procedure_steps.append({
                "step_number": i,
                "step_id": step.get("step_id", str(i)),
                "title": step.get("name", f"Step {i}"),
                "description": step.get("description", ""),
                "responsible_role": step.get("role", "Operator"),
                "estimated_duration": step.get("duration_minutes", 15),
                "inputs": step.get("inputs", []),
                "outputs": step.get("outputs", []),
                "notes": step.get("notes", "")
            })
        
        return procedure_steps
    
    async def _generate_roles(self, workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate roles and responsibilities."""
        roles = {}
        
        for step in workflow_data.get("steps", []):
            role = step.get("role", "Operator")
            if role not in roles:
                roles[role] = {
                    "role_name": role,
                    "responsibilities": [],
                    "steps_involved": []
                }
            roles[role]["steps_involved"].append(step.get("name", ""))
            roles[role]["responsibilities"].append(f"Execute {step.get('name', 'step')}")
        
        return list(roles.values())
    
    async def _generate_checklists(self, procedure_steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate checklists for procedure steps."""
        checklists = []
        
        # Pre-process checklist
        checklists.append({
            "checklist_id": "pre_process",
            "title": "Pre-Process Checklist",
            "items": [
                {"item": "All prerequisites met", "checked": False},
                {"item": "Required permissions obtained", "checked": False},
                {"item": "Systems accessible", "checked": False}
            ]
        })
        
        # Step completion checklist
        step_items = [
            {"item": f"Step {s['step_number']}: {s['title']} completed", "checked": False}
            for s in procedure_steps
        ]
        checklists.append({
            "checklist_id": "step_completion",
            "title": "Step Completion Checklist",
            "items": step_items
        })
        
        # Post-process checklist
        checklists.append({
            "checklist_id": "post_process",
            "title": "Post-Process Checklist",
            "items": [
                {"item": "All outputs verified", "checked": False},
                {"item": "Documentation updated", "checked": False},
                {"item": "Stakeholders notified", "checked": False}
            ]
        })
        
        return checklists
    
    async def _store_sop(self, sop: Dict[str, Any], context: ExecutionContext) -> Optional[str]:
        """Store SOP in Artifact Plane."""
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    result = await artifact_plane.create_artifact(
                        artifact_type="sop",
                        content=sop,
                        metadata={"workflow_id": sop.get("workflow_id")},
                        tenant_id=context.tenant_id,
                        include_payload=True
                    )
                    return result.get("artifact_id")
            except Exception as e:
                self.logger.warning(f"Could not store SOP: {e}")
        return None
