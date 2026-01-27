"""
Solution Creation Journey Orchestrator

Composes the solution creation journey:
1. Validate solution_source and source_id
2. Execute create_solution intent
3. Register platform solution via Solution SDK
4. Return solution artifact reference

WHAT (Journey Role): I orchestrate platform solution creation
HOW (Journey Implementation): I compose create_solution intent

Key Principle: Journey orchestrators compose intent services into journeys.
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


class SolutionCreationJourney:
    """
    Solution Creation Journey Orchestrator.
    
    Journey Flow:
    1. Validate solution_source and source_id (required)
    2. Execute create_solution intent
    3. Register platform solution
    4. Return solution reference
    
    Provides MCP Tools:
    - outcomes_create_solution: Create platform solution from artifact
    """
    
    JOURNEY_ID = "solution_creation"
    JOURNEY_NAME = "Solution Creation"
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        """Initialize Solution Creation Journey."""
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        
        self.journey_id = self.JOURNEY_ID
        self.journey_name = self.JOURNEY_NAME
        
        self._intent_service = None
        self.telemetry_service = None
    
    async def compose_journey(
        self,
        context: ExecutionContext,
        journey_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compose the solution creation journey.
        
        Args:
            context: Execution context
            journey_params: Journey parameters including:
                - solution_source: Source type (roadmap, poc, blueprint) (required)
                - source_id: Source artifact ID (required)
                - solution_name: Optional solution name
        
        Returns:
            Journey result with solution artifact
        """
        journey_params = journey_params or {}
        
        self.logger.info(f"Composing journey: {self.journey_name}")
        
        await self._ensure_telemetry()
        
        journey_execution_id = generate_event_id()
        await self._record_telemetry({
            "action": "journey_started",
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id
        }, context.tenant_id)
        
        try:
            # Validate required parameters
            solution_source = journey_params.get("solution_source")
            source_id = journey_params.get("source_id")
            
            if not solution_source:
                raise ValueError("solution_source is required (roadmap, poc, or blueprint)")
            if not source_id:
                raise ValueError("source_id is required")
            
            valid_sources = ["roadmap", "poc", "blueprint"]
            if solution_source not in valid_sources:
                raise ValueError(f"Invalid solution_source: {solution_source}. Must be one of: {valid_sources}")
            
            # Get intent service
            intent_service = await self._get_intent_service()
            
            # Execute create_solution intent
            result = await intent_service.execute(context, journey_params)
            
            # Build journey result
            journey_result = self._build_journey_result(
                intent_result=result,
                journey_execution_id=journey_execution_id
            )
            
            await self._record_telemetry({
                "action": "journey_completed",
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "solution_source": solution_source,
                "source_id": source_id
            }, context.tenant_id)
            
            return journey_result
            
        except Exception as e:
            self.logger.error(f"Journey failed: {e}", exc_info=True)
            
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
                "events": [{"type": "journey_failed", "journey_id": self.journey_id, "error": str(e)}]
            }
    
    async def _get_intent_service(self):
        """Get or create the intent service."""
        if not self._intent_service:
            from symphainy_coexistence_fabric.symphainy_platform.realms.outcomes.intent_services import (
                CreateSolutionService
            )
            self._intent_service = CreateSolutionService(
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
                {"type": "journey_completed", "journey_id": self.journey_id, "journey_execution_id": journey_execution_id},
                *intent_result.get("events", [])
            ]
        }
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get SOA APIs provided by this journey."""
        return {
            "create_solution": {
                "handler": self._soa_create_solution,
                "description": "Create platform solution from artifact",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "solution_source": {
                            "type": "string",
                            "enum": ["roadmap", "poc", "blueprint"],
                            "description": "Source type"
                        },
                        "source_id": {
                            "type": "string",
                            "description": "Source artifact ID"
                        },
                        "solution_name": {
                            "type": "string",
                            "description": "Solution name"
                        },
                        "tenant_id": {"type": "string", "description": "Tenant identifier"},
                        "session_id": {"type": "string", "description": "Session identifier"}
                    },
                    "required": ["solution_source", "source_id", "tenant_id", "session_id"]
                }
            }
        }
    
    async def _soa_create_solution(
        self,
        solution_source: str,
        source_id: str,
        tenant_id: str,
        session_id: str,
        solution_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """SOA API: Create platform solution."""
        execution_id = generate_event_id()
        
        context = ExecutionContext(
            execution_id=execution_id,
            tenant_id=tenant_id,
            session_id=session_id,
            intent=None,
            state_surface=self.state_surface
        )
        
        journey_params = {
            "solution_source": solution_source,
            "source_id": source_id
        }
        if solution_name:
            journey_params["solution_name"] = solution_name
        
        return await self.compose_journey(context, journey_params)
    
    async def _ensure_telemetry(self):
        if not self.telemetry_service and self.public_works:
            try:
                self.telemetry_service = self.public_works.get_telemetry_service()
            except Exception:
                pass
    
    async def _record_telemetry(self, telemetry_data: Dict[str, Any], tenant_id: str):
        if self.telemetry_service:
            try:
                await self.telemetry_service.record({"journey_id": self.journey_id, "tenant_id": tenant_id, **telemetry_data})
            except Exception:
                pass
