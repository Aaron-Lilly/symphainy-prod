"""
Platform SDK Intent Service Base

New base class for intent services that use PlatformContext (ctx).
This is the recommended base class for all new intent services.

Usage:
    from symphainy_platform.civic_systems.platform_sdk import PlatformIntentService
    
    class MyIntentService(PlatformIntentService):
        intent_type = "my_intent"
        
        async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
            # Parse a file using ctx.platform
            parsed = await ctx.platform.parse(file_ref, file_type="pdf")
            
            # Store result using ctx.state_surface (Runtime)
            await ctx.state_surface.store_file_reference(...)
            
            # Check data boundary using ctx.governance
            access = await ctx.governance.data_steward.request_data_access(...)
            
            return {"artifacts": {...}, "events": [...]}

Migration from BaseIntentService:
    Old: def __init__(self, service_id, intent_type, public_works, state_surface)
    New: def __init__(self, service_id, intent_type)  # ctx provides everything
    
    Old: async def execute(self, context: ExecutionContext, params)
    New: async def execute(self, ctx: PlatformContext) -> Dict[str, Any]
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from utilities import get_logger, get_clock, generate_event_id

from .context import PlatformContext
from symphainy_platform.runtime.artifact_registry import (
    ArtifactRecord,
    Materialization,
    SemanticDescriptor,
    ProducedBy,
    LifecycleState
)


class PlatformIntentService:
    """
    Base class for intent services using PlatformContext.
    
    This is the recommended base class for all new intent services.
    It receives the full PlatformContext (ctx) which provides access to:
    
    - ctx.platform    → Capability operations (parse, visualize, etc.)
    - ctx.governance  → Smart City SDKs (data_steward, auth, etc.)
    - ctx.reasoning   → Agentic (LLM, agents)
    - ctx.state_surface → State (Runtime owns)
    - ctx.artifacts   → Artifact registry (Runtime owns)
    - ctx.wal         → Write-ahead log (Runtime owns)
    
    Subclasses must:
    1. Set intent_type class attribute
    2. Override execute(ctx) method
    """
    
    # Must be set by subclass
    intent_type: str = ""
    
    def __init__(
        self,
        service_id: Optional[str] = None,
        intent_type: Optional[str] = None
    ):
        """
        Initialize platform intent service.
        
        Args:
            service_id: Optional service identifier (defaults to class name)
            intent_type: Optional intent type (defaults to class attribute)
        """
        self.service_id = service_id or self.__class__.__name__
        if intent_type:
            self.intent_type = intent_type
        
        if not self.intent_type:
            raise ValueError(f"intent_type must be set for {self.__class__.__name__}")
        
        self.logger = get_logger(f"IntentService:{self.service_id}")
        self.clock = get_clock()
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute the intent service.
        
        Subclasses must override this method.
        
        Args:
            ctx: PlatformContext with full platform access
        
        Returns:
            Dict with:
                - artifacts: Dict[str, Any] - Produced artifacts
                - events: List[Dict] - Events to emit
                - status: str - "success" or "failed"
                - error: str (optional) - Error message if failed
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement execute()")
    
    async def __call__(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Callable interface - validates and executes.
        
        Args:
            ctx: PlatformContext
        
        Returns:
            Execution result
        """
        # Validate intent type matches
        if ctx.intent.intent_type != self.intent_type:
            raise ValueError(
                f"Intent type mismatch: expected {self.intent_type}, "
                f"got {ctx.intent.intent_type}"
            )
        
        # Record telemetry start
        await self._record_telemetry_start(ctx)
        
        try:
            # Execute
            result = await self.execute(ctx)
            
            # Record telemetry success
            await self._record_telemetry_end(ctx, result, success=True)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Intent execution failed: {e}", exc_info=True)
            
            # Record telemetry failure
            await self._record_telemetry_end(ctx, {"error": str(e)}, success=False)
            
            return {
                "artifacts": {},
                "events": [],
                "status": "failed",
                "error": str(e)
            }
    
    # ========================================================================
    # ARTIFACT HELPERS
    # ========================================================================
    
    def create_artifact_record(
        self,
        artifact_id: str,
        artifact_type: str,
        ctx: PlatformContext,
        semantic_descriptor: SemanticDescriptor,
        parent_artifacts: Optional[List[str]] = None,
        materializations: Optional[List[Materialization]] = None,
        lifecycle_state: str = LifecycleState.READY
    ) -> ArtifactRecord:
        """
        Create an artifact record.
        
        Args:
            artifact_id: Artifact identifier
            artifact_type: Type of artifact
            ctx: Platform context
            semantic_descriptor: What the artifact means
            parent_artifacts: Optional lineage
            materializations: Optional materializations
            lifecycle_state: Initial lifecycle state
        
        Returns:
            ArtifactRecord
        """
        return ArtifactRecord(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            tenant_id=ctx.tenant_id,
            produced_by=ProducedBy(
                intent=self.intent_type,
                execution_id=ctx.execution_id
            ),
            parent_artifacts=parent_artifacts or [],
            lifecycle_state=lifecycle_state,
            semantic_descriptor=semantic_descriptor,
            materializations=materializations or []
        )
    
    async def register_artifact(
        self,
        artifact: ArtifactRecord,
        ctx: PlatformContext
    ) -> bool:
        """
        Register artifact with Runtime artifact registry.
        
        Args:
            artifact: Artifact record
            ctx: Platform context
        
        Returns:
            True if successful
        """
        if not ctx.artifacts:
            self.logger.error("Artifact registry not available")
            return False
        
        try:
            success = await ctx.artifacts.register_artifact(
                artifact=artifact,
                tenant_id=ctx.tenant_id
            )
            
            if success:
                self.logger.info(f"✅ Registered artifact: {artifact.artifact_id}")
            else:
                self.logger.error(f"❌ Failed to register artifact: {artifact.artifact_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error registering artifact: {e}", exc_info=True)
            return False
    
    # ========================================================================
    # TELEMETRY HELPERS
    # ========================================================================
    
    async def _record_telemetry_start(self, ctx: PlatformContext) -> None:
        """Record telemetry for execution start."""
        if not ctx.governance:
            return
        
        try:
            await ctx.governance.telemetry.record_telemetry(
                telemetry_data={
                    "service_id": self.service_id,
                    "intent_type": self.intent_type,
                    "execution_id": ctx.execution_id,
                    "action": "execute",
                    "status": "started",
                    "timestamp": self.clock.now_iso()
                },
                tenant_id=ctx.tenant_id
            )
        except Exception as e:
            self.logger.debug(f"Failed to record start telemetry: {e}")
    
    async def _record_telemetry_end(
        self,
        ctx: PlatformContext,
        result: Dict[str, Any],
        success: bool
    ) -> None:
        """Record telemetry for execution end."""
        if not ctx.governance:
            return
        
        try:
            await ctx.governance.telemetry.record_telemetry(
                telemetry_data={
                    "service_id": self.service_id,
                    "intent_type": self.intent_type,
                    "execution_id": ctx.execution_id,
                    "action": "execute",
                    "status": "completed" if success else "failed",
                    "artifact_count": len(result.get("artifacts", {})),
                    "event_count": len(result.get("events", [])),
                    "timestamp": self.clock.now_iso()
                },
                tenant_id=ctx.tenant_id
            )
        except Exception as e:
            self.logger.debug(f"Failed to record end telemetry: {e}")
    
    # ========================================================================
    # VALIDATION HELPERS
    # ========================================================================
    
    def validate_params(
        self,
        ctx: PlatformContext,
        required_params: List[str]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate required parameters are present.
        
        Args:
            ctx: Platform context
            required_params: List of required parameter names
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        params = ctx.intent.parameters
        
        for param in required_params:
            if param not in params:
                return False, f"Required parameter '{param}' not provided"
            if params[param] is None:
                return False, f"Required parameter '{param}' is None"
        
        return True, None
    
    def get_param(
        self,
        ctx: PlatformContext,
        param_name: str,
        default: Any = None
    ) -> Any:
        """
        Get parameter from intent.
        
        Args:
            ctx: Platform context
            param_name: Parameter name
            default: Default value if not found
        
        Returns:
            Parameter value or default
        """
        return ctx.intent.parameters.get(param_name, default)
