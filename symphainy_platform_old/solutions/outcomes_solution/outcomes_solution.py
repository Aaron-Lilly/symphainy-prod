"""
Outcomes Solution - Outcomes Realm Platform Solution

The top-level solution that composes outcomes journeys, exposes SOA APIs,
and wires up with the frontend via Experience SDK.

WHAT (Solution Role): I provide outcomes capabilities for the platform
HOW (Solution Implementation): I compose outcomes journeys and expose SOA APIs

Key Principle: The platform runs Solutions; Solutions run systems.
Solutions bind domain services to external systems.

Architecture:
- OutcomesSolution composes journey orchestrators
- Each journey orchestrator provides SOA APIs
- OutcomesSolutionMCPServer aggregates and exposes all SOA APIs as MCP tools
- compose_journey intent allows invoking journeys programmatically

Naming Convention:
- Realm: Outcomes Realm
- Solution: OutcomesSolution (platform construct)
- Artifacts: outcome_* prefix
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.intent_model import Intent, IntentFactory
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.civic_systems.platform_sdk.solution_model import (
    Solution,
    SolutionContext,
    DomainServiceBinding
)
from symphainy_platform.civic_systems.platform_sdk.solution_builder import SolutionBuilder
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact

# Import journey orchestrators
from .journeys.outcome_synthesis_journey import OutcomeSynthesisJourney
from .journeys.roadmap_generation_journey import RoadmapGenerationJourney
from .journeys.poc_proposal_journey import POCProposalJourney
from .journeys.blueprint_creation_journey import BlueprintCreationJourney
from .journeys.solution_creation_journey import SolutionCreationJourney
from .journeys.artifact_export_journey import ArtifactExportJourney


class OutcomesSolution:
    """
    Outcomes Solution - Outcomes Realm Platform Solution.
    
    Composes outcomes journeys:
    - OutcomeSynthesisJourney: Synthesize outcomes from all pillars
    - RoadmapGenerationJourney: Generate strategic roadmaps
    - POCProposalJourney: Create POC proposals
    - BlueprintCreationJourney: Create coexistence blueprints
    - SolutionCreationJourney: Create platform solutions
    - ArtifactExportJourney: Export artifacts in various formats
    
    Exposes SOA APIs:
    - compose_journey: Invoke a journey by ID
    - get_journeys: List available journeys
    - get_journey_status: Get journey execution status
    
    Supports compose_journey intent pattern for programmatic journey invocation.
    """
    
    SOLUTION_ID = "outcomes_solution"
    SOLUTION_NAME = "Outcomes Solution"
    
    # Supported intent types for this solution
    SUPPORTED_INTENTS = [
        "compose_journey",
        "synthesize_outcome",
        "generate_roadmap",
        "create_poc",
        "create_blueprint",
        "create_solution",
        "export_artifact"
    ]
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        """
        Initialize Outcomes Solution.
        
        Args:
            public_works: Public Works Foundation Service
            state_surface: State Surface for artifact management
        """
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        
        # Solution configuration
        self.solution_id = self.SOLUTION_ID
        self.solution_name = self.SOLUTION_NAME
        
        # Initialize journey orchestrators
        self._journeys: Dict[str, Any] = {}
        self._initialize_journeys()
        
        # Build solution model
        self._solution_model = self._build_solution_model()
        
        # MCP Server (lazy initialization)
        self._mcp_server = None
        
        # Telemetry
        self.telemetry_service = None
    
    def _initialize_journeys(self):
        """Initialize all journey orchestrators."""
        # Outcome Synthesis Journey
        self._journeys["outcome_synthesis"] = OutcomeSynthesisJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        
        # Roadmap Generation Journey
        self._journeys["roadmap_generation"] = RoadmapGenerationJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        
        # POC Proposal Journey
        self._journeys["poc_proposal"] = POCProposalJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        
        # Blueprint Creation Journey
        self._journeys["blueprint_creation"] = BlueprintCreationJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        
        # Solution Creation Journey
        self._journeys["solution_creation"] = SolutionCreationJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        
        # Artifact Export Journey
        self._journeys["artifact_export"] = ArtifactExportJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        
        self.logger.info(f"Initialized {len(self._journeys)} journey orchestrators")
    
    def _build_solution_model(self) -> Solution:
        """Build formal Solution model."""
        builder = SolutionBuilder(solution_id=self.solution_id)
        
        builder.with_context(
            goals=[
                "Synthesize business outcomes from all pillars",
                "Generate strategic roadmaps and POC proposals",
                "Create coexistence blueprints and platform solutions",
                "Export artifacts for stakeholder consumption"
            ],
            constraints=[
                "All operations via intents (no direct API calls)",
                "All artifacts registered in Artifact Plane",
                "No backward compatibility - follow current patterns only"
            ],
            risk="Low"
        )
        
        builder.add_domain_binding(
            domain="outcomes",
            system_name="artifact_storage",
            adapter_type="artifact_plane_adapter",
            adapter_config={
                "artifact_prefix": "outcome_"
            }
        )
        
        builder.register_intents(self.SUPPORTED_INTENTS)
        
        builder.with_metadata({
            "solution_name": self.SOLUTION_NAME,
            "version": "1.0.0",
            "journeys": list(self._journeys.keys())
        })
        
        return builder.build()
    
    def get_journeys(self) -> Dict[str, Any]:
        """
        Get all journey orchestrators.
        
        Used by OutcomesSolutionMCPServer to register tools.
        
        Returns:
            Dict of journey_id -> journey orchestrator
        """
        return self._journeys.copy()
    
    def get_journey(self, journey_id: str) -> Optional[Any]:
        """Get a specific journey orchestrator."""
        return self._journeys.get(journey_id)
    
    async def initialize_mcp_server(self):
        """
        Initialize MCP server.
        
        Should be called after solution initialization.
        
        Returns:
            OutcomesSolutionMCPServer instance
        """
        if not self._mcp_server:
            from .mcp_server.outcomes_solution_mcp_server import OutcomesSolutionMCPServer
            
            self._mcp_server = OutcomesSolutionMCPServer(
                solution=self,
                public_works=self.public_works,
                state_surface=self.state_surface
            )
            await self._mcp_server.initialize()
        
        return self._mcp_server
    
    def get_mcp_server(self):
        """Get MCP server instance (may be None if not initialized)."""
        return self._mcp_server
    
    async def handle_intent(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle intent by routing to appropriate journey or handler.
        
        This is the main entry point for intent handling at the solution level.
        
        Args:
            intent: The intent to handle
            context: Execution context
        
        Returns:
            Dict with "artifacts" and "events" keys
        """
        intent_type = intent.intent_type
        
        self.logger.info(f"Handling intent: {intent_type}")
        
        # Initialize telemetry if needed
        await self._ensure_telemetry()
        
        # Handle compose_journey intent
        if intent_type == "compose_journey":
            return await self._handle_compose_journey(intent, context)
        
        # Route to appropriate journey based on intent type
        journey = self._find_journey_for_intent(intent_type)
        if journey:
            # For journey-level intents, use compose_journey
            return await journey.compose_journey(context, intent.parameters)
        
        # Fallback to unknown intent
        raise ValueError(f"Unknown intent type: {intent_type} (Solution: {self.solution_id})")
    
    def _find_journey_for_intent(self, intent_type: str) -> Optional[Any]:
        """Find the journey that handles a given intent type."""
        # Map intent types to journeys
        intent_to_journey = {
            "synthesize_outcome": "outcome_synthesis",
            "generate_roadmap": "roadmap_generation",
            "create_poc": "poc_proposal",
            "create_blueprint": "blueprint_creation",
            "create_solution": "solution_creation",
            "export_artifact": "artifact_export",
        }
        
        journey_id = intent_to_journey.get(intent_type)
        if journey_id:
            return self._journeys.get(journey_id)
        
        return None
    
    async def _handle_compose_journey(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle compose_journey intent.
        
        This is the special intent for invoking journeys programmatically.
        
        Parameters:
            - journey_id: Journey identifier
            - journey_params: Parameters for the journey
        
        Returns:
            Journey execution result
        """
        journey_id = intent.parameters.get("journey_id")
        journey_params = intent.parameters.get("journey_params", {})
        
        if not journey_id:
            raise ValueError("journey_id is required for compose_journey intent")
        
        journey = self._journeys.get(journey_id)
        if not journey:
            available = list(self._journeys.keys())
            raise ValueError(f"Unknown journey: {journey_id}. Available: {available}")
        
        self.logger.info(f"Composing journey: {journey_id}")
        
        # Execute journey
        result = await journey.compose_journey(context, journey_params)
        
        return result
    
    # ========================================
    # SOA API Handlers (solution-level)
    # ========================================
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """
        Get solution-level SOA APIs.
        
        Returns:
            Dict of api_name -> api_definition
        """
        return {
            "compose_journey": {
                "handler": self._soa_compose_journey,
                "description": "Invoke an outcomes journey by ID",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "journey_id": {
                            "type": "string",
                            "description": "Journey identifier (e.g., outcome_synthesis, roadmap_generation)",
                            "enum": list(self._journeys.keys())
                        },
                        "journey_params": {
                            "type": "object",
                            "description": "Parameters for the journey"
                        },
                        "tenant_id": {
                            "type": "string",
                            "description": "Tenant identifier"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier"
                        }
                    },
                    "required": ["journey_id", "tenant_id", "session_id"]
                }
            },
            "get_journeys": {
                "handler": self._soa_get_journeys,
                "description": "List all available outcomes journeys",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "get_journey_status": {
                "handler": self._soa_get_journey_status,
                "description": "Get status of a journey execution",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "journey_execution_id": {
                            "type": "string",
                            "description": "Journey execution ID"
                        },
                        "tenant_id": {
                            "type": "string",
                            "description": "Tenant identifier"
                        }
                    },
                    "required": ["journey_execution_id", "tenant_id"]
                }
            }
        }
    
    async def _soa_compose_journey(
        self,
        journey_id: str,
        tenant_id: str,
        session_id: str,
        journey_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """SOA API: Compose journey by ID."""
        # Create execution context
        from symphainy_platform.runtime.execution_context import ExecutionContext
        
        execution_id = generate_event_id()
        
        # Create minimal context for SOA call
        context = ExecutionContext(
            execution_id=execution_id,
            tenant_id=tenant_id,
            session_id=session_id,
            intent=None,  # No intent for SOA call
            state_surface=self.state_surface
        )
        
        journey = self._journeys.get(journey_id)
        if not journey:
            available = list(self._journeys.keys())
            return {
                "success": False,
                "error": f"Unknown journey: {journey_id}. Available: {available}"
            }
        
        try:
            result = await journey.compose_journey(context, journey_params or {})
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _soa_get_journeys(self) -> Dict[str, Any]:
        """SOA API: Get all available journeys."""
        journeys_info = []
        
        for journey_id, journey in self._journeys.items():
            journey_info = {
                "journey_id": journey_id,
                "journey_name": getattr(journey, 'JOURNEY_NAME', journey_id),
                "description": getattr(journey, '__doc__', '').split('\n')[0].strip() if getattr(journey, '__doc__', None) else ''
            }
            journeys_info.append(journey_info)
        
        return {
            "success": True,
            "solution_id": self.solution_id,
            "journeys": journeys_info
        }
    
    async def _soa_get_journey_status(
        self,
        journey_execution_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """SOA API: Get journey execution status."""
        # Try to get status from state surface
        if self.state_surface:
            try:
                status = await self.state_surface.get_execution_state(
                    key=f"journey_status_{journey_execution_id}",
                    tenant_id=tenant_id
                )
                if status:
                    return {
                        "success": True,
                        "journey_execution_id": journey_execution_id,
                        "status": status
                    }
            except Exception as e:
                self.logger.warning(f"Could not retrieve journey status: {e}")
        
        return {
            "success": False,
            "error": f"Status not found for journey execution: {journey_execution_id}"
        }
    
    # ========================================
    # Experience SDK Integration
    # ========================================
    
    def get_experience_sdk_config(self) -> Dict[str, Any]:
        """
        Get Experience SDK configuration for frontend integration.
        
        Returns:
            Dict with configuration for Experience SDK
        """
        return {
            "solution_id": self.solution_id,
            "solution_name": self.solution_name,
            "supported_intents": self.SUPPORTED_INTENTS,
            "available_journeys": list(self._journeys.keys()),
            "mcp_server_available": self._mcp_server is not None,
            "soa_apis": list(self.get_soa_apis().keys()),
            "integration_patterns": {
                "intent_submission": {
                    "method": "submitIntent",
                    "example": {
                        "intent_type": "synthesize_outcome",
                        "parameters": {}
                    }
                },
                "journey_composition": {
                    "method": "submitIntent",
                    "example": {
                        "intent_type": "compose_journey",
                        "parameters": {
                            "journey_id": "outcome_synthesis",
                            "journey_params": {}
                        }
                    }
                },
                "mcp_tool_call": {
                    "method": "callMcpTool",
                    "example": {
                        "tool_name": "outcomes_synthesize",
                        "parameters": {}
                    }
                }
            }
        }
    
    # ========================================
    # Telemetry
    # ========================================
    
    async def _ensure_telemetry(self):
        """Ensure telemetry service is initialized."""
        if not self.telemetry_service and self.public_works:
            try:
                self.telemetry_service = self.public_works.get_telemetry_service()
            except Exception as e:
                self.logger.warning(f"Telemetry service not available: {e}")
    
    async def _record_telemetry(self, telemetry_data: Dict[str, Any], tenant_id: str):
        """Record telemetry data."""
        if self.telemetry_service:
            try:
                await self.telemetry_service.record({
                    "solution_id": self.solution_id,
                    "tenant_id": tenant_id,
                    **telemetry_data
                })
            except Exception as e:
                self.logger.warning(f"Failed to record telemetry: {e}")
