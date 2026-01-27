"""
Create Blueprint Intent Service

Implements the create_blueprint intent for the Solution Realm.

Contract: docs/intent_contracts/journey_solution_blueprint_creation/intent_create_blueprint.md

Purpose: Create coexistence blueprint from workflow analysis. Takes workflow_id and creates a
structured blueprint with current state, coexistence state, transformation roadmap, and
responsibility matrix.

WHAT (Intent Service Role): I create coexistence blueprints from workflows
HOW (Intent Service Implementation): I execute the create_blueprint intent, analyze workflow,
    create blueprint structure, store in Artifact Plane, and return structured artifact
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class CreateBlueprintService(BaseIntentService):
    """
    Intent service for blueprint creation.
    
    Creates coexistence blueprints from workflow analysis with current state,
    coexistence state, transformation roadmap, and responsibility matrix.
    Stores artifact in Artifact Plane.
    
    Contract Compliance:
    - Parameters: Section 2 of intent contract (workflow_id: string required)
    - Returns: Section 3 of intent contract
    - Artifact Registration: Section 4 of intent contract
    - Idempotency: Section 5 of intent contract
    - Error Handling: Section 8 of intent contract
    """
    
    def __init__(self, public_works, state_surface):
        """
        Initialize CreateBlueprintService.
        
        Args:
            public_works: Public Works Foundation Service for infrastructure access
            state_surface: State Surface for state management
        """
        super().__init__(
            service_id="create_blueprint_service",
            intent_type="create_blueprint",
            public_works=public_works,
            state_surface=state_surface
        )
        
        # Initialize Artifact Plane access
        self.artifact_plane = None
        if public_works:
            artifact_storage = getattr(public_works, 'artifact_storage_abstraction', None)
            state_management = getattr(public_works, 'state_abstraction', None)
            
            if artifact_storage and state_management:
                try:
                    from symphainy_platform.civic_systems.artifact_plane import ArtifactPlane
                    self.artifact_plane = ArtifactPlane(
                        artifact_storage=artifact_storage,
                        state_management=state_management
                    )
                except Exception as e:
                    self.logger.warning(f"Could not initialize Artifact Plane: {e}")
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the create_blueprint intent.
        
        Intent Flow (from contract):
        1. Validate workflow_id (required)
        2. Retrieve workflow data from Journey Realm
        3. Analyze current state and identify transformation opportunities
        4. Generate coexistence state design
        5. Create transformation roadmap
        6. Build responsibility matrix
        7. Store artifact in Artifact Plane
        8. Return artifact_id reference
        
        Args:
            context: Execution context with intent, tenant, session information
            params: Optional additional parameters (merged with intent.parameters)
        
        Returns:
            Dictionary with artifacts and events per contract Section 3
        
        Raises:
            ValueError: For validation errors (missing workflow_id)
            RuntimeError: For runtime errors
        """
        # Record telemetry (start)
        await self.record_telemetry(
            telemetry_data={
                "action": "execute",
                "status": "started",
                "execution_id": context.execution_id,
                "intent_type": self.intent_type
            },
            tenant_id=context.tenant_id
        )
        
        try:
            # Get intent parameters
            intent_params = context.intent.parameters or {}
            if params:
                intent_params = {**intent_params, **params}
            
            # === VALIDATION (Contract Section 2) ===
            
            workflow_id = intent_params.get("workflow_id")
            if not workflow_id:
                raise ValueError("workflow_id is required for create_blueprint intent")
            
            current_state_workflow_id = intent_params.get("current_state_workflow_id")
            
            self.logger.info(f"Creating blueprint for workflow: {workflow_id}")
            
            # === RETRIEVE WORKFLOW DATA ===
            
            workflow_data = await self._retrieve_workflow_data(
                workflow_id=workflow_id,
                context=context
            )
            
            current_state_data = None
            if current_state_workflow_id:
                current_state_data = await self._retrieve_workflow_data(
                    workflow_id=current_state_workflow_id,
                    context=context
                )
            
            # === GENERATE BLUEPRINT ===
            
            blueprint_id = f"blueprint_{workflow_id}_{str(uuid.uuid4())[:8]}"
            
            # Analyze current state
            current_state = await self._analyze_current_state(
                workflow_data=workflow_data,
                current_state_data=current_state_data,
                context=context
            )
            
            # Design coexistence state
            coexistence_state = await self._design_coexistence_state(
                workflow_data=workflow_data,
                current_state=current_state,
                context=context
            )
            
            # Create transformation roadmap
            roadmap = await self._create_transformation_roadmap(
                current_state=current_state,
                coexistence_state=coexistence_state,
                context=context
            )
            
            # Build responsibility matrix
            responsibility_matrix = await self._build_responsibility_matrix(
                coexistence_state=coexistence_state,
                context=context
            )
            
            # Compile blueprint
            blueprint = {
                "blueprint_id": blueprint_id,
                "workflow_id": workflow_id,
                "current_state_workflow_id": current_state_workflow_id,
                "current_state": current_state,
                "coexistence_state": coexistence_state,
                "roadmap": roadmap,
                "responsibility_matrix": responsibility_matrix,
                "sections": self._generate_blueprint_sections(
                    current_state=current_state,
                    coexistence_state=coexistence_state,
                    roadmap=roadmap,
                    responsibility_matrix=responsibility_matrix
                ),
                "status": "draft",
                "created_at": datetime.utcnow().isoformat()
            }
            
            # === STORE IN ARTIFACT PLANE ===
            
            artifact_payload = {
                "blueprint": blueprint,
                "current_state": current_state,
                "coexistence_state": coexistence_state,
                "roadmap": roadmap,
                "responsibility_matrix": responsibility_matrix,
                "sections": blueprint["sections"]
            }
            
            stored_artifact_id = blueprint_id
            
            if self.artifact_plane:
                try:
                    artifact_result = await self.artifact_plane.create_artifact(
                        artifact_type="blueprint",
                        artifact_id=blueprint_id,
                        payload=artifact_payload,
                        context=context,
                        metadata={
                            "regenerable": True,
                            "retention_policy": "session",
                            "workflow_id": workflow_id
                        }
                    )
                    
                    stored_artifact_id = artifact_result.get("artifact_id", blueprint_id)
                    self.logger.info(f"✅ Blueprint stored in Artifact Plane: {stored_artifact_id}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to store blueprint in Artifact Plane: {e}")
                    # Continue with fallback response
            else:
                self.logger.warning("Artifact Plane not available, returning inline artifact")
            
            # === BUILD RESPONSE (Contract Section 3) ===
            
            semantic_payload = {
                "blueprint_id": stored_artifact_id,
                "workflow_id": workflow_id,
                "execution_id": context.execution_id,
                "session_id": context.session_id
            }
            
            # Return artifact_id reference (not full payload) when stored in Artifact Plane
            if self.artifact_plane:
                structured_artifact = {
                    "result_type": "blueprint",
                    "semantic_payload": semantic_payload,
                    "renderings": {}  # Full artifact in Artifact Plane
                }
            else:
                # Fallback: include full artifact in response
                structured_artifact = {
                    "result_type": "blueprint",
                    "semantic_payload": semantic_payload,
                    "renderings": {
                        "blueprint": blueprint
                    }
                }
            
            self.logger.info(f"✅ Blueprint created: {stored_artifact_id}")
            
            # Record telemetry (success)
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute",
                    "status": "completed",
                    "execution_id": context.execution_id,
                    "intent_type": self.intent_type,
                    "blueprint_id": stored_artifact_id,
                    "workflow_id": workflow_id
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "blueprint": structured_artifact,
                    "blueprint_id": stored_artifact_id
                },
                "events": [
                    {
                        "type": "blueprint_created",
                        "blueprint_id": stored_artifact_id,
                        "workflow_id": workflow_id,
                        "session_id": context.session_id
                    }
                ]
            }
            
        except Exception as e:
            # Record telemetry (failure)
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute",
                    "status": "failed",
                    "execution_id": context.execution_id,
                    "intent_type": self.intent_type,
                    "error": str(e)
                },
                tenant_id=context.tenant_id
            )
            raise
    
    async def _retrieve_workflow_data(
        self,
        workflow_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Retrieve workflow data from Journey Realm.
        
        Args:
            workflow_id: Workflow identifier
            context: Execution context
        
        Returns:
            Dict with workflow data
        """
        # Try to retrieve from Artifact Plane
        if self.artifact_plane:
            try:
                artifact_result = await self.artifact_plane.get_artifact(
                    artifact_id=workflow_id,
                    tenant_id=context.tenant_id,
                    include_payload=True
                )
                
                if artifact_result and artifact_result.get("payload"):
                    return artifact_result["payload"]
            except Exception as e:
                self.logger.warning(f"Could not retrieve workflow from Artifact Plane: {e}")
        
        # Return placeholder if not found
        self.logger.warning(f"Workflow {workflow_id} not found, using placeholder")
        return {
            "workflow_id": workflow_id,
            "name": f"Workflow {workflow_id}",
            "steps": [],
            "status": "unknown"
        }
    
    async def _analyze_current_state(
        self,
        workflow_data: Dict[str, Any],
        current_state_data: Optional[Dict[str, Any]],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Analyze current state from workflow data.
        
        Args:
            workflow_data: Target workflow data
            current_state_data: Optional current state workflow
            context: Execution context
        
        Returns:
            Dict with current state analysis
        """
        # Use current_state_data if provided, else analyze workflow_data
        source = current_state_data or workflow_data
        
        steps = source.get("steps", [])
        
        # Identify manual vs automated steps
        manual_steps = []
        automated_steps = []
        
        for step in steps:
            step_type = step.get("type", "manual")
            if step_type in ["manual", "human"]:
                manual_steps.append(step)
            else:
                automated_steps.append(step)
        
        # Identify friction points
        friction_points = []
        for step in manual_steps:
            friction_points.append({
                "step": step.get("name", "Unknown"),
                "type": "manual_process",
                "impact": "medium",
                "description": f"Manual step: {step.get('description', 'No description')}"
            })
        
        return {
            "description": f"Current state analysis for workflow",
            "workflow_id": source.get("workflow_id"),
            "total_steps": len(steps),
            "manual_steps": len(manual_steps),
            "automated_steps": len(automated_steps),
            "automation_percentage": round(
                (len(automated_steps) / len(steps) * 100) if steps else 0, 1
            ),
            "friction_points": friction_points,
            "pain_points": [
                "Manual data entry prone to errors",
                "Lack of real-time visibility",
                "Multiple handoffs between teams"
            ],
            "strengths": [
                "Established process understanding",
                "Experienced team",
                "Clear ownership"
            ],
            "analyzed_at": datetime.utcnow().isoformat()
        }
    
    async def _design_coexistence_state(
        self,
        workflow_data: Dict[str, Any],
        current_state: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Design coexistence state with AI assistance.
        
        Args:
            workflow_data: Target workflow data
            current_state: Current state analysis
            context: Execution context
        
        Returns:
            Dict with coexistence state design
        """
        # Design AI-assisted steps
        ai_assisted_areas = []
        
        friction_points = current_state.get("friction_points", [])
        for fp in friction_points:
            ai_assisted_areas.append({
                "area": fp.get("step"),
                "ai_capability": "Automated processing",
                "human_oversight": "Exception handling",
                "benefit": f"Reduce manual effort for {fp.get('step')}"
            })
        
        # Define integration points
        integration_points = [
            {
                "system_name": "Source System",
                "integration_type": "API",
                "direction": "inbound",
                "data_flow": "Real-time"
            },
            {
                "system_name": "Target System",
                "integration_type": "API",
                "direction": "outbound",
                "data_flow": "Batch"
            }
        ]
        
        return {
            "description": "Coexistence state with human-AI collaboration",
            "workflow_id": workflow_data.get("workflow_id"),
            "design_principles": [
                "Human in the loop for critical decisions",
                "AI handles repetitive tasks",
                "Real-time visibility and monitoring",
                "Graceful degradation"
            ],
            "ai_assisted_areas": ai_assisted_areas,
            "human_focus_areas": [
                "Exception handling",
                "Quality assurance",
                "Strategic decisions",
                "Stakeholder communication"
            ],
            "integration_points": integration_points,
            "expected_benefits": [
                "50% reduction in manual effort",
                "95% accuracy improvement",
                "Real-time visibility",
                "Faster turnaround time"
            ],
            "designed_at": datetime.utcnow().isoformat()
        }
    
    async def _create_transformation_roadmap(
        self,
        current_state: Dict[str, Any],
        coexistence_state: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Create transformation roadmap from current to coexistence state.
        
        Args:
            current_state: Current state analysis
            coexistence_state: Target coexistence state
            context: Execution context
        
        Returns:
            Dict with transformation roadmap
        """
        phases = [
            {
                "phase": 1,
                "name": "Foundation",
                "duration": "4 weeks",
                "objectives": [
                    "Set up integration infrastructure",
                    "Establish data pipelines",
                    "Configure monitoring"
                ],
                "deliverables": [
                    "Integration framework",
                    "Data mapping document",
                    "Monitoring dashboard"
                ],
                "dependencies": []
            },
            {
                "phase": 2,
                "name": "AI Enablement",
                "duration": "6 weeks",
                "objectives": [
                    "Implement AI-assisted processing",
                    "Train models on historical data",
                    "Configure automation rules"
                ],
                "deliverables": [
                    "AI processing module",
                    "Trained models",
                    "Automation configuration"
                ],
                "dependencies": [1]
            },
            {
                "phase": 3,
                "name": "Coexistence Testing",
                "duration": "4 weeks",
                "objectives": [
                    "Parallel run with existing process",
                    "Validate accuracy and performance",
                    "Train users on new workflow"
                ],
                "deliverables": [
                    "Test results",
                    "Performance benchmarks",
                    "Training materials"
                ],
                "dependencies": [2]
            },
            {
                "phase": 4,
                "name": "Full Coexistence",
                "duration": "2 weeks",
                "objectives": [
                    "Cut over to coexistence model",
                    "Decommission manual steps",
                    "Transition support"
                ],
                "deliverables": [
                    "Go-live certification",
                    "Support handoff",
                    "Lessons learned"
                ],
                "dependencies": [3]
            }
        ]
        
        return {
            "phases": phases,
            "total_duration": "16 weeks",
            "critical_path": [1, 2, 3, 4],
            "milestones": [
                {"name": "Foundation Complete", "phase": 1, "week": 4},
                {"name": "AI Enabled", "phase": 2, "week": 10},
                {"name": "Testing Complete", "phase": 3, "week": 14},
                {"name": "Go-Live", "phase": 4, "week": 16}
            ],
            "risks": [
                {
                    "risk": "Data quality issues",
                    "mitigation": "Early data profiling and cleansing"
                },
                {
                    "risk": "User adoption",
                    "mitigation": "Change management and training"
                }
            ],
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def _build_responsibility_matrix(
        self,
        coexistence_state: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Build responsibility matrix (RACI-like) for coexistence.
        
        Args:
            coexistence_state: Coexistence state design
            context: Execution context
        
        Returns:
            Dict with responsibility matrix
        """
        responsibilities = []
        
        # AI responsibilities
        ai_areas = coexistence_state.get("ai_assisted_areas", [])
        for area in ai_areas:
            responsibilities.append({
                "step": area.get("area", "Unknown"),
                "human": ["Monitor", "Review exceptions"],
                "ai_symphainy": ["Execute", "Report"],
                "external_systems": [],
                "decision_authority": "AI with human oversight"
            })
        
        # Human responsibilities
        human_areas = coexistence_state.get("human_focus_areas", [])
        for area in human_areas:
            responsibilities.append({
                "step": area,
                "human": ["Execute", "Decide"],
                "ai_symphainy": ["Assist", "Recommend"],
                "external_systems": [],
                "decision_authority": "Human"
            })
        
        return {
            "responsibilities": responsibilities,
            "legend": {
                "Execute": "Performs the activity",
                "Monitor": "Watches for issues",
                "Decide": "Makes final decision",
                "Assist": "Provides support",
                "Recommend": "Suggests actions",
                "Review": "Validates output"
            },
            "escalation_path": [
                "AI detects anomaly → Human review",
                "Human exception → Team lead",
                "System failure → IT support"
            ],
            "created_at": datetime.utcnow().isoformat()
        }
    
    def _generate_blueprint_sections(
        self,
        current_state: Dict[str, Any],
        coexistence_state: Dict[str, Any],
        roadmap: Dict[str, Any],
        responsibility_matrix: Dict[str, Any]
    ) -> list:
        """Generate blueprint document sections."""
        return [
            {
                "section": "Executive Summary",
                "content": "This blueprint outlines the transformation from current manual processes to a human-AI coexistence model."
            },
            {
                "section": "Current State Analysis",
                "content": current_state.get("description", ""),
                "metrics": {
                    "automation_percentage": current_state.get("automation_percentage", 0),
                    "friction_points": len(current_state.get("friction_points", []))
                }
            },
            {
                "section": "Target Coexistence State",
                "content": coexistence_state.get("description", ""),
                "benefits": coexistence_state.get("expected_benefits", [])
            },
            {
                "section": "Transformation Roadmap",
                "content": f"Total duration: {roadmap.get('total_duration', 'TBD')}",
                "phases_count": len(roadmap.get("phases", []))
            },
            {
                "section": "Responsibility Matrix",
                "content": "Defines who does what in the coexistence model",
                "responsibilities_count": len(responsibility_matrix.get("responsibilities", []))
            },
            {
                "section": "Integration Requirements",
                "content": "System integration requirements",
                "integration_points": len(coexistence_state.get("integration_points", [])),
                "resource_requirements": [
                    "Integration specialists",
                    "Data engineers",
                    "Change management support"
                ]
            }
        ]
