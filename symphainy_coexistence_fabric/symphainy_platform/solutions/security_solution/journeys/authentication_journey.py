"""
Authentication Journey Orchestrator

Composes authentication operations into a coherent user journey.

WHAT (Journey Role): I compose authentication operations (login, validate, logout)
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
    AuthenticateUserService,
    ValidateTokenService,
    TerminateSessionService
)


class AuthenticationJourney(BaseOrchestrator):
    """
    Authentication Journey Orchestrator.
    
    Composes:
    - AuthenticateUserService for login
    - ValidateTokenService for token validation
    - TerminateSessionService for logout
    
    SOA APIs:
    - authenticate_user: Login with credentials
    - validate_token: Validate authentication token
    - terminate_session: Logout
    """
    
    JOURNEY_ID = "journey_security_authentication"
    
    def __init__(self, public_works=None, state_surface=None):
        """Initialize AuthenticationJourney."""
        super().__init__(
            orchestrator_id="authentication_journey",
            public_works=public_works
        )
        self.state_surface = state_surface
        
        # Initialize intent services
        self.authenticate_user_service = AuthenticateUserService(
            public_works=public_works,
            state_surface=state_surface
        )
        self.validate_token_service = ValidateTokenService(
            public_works=public_works,
            state_surface=state_surface
        )
        self.terminate_session_service = TerminateSessionService(
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def compose_journey(
        self,
        journey_id: str,
        context: ExecutionContext,
        journey_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compose authentication journey.
        
        Args:
            journey_id: The journey being composed
            context: Execution context
            journey_params: Journey-specific parameters
            
        Returns:
            Dict with artifacts and events
        """
        journey_execution_id = f"auth_journey_{generate_event_id()}"
        start_time = datetime.utcnow()
        
        self.logger.info(f"Starting authentication journey: {journey_execution_id}")
        
        try:
            params = journey_params or {}
            
            if journey_id in ["authentication", "authenticate_user"]:
                result = await self.authenticate_user_service.execute(context, params)
            elif journey_id == "validate_token":
                result = await self.validate_token_service.execute(context, params)
            elif journey_id == "terminate_session":
                result = await self.terminate_session_service.execute(context, params)
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
            "authenticate_user": self._handle_authenticate_user_soa,
            "validate_token": self._handle_validate_token_soa,
            "terminate_session": self._handle_terminate_session_soa
        }
    
    async def _handle_authenticate_user_soa(
        self,
        context: ExecutionContext,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """SOA API handler for authenticate_user."""
        return await self.compose_journey(
            journey_id="authenticate_user",
            context=context,
            journey_params=params
        )
    
    async def _handle_validate_token_soa(
        self,
        context: ExecutionContext,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """SOA API handler for validate_token."""
        return await self.compose_journey(
            journey_id="validate_token",
            context=context,
            journey_params=params
        )
    
    async def _handle_terminate_session_soa(
        self,
        context: ExecutionContext,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """SOA API handler for terminate_session."""
        return await self.compose_journey(
            journey_id="terminate_session",
            context=context,
            journey_params=params
        )
