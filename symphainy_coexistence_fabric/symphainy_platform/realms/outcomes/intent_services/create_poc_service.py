"""
Create POC Intent Service

Implements the create_poc intent for the Outcomes Realm.

Contract: docs/intent_contracts/journey_outcomes_poc_proposal/intent_create_poc.md

Purpose: Create Proof of Concept proposal from description. Takes description and creates a
structured POC proposal with objectives, scope, deliverables, timeline, and resources.

WHAT (Intent Service Role): I create POC proposals from descriptions
HOW (Intent Service Implementation): I execute the create_poc intent, create POC structure,
    generate visualization, store in Artifact Plane, and return structured artifact

Naming Convention:
- Realm: Outcomes Realm
- Artifacts: outcome_poc
- Solution = platform construct (OutcomesSolution)
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


class CreatePOCService(BaseIntentService):
    """
    Intent service for POC proposal creation.
    
    Creates Proof of Concept proposals from descriptions with objectives,
    scope, deliverables, timeline, and resource estimates. Stores artifact
    in Artifact Plane.
    
    Contract Compliance:
    - Parameters: Section 2 of intent contract (description: string required)
    - Returns: Section 3 of intent contract
    - Artifact Registration: Section 4 of intent contract
    - Idempotency: Section 5 of intent contract
    - Error Handling: Section 8 of intent contract
    """
    
    def __init__(self, public_works, state_surface):
        """
        Initialize CreatePOCService.
        
        Args:
            public_works: Public Works Foundation Service for infrastructure access
            state_surface: State Surface for state management
        """
        super().__init__(
            service_id="create_poc_service",
            intent_type="create_poc",
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
        Execute the create_poc intent.
        
        Intent Flow (from contract):
        1. Validate description (required)
        2. Generate POC proposal structure
        3. Create scope, deliverables, timeline
        4. Generate POC visualization (optional)
        5. Store artifact in Artifact Plane
        6. Return artifact_id reference
        
        Args:
            context: Execution context with intent, tenant, session information
            params: Optional additional parameters (merged with intent.parameters)
        
        Returns:
            Dictionary with artifacts and events per contract Section 3
        
        Raises:
            ValueError: For validation errors (missing description)
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
            
            description = intent_params.get("description", "")
            if not description:
                raise ValueError("Description is required for POC creation")
            
            poc_options = intent_params.get("poc_options", {})
            
            self.logger.info(f"Creating POC proposal from description: {description[:100]}...")
            
            # === GENERATE POC PROPOSAL ===
            
            proposal_id = f"poc_{str(uuid.uuid4())}"
            
            # Generate POC proposal structure
            poc_proposal = await self._generate_poc_proposal(
                description=description,
                poc_options=poc_options,
                context=context
            )
            
            # Ensure IDs are set
            poc_proposal["poc_id"] = proposal_id
            poc_proposal["proposal_id"] = proposal_id
            
            # === GENERATE VISUALIZATION (optional) ===
            
            poc_visual = None
            if self.public_works:
                try:
                    visual_abstraction = self.public_works.get_visual_generation_abstraction()
                    if visual_abstraction:
                        visual_result = await visual_abstraction.create_poc_visual(
                            poc_data=poc_proposal,
                            tenant_id=context.tenant_id
                        )
                        
                        if visual_result and visual_result.success:
                            poc_visual = {
                                "image_base64": visual_result.image_base64,
                                "storage_path": visual_result.metadata.get("storage_path")
                            }
                except Exception as e:
                    self.logger.warning(f"Failed to generate POC visualization: {e}")
            
            # === STORE IN ARTIFACT PLANE ===
            
            artifact_payload = {
                "poc_proposal": poc_proposal,
                "proposal": poc_proposal.get("proposal", poc_proposal)
            }
            
            if poc_visual:
                artifact_payload["poc_visual"] = poc_visual
            
            stored_artifact_id = proposal_id
            
            if self.artifact_plane:
                try:
                    artifact_result = await self.artifact_plane.create_artifact(
                        artifact_type="poc",
                        artifact_id=proposal_id,
                        payload=artifact_payload,
                        context=context,
                        metadata={
                            "regenerable": True,
                            "retention_policy": "session",
                            "description_length": len(description)
                        }
                    )
                    
                    stored_artifact_id = artifact_result.get("artifact_id", proposal_id)
                    self.logger.info(f"✅ POC stored in Artifact Plane: {stored_artifact_id}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to store POC in Artifact Plane: {e}")
                    # Continue with fallback response
            else:
                self.logger.warning("Artifact Plane not available, returning inline artifact")
            
            # === BUILD RESPONSE (Contract Section 3) ===
            
            semantic_payload = {
                "proposal_id": stored_artifact_id,
                "poc_id": stored_artifact_id,
                "execution_id": context.execution_id,
                "session_id": context.session_id
            }
            
            # Return artifact_id reference (not full payload) when stored in Artifact Plane
            if self.artifact_plane:
                structured_artifact = {
                    "result_type": "poc",
                    "semantic_payload": semantic_payload,
                    "renderings": {}  # Full artifact in Artifact Plane
                }
            else:
                # Fallback: include full artifact in response
                structured_artifact = {
                    "result_type": "poc",
                    "semantic_payload": semantic_payload,
                    "renderings": {
                        "poc_proposal": poc_proposal,
                        "proposal": poc_proposal.get("proposal")
                    }
                }
                if poc_visual:
                    structured_artifact["renderings"]["poc_visual"] = poc_visual
            
            self.logger.info(f"✅ POC proposal created: {stored_artifact_id}")
            
            # Record telemetry (success)
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute",
                    "status": "completed",
                    "execution_id": context.execution_id,
                    "intent_type": self.intent_type,
                    "proposal_id": stored_artifact_id
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "poc": structured_artifact,
                    "proposal_id": stored_artifact_id,
                    "poc_id": stored_artifact_id
                },
                "events": [
                    {
                        "type": "poc_proposal_created",
                        "proposal_id": stored_artifact_id,
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
    
    async def _generate_poc_proposal(
        self,
        description: str,
        poc_options: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate POC proposal structure.
        
        Args:
            description: POC description
            poc_options: POC generation options
            context: Execution context
        
        Returns:
            Dict with POC proposal
        """
        proposal_id = generate_event_id()
        
        # Generate title from description
        title = poc_options.get("title") or self._generate_title(description)
        
        # Generate objectives based on description
        objectives = self._generate_objectives(description)
        
        # Generate scope
        scope = self._generate_scope(description, poc_options)
        
        # Generate timeline
        duration = poc_options.get("timeline", "3 months")
        timeline = self._generate_timeline(duration)
        
        # Generate resource requirements
        resources = self._generate_resources(poc_options)
        
        # Generate success criteria
        success_criteria = self._generate_success_criteria(description)
        
        # Generate risks
        risks = self._generate_risks(description)
        
        # Generate financials
        financials = self._generate_financials(poc_options)
        
        proposal = {
            "proposal_id": proposal_id,
            "title": title,
            "description": description,
            "objectives": objectives,
            "scope": scope,
            "timeline": timeline,
            "resources": resources,
            "success_criteria": success_criteria,
            "risks": risks,
            "financials": financials,
            "status": "draft",
            "created_at": datetime.utcnow().isoformat()
        }
        
        return {
            "proposal_id": proposal_id,
            "proposal": proposal,
            "created_at": datetime.utcnow().isoformat()
        }
    
    def _generate_title(self, description: str) -> str:
        """Generate POC title from description."""
        # Take first sentence or first 50 chars
        if "." in description[:100]:
            title = description.split(".")[0]
        else:
            title = description[:50]
        
        return f"POC: {title.strip()}"
    
    def _generate_objectives(self, description: str) -> list:
        """Generate objectives from description."""
        objectives = [
            "Validate technical feasibility of the proposed solution",
            "Demonstrate key capabilities and integrations",
            "Identify potential risks and mitigation strategies",
            "Establish baseline metrics for success measurement"
        ]
        
        # Add description-specific objective
        objectives.insert(0, f"Demonstrate: {description[:100]}...")
        
        return objectives
    
    def _generate_scope(self, description: str, poc_options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate scope definition."""
        return {
            "in_scope": [
                "Core functionality demonstration",
                "Integration with primary systems",
                "Data flow validation",
                "User acceptance testing"
            ],
            "out_of_scope": [
                "Full production deployment",
                "Performance optimization",
                "Complete documentation",
                "Training and change management"
            ],
            "assumptions": [
                "Access to required systems and data",
                "Stakeholder availability for reviews",
                "Infrastructure resources available"
            ],
            "constraints": poc_options.get("constraints", [
                "Limited timeline (3 months)",
                "Dedicated team of 3-5 resources",
                "Sandbox environment only"
            ])
        }
    
    def _generate_timeline(self, duration: str) -> Dict[str, Any]:
        """Generate timeline structure."""
        return {
            "duration": duration,
            "phases": [
                {
                    "phase": 1,
                    "name": "Setup & Design",
                    "duration": "2 weeks",
                    "deliverables": [
                        "Environment setup",
                        "Technical design",
                        "Test plan"
                    ]
                },
                {
                    "phase": 2,
                    "name": "Development",
                    "duration": "6 weeks",
                    "deliverables": [
                        "Core functionality",
                        "Integrations",
                        "Data pipeline"
                    ]
                },
                {
                    "phase": 3,
                    "name": "Testing & Validation",
                    "duration": "3 weeks",
                    "deliverables": [
                        "Functional testing",
                        "Integration testing",
                        "UAT"
                    ]
                },
                {
                    "phase": 4,
                    "name": "Demo & Review",
                    "duration": "1 week",
                    "deliverables": [
                        "Demo sessions",
                        "Feedback collection",
                        "Final report"
                    ]
                }
            ],
            "milestones": [
                {"name": "Kickoff", "week": 1},
                {"name": "Design Complete", "week": 2},
                {"name": "Dev Complete", "week": 8},
                {"name": "UAT Complete", "week": 11},
                {"name": "POC Complete", "week": 12}
            ]
        }
    
    def _generate_resources(self, poc_options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate resource requirements."""
        return {
            "team": [
                {"role": "POC Lead", "allocation": "100%", "count": 1},
                {"role": "Solution Architect", "allocation": "50%", "count": 1},
                {"role": "Developer", "allocation": "100%", "count": 2},
                {"role": "QA Engineer", "allocation": "50%", "count": 1}
            ],
            "infrastructure": [
                "Development environment",
                "Sandbox/test environment",
                "CI/CD pipeline",
                "Monitoring tools"
            ],
            "external_dependencies": poc_options.get("external_dependencies", [
                "API access to source systems",
                "Sample data sets",
                "Technical documentation"
            ])
        }
    
    def _generate_success_criteria(self, description: str) -> list:
        """Generate success criteria."""
        return [
            {
                "criterion": "Functional completeness",
                "measure": "All in-scope features demonstrated",
                "target": "100%"
            },
            {
                "criterion": "Technical validation",
                "measure": "Core integrations working",
                "target": "All critical paths tested"
            },
            {
                "criterion": "Stakeholder approval",
                "measure": "Business sign-off obtained",
                "target": "Go/No-Go decision"
            },
            {
                "criterion": "Performance baseline",
                "measure": "Response time within acceptable range",
                "target": "<5 seconds for key operations"
            }
        ]
    
    def _generate_risks(self, description: str) -> list:
        """Generate risk assessment."""
        return [
            {
                "risk": "Technical complexity underestimated",
                "probability": "Medium",
                "impact": "High",
                "mitigation": "Early technical spike, phased approach"
            },
            {
                "risk": "Resource availability",
                "probability": "Medium",
                "impact": "Medium",
                "mitigation": "Early resource allocation, backup resources identified"
            },
            {
                "risk": "Integration challenges",
                "probability": "High",
                "impact": "Medium",
                "mitigation": "Early integration testing, mock services"
            },
            {
                "risk": "Scope creep",
                "probability": "Medium",
                "impact": "Medium",
                "mitigation": "Clear scope definition, change control process"
            }
        ]
    
    def _generate_financials(self, poc_options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate financial estimates."""
        if "financials" in poc_options:
            return poc_options["financials"]
        
        return {
            "estimated_cost": 75000,
            "cost_breakdown": {
                "personnel": 60000,
                "infrastructure": 10000,
                "tools_licenses": 5000
            },
            "roi_projection": {
                "expected_savings": "To be determined post-POC",
                "payback_period": "To be determined post-POC"
            },
            "budget_status": "Pending approval"
        }
