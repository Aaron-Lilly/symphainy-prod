"""
Session Management Journey Orchestrator

Composes session management operations into a coherent user journey.

WHAT (Journey Role): I compose session operations (create, validate, authorize)
HOW (Journey Implementation): I orchestrate Security Realm intent services
    and expose SOA APIs for MCP server
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utilities import get_logger, generate_event_id
from symphainy_platform.bases.orchestrator_base import BaseOrchestrator
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.realms.security import (
    CreateSessionService,
    ValidateAuthorizationService
)


class SessionManagementJourney(BaseOrchestrator):
    """
    Session Management Journey Orchestrator.
    
    Composes:
    - CreateSessionService for session creation
    - ValidateAuthorizationService for permission checks
    
    SOA APIs:
    - create_session: Create authenticated session
    - validate_authorization: Check user permissions
    """
    
    JOURNEY_ID = "journey_security_session_management"
    
    def __init__(self, public_works=None, state_surface=None):
        """Initialize SessionManagementJourney."""
        super().__init__(
            orchestrator_id="session_management_journey",
            public_works=public_works
        )
        self.state_surface = state_surface
        
        # Initialize intent services
        self.create_session_service = CreateSessionService(
            public_works=public_works,
            state_surface=state_surface
        )
        self.validate_authorization_service = ValidateAuthorizationService(
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def compose_journey(
        self,
        journey_id: Optional[str] = None,
        context: Optional[ExecutionContext] = None,
        journey_params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Compose session management journey.
        
        Args:
            journey_id: The journey being composed (defaults to 'session_management')
            context: Execution context (can also be passed as kwarg)
            journey_params: Journey-specific parameters (can also be passed as kwarg)
            **kwargs: Additional kwargs for flexibility
            
        Returns:
            Dict with artifacts and events
        """
        # Handle flexible calling conventions (positional vs kwargs)
        if context is None:
            context = kwargs.get('context')
        if journey_params is None:
            journey_params = kwargs.get('journey_params', {})
        if journey_id is None:
            journey_id = kwargs.get('journey_id', 'session_management')
        
        # Validate context
        if context is None:
            raise ValueError("context is required for compose_journey")
        
        journey_execution_id = f"session_journey_{generate_event_id()}"
        start_time = datetime.utcnow()
        
        self.logger.info(f"Starting session management journey: {journey_execution_id}")
        
        try:
            params = journey_params or {}
            
            if journey_id in ["session_management", "create_session", "create", "validate"]:
                # Handle common action parameter pattern
                action = params.get("action")
                if action == "validate" or journey_id == "validate_authorization":
                    result = await self.validate_authorization_service.execute(context, params)
                else:
                    result = await self.create_session_service.execute(context, params)
            elif journey_id == "validate_authorization":
                result = await self.validate_authorization_service.execute(context, params)
            else:
                raise ValueError(f"Unknown journey_id: {journey_id}")
            
            # Record telemetry
            end_time = datetime.utcnow()
            latency_ms = (end_time - start_time).total_seconds() * 1000
            
            await self.record_telemetry(
                telemetry_data={
                    "journey_id": journey_id,
                    "journey_execution_id": journey_execution_id,
                    "latency_ms": latency_ms,
                    "status": "completed"
                },
                tenant_id=context.tenant_id
            )
            
            # Add journey metadata
            result["journey_execution_id"] = journey_execution_id
            result["journey_id"] = self.JOURNEY_ID
            
            return result
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={
                    "journey_id": journey_id,
                    "journey_execution_id": journey_execution_id,
                    "status": "failed",
                    "error": str(e)
                },
                tenant_id=context.tenant_id
            )
            raise
    
    def get_soa_apis(self) -> Dict[str, Callable]:
        """Get SOA APIs for this journey."""
        return {
            "create_session": self._handle_create_session_soa,
            "validate_authorization": self._handle_validate_authorization_soa
        }
    
    async def _handle_create_session_soa(
        self,
        context: ExecutionContext,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """SOA API handler for create_session."""
        return await self.compose_journey(
            journey_id="create_session",
            context=context,
            journey_params=params
        )
    
    async def _handle_validate_authorization_soa(
        self,
        context: ExecutionContext,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """SOA API handler for validate_authorization."""
        return await self.compose_journey(
            journey_id="validate_authorization",
            context=context,
            journey_params=params
        )
