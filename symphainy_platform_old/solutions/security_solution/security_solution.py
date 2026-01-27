"""
Security Solution - Platform Construct for Security Realm

Composes Security Realm journeys and exposes SOA APIs for agent consumption.

WHAT (Solution Role): I compose Security Realm journeys and expose APIs
HOW (Solution Implementation): I route intents to journey orchestrators
    and aggregate SOA APIs for MCP server registration

Architecture:
- Foundational solution - all other solutions depend on this
- Wraps Security Guard SDK infrastructure in solution pattern
- Composes Authentication and Registration journeys
- Enables MCP tools for agent-based security operations

Note: This solution wraps existing working infrastructure (Security Guard SDK,
auth_abstraction, etc.) - it doesn't replace them. The frontend can continue
to call /api/auth/* endpoints, which can optionally route through this solution.
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


class SecuritySolution:
    """
    Security Solution - Platform construct for Security Realm.
    
    Composes journeys:
    - Authentication Journey (login, token validation, logout)
    - Registration Journey (signup, email check)
    - Session Management Journey (create, validate, terminate)
    """
    
    SOLUTION_ID = "security_solution"
    SOLUTION_VERSION = "1.0"
    
    SUPPORTED_INTENTS = [
        "compose_journey",
        # Authentication
        "authenticate_user",
        "validate_token",
        "terminate_session",
        # Registration
        "create_user_account",
        "check_email_availability",
        # Session
        "create_session",
        "validate_authorization"
    ]
    
    def __init__(self, public_works=None, state_surface=None):
        """
        Initialize Security Solution.
        
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
        
        self.logger.info(f"SecuritySolution initialized: {self.SOLUTION_ID} v{self.SOLUTION_VERSION}")
    
    def _initialize_journeys(self):
        """Initialize journey orchestrators."""
        from .journeys.authentication_journey import AuthenticationJourney
        from .journeys.registration_journey import RegistrationJourney
        from .journeys.session_management_journey import SessionManagementJourney
        
        self._journeys["authentication"] = AuthenticationJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        self._journeys["registration"] = RegistrationJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        self._journeys["session_management"] = SessionManagementJourney(
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
        
        self.logger.info(f"SecuritySolution handling intent: {intent_type}")
        
        if intent_type == "compose_journey":
            return await self._handle_compose_journey(intent, context)
        
        # Route to appropriate journey based on intent type
        if intent_type in ["authenticate_user", "validate_token", "terminate_session"]:
            return await self._journeys["authentication"].compose_journey(
                journey_id=intent_type,
                context=context,
                journey_params=intent.parameters
            )
        
        if intent_type in ["create_user_account", "check_email_availability"]:
            return await self._journeys["registration"].compose_journey(
                journey_id=intent_type,
                context=context,
                journey_params=intent.parameters
            )
        
        if intent_type in ["create_session", "validate_authorization"]:
            return await self._journeys["session_management"].compose_journey(
                journey_id=intent_type,
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
            "authentication": "authentication",
            "registration": "registration",
            "session_management": "session_management",
            # Intent-based mappings
            "authenticate_user": "authentication",
            "validate_token": "authentication",
            "terminate_session": "authentication",
            "create_user_account": "registration",
            "check_email_availability": "registration",
            "create_session": "session_management",
            "validate_authorization": "session_management"
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
        
        self.logger.info(f"SecuritySolution aggregated {len(soa_apis)} SOA APIs")
        return soa_apis
    
    def initialize_mcp_server(self):
        """
        Initialize MCP server for this solution.
        
        Returns:
            Configured MCP server instance
        """
        from .mcp_server.security_solution_mcp_server import SecuritySolutionMCPServer
        
        mcp_server = SecuritySolutionMCPServer(
            solution=self,
            public_works=self.public_works
        )
        
        self.logger.info("SecuritySolution MCP server initialized")
        return mcp_server
    
    def get_solution_info(self) -> Dict[str, Any]:
        """Get solution metadata."""
        return {
            "solution_id": self.SOLUTION_ID,
            "solution_version": self.SOLUTION_VERSION,
            "realm": "security",
            "supported_intents": self.SUPPORTED_INTENTS,
            "journeys": list(self._journeys.keys()),
            "status": "active",
            "foundational": True  # All other solutions depend on this
        }
