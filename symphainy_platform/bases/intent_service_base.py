"""
Base Intent Service - Base Class for Intent Services

Base class for intent services that provide atomic platform capabilities.

WHAT (Intent Service Role): I provide atomic platform capabilities
HOW (Intent Service Implementation): I execute intents, create artifacts, register with State Surface

Key Principle: Intent services are atomic capabilities. They execute intents,
create artifacts, register them with State Surface, and report telemetry.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

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


class BaseIntentService(ABC):
    """
    Base class for intent services.
    
    Provides:
    - Logger and clock utilities
    - Public Works access
    - Execution context handling
    - Artifact creation and registration
    - Telemetry reporting
    - Contract compliance validation
    
    Intent services follow a simple pattern:
    1. Validate parameters against contract
    2. Execute the operation using enabling services
    3. Create artifacts and register them
    4. Record telemetry
    5. Return result with artifacts and events
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
            service_id: Unique service identifier (e.g., "parse_content_service")
            intent_type: Intent type this service handles (e.g., "parse_content")
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
        
        # Telemetry service (lazy initialization)
        self._telemetry_service = None
    
    @property
    def telemetry_service(self):
        """Get or initialize telemetry service."""
        if not self._telemetry_service and self.public_works:
            self._telemetry_service = getattr(self.public_works, 'telemetry_service', None)
        return self._telemetry_service
    
    async def record_telemetry(
        self,
        telemetry_data: Dict[str, Any],
        tenant_id: str
    ) -> Optional[Any]:
        """
        Record telemetry for this service operation.
        
        Args:
            telemetry_data: Telemetry data dictionary
            tenant_id: Tenant identifier
        
        Returns:
            Telemetry record if service available, None otherwise
        """
        if not self.telemetry_service:
            return None
        
        try:
            return await self.telemetry_service.record_telemetry(
                telemetry_data={
                    "service_id": self.service_id,
                    "intent_type": self.intent_type,
                    "timestamp": self.clock.now().isoformat(),
                    **telemetry_data
                },
                tenant_id=tenant_id
            )
        except Exception as e:
            self.logger.warning(f"Failed to record telemetry: {e}")
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
            self.logger.warning("State Surface not available, skipping artifact registration")
            return False
        
        try:
            # Get artifact registry from state surface
            artifact_registry = getattr(self.state_surface, 'artifact_registry', None)
            if not artifact_registry:
                self.logger.warning("Artifact registry not available")
                return False
            
            success = await artifact_registry.register_artifact(
                artifact=artifact,
                tenant_id=context.tenant_id
            )
            
            if success:
                self.logger.info(f"Registered artifact: {artifact.artifact_id}")
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
        parent_artifacts: Optional[List[str]] = None,
        materializations: Optional[List[Materialization]] = None,
        lifecycle_state: str = LifecycleState.READY
    ) -> ArtifactRecord:
        """
        Create an artifact record.
        
        Args:
            artifact_id: Artifact identifier
            artifact_type: Artifact type (e.g., "parsed_content", "embeddings")
            context: Execution context
            semantic_descriptor: Semantic descriptor for the artifact
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
    
    def validate_params(
        self,
        params: Dict[str, Any],
        required_params: List[str],
        param_types: Optional[Dict[str, type]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate intent parameters.
        
        Args:
            params: Intent parameters
            required_params: List of required parameter names
            param_types: Optional dict mapping param names to expected types
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required parameters
        for param in required_params:
            if param not in params or params[param] is None:
                return False, f"Required parameter '{param}' not provided"
        
        # Check parameter types
        if param_types:
            for param, expected_type in param_types.items():
                if param in params and params[param] is not None:
                    if not isinstance(params[param], expected_type):
                        return False, f"Parameter '{param}' must be {expected_type.__name__}"
        
        return True, None
    
    @abstractmethod
    async def execute(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Execute the intent service.
        
        Args:
            intent: The intent to execute
            context: Execution context
        
        Returns:
            Execution result with "artifacts" and "events" keys
        
        Subclasses must implement this method with their specific logic.
        """
        pass
    
    async def __call__(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Allow service to be called as a function.
        
        Args:
            intent: The intent to execute
            context: Execution context
        
        Returns:
            Execution result
        """
        # Validate intent type
        if intent.intent_type != self.intent_type:
            raise ValueError(
                f"Intent type mismatch: expected {self.intent_type}, "
                f"got {intent.intent_type}"
            )
        
        # Record start telemetry
        await self.record_telemetry(
            telemetry_data={
                "action": "execute",
                "status": "started",
                "execution_id": context.execution_id
            },
            tenant_id=context.tenant_id
        )
        
        start_time = self.clock.now()
        
        try:
            # Execute the service
            result = await self.execute(intent, context)
            
            # Record success telemetry
            duration_ms = (self.clock.now() - start_time).total_seconds() * 1000
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute",
                    "status": "completed",
                    "execution_id": context.execution_id,
                    "duration_ms": duration_ms
                },
                tenant_id=context.tenant_id
            )
            
            return result
            
        except Exception as e:
            # Record error telemetry
            duration_ms = (self.clock.now() - start_time).total_seconds() * 1000
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute",
                    "status": "failed",
                    "execution_id": context.execution_id,
                    "duration_ms": duration_ms,
                    "error": str(e)
                },
                tenant_id=context.tenant_id
            )
            raise
