"""
Outcome Synthesis Journey Orchestrator

Composes the outcome synthesis journey:
1. Read pillar summaries from session state
2. Execute synthesize_outcome intent
3. Return synthesis result with visualizations

WHAT (Journey Role): I orchestrate outcome synthesis from all pillars
HOW (Journey Implementation): I compose synthesize_outcome intent with session state

Key Principle: Journey orchestrators compose intent services into journeys.
They use BaseOrchestrator.compose_journey() pattern.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.execution_context import ExecutionContext


class OutcomeSynthesisJourney:
    """
    Outcome Synthesis Journey Orchestrator.
    
    Journey Flow:
    1. Read pillar summaries from session state
    2. Execute synthesize_outcome intent
    3. Generate realm-specific visualizations
    4. Return synthesis result
    
    Provides MCP Tools:
    - outcomes_synthesize: Synthesize outcomes from session pillars
    """
    
    JOURNEY_ID = "outcome_synthesis"
    JOURNEY_NAME = "Outcome Synthesis"
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        """
        Initialize Outcome Synthesis Journey.
        
        Args:
            public_works: Public Works Foundation Service
            state_surface: State Surface for artifact management
        """
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        
        # Journey configuration
        self.journey_id = self.JOURNEY_ID
        self.journey_name = self.JOURNEY_NAME
        
        # Intent service (lazy loaded)
        self._intent_service = None
        
        # Telemetry
        self.telemetry_service = None
    
    async def compose_journey(
        self,
        context: ExecutionContext,
        journey_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compose the outcome synthesis journey.
        
        This method orchestrates the complete journey:
        1. Validate journey parameters
        2. Execute synthesize_outcome intent via intent service
        3. Return journey result with artifacts and events
        
        Args:
            context: Execution context
            journey_params: Journey parameters including:
                - synthesis_options: Optional synthesis options
        
        Returns:
            Journey result with artifacts and events
        """
        journey_params = journey_params or {}
        
        self.logger.info(f"Composing journey: {self.journey_name}")
        
        # Initialize telemetry if needed
        await self._ensure_telemetry()
        
        # Record journey start
        journey_execution_id = generate_event_id()
        await self._record_telemetry({
            "action": "journey_started",
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id
        }, context.tenant_id)
        
        try:
            # Get intent service
            intent_service = await self._get_intent_service()
            
            # Execute synthesize_outcome intent
            result = await intent_service.execute(context, journey_params)
            
            # Build journey result
            journey_result = self._build_journey_result(
                intent_result=result,
                journey_execution_id=journey_execution_id
            )
            
            # Record journey completion
            await self._record_telemetry({
                "action": "journey_completed",
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id
            }, context.tenant_id)
            
            return journey_result
            
        except Exception as e:
            self.logger.error(f"Journey failed: {e}", exc_info=True)
            
            # Record journey failure
            await self._record_telemetry({
                "action": "journey_failed",
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "error": str(e)
            }, context.tenant_id)
            
            return {
                "success": False,
                "error": str(e),
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "artifacts": {},
                "events": [
                    {
                        "type": "journey_failed",
                        "journey_id": self.journey_id,
                        "error": str(e)
                    }
                ]
            }
    
    async def _get_intent_service(self):
        """Get or create the intent service."""
        if not self._intent_service:
            # Import here to avoid circular imports
            from symphainy_coexistence_fabric.symphainy_platform.realms.outcomes.intent_services import (
                SynthesizeOutcomeService
            )
            self._intent_service = SynthesizeOutcomeService(
                public_works=self.public_works,
                state_surface=self.state_surface
            )
        return self._intent_service
    
    def _build_journey_result(
        self,
        intent_result: Dict[str, Any],
        journey_execution_id: str
    ) -> Dict[str, Any]:
        """Build journey result from intent result."""
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": intent_result.get("artifacts", {}),
            "events": [
                {
                    "type": "journey_completed",
                    "journey_id": self.journey_id,
                    "journey_execution_id": journey_execution_id
                },
                *intent_result.get("events", [])
            ]
        }
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """
        Get SOA APIs provided by this journey.
        
        Returns:
            Dict of api_name -> api_definition
        """
        return {
            "synthesize": {
                "handler": self._soa_synthesize,
                "description": "Synthesize outcomes from all pillars",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "tenant_id": {
                            "type": "string",
                            "description": "Tenant identifier"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier"
                        },
                        "synthesis_options": {
                            "type": "object",
                            "description": "Optional synthesis options"
                        }
                    },
                    "required": ["tenant_id", "session_id"]
                }
            }
        }
    
    async def _soa_synthesize(
        self,
        tenant_id: str,
        session_id: str,
        synthesis_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """SOA API: Synthesize outcomes."""
        execution_id = generate_event_id()
        
        # Create minimal context for SOA call
        context = ExecutionContext(
            execution_id=execution_id,
            tenant_id=tenant_id,
            session_id=session_id,
            intent=None,
            state_surface=self.state_surface
        )
        
        journey_params = {}
        if synthesis_options:
            journey_params["synthesis_options"] = synthesis_options
        
        return await self.compose_journey(context, journey_params)
    
    async def _ensure_telemetry(self):
        """Ensure telemetry service is initialized."""
        if not self.telemetry_service and self.public_works:
            try:
                self.telemetry_service = self.public_works.get_telemetry_service()
            except Exception:
                pass
    
    async def _record_telemetry(self, telemetry_data: Dict[str, Any], tenant_id: str):
        """Record telemetry data."""
        if self.telemetry_service:
            try:
                await self.telemetry_service.record({
                    "journey_id": self.journey_id,
                    "tenant_id": tenant_id,
                    **telemetry_data
                })
            except Exception:
                pass
