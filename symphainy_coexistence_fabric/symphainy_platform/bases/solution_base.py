"""
Base Solution - Base Class for Platform Solutions

Base class for all solutions in the platform. Solutions are the top-level
constructs that compose journeys and expose SOA APIs.

WHAT (Solution Role): I compose journeys and expose SOA APIs
HOW (Solution Implementation): I route intents to journeys, aggregate APIs, integrate with MCP

Key Principle: The platform runs Solutions; Solutions run systems.
Solutions bind domain services to external systems via journeys.

Architecture:
- BaseSolution provides standard solution infrastructure
- Solutions compose journey orchestrators
- Solutions expose SOA APIs via get_soa_apis()
- Solutions integrate with MCP servers
- Solutions support compose_journey intent for programmatic journey invocation

See also: SOLUTION_PATTERN.md for detailed pattern documentation
"""

import sys
from pathlib import Path

# Add project root to path
def _find_project_root():
    path = Path(__file__).resolve()
    for parent in path.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return path.parents[3]  # Fallback

project_root = _find_project_root()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable

from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.intent_model import Intent, IntentFactory
from symphainy_platform.runtime.execution_context import ExecutionContext


class BaseSolution(ABC):
    """
    Base class for platform solutions.
    
    Provides:
    - Standard solution infrastructure (logger, clock, public_works)
    - Journey orchestrator management
    - SOA API aggregation
    - MCP server integration
    - compose_journey intent handling
    - Experience SDK configuration
    - Standardized result building via build_journey_result()
    
    Subclasses must:
    - Define SOLUTION_ID and SOLUTION_NAME class attributes
    - Define SUPPORTED_INTENTS class attribute listing all handled intent types
    - Implement _initialize_journeys() to set up journey orchestrators
    - Implement handle_intent() to route intents to journeys
    """
    
    # Class attributes to be defined by subclasses
    SOLUTION_ID: str = "base_solution"
    SOLUTION_NAME: str = "Base Solution"
    SOLUTION_VERSION: str = "1.0"
    
    # Supported intent types - subclasses should override
    SUPPORTED_INTENTS: List[str] = ["compose_journey"]
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        """
        Initialize base solution.
        
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
        
        # Journey orchestrators
        self._journeys: Dict[str, Any] = {}
        
        # MCP Server (lazy initialization)
        self._mcp_server = None
        
        # Telemetry service
        self.telemetry_service = None
    
    @abstractmethod
    def _initialize_journeys(self):
        """
        Initialize journey orchestrators.
        
        Must be implemented by subclasses to create and register
        journey orchestrators in self._journeys.
        """
        pass
    
    @abstractmethod
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
        pass
    
    # ========================================
    # Journey Management
    # ========================================
    
    def get_journeys(self) -> Dict[str, Any]:
        """
        Get all journey orchestrators.
        
        Returns:
            Dict of journey_id -> journey orchestrator
        """
        return self._journeys.copy()
    
    def get_journey(self, journey_id: str) -> Optional[Any]:
        """
        Get a specific journey orchestrator.
        
        Args:
            journey_id: Journey identifier
        
        Returns:
            Journey orchestrator or None
        """
        return self._journeys.get(journey_id)
    
    def list_journey_ids(self) -> List[str]:
        """
        List all journey IDs.
        
        Returns:
            List of journey identifiers
        """
        return list(self._journeys.keys())
    
    # ========================================
    # compose_journey Handling
    # ========================================
    
    async def _handle_compose_journey(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle compose_journey intent.
        
        This is the standard intent for invoking journeys programmatically.
        
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
    # Standardized Result Building
    # ========================================
    
    @staticmethod
    def build_journey_result(
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        artifacts: Optional[Dict[str, Any]] = None,
        events: Optional[List[Dict[str, Any]]] = None,
        error: Optional[str] = None,
        error_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build a standardized journey result.
        
        This is the canonical way to build journey results.
        All journeys should use this method to ensure consistent response format.
        
        Args:
            success: Whether the journey succeeded
            data: Journey-specific data (included in artifacts)
            artifacts: Additional artifacts to include
            events: Events to emit
            error: Error message (if success=False)
            error_code: Error code (if success=False)
        
        Returns:
            Standardized result dict with:
            - success: bool
            - artifacts: dict
            - events: list
            - error/error_code (if applicable)
        """
        result = {
            "success": success,
            "artifacts": artifacts or {},
            "events": events or []
        }
        
        # Include data in artifacts if provided
        if data:
            result["artifacts"]["data"] = data
        
        # Include error info if not successful
        if not success:
            if error:
                result["error"] = error
            if error_code:
                result["error_code"] = error_code
        
        return result
    
    # ========================================
    # SOA API Aggregation
    # ========================================
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all SOA APIs from this solution and its journeys.
        
        Returns:
            Dict of API name -> API definition
        """
        soa_apis = {}
        
        # Solution-level APIs
        solution_apis = self._get_solution_soa_apis()
        soa_apis.update(solution_apis)
        
        # Journey-level APIs
        for journey_id, journey in self._journeys.items():
            if hasattr(journey, 'get_soa_apis'):
                journey_apis = journey.get_soa_apis()
                for api_name, api_def in journey_apis.items():
                    # Optionally prefix with journey ID to avoid conflicts
                    soa_apis[api_name] = api_def
        
        self.logger.debug(f"Aggregated {len(soa_apis)} SOA APIs")
        return soa_apis
    
    def _get_solution_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """
        Get solution-level SOA APIs.
        
        Override in subclasses to add solution-level APIs.
        
        Returns:
            Dict of API name -> API definition
        """
        return {
            "compose_journey": {
                "handler": self._handle_compose_journey_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "journey_id": {
                            "type": "string",
                            "description": "Journey identifier"
                        },
                        "journey_params": {
                            "type": "object",
                            "description": "Journey-specific parameters"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "User context (tenant_id, session_id)"
                        }
                    },
                    "required": ["journey_id"]
                },
                "description": f"Compose and execute a {self.solution_name} journey"
            },
            "list_journeys": {
                "handler": self._handle_list_journeys_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "description": f"List available {self.solution_name} journeys"
            },
            "get_solution_info": {
                "handler": self._handle_get_solution_info_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "description": f"Get {self.solution_name} information"
            }
        }
    
    async def _handle_compose_journey_soa(self, **kwargs) -> Dict[str, Any]:
        """SOA API handler for compose_journey."""
        journey_id = kwargs.get("journey_id")
        journey_params = kwargs.get("journey_params", {})
        user_context = kwargs.get("user_context", {})
        
        # Create execution context
        context = ExecutionContext(
            execution_id=generate_event_id(),
            tenant_id=user_context.get("tenant_id", "default"),
            session_id=user_context.get("session_id", generate_event_id()),
            solution_id=self.solution_id
        )
        context.state_surface = self.state_surface
        
        # Create intent
        intent = IntentFactory.create_intent(
            intent_type="compose_journey",
            tenant_id=context.tenant_id,
            session_id=context.session_id,
            solution_id=self.solution_id,
            parameters={
                "journey_id": journey_id,
                "journey_params": journey_params
            }
        )
        
        return await self._handle_compose_journey(intent, context)
    
    async def _handle_list_journeys_soa(self, **kwargs) -> Dict[str, Any]:
        """SOA API handler for list_journeys."""
        journeys = []
        
        for journey_id, journey in self._journeys.items():
            journey_info = {
                "journey_id": journey_id,
                "journey_name": getattr(journey, 'JOURNEY_NAME', journey_id),
                "description": getattr(journey, '__doc__', '').strip().split('\n')[0] if hasattr(journey, '__doc__') and journey.__doc__ else ''
            }
            
            # Get SOA APIs if available
            if hasattr(journey, 'get_soa_apis'):
                journey_info["available_actions"] = list(journey.get_soa_apis().keys())
            
            journeys.append(journey_info)
        
        return self.build_journey_result(
            success=True,
            data={
                "solution_id": self.solution_id,
                "journeys": journeys,
                "journey_count": len(journeys)
            }
        )
    
    async def _handle_get_solution_info_soa(self, **kwargs) -> Dict[str, Any]:
        """SOA API handler for get_solution_info."""
        return self.build_journey_result(
            success=True,
            data={
                "solution_id": self.solution_id,
                "solution_name": self.solution_name,
                "solution_version": self.SOLUTION_VERSION,
                "supported_intents": self.SUPPORTED_INTENTS,
                "journeys": list(self._journeys.keys())
            }
        )
    
    # ========================================
    # MCP Server Integration
    # ========================================
    
    async def initialize_mcp_server(self):
        """
        Initialize MCP server.
        
        Override in subclasses to provide solution-specific MCP server.
        
        Returns:
            MCP server instance or None
        """
        # Subclasses should override to provide MCP server
        self.logger.warning("initialize_mcp_server not implemented")
        return None
    
    def get_mcp_server(self):
        """Get MCP server instance (may be None if not initialized)."""
        return self._mcp_server
    
    # ========================================
    # Experience SDK Integration
    # ========================================
    
    def get_experience_sdk_config(self) -> Dict[str, Any]:
        """
        Get configuration for Experience SDK integration.
        
        This configuration tells the frontend how to interact with this solution.
        
        Returns:
            Dict with Experience SDK configuration
        """
        # Collect all SOA APIs
        all_apis = self.get_soa_apis()
        
        return {
            "solution_id": self.solution_id,
            "solution_name": self.solution_name,
            "solution_version": self.SOLUTION_VERSION,
            "supported_intents": self.SUPPORTED_INTENTS,
            "journeys": [
                {
                    "journey_id": jid,
                    "journey_name": getattr(j, 'JOURNEY_NAME', jid)
                }
                for jid, j in self._journeys.items()
            ],
            "soa_apis": {
                name: {
                    "input_schema": api_def.get("input_schema", {}),
                    "description": api_def.get("description", "")
                }
                for name, api_def in all_apis.items()
            },
            "integration_patterns": {
                "intent_submission": {
                    "description": "Submit intents via Experience SDK submitIntent()",
                    "example": {
                        "intent_type": "compose_journey",
                        "parameters": {
                            "journey_id": "<journey_id>",
                            "journey_params": {}
                        }
                    }
                },
                "journey_invocation": {
                    "description": "Invoke journeys directly via compose_journey intent",
                    "available_journeys": list(self._journeys.keys())
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
                from symphainy_platform.civic_systems.agentic.telemetry.agentic_telemetry_service import AgenticTelemetryService
                self.telemetry_service = AgenticTelemetryService()
            except Exception as e:
                self.logger.debug(f"Telemetry service not available: {e}")
    
    # ========================================
    # Solution Info
    # ========================================
    
    def get_solution_info(self) -> Dict[str, Any]:
        """
        Get solution metadata.
        
        Returns:
            Dict with solution information
        """
        return {
            "solution_id": self.solution_id,
            "solution_name": self.solution_name,
            "solution_version": self.SOLUTION_VERSION,
            "supported_intents": self.SUPPORTED_INTENTS,
            "journeys": list(self._journeys.keys()),
            "status": "active"
        }
