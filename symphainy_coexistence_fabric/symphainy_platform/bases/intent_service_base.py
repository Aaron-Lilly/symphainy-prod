"""
Base Intent Service - Base Class for Intent Services

Base class for intent services that provide atomic platform capabilities.

WHAT (Intent Service Role): I provide atomic platform capabilities
HOW (Intent Service Implementation): I execute intents, create artifacts, register with State Surface

Key Principle: Intent services are atomic capabilities. They execute intents,
create artifacts, register them with State Surface, and report telemetry.
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

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from utilities import get_logger, get_clock, generate_event_id

from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.runtime.artifact_registry import (
    ArtifactRecord,
    Materialization,
    SemanticDescriptor,
    ProducedBy,
    LifecycleState
)
from symphainy_platform.civic_systems.smart_city.sdk.nurse_sdk import NurseSDK


class BaseIntentService(ABC):
    """
    Base class for intent services.
    
    Provides:
    - Logger and clock utilities
    - Public Works access
    - Execution context handling
    - Artifact creation and registration
    - Telemetry reporting (via Nurse SDK)
    - Contract compliance validation
    """
    
    def __init__(
        self,
        service_id: str,
        intent_type: str,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        """
        Initialize base intent service.
        
        Args:
            service_id: Unique service identifier
            intent_type: Intent type this service handles (e.g., "parse_file")
            public_works: Public Works Foundation Service
            state_surface: State Surface (for artifact registration)
        """
        self.service_id = service_id
        self.intent_type = intent_type
        self.public_works = public_works
        self.state_surface = state_surface
        
        # Logger and clock
        self.logger = get_logger(f"IntentService:{service_id}")
        self.clock = get_clock()
        
        # Initialize Nurse SDK for telemetry reporting
        self.nurse_sdk = None
        if public_works:
            # Get telemetry abstraction from Public Works
            telemetry_abstraction = getattr(public_works, 'telemetry_abstraction', None)
            if telemetry_abstraction:
                self.nurse_sdk = NurseSDK(telemetry_abstraction=telemetry_abstraction)
    
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
            self.logger.warning("Nurse SDK not available, skipping telemetry")
            return None
        
        try:
            telemetry_record = await self.nurse_sdk.record_telemetry(
                telemetry_data={
                    "service_id": self.service_id,
                    "intent_type": self.intent_type,
                    **telemetry_data
                },
                tenant_id=tenant_id
            )
            return telemetry_record
        except Exception as e:
            self.logger.error(f"Failed to record telemetry: {e}", exc_info=True)
            return None
    
    async def register_artifact(
        self,
        artifact: ArtifactRecord,
        context: ExecutionContext
    ) -> bool:
        """
        Register artifact with State Surface.
        
        Args:
            artifact: Artifact record to register
            context: Execution context
        
        Returns:
            True if registration successful
        """
        if not self.state_surface:
            self.logger.error("State Surface not available, cannot register artifact")
            return False
        
        try:
            # Register artifact via State Surface
            success = await self.state_surface.artifact_registry.register_artifact(
                artifact=artifact,
                tenant_id=context.tenant_id
            )
            
            if success:
                self.logger.info(f"Registered artifact: {artifact.artifact_id} ({artifact.artifact_type})")
            else:
                self.logger.error(f"Failed to register artifact: {artifact.artifact_id}")
            
            return success
        except Exception as e:
            self.logger.error(f"Error registering artifact: {e}", exc_info=True)
            return False
    
    def create_artifact_record(
        self,
        artifact_id: str,
        artifact_type: str,
        context: ExecutionContext,
        semantic_descriptor: SemanticDescriptor,
        parent_artifacts: Optional[list[str]] = None,
        materializations: Optional[list[Materialization]] = None,
        lifecycle_state: str = LifecycleState.READY
    ) -> ArtifactRecord:
        """
        Create an artifact record (helper method).
        
        Args:
            artifact_id: Artifact identifier
            artifact_type: Artifact type (e.g., "file", "parsed_content", "embeddings")
            context: Execution context
            semantic_descriptor: Semantic descriptor
            parent_artifacts: Optional list of parent artifact IDs
            materializations: Optional list of materializations
            lifecycle_state: Lifecycle state (default: READY)
        
        Returns:
            ArtifactRecord
        """
        return ArtifactRecord(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            tenant_id=context.tenant_id,
            produced_by=ProducedBy(
                intent=self.intent_type,
                execution_id=context.execution_id
            ),
            parent_artifacts=parent_artifacts or [],
            lifecycle_state=lifecycle_state,
            semantic_descriptor=semantic_descriptor,
            materializations=materializations or []
        )
    
    @abstractmethod
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the intent service.
        
        Args:
            context: Execution context
            params: Optional intent parameters
        
        Returns:
            Execution result with artifacts and events
        
        Raises:
            ValueError: If intent type doesn't match
            Exception: If execution fails
        """
        # Validate intent type
        if context.intent.intent_type != self.intent_type:
            raise ValueError(
                f"Intent type mismatch: expected {self.intent_type}, "
                f"got {context.intent.intent_type}"
            )
        
        # Record telemetry (start)
        await self.record_telemetry(
            telemetry_data={
                "action": "execute",
                "status": "started",
                "execution_id": context.execution_id
            },
            tenant_id=context.tenant_id
        )
        
        # Subclasses must implement actual execution logic
        raise NotImplementedError("Subclasses must implement execute()")
    
    def validate_contract_compliance(
        self,
        intent_contract: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate that execution result complies with intent contract.
        
        Args:
            intent_contract: Intent contract definition
            execution_result: Execution result to validate
        
        Returns:
            Tuple of (is_compliant, error_message)
        """
        # Basic validation - can be extended by subclasses
        if not execution_result:
            return False, "Execution result is empty"
        
        # Check for required artifacts
        required_artifacts = intent_contract.get("required_artifacts", [])
        artifacts = execution_result.get("artifacts", {})
        
        for artifact_type in required_artifacts:
            if artifact_type not in artifacts:
                return False, f"Required artifact {artifact_type} not found in result"
        
        # Check return types match contract
        return_types = intent_contract.get("returns", {})
        for key, expected_type in return_types.items():
            if key in execution_result:
                actual_value = execution_result[key]
                # Basic type checking (can be extended)
                if expected_type == "artifact" and not isinstance(actual_value, dict):
                    return False, f"Expected artifact dict for {key}, got {type(actual_value)}"
        
        return True, None
    
    def validate_params(
        self,
        params: Dict[str, Any],
        intent_contract: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate intent parameters against contract.
        
        Args:
            params: Intent parameters
            intent_contract: Intent contract definition
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required parameters
        required_params = intent_contract.get("parameters", {}).get("required", [])
        for param in required_params:
            if param not in params:
                return False, f"Required parameter {param} not provided"
        
        # Check parameter types (basic validation)
        param_types = intent_contract.get("parameters", {}).get("types", {})
        for param, expected_type in param_types.items():
            if param in params:
                actual_value = params[param]
                # Basic type checking (can be extended)
                if expected_type == "str" and not isinstance(actual_value, str):
                    return False, f"Parameter {param} must be str, got {type(actual_value)}"
                elif expected_type == "int" and not isinstance(actual_value, int):
                    return False, f"Parameter {param} must be int, got {type(actual_value)}"
                elif expected_type == "dict" and not isinstance(actual_value, dict):
                    return False, f"Parameter {param} must be dict, got {type(actual_value)}"
        
        return True, None
