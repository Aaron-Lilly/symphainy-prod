"""
Coexistence Solution - Platform Entry Point & Navigation

The Coexistence Solution is the front door to the Symphainy Platform.
Previously known as "Landing Page", this solution handles platform
introduction, navigation, and AI-powered guidance.

WHAT (Coexistence Role): I am the platform's front door and navigator
HOW (Coexistence Implementation): I compose introduction, navigation, and guide agent journeys

Key Concept: Coexistence means enabling existing systems to work together
with modern AI capabilities without requiring replacement.
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

from .journeys.introduction_journey import IntroductionJourney
from .journeys.navigation_journey import NavigationJourney
from .journeys.guide_agent_journey import GuideAgentJourney


class CoexistenceSolution:
    """
    Coexistence Solution - Platform Entry Point & Navigation.
    
    The sexy name for what was previously "Landing Page".
    
    Composes journeys:
    - IntroductionJourney: Platform introduction, solution catalog, coexistence concepts
    - NavigationJourney: Solution routing and context management
    - GuideAgentJourney: AI-powered guidance and specialist routing
    
    MCP Tool prefix: coexist_
    """
    
    SOLUTION_ID = "coexistence"
    SOLUTION_NAME = "Coexistence Solution"
    
    SUPPORTED_INTENTS = [
        "compose_journey",
        # Introduction
        "introduce_platform",
        "show_solution_catalog",
        "explain_coexistence",
        # Navigation
        "navigate_to_solution",
        "get_solution_context",
        "establish_solution_context",
        # Guide Agent
        "initiate_guide_agent",
        "process_guide_agent_message",
        "route_to_liaison_agent"
    ]
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None,
        solution_registry: Optional[Any] = None,
        agent_framework: Optional[Any] = None,
        curator: Optional[Any] = None
    ):
        """
        Initialize Coexistence Solution.
        
        Args:
            public_works: Public Works Foundation Service
            state_surface: State Surface for artifact management
            solution_registry: Solution Registry for navigation
            agent_framework: Agent Framework for GuideAgent
            curator: Curator for MCP tool discovery
        """
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        self.solution_registry = solution_registry
        self.agent_framework = agent_framework
        self.curator = curator
        
        self.solution_id = self.SOLUTION_ID
        self.solution_name = self.SOLUTION_NAME
        
        # Initialize journeys
        self._journeys: Dict[str, Any] = {}
        self._initialize_journeys()
        
        # MCP Server (lazy initialization)
        self._mcp_server = None
        
        self.logger.info("🌐 Coexistence Solution initialized - Platform front door ready")
    
    def _initialize_journeys(self):
        """Initialize all journey orchestrators."""
        # Introduction Journey
        self._journeys["introduction"] = IntroductionJourney(
            public_works=self.public_works,
            state_surface=self.state_surface,
            solution_registry=self.solution_registry
        )
        
        # Navigation Journey
        self._journeys["navigation"] = NavigationJourney(
            public_works=self.public_works,
            state_surface=self.state_surface,
            solution_registry=self.solution_registry
        )
        
        # Guide Agent Journey
        self._journeys["guide_agent"] = GuideAgentJourney(
            public_works=self.public_works,
            state_surface=self.state_surface,
            curator=self.curator,
            agent_framework=self.agent_framework
        )
        
        self.logger.info(f"🌐 Initialized {len(self._journeys)} Coexistence journeys")
    
    def get_journeys(self) -> Dict[str, Any]:
        """Get all journey orchestrators."""
        return self._journeys.copy()
    
    def get_journey(self, journey_id: str) -> Optional[Any]:
        """Get a specific journey orchestrator."""
        return self._journeys.get(journey_id)
    
    async def initialize_mcp_server(self):
        """Initialize MCP server."""
        if not self._mcp_server:
            from .mcp_server.coexistence_mcp_server import CoexistenceMCPServer
            
            self._mcp_server = CoexistenceMCPServer(
                coexistence_solution=self,
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
        
        self.logger.info(f"🌐 Coexistence handling intent: {intent_type}")
        
        # Handle compose_journey intent
        if intent_type == "compose_journey":
            return await self._handle_compose_journey(intent, context)
        
        # Route to appropriate journey
        journey = self._find_journey_for_intent(intent_type)
        if journey:
            # Map intent to journey action
            action = self._map_intent_to_action(intent_type)
            params = {**intent.parameters, "action": action}
            return await journey.compose_journey(context, params)
        
        raise ValueError(f"Unknown intent type: {intent_type} (Coexistence)")
    
    def _find_journey_for_intent(self, intent_type: str) -> Optional[Any]:
        """Find journey for intent type."""
        intent_to_journey = {
            # Introduction
            "introduce_platform": "introduction",
            "show_solution_catalog": "introduction",
            "explain_coexistence": "introduction",
            # Navigation
            "navigate_to_solution": "navigation",
            "get_solution_context": "navigation",
            "establish_solution_context": "navigation",
            # Guide Agent
            "initiate_guide_agent": "guide_agent",
            "process_guide_agent_message": "guide_agent",
            "route_to_liaison_agent": "guide_agent"
        }
        
        journey_id = intent_to_journey.get(intent_type)
        return self._journeys.get(journey_id) if journey_id else None
    
    def _map_intent_to_action(self, intent_type: str) -> str:
        """Map intent type to journey action."""
        intent_to_action = {
            # Introduction
            "introduce_platform": "introduce",
            "show_solution_catalog": "catalog",
            "explain_coexistence": "explain",
            # Navigation
            "navigate_to_solution": "navigate",
            "get_solution_context": "get_context",
            "establish_solution_context": "establish_context",
            # Guide Agent
            "initiate_guide_agent": "initiate",
            "process_guide_agent_message": "message",
            "route_to_liaison_agent": "route_liaison"
        }
        return intent_to_action.get(intent_type, intent_type)
    
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
        
        self.logger.info(f"🌐 Composing journey: {journey_id}")
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
                "description": "Compose and execute a Coexistence journey"
            },
            "list_journeys": {
                "handler": self._handle_list_journeys_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {"user_context": {"type": "object"}}
                },
                "description": "List available Coexistence journeys"
            },
            "get_coexistence_info": {
                "handler": self._handle_get_info_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {"user_context": {"type": "object"}}
                },
                "description": "Get Coexistence Solution information"
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
        """SOA API handler for get_coexistence_info."""
        return {
            "success": True,
            "solution_id": self.solution_id,
            "solution_name": self.solution_name,
            "description": "Coexistence Solution - Platform Entry Point & Navigation",
            "supported_intents": self.SUPPORTED_INTENTS,
            "journeys": list(self._journeys.keys()),
            "capabilities": [
                "Platform Introduction - Welcome and onboarding",
                "Solution Catalog - Browse available solutions",
                "Coexistence Explanation - Educational content",
                "Solution Navigation - Route to solutions",
                "Context Management - Track user journey",
                "Guide Agent - AI-powered assistance"
            ]
        }
