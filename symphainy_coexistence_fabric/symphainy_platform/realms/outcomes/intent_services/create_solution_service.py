"""
Create Solution Intent Service

Implements the create_solution intent for the Outcomes Realm.

Contract: docs/intent_contracts/journey_outcomes_creation/intent_create_solution.md

Purpose: Create platform solution from roadmap, POC, or blueprint. Retrieves source artifact
from Artifact Plane and creates a registered platform solution using Solution SDK.

WHAT (Intent Service Role): I create platform solutions from source artifacts
HOW (Intent Service Implementation): I execute the create_solution intent, retrieve source
    artifact, build solution via Solution SDK, register it, and return structured artifact

Naming Convention:
- Realm: Outcomes Realm
- Solution (intent) = registers artifacts as platform solutions
- Solution (platform) = OutcomesSolution that composes journeys
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class CreateSolutionService(BaseIntentService):
    """
    Intent service for platform solution creation.
    
    Creates platform solutions from roadmap, POC, or blueprint artifacts.
    Uses Solution SDK (Platform SDK) to create and register solutions.
    
    Contract Compliance:
    - Parameters: Section 2 of intent contract (solution_source, source_id required)
    - Returns: Section 3 of intent contract
    - Artifact Registration: Section 4 of intent contract
    - Idempotency: Section 5 of intent contract
    - Error Handling: Section 8 of intent contract
    """
    
    def __init__(self, public_works, state_surface):
        """
        Initialize CreateSolutionService.
        
        Args:
            public_works: Public Works Foundation Service for infrastructure access
            state_surface: State Surface for state management
        """
        super().__init__(
            service_id="create_solution_service",
            intent_type="create_solution",
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
        
        # Initialize Solution Registry
        self.solution_registry = None
        try:
            from symphainy_platform.civic_systems.platform_sdk.solution_registry import SolutionRegistry
            self.solution_registry = SolutionRegistry()
        except Exception as e:
            self.logger.warning(f"Could not initialize Solution Registry: {e}")
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the create_solution intent.
        
        Intent Flow (from contract):
        1. Validate solution_source and source_id (required)
        2. Retrieve source artifact from Artifact Plane
        3. Extract goals and constraints from source
        4. Build solution using Solution SDK
        5. Register solution in Solution Registry
        6. Return solution result
        
        Args:
            context: Execution context with intent, tenant, session information
            params: Optional additional parameters (merged with intent.parameters)
        
        Returns:
            Dictionary with artifacts and events per contract Section 3
        
        Raises:
            ValueError: For validation errors
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
            
            solution_source = intent_params.get("solution_source")
            source_id = intent_params.get("source_id")
            source_data = intent_params.get("source_data")  # Optional inline data
            
            if not solution_source:
                raise ValueError("solution_source is required (must be 'roadmap', 'poc', or 'blueprint')")
            
            if not source_id:
                raise ValueError("source_id is required")
            
            if solution_source not in ["roadmap", "poc", "blueprint"]:
                raise ValueError(f"Invalid solution_source: {solution_source}. Must be 'roadmap', 'poc', or 'blueprint'")
            
            self.logger.info(f"Creating solution from {solution_source}: {source_id}")
            
            # === RETRIEVE SOURCE ARTIFACT ===
            
            if not source_data:
                source_data = await self._retrieve_source_artifact(
                    solution_source=solution_source,
                    source_id=source_id,
                    context=context
                )
            
            if not source_data:
                raise ValueError(
                    f"Source {solution_source} with id {source_id} not found. "
                    f"Please ensure the {solution_source} was created successfully."
                )
            
            # === BUILD SOLUTION ===
            
            solution_result = await self._build_solution(
                solution_source=solution_source,
                source_id=source_id,
                source_data=source_data,
                context=context
            )
            
            solution_id = solution_result.get("solution_id")
            
            self.logger.info(f"✅ Solution created: {solution_id}")
            
            # Record telemetry (success)
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute",
                    "status": "completed",
                    "execution_id": context.execution_id,
                    "intent_type": self.intent_type,
                    "solution_id": solution_id,
                    "solution_source": solution_source
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "solution": solution_result,
                    "solution_id": solution_id
                },
                "events": [
                    {
                        "type": "solution_created",
                        "solution_id": solution_id,
                        "source": solution_source,
                        "source_id": source_id,
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
    
    async def _retrieve_source_artifact(
        self,
        solution_source: str,
        source_id: str,
        context: ExecutionContext
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve source artifact from Artifact Plane or execution state.
        
        Args:
            solution_source: Source type (roadmap, poc, blueprint)
            source_id: Source artifact ID
            context: Execution context
        
        Returns:
            Source artifact data or None if not found
        """
        source_data = None
        
        # Try Artifact Plane first (canonical storage)
        if self.artifact_plane:
            try:
                self.logger.info(f"Retrieving {solution_source} from Artifact Plane: {source_id}")
                
                artifact_result = await self.artifact_plane.get_artifact(
                    artifact_id=source_id,
                    tenant_id=context.tenant_id,
                    include_payload=True,
                    include_visuals=False
                )
                
                if artifact_result and artifact_result.get("payload"):
                    payload = artifact_result["payload"]
                    
                    # Extract actual data based on source type
                    if solution_source == "roadmap":
                        source_data = payload.get("roadmap") or payload.get("strategic_plan") or payload
                    elif solution_source == "poc":
                        source_data = payload.get("poc_proposal") or payload.get("proposal") or payload
                    elif solution_source == "blueprint":
                        source_data = payload.get("blueprint") or payload
                    else:
                        source_data = payload
                    
                    if source_data:
                        self.logger.info(f"✅ Retrieved {solution_source} from Artifact Plane")
                        return source_data
                        
            except Exception as e:
                self.logger.warning(f"Failed to retrieve from Artifact Plane: {e}")
        
        # Fallback: Try execution state (for backward compatibility)
        if not source_data and self.state_surface:
            try:
                self.logger.info(f"Trying execution state fallback for {source_id}")
                
                execution_state = await context.state_surface.get_execution_state(
                    source_id,
                    context.tenant_id
                )
                
                if execution_state:
                    artifacts = execution_state.get("artifacts", {})
                    artifact = artifacts.get(solution_source)
                    
                    if artifact:
                        if isinstance(artifact, dict) and "renderings" in artifact:
                            renderings = artifact.get("renderings", {})
                            source_data = (
                                renderings.get(solution_source) or 
                                renderings.get("roadmap") or 
                                renderings.get("poc_proposal") or
                                renderings.get("blueprint")
                            )
                        else:
                            source_data = artifact
                        
                        if source_data:
                            self.logger.info(f"✅ Retrieved {solution_source} from execution state")
                            return source_data
                            
            except Exception as e:
                self.logger.warning(f"Failed to retrieve from execution state: {e}")
        
        return None
    
    async def _build_solution(
        self,
        solution_source: str,
        source_id: str,
        source_data: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Build platform solution from source artifact.
        
        Uses Solution SDK to create and register the solution.
        
        Args:
            solution_source: Source type (roadmap, poc, blueprint)
            source_id: Source artifact ID
            source_data: Source artifact data
            context: Execution context
        
        Returns:
            Dict with solution data
        """
        # Parse source data if bytes
        if isinstance(source_data, bytes):
            import json
            source_data = json.loads(source_data.decode('utf-8'))
        
        # Extract goals and constraints based on source type
        goals = []
        constraints = []
        
        if solution_source == "roadmap":
            goals, constraints = self._extract_from_roadmap(source_data)
        elif solution_source == "poc":
            goals, constraints = self._extract_from_poc(source_data)
        elif solution_source == "blueprint":
            goals, constraints = self._extract_from_blueprint(source_data)
        
        # Build solution using Solution SDK
        try:
            from symphainy_platform.civic_systems.platform_sdk.solution_builder import SolutionBuilder
            
            solution_builder = SolutionBuilder()
            
            # Set context
            solution_builder.with_context(
                goals=goals,
                constraints=constraints,
                risk="Medium",
                metadata={
                    "source": solution_source,
                    "source_id": source_id,
                    "tenant_id": context.tenant_id
                }
            )
            
            # Add domain bindings
            for domain in ["content", "insights", "journey"]:
                solution_builder.add_domain_binding(
                    domain=domain,
                    system_name="symphainy_platform",
                    adapter_type="internal_adapter",
                    adapter_config={},
                    metadata={"realm": domain}
                )
            
            # Register intents based on source
            intents = self._get_intents_for_source(solution_source)
            solution_builder.register_intents(intents)
            
            # Build solution
            solution = solution_builder.build()
            
            # Register solution
            if self.solution_registry:
                if self.solution_registry.register_solution(solution):
                    self.logger.info(f"Solution registered: {solution.solution_id}")
                else:
                    self.logger.warning(f"Failed to register solution: {solution.solution_id}")
            
            return {
                "solution_id": solution.solution_id,
                "solution": solution.to_dict(),
                "source": solution_source,
                "source_id": source_id,
                "goals": goals,
                "constraints": constraints,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except ImportError as e:
            self.logger.warning(f"Solution SDK not available: {e}")
            
            # Fallback: Create basic solution structure
            solution_id = f"solution_{str(uuid.uuid4())}"
            
            return {
                "solution_id": solution_id,
                "solution": {
                    "solution_id": solution_id,
                    "goals": goals,
                    "constraints": constraints,
                    "source": solution_source,
                    "source_id": source_id,
                    "domain_bindings": ["content", "insights", "journey"],
                    "intents": self._get_intents_for_source(solution_source)
                },
                "source": solution_source,
                "source_id": source_id,
                "created_at": datetime.utcnow().isoformat()
            }
    
    def _extract_from_roadmap(self, source_data: Dict[str, Any]) -> tuple:
        """Extract goals and constraints from roadmap."""
        goals = []
        constraints = []
        
        roadmap = source_data.get("roadmap", {}) or source_data
        strategic_plan = source_data.get("strategic_plan", {})
        
        # Extract goals from strategic plan
        goals.extend(strategic_plan.get("goals", []))
        
        # Extract phases as objectives
        phases = roadmap.get("phases", [])
        for phase in phases:
            if phase.get("status") == "completed":
                goals.append(f"Complete {phase.get('phase', 'phase')}")
        
        # Extract constraints from timeline
        timeline = roadmap.get("timeline", {})
        if timeline.get("total_duration"):
            constraints.append(f"Timeline: {timeline['total_duration']}")
        
        return goals, constraints
    
    def _extract_from_poc(self, source_data: Dict[str, Any]) -> tuple:
        """Extract goals and constraints from POC."""
        goals = []
        constraints = []
        
        proposal = source_data.get("proposal", {}) or source_data
        
        # Extract objectives as goals
        goals.extend(proposal.get("objectives", []))
        
        # Extract constraints from scope
        scope = proposal.get("scope", {})
        constraints.extend(scope.get("constraints", []))
        
        # Extract timeline as constraint
        timeline = proposal.get("timeline", {})
        if timeline.get("duration"):
            constraints.append(f"POC Duration: {timeline['duration']}")
        
        # Extract budget as constraint
        financials = proposal.get("financials", {})
        if financials.get("estimated_cost"):
            constraints.append(f"Budget: ${financials['estimated_cost']}")
        
        return goals, constraints
    
    def _extract_from_blueprint(self, source_data: Dict[str, Any]) -> tuple:
        """Extract goals and constraints from blueprint."""
        goals = []
        constraints = []
        
        blueprint = source_data.get("blueprint", {}) or source_data
        
        # Extract goals from roadmap phases
        roadmap = blueprint.get("roadmap", {})
        phases = roadmap.get("phases", [])
        for phase in phases:
            phase_name = phase.get("name", f"Phase {phase.get('phase', '')}")
            for objective in phase.get("objectives", []):
                goals.append(f"{phase_name}: {objective}")
        
        # Extract constraints from coexistence state
        coexistence_state = blueprint.get("coexistence_state", {})
        integration_points = coexistence_state.get("integration_points", [])
        for point in integration_points:
            system_name = point.get("system_name", "External System")
            constraints.append(f"Integration: {system_name}")
        
        # Extract constraints from responsibility matrix
        responsibility_matrix = blueprint.get("responsibility_matrix", {})
        responsibilities = responsibility_matrix.get("responsibilities", [])
        for resp in responsibilities:
            external_systems = resp.get("external_systems", [])
            for ext_sys in external_systems:
                constraints.append(f"External dependency: {ext_sys}")
        
        return goals, constraints
    
    def _get_intents_for_source(self, solution_source: str) -> list:
        """Get relevant intents based on source type."""
        base_intents = ["synthesize_outcome", "create_solution"]
        
        if solution_source == "roadmap":
            return base_intents + ["generate_roadmap"]
        elif solution_source == "poc":
            return base_intents + ["create_poc"]
        elif solution_source == "blueprint":
            return base_intents + ["create_blueprint", "analyze_coexistence", "create_workflow"]
        
        return base_intents
