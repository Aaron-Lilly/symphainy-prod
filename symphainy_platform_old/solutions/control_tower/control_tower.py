"""
Control Tower - Platform Command Center

The Control Tower is the nerve center of the Symphainy Platform.
Previously known as "Admin Dashboard", this is the sexier name.

WHAT (Control Tower Role): I am the platform's command center
HOW (Control Tower Implementation): I compose monitoring, management, and composition journeys

Key Capabilities:
- Platform Monitoring: Real-time observability
- Solution Management: Lifecycle management
- Developer Experience: Docs and patterns
- Solution Composition: Guided creation
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.intent_model import Intent, IntentFactory
from symphainy_platform.runtime.execution_context import ExecutionContext

from .journeys.platform_monitoring_journey import PlatformMonitoringJourney
from .journeys.solution_management_journey import SolutionManagementJourney
from .journeys.developer_docs_journey import DeveloperDocsJourney
from .journeys.solution_composition_journey import SolutionCompositionJourney


class ControlTower:
    """
    Control Tower - Platform Command Center.
    
    The sexy name for what was previously "Admin Dashboard".
    
    Composes journeys:
    - PlatformMonitoringJourney: Real-time platform observability
    - SolutionManagementJourney: Solution lifecycle management
    - DeveloperDocsJourney: Documentation and patterns
    - SolutionCompositionJourney: Guided solution creation
    
    MCP Tool prefix: tower_
    """
    
    SOLUTION_ID = "control_tower"
    SOLUTION_NAME = "Control Tower"
    
    SUPPORTED_INTENTS = [
        "compose_journey",
        # Platform Monitoring
        "get_platform_statistics",
        "get_execution_metrics",
        "get_realm_health",
        "get_system_health",
        # Solution Management
        "list_solutions",
        "get_solution_status",
        "get_solution_metrics",
        "manage_solution",
        # Developer Docs
        "get_documentation",
        "get_patterns",
        "get_code_examples",
        "validate_solution",
        # Solution Composition
        "get_solution_templates",
        "compose_solution",
        "get_composition_guide"
    ]
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None,
        runtime_client: Optional[Any] = None,
        realm_registry: Optional[Any] = None,
        solution_registry: Optional[Any] = None
    ):
        """
        Initialize Control Tower.
        
        Args:
            public_works: Public Works Foundation Service
            state_surface: State Surface for artifact management
            runtime_client: Runtime client for metrics
            realm_registry: Realm registry for health
            solution_registry: Solution registry for management
        """
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        self.runtime_client = runtime_client
        self.realm_registry = realm_registry
        self.solution_registry = solution_registry
        
        self.solution_id = self.SOLUTION_ID
        self.solution_name = self.SOLUTION_NAME
        
        # Initialize journeys
        self._journeys: Dict[str, Any] = {}
        self._initialize_journeys()
        
        # MCP Server (lazy initialization)
        self._mcp_server = None
        
        self.logger.info("🗼 Control Tower initialized - Platform Command Center ready")
    
    def _initialize_journeys(self):
        """Initialize all journey orchestrators."""
        # Platform Monitoring
        self._journeys["platform_monitoring"] = PlatformMonitoringJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        
        # Solution Management
        self._journeys["solution_management"] = SolutionManagementJourney(
            public_works=self.public_works,
            state_surface=self.state_surface,
            solution_registry=self.solution_registry
        )
        
        # Developer Docs
        self._journeys["developer_docs"] = DeveloperDocsJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        
        # Solution Composition
        self._journeys["solution_composition"] = SolutionCompositionJourney(
            public_works=self.public_works,
            state_surface=self.state_surface,
            solution_registry=self.solution_registry
        )
        
        self.logger.info(f"🗼 Initialized {len(self._journeys)} Control Tower journeys")
    
    def get_journeys(self) -> Dict[str, Any]:
        """Get all journey orchestrators."""
        return self._journeys.copy()
    
    def get_journey(self, journey_id: str) -> Optional[Any]:
        """Get a specific journey orchestrator."""
        return self._journeys.get(journey_id)
    
    async def initialize_mcp_server(self):
        """Initialize MCP server."""
        if not self._mcp_server:
            from .mcp_server.control_tower_mcp_server import ControlTowerMCPServer
            
            self._mcp_server = ControlTowerMCPServer(
                control_tower=self,
                public_works=self.public_works,
                state_surface=self.state_surface
            )
            await self._mcp_server.initialize()
        
        return self._mcp_server
    
    def get_mcp_server(self):
        """Get MCP server instance."""
        return self._mcp_server
    
    async def handle_intent(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle intent by routing to appropriate journey."""
        intent_type = intent.intent_type
        
        self.logger.info(f"🗼 Control Tower handling intent: {intent_type}")
        
        # Handle compose_journey intent
        if intent_type == "compose_journey":
            return await self._handle_compose_journey(intent, context)
        
        # Route to appropriate journey
        journey = self._find_journey_for_intent(intent_type)
        if journey:
            return await journey.compose_journey(context, intent.parameters)
        
        raise ValueError(f"Unknown intent type: {intent_type} (Control Tower)")
    
    def _find_journey_for_intent(self, intent_type: str) -> Optional[Any]:
        """Find journey for intent type."""
        intent_to_journey = {
            # Platform Monitoring
            "get_platform_statistics": "platform_monitoring",
            "get_execution_metrics": "platform_monitoring",
            "get_realm_health": "platform_monitoring",
            "get_system_health": "platform_monitoring",
            # Solution Management
            "list_solutions": "solution_management",
            "get_solution_status": "solution_management",
            "get_solution_metrics": "solution_management",
            "manage_solution": "solution_management",
            # Developer Docs
            "get_documentation": "developer_docs",
            "get_patterns": "developer_docs",
            "get_code_examples": "developer_docs",
            "validate_solution": "developer_docs",
            # Solution Composition
            "get_solution_templates": "solution_composition",
            "compose_solution": "solution_composition",
            "get_composition_guide": "solution_composition"
        }
        
        journey_id = intent_to_journey.get(intent_type)
        return self._journeys.get(journey_id) if journey_id else None
    
    async def _handle_compose_journey(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle compose_journey intent."""
        journey_id = intent.parameters.get("journey_id")
        journey_params = intent.parameters.get("journey_params", {})
        
        if not journey_id:
            raise ValueError("journey_id is required for compose_journey")
        
        journey = self._journeys.get(journey_id)
        if not journey:
            available = list(self._journeys.keys())
            raise ValueError(f"Unknown journey: {journey_id}. Available: {available}")
        
        self.logger.info(f"🗼 Composing journey: {journey_id}")
        return await journey.compose_journey(context, journey_params)
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get solution-level SOA API definitions."""
        return {
            "compose_journey": {
                "handler": self._handle_compose_journey_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "journey_id": {"type": "string", "enum": list(self._journeys.keys())},
                        "journey_params": {"type": "object"},
                        "user_context": {"type": "object"}
                    },
                    "required": ["journey_id"]
                },
                "description": "Compose and execute a Control Tower journey"
            },
            "list_journeys": {
                "handler": self._handle_list_journeys_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {"user_context": {"type": "object"}}
                },
                "description": "List available Control Tower journeys"
            },
            "get_control_tower_info": {
                "handler": self._handle_get_info_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {"user_context": {"type": "object"}}
                },
                "description": "Get Control Tower information"
            }
        }
    
    async def _handle_compose_journey_soa(self, **kwargs) -> Dict[str, Any]:
        """SOA API handler for compose_journey."""
        user_context = kwargs.get("user_context", {})
        
        context = ExecutionContext(
            execution_id=generate_event_id(),
            tenant_id=user_context.get("tenant_id", "default"),
            session_id=user_context.get("session_id", generate_event_id()),
            solution_id=self.solution_id
        )
        context.state_surface = self.state_surface
        
        intent = IntentFactory.create_intent(
            intent_type="compose_journey",
            tenant_id=context.tenant_id,
            session_id=context.session_id,
            solution_id=self.solution_id,
            parameters={
                "journey_id": kwargs.get("journey_id"),
                "journey_params": kwargs.get("journey_params", {})
            }
        )
        
        return await self._handle_compose_journey(intent, context)
    
    async def _handle_list_journeys_soa(self, **kwargs) -> Dict[str, Any]:
        """SOA API handler for list_journeys."""
        journeys = []
        
        for journey_id, journey in self._journeys.items():
            journeys.append({
                "journey_id": journey_id,
                "journey_name": getattr(journey, 'JOURNEY_NAME', journey_id),
                "description": getattr(journey, '__doc__', '').strip().split('\n')[0] if hasattr(journey, '__doc__') and journey.__doc__ else ''
            })
        
        return {
            "success": True,
            "solution_id": self.solution_id,
            "journeys": journeys,
            "journey_count": len(journeys)
        }
    
    async def _handle_get_info_soa(self, **kwargs) -> Dict[str, Any]:
        """SOA API handler for get_control_tower_info."""
        return {
            "success": True,
            "solution_id": self.solution_id,
            "solution_name": self.solution_name,
            "description": "Control Tower - Platform Command Center",
            "supported_intents": self.SUPPORTED_INTENTS,
            "journeys": list(self._journeys.keys()),
            "capabilities": [
                "Platform Monitoring - Real-time observability",
                "Solution Management - Lifecycle management",
                "Developer Experience - Docs and patterns",
                "Solution Composition - Guided creation"
            ]
        }
