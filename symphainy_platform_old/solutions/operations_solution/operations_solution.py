"""
Operations Solution - Platform Construct for Operations Realm

Composes Operations Realm journeys and exposes SOA APIs for agent consumption.

WHAT (Solution Role): I compose Operations Realm journeys and expose APIs
HOW (Solution Implementation): I route intents to journey orchestrators
    and aggregate SOA APIs for MCP server registration

Architecture:
- Solution composes journeys (not direct service calls)
- Journeys compose intent services
- Solution exposes aggregated SOA APIs
- MCP server wraps APIs as tools for agents

Naming Convention:
- Realm: Operations Realm (user-facing domain)
- Solution: OperationsSolution (platform construct)
- Artifacts: operations_* (e.g., operations_workflow, operations_sop)
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utilities import get_logger
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.runtime.execution_context import ExecutionContext


class OperationsSolution:
    """
    Operations Solution - Platform construct for Operations Realm.
    
    Composes journeys:
    - Workflow Management Journey
    - SOP Management Journey
    - Coexistence Analysis Journey
    - Process Optimization Journey
    """
    
    SOLUTION_ID = "operations_solution"
    SOLUTION_VERSION = "1.0"
    
    SUPPORTED_INTENTS = [
        "compose_journey",
        # Workflow Management
        "create_workflow",
        # SOP Management
        "generate_sop",
        "generate_sop_from_chat",
        "sop_chat_message",
        # Coexistence Analysis
        "analyze_coexistence",
        # Process Optimization
        "optimize_process"
    ]
    
    def __init__(self, public_works=None, state_surface=None):
        """
        Initialize Operations Solution.
        
        Args:
            public_works: Public Works Foundation Service
            state_surface: State Surface for execution state
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        self.state_surface = state_surface
        
        # Initialize journeys
        self._journeys = {}
        self._initialize_journeys()
        
        self.logger.info(f"OperationsSolution initialized: {self.SOLUTION_ID} v{self.SOLUTION_VERSION}")
    
    def _initialize_journeys(self):
        """Initialize journey orchestrators."""
        from .journeys.workflow_management_journey import WorkflowManagementJourney
        from .journeys.sop_management_journey import SOPManagementJourney
        from .journeys.coexistence_analysis_journey import CoexistenceAnalysisJourney
        from .journeys.process_optimization_journey import ProcessOptimizationJourney
        
        self._journeys["workflow_management"] = WorkflowManagementJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        self._journeys["sop_management"] = SOPManagementJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        self._journeys["coexistence_analysis"] = CoexistenceAnalysisJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        self._journeys["process_optimization"] = ProcessOptimizationJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
    
    async def handle_intent(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle intent by routing to appropriate journey.
        
        Args:
            intent: The intent to handle
            context: Execution context
            
        Returns:
            Dict with artifacts and events
        """
        intent_type = intent.intent_type
        
        self.logger.info(f"OperationsSolution handling intent: {intent_type}")
        
        if intent_type == "compose_journey":
            return await self._handle_compose_journey(intent, context)
        
        # Route to appropriate journey based on intent type
        if intent_type == "create_workflow":
            return await self._journeys["workflow_management"].compose_journey(
                journey_id="create_workflow",
                context=context,
                journey_params=intent.parameters
            )
        
        if intent_type in ["generate_sop", "generate_sop_from_chat", "sop_chat_message"]:
            return await self._journeys["sop_management"].compose_journey(
                journey_id=intent_type,
                context=context,
                journey_params=intent.parameters
            )
        
        if intent_type == "analyze_coexistence":
            return await self._journeys["coexistence_analysis"].compose_journey(
                journey_id="analyze_coexistence",
                context=context,
                journey_params=intent.parameters
            )
        
        if intent_type == "optimize_process":
            return await self._journeys["process_optimization"].compose_journey(
                journey_id="optimize_process",
                context=context,
                journey_params=intent.parameters
            )
        
        raise ValueError(f"Unsupported intent type: {intent_type}")
    
    async def _handle_compose_journey(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle compose_journey meta-intent."""
        params = intent.parameters or {}
        journey_id = params.get("journey_id")
        journey_params = params.get("journey_params", {})
        
        if not journey_id:
            raise ValueError("journey_id is required for compose_journey")
        
        # Map journey_id to journey orchestrator
        journey_mapping = {
            "workflow_management": "workflow_management",
            "sop_management": "sop_management",
            "coexistence_analysis": "coexistence_analysis",
            "process_optimization": "process_optimization",
            # Alternative names
            "create_workflow": "workflow_management",
            "generate_sop": "sop_management",
            "analyze_coexistence": "coexistence_analysis",
            "optimize_process": "process_optimization"
        }
        
        journey_key = journey_mapping.get(journey_id)
        if not journey_key:
            raise ValueError(f"Unknown journey_id: {journey_id}")
        
        journey = self._journeys.get(journey_key)
        if not journey:
            raise ValueError(f"Journey not found: {journey_key}")
        
        return await journey.compose_journey(
            journey_id=journey_id,
            context=context,
            journey_params=journey_params
        )
    
    def get_soa_apis(self) -> Dict[str, Callable]:
        """
        Get aggregated SOA APIs from all journeys.
        
        Returns:
            Dict mapping API names to handlers
        """
        soa_apis = {}
        
        # Collect APIs from all journeys
        for journey_name, journey in self._journeys.items():
            if hasattr(journey, "get_soa_apis"):
                journey_apis = journey.get_soa_apis()
                soa_apis.update(journey_apis)
        
        self.logger.info(f"OperationsSolution aggregated {len(soa_apis)} SOA APIs")
        return soa_apis
    
    def initialize_mcp_server(self):
        """
        Initialize MCP server for this solution.
        
        Returns:
            Configured MCP server instance
        """
        from .mcp_server.operations_solution_mcp_server import OperationsSolutionMCPServer
        
        mcp_server = OperationsSolutionMCPServer(
            solution=self,
            public_works=self.public_works
        )
        
        self.logger.info("OperationsSolution MCP server initialized")
        return mcp_server
    
    def get_solution_info(self) -> Dict[str, Any]:
        """Get solution metadata."""
        return {
            "solution_id": self.SOLUTION_ID,
            "solution_version": self.SOLUTION_VERSION,
            "realm": "operations",
            "supported_intents": self.SUPPORTED_INTENTS,
            "journeys": list(self._journeys.keys()),
            "status": "active"
        }
