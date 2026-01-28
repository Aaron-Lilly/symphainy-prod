"""
Generate Roadmap Intent Service

Implements the generate_roadmap intent for the Outcomes Realm.

Contract: docs/intent_contracts/journey_outcomes_roadmap_generation/intent_generate_roadmap.md

Purpose: Generate strategic roadmap from business goals. Takes goals array and creates a
structured roadmap with phases, milestones, timeline, and dependencies.

WHAT (Intent Service Role): I generate strategic roadmaps from goals
HOW (Intent Service Implementation): I execute the generate_roadmap intent, create roadmap
    structure, generate visualization, store in Artifact Plane, and return structured artifact

Naming Convention:
- Realm: Outcomes Realm
- Artifacts: outcome_roadmap
- Solution = platform construct (OutcomesSolution)
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class GenerateRoadmapService(BaseIntentService):
    """
    Intent service for roadmap generation.
    
    Generates strategic roadmaps from business goals with phases, milestones,
    timeline, and dependencies. Stores artifact in Artifact Plane.
    
    Contract Compliance:
    - Parameters: Section 2 of intent contract (goals: string[] required)
    - Returns: Section 3 of intent contract
    - Artifact Registration: Section 4 of intent contract
    - Idempotency: Section 5 of intent contract
    - Error Handling: Section 8 of intent contract
    """
    
    def __init__(self, public_works, state_surface):
        """
        Initialize GenerateRoadmapService.
        
        Args:
            public_works: Public Works Foundation Service for infrastructure access
            state_surface: State Surface for state management
        """
        super().__init__(
            service_id="generate_roadmap_service",
            intent_type="generate_roadmap",
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
        Execute the generate_roadmap intent.
        
        Intent Flow (from contract):
        1. Validate goals array (required)
        2. Generate roadmap structure with phases and milestones
        3. Create strategic plan
        4. Generate roadmap visualization (optional)
        5. Store artifact in Artifact Plane
        6. Return artifact_id reference
        
        Args:
            context: Execution context with intent, tenant, session information
            params: Optional additional parameters (merged with intent.parameters)
        
        Returns:
            Dictionary with artifacts and events per contract Section 3
        
        Raises:
            ValueError: For validation errors (missing goals)
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
            
            goals = intent_params.get("goals", [])
            if not goals or len(goals) == 0:
                raise ValueError("Goals are required for roadmap generation. Provide goals as string array.")
            
            roadmap_options = intent_params.get("roadmap_options", {})
            
            self.logger.info(f"Generating roadmap for {len(goals)} goals")
            
            # === GENERATE ROADMAP ===
            
            roadmap_id = f"roadmap_{str(uuid.uuid4())}"
            
            # Generate roadmap structure
            roadmap = await self._generate_roadmap_structure(
                goals=goals,
                roadmap_options=roadmap_options,
                context=context
            )
            
            # Ensure roadmap_id is set
            roadmap["roadmap_id"] = roadmap_id
            
            # Generate strategic plan
            strategic_plan = await self._generate_strategic_plan(
                goals=goals,
                roadmap=roadmap,
                roadmap_options=roadmap_options,
                context=context
            )
            
            # === GENERATE VISUALIZATION (optional) ===
            
            roadmap_visual = None
            if self.public_works:
                try:
                    visual_abstraction = self.public_works.get_visual_generation_abstraction()
                    if visual_abstraction:
                        visual_result = await visual_abstraction.create_roadmap_visual(
                            roadmap_data=roadmap,
                            tenant_id=context.tenant_id
                        )
                        
                        if visual_result and visual_result.success:
                            roadmap_visual = {
                                "image_base64": visual_result.image_base64,
                                "storage_path": visual_result.metadata.get("storage_path")
                            }
                except Exception as e:
                    self.logger.warning(f"Failed to generate roadmap visualization: {e}")
            
            # === STORE IN ARTIFACT PLANE ===
            
            artifact_payload = {
                "roadmap": roadmap,
                "strategic_plan": strategic_plan
            }
            
            if roadmap_visual:
                artifact_payload["roadmap_visual"] = roadmap_visual
            
            stored_artifact_id = roadmap_id
            
            if self.artifact_plane:
                try:
                    artifact_result = await self.artifact_plane.create_artifact(
                        artifact_type="roadmap",
                        artifact_id=roadmap_id,
                        payload=artifact_payload,
                        context=context,
                        metadata={
                            "regenerable": True,
                            "retention_policy": "session",
                            "goals_count": len(goals)
                        }
                    )
                    
                    stored_artifact_id = artifact_result.get("artifact_id", roadmap_id)
                    self.logger.info(f"✅ Roadmap stored in Artifact Plane: {stored_artifact_id}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to store roadmap in Artifact Plane: {e}")
                    # Continue with fallback response
            else:
                self.logger.warning("Artifact Plane not available, returning inline artifact")
            
            # === BUILD RESPONSE (Contract Section 3) ===
            
            semantic_payload = {
                "roadmap_id": stored_artifact_id,
                "execution_id": context.execution_id,
                "session_id": context.session_id,
                "goals_count": len(goals)
            }
            
            # Return artifact_id reference (not full payload) when stored in Artifact Plane
            if self.artifact_plane:
                structured_artifact = {
                    "result_type": "roadmap",
                    "semantic_payload": semantic_payload,
                    "renderings": {}  # Full artifact in Artifact Plane
                }
            else:
                # Fallback: include full artifact in response
                structured_artifact = {
                    "result_type": "roadmap",
                    "semantic_payload": semantic_payload,
                    "renderings": {
                        "roadmap": roadmap,
                        "strategic_plan": strategic_plan
                    }
                }
                if roadmap_visual:
                    structured_artifact["renderings"]["roadmap_visual"] = roadmap_visual
            
            self.logger.info(f"✅ Roadmap generated: {stored_artifact_id}")
            
            # Record telemetry (success)
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute",
                    "status": "completed",
                    "execution_id": context.execution_id,
                    "intent_type": self.intent_type,
                    "roadmap_id": stored_artifact_id,
                    "goals_count": len(goals)
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "roadmap": structured_artifact,
                    "roadmap_id": stored_artifact_id
                },
                "events": [
                    {
                        "type": "roadmap_generated",
                        "roadmap_id": stored_artifact_id,
                        "session_id": context.session_id,
                        "goals_count": len(goals)
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
    
    async def _generate_roadmap_structure(
        self,
        goals: List[str],
        roadmap_options: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate roadmap structure with phases and milestones.
        
        Args:
            goals: List of business goals
            roadmap_options: Roadmap generation options
            context: Execution context
        
        Returns:
            Dict with roadmap structure
        """
        phases = []
        milestones = []
        
        # Generate phases based on goals
        timeline = roadmap_options.get("timeline", "12 months")
        
        # Phase 1: Analysis & Planning
        phases.append({
            "phase": 1,
            "name": "Analysis & Planning",
            "description": "Analyze current state and plan transformation",
            "duration": "2 months",
            "status": "pending",
            "objectives": [
                "Complete data discovery",
                "Document current processes",
                "Define success criteria"
            ],
            "deliverables": [
                "Current state analysis",
                "Gap analysis",
                "Project plan"
            ]
        })
        
        milestones.append({
            "milestone_id": "m1",
            "name": "Analysis Complete",
            "phase": 1,
            "target_date": "Month 2",
            "status": "pending"
        })
        
        # Phase 2: Design & Development
        phases.append({
            "phase": 2,
            "name": "Design & Development",
            "description": "Design solution architecture and develop components",
            "duration": "4 months",
            "status": "pending",
            "objectives": [
                "Design target architecture",
                "Develop integration components",
                "Create data mappings"
            ],
            "deliverables": [
                "Solution architecture",
                "Integration design",
                "Data mapping specifications"
            ]
        })
        
        milestones.append({
            "milestone_id": "m2",
            "name": "Design Complete",
            "phase": 2,
            "target_date": "Month 4",
            "status": "pending"
        })
        
        milestones.append({
            "milestone_id": "m3",
            "name": "Development Complete",
            "phase": 2,
            "target_date": "Month 6",
            "status": "pending"
        })
        
        # Phase 3: Testing & Validation
        phases.append({
            "phase": 3,
            "name": "Testing & Validation",
            "description": "Test solution and validate against requirements",
            "duration": "3 months",
            "status": "pending",
            "objectives": [
                "Execute test plans",
                "Validate data accuracy",
                "Performance testing"
            ],
            "deliverables": [
                "Test results",
                "Validation report",
                "Performance benchmarks"
            ]
        })
        
        milestones.append({
            "milestone_id": "m4",
            "name": "UAT Complete",
            "phase": 3,
            "target_date": "Month 8",
            "status": "pending"
        })
        
        # Phase 4: Deployment & Transition
        phases.append({
            "phase": 4,
            "name": "Deployment & Transition",
            "description": "Deploy solution and transition operations",
            "duration": "3 months",
            "status": "pending",
            "objectives": [
                "Deploy to production",
                "Execute data migration",
                "Transition support"
            ],
            "deliverables": [
                "Production deployment",
                "Migration completion",
                "Support handoff"
            ]
        })
        
        milestones.append({
            "milestone_id": "m5",
            "name": "Go-Live",
            "phase": 4,
            "target_date": "Month 10",
            "status": "pending"
        })
        
        milestones.append({
            "milestone_id": "m6",
            "name": "Project Complete",
            "phase": 4,
            "target_date": "Month 12",
            "status": "pending"
        })
        
        # Add goal-specific deliverables
        for i, goal in enumerate(goals):
            # Find appropriate phase for goal
            phase_idx = min(i % len(phases), len(phases) - 1)
            phases[phase_idx]["objectives"].append(goal)
        
        return {
            "phases": phases,
            "milestones": milestones,
            "timeline": {
                "total_duration": timeline,
                "start_date": "TBD",
                "end_date": "TBD"
            },
            "resources": {
                "estimated_team_size": 5,
                "key_roles": [
                    "Project Manager",
                    "Solution Architect",
                    "Data Engineer",
                    "Business Analyst",
                    "QA Lead"
                ]
            },
            "risks": [
                {
                    "risk": "Data quality issues",
                    "impact": "High",
                    "mitigation": "Early data profiling and quality assessment"
                },
                {
                    "risk": "Integration complexity",
                    "impact": "Medium",
                    "mitigation": "Phased integration approach"
                }
            ],
            "dependencies": [
                {
                    "from_phase": 1,
                    "to_phase": 2,
                    "type": "finish-to-start"
                },
                {
                    "from_phase": 2,
                    "to_phase": 3,
                    "type": "finish-to-start"
                },
                {
                    "from_phase": 3,
                    "to_phase": 4,
                    "type": "finish-to-start"
                }
            ],
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def _generate_strategic_plan(
        self,
        goals: List[str],
        roadmap: Dict[str, Any],
        roadmap_options: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate strategic plan from goals.
        
        Args:
            goals: List of business goals
            roadmap: Generated roadmap structure
            roadmap_options: Roadmap generation options
            context: Execution context
        
        Returns:
            Dict with strategic plan
        """
        plan_id = generate_event_id()
        
        # Convert goals to objectives with strategies
        objectives = []
        for i, goal in enumerate(goals):
            objectives.append({
                "objective_id": f"obj_{i+1}",
                "description": goal,
                "priority": "high" if i < 3 else "medium",
                "strategies": [
                    f"Define metrics for measuring '{goal}'",
                    f"Identify stakeholders for '{goal}'",
                    f"Develop action plan for '{goal}'"
                ]
            })
        
        # Define success metrics
        metrics = [
            {
                "metric": "On-time delivery",
                "target": "100% of milestones met",
                "measurement": "Milestone tracking"
            },
            {
                "metric": "Quality score",
                "target": ">95% defect-free",
                "measurement": "QA testing results"
            },
            {
                "metric": "Stakeholder satisfaction",
                "target": ">90% approval",
                "measurement": "Feedback surveys"
            }
        ]
        
        return {
            "plan_id": plan_id,
            "goals": goals,
            "objectives": objectives,
            "strategies": [
                "Phased implementation approach",
                "Continuous stakeholder engagement",
                "Agile delivery methodology",
                "Risk-based testing strategy"
            ],
            "tactics": [
                "Weekly status meetings",
                "Bi-weekly sprint reviews",
                "Monthly steering committee updates"
            ],
            "metrics": metrics,
            "timeline": roadmap_options.get("timeline", "12 months"),
            "created_at": datetime.utcnow().isoformat()
        }
