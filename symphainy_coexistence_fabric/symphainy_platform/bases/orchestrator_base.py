"""
Base Orchestrator - Concrete Base for Journey Orchestrators

Concrete base for journey orchestrators. No ABC, no Protocol—type-hint as BaseOrchestrator.
See docs/architecture/PLATFORM_BASES_DISCIPLINE.md for common pattern.

WHAT (Orchestrator Role): I compose intent services into journeys
HOW (Orchestrator Implementation): I coordinate intent execution, manage sagas, expose SOA APIs

Key Principle: Orchestrators compose journeys. They coordinate intent services,
manage saga patterns, expose SOA APIs, and report telemetry.
"""

import sys
from pathlib import Path

# Add project root to path
# Add project root to path - find root by looking for pyproject.toml
def _find_project_root():
    path = Path(__file__).resolve()
    for parent in path.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return path.parents[3]  # Fallback

project_root = _find_project_root()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from utilities import get_logger, get_clock

from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.civic_systems.smart_city.sdk.nurse_sdk import NurseSDK


class BaseOrchestrator:
    """
    Concrete base for journey orchestrators. No ABC, no Protocol—type-hint as BaseOrchestrator.
    
    Provides:
    - Logger and clock utilities
    - Public Works access
    - Intent service composition
    - SOA API registration
    - MCP tool exposure
    - Saga coordination
    - Telemetry reporting (via Nurse SDK)
    """
    
    def __init__(
        self,
        orchestrator_id: str,
        public_works: Optional[Any] = None,
        intent_registry: Optional[Any] = None,
        state_surface: Optional[Any] = None,
        curator_sdk: Optional[Any] = None
    ):
        """
        Initialize base orchestrator.
        
        Args:
            orchestrator_id: Unique orchestrator identifier
            public_works: Public Works Foundation Service
            intent_registry: Intent Registry (for intent service discovery)
            state_surface: State Surface (for artifact resolution)
            curator_sdk: Curator SDK (for SOA API registration)
        """
        self.orchestrator_id = orchestrator_id
        self.public_works = public_works
        self.intent_registry = intent_registry
        self.state_surface = state_surface
        self.curator_sdk = curator_sdk
        
        # Logger and clock
        self.logger = get_logger(f"Orchestrator:{orchestrator_id}")
        self.clock = get_clock()
        
        # Initialize Nurse SDK for telemetry reporting
        self.nurse_sdk = None
        if public_works:
            # Get telemetry abstraction from Public Works
            telemetry_abstraction = getattr(public_works, 'telemetry_abstraction', None)
            if telemetry_abstraction:
                self.nurse_sdk = NurseSDK(telemetry_abstraction=telemetry_abstraction)
        
        # SOA API registry (for exposing intent services as SOA APIs)
        self._soa_apis: Dict[str, Dict[str, Any]] = {}
        
        # MCP tools (for exposing SOA APIs as MCP tools)
        self._mcp_tools: Dict[str, Dict[str, Any]] = {}
    
    async def record_telemetry(
        self,
        telemetry_data: Dict[str, Any],
        tenant_id: str
    ) -> Optional[Any]:
        """
        Record telemetry via Nurse SDK.
        
        Args:
            telemetry_data: Telemetry data dictionary
            tenant_id: Tenant identifier
        
        Returns:
            TelemetryRecord if Nurse SDK available, None otherwise
        """
        if not self.nurse_sdk:
            raise RuntimeError(
                "Nurse SDK not wired; cannot record telemetry. Platform contract §8A."
            )
        
        try:
            telemetry_record = await self.nurse_sdk.record_telemetry(
                telemetry_data={
                    "orchestrator_id": self.orchestrator_id,
                    **telemetry_data
                },
                tenant_id=tenant_id
            )
            return telemetry_record
        except Exception as e:
            self.logger.error(f"Failed to record telemetry: {e}", exc_info=True)
            return None
    
    def register_soa_api(
        self,
        api_name: str,
        api_definition: Dict[str, Any]
    ) -> bool:
        """
        Register a SOA API (intent service exposed as SOA API).
        
        Args:
            api_name: API name (e.g., "parse_file")
            api_definition: API definition (method, parameters, returns, etc.)
        
        Returns:
            True if registration successful
        """
        self._soa_apis[api_name] = api_definition
        self.logger.info(f"Registered SOA API: {api_name}")
        
        # Register with Curator if available
        if self.curator_sdk:
            try:
                # Register SOA API with Curator
                # (Implementation depends on Curator SDK interface)
                pass
            except Exception as e:
                self.logger.error(f"Failed to register SOA API with Curator: {e}", exc_info=True)
        
        return True
    
    def register_mcp_tool(
        self,
        tool_name: str,
        tool_definition: Dict[str, Any]
    ) -> bool:
        """
        Register an MCP tool (SOA API exposed as MCP tool).
        
        Args:
            tool_name: Tool name (e.g., "parse_file")
            tool_definition: Tool definition (handler, input_schema, description, etc.)
        
        Returns:
            True if registration successful
        """
        self._mcp_tools[tool_name] = tool_definition
        self.logger.info(f"Registered MCP tool: {tool_name}")
        
        # Register with Curator if available
        if self.curator_sdk:
            try:
                # Register MCP tool with Curator
                # (Implementation depends on Curator SDK interface)
                pass
            except Exception as e:
                self.logger.error(f"Failed to register MCP tool with Curator: {e}", exc_info=True)
        
        return True
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered SOA APIs."""
        return self._soa_apis.copy()
    
    def get_mcp_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered MCP tools."""
        return self._mcp_tools.copy()
    
    async def compose_journey(
        self,
        journey_id: str,
        context: ExecutionContext,
        journey_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compose a journey by orchestrating intent services. Subclasses must override.

        Args:
            journey_id: Journey identifier
            context: Execution context
            journey_params: Optional journey-specific parameters

        Returns:
            Journey execution result with artifacts and events
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement compose_journey(journey_id, context, journey_params)"
        )
    
    async def coordinate_saga(
        self,
        saga_id: str,
        steps: List[Dict[str, Any]],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Coordinate a saga pattern (distributed transaction).
        
        Args:
            saga_id: Saga identifier
            steps: List of saga steps (each with intent_type, params, compensation)
            context: Execution context
        
        Returns:
            Saga execution result
        """
        self.logger.info(f"Coordinating saga: {saga_id}")
        
        # Record telemetry
        await self.record_telemetry(
            telemetry_data={
                "action": "coordinate_saga",
                "saga_id": saga_id,
                "step_count": len(steps),
                "status": "started"
            },
            tenant_id=context.tenant_id
        )
        
        # Saga coordination logic
        # Execute steps sequentially or in parallel
        # Handle failures with compensating transactions
        # Record saga state in State Surface
        
        # Placeholder for saga implementation
        raise NotImplementedError("Saga coordination to be implemented by subclasses")
    
    def validate_contract_compliance(
        self,
        journey_contract: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate that execution result complies with journey contract.
        
        Args:
            journey_contract: Journey contract definition
            execution_result: Execution result to validate
        
        Returns:
            Tuple of (is_compliant, error_message)
        """
        # Basic validation - can be extended by subclasses
        if not execution_result:
            return False, "Execution result is empty"
        
        # Check for required artifacts
        required_artifacts = journey_contract.get("required_artifacts", [])
        artifacts = execution_result.get("artifacts", {})
        
        for artifact_type in required_artifacts:
            if artifact_type not in artifacts:
                return False, f"Required artifact {artifact_type} not found in result"
        
        return True, None
