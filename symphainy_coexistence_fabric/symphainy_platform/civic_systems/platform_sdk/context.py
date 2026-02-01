"""
Platform Context - The Unified Execution Context (ctx)

PlatformContext is the 'ctx' object that intent services receive.
It provides access to all platform capabilities through four services.

Architecture:
    - ctx.platform    → Capability-oriented operations
    - ctx.governance  → Smart City SDKs (9 roles)
    - ctx.reasoning   → Agentic (LLM, agents)
    - ctx.experience  → Experience metadata
    
Plus Runtime-provided resources:
    - ctx.state_surface → State (Runtime owns)
    - ctx.wal           → Write-ahead log (Runtime owns)
    - ctx.artifacts     → Artifact registry (Runtime owns)
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime

from utilities import get_logger, get_clock

if TYPE_CHECKING:
    from symphainy_platform.runtime.intent_model import Intent
    from symphainy_platform.runtime.state_surface import StateSurface
    from symphainy_platform.runtime.wal import WriteAheadLog
    from symphainy_platform.runtime.artifact_registry import ArtifactRegistry
    from .services.governance_service import GovernanceService
    from .services.reasoning_service import ReasoningService
    from .services.platform_service import PlatformService


@dataclass
class PlatformContext:
    """
    Unified execution context for intent services.
    
    This is the 'ctx' object that capability implementations receive.
    It provides governed access to all platform resources.
    
    Attributes:
        execution_id: Unique execution identifier
        intent: The intent being executed
        tenant_id: Tenant identifier (for isolation)
        session_id: Session identifier
        solution_id: Solution identifier
        
        state_surface: Runtime state management (Runtime owns)
        wal: Write-ahead log (Runtime owns)
        artifacts: Artifact registry (Runtime owns)
        
        platform: Capability-oriented operations (parse, analyze, visualize, etc.)
        governance: Smart City SDKs (all 9 roles)
        reasoning: Agentic (LLM, agents)
        experience: Experience metadata
        
        metadata: Additional execution metadata
        created_at: Context creation timestamp
    """
    # Execution identity
    execution_id: str
    intent: "Intent"
    tenant_id: str
    session_id: str
    solution_id: str
    
    # Runtime-provided resources (Runtime owns these)
    state_surface: Optional["StateSurface"] = None
    wal: Optional["WriteAheadLog"] = None
    artifacts: Optional["ArtifactRegistry"] = None
    
    # Four SDK services
    platform: Optional["PlatformService"] = None
    governance: Optional["GovernanceService"] = None
    reasoning: Optional["ReasoningService"] = None
    experience: Optional[Dict[str, Any]] = None  # Narrow surface, just metadata for now
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: get_clock().now_utc())
    
    def __post_init__(self):
        """Validate context after initialization."""
        self._logger = get_logger("PlatformContext")
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate the platform context.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.execution_id:
            return False, "execution_id is required"
        if not self.intent:
            return False, "intent is required"
        if not self.tenant_id:
            return False, "tenant_id is required"
        if not self.session_id:
            return False, "session_id is required"
        if not self.solution_id:
            return False, "solution_id is required"
        
        # Validate intent matches context
        if self.tenant_id != self.intent.tenant_id:
            return False, "tenant_id mismatch between context and intent"
        if self.session_id != self.intent.session_id:
            return False, "session_id mismatch between context and intent"
        
        return True, None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary (for logging/debugging)."""
        return {
            "execution_id": self.execution_id,
            "intent_type": self.intent.intent_type if self.intent else None,
            "tenant_id": self.tenant_id,
            "session_id": self.session_id,
            "solution_id": self.solution_id,
            "has_state_surface": self.state_surface is not None,
            "has_wal": self.wal is not None,
            "has_artifacts": self.artifacts is not None,
            "has_platform": self.platform is not None,
            "has_governance": self.governance is not None,
            "has_reasoning": self.reasoning is not None,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }
    
    def to_execution_context(self) -> Any:
        """
        Create an ExecutionContext from this PlatformContext.
        
        This maintains the audit trail when calling library services that
        require ExecutionContext. The execution_id and intent are preserved.
        
        Returns:
            ExecutionContext with same identity as this PlatformContext
        
        Note:
            DISPOSABLE WRAPPER PATTERN: When Platform SDK wrapper methods need to
            call library services that require ExecutionContext, they should use
            ctx.to_execution_context() to preserve the audit trail, rather than
            creating a new context with a different execution_id.
        """
        from symphainy_platform.runtime.execution_context import ExecutionContext
        
        return ExecutionContext(
            execution_id=self.execution_id,
            intent=self.intent,
            tenant_id=self.tenant_id,
            session_id=self.session_id,
            solution_id=self.solution_id,
            state_surface=self.state_surface,
            wal=self.wal,
            metadata=self.metadata
        )


class PlatformContextFactory:
    """
    Factory for creating PlatformContext instances.
    
    Builds the full ctx object from Runtime execution context,
    wiring up all four SDK services.
    """
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional["StateSurface"] = None,
        wal: Optional["WriteAheadLog"] = None,
        artifact_registry: Optional["ArtifactRegistry"] = None,
        governance_service: Optional["GovernanceService"] = None,
        reasoning_service: Optional["ReasoningService"] = None,
        platform_service: Optional["PlatformService"] = None,
    ):
        """
        Initialize the factory with platform resources.
        
        Args:
            public_works: Public Works foundation service
            state_surface: Runtime state surface
            wal: Write-ahead log
            artifact_registry: Artifact registry
            governance_service: Pre-built governance service (optional)
            reasoning_service: Pre-built reasoning service (optional)
            platform_service: Pre-built platform service (optional)
        """
        self.public_works = public_works
        self.state_surface = state_surface
        self.wal = wal
        self.artifact_registry = artifact_registry
        self._governance_service = governance_service
        self._reasoning_service = reasoning_service
        self._platform_service = platform_service
        self._logger = get_logger("PlatformContextFactory")
        self._clock = get_clock()
    
    def create_context(
        self,
        intent: "Intent",
        execution_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PlatformContext:
        """
        Create a PlatformContext for intent execution.
        
        Args:
            intent: The intent being executed
            execution_id: Optional execution ID (generated if not provided)
            metadata: Optional execution metadata
        
        Returns:
            Fully-wired PlatformContext
        """
        from utilities import generate_event_id
        
        if execution_id is None:
            execution_id = generate_event_id()
        
        # Build services if not pre-built
        governance = self._governance_service or self._build_governance_service()
        reasoning = self._reasoning_service or self._build_reasoning_service()
        platform = self._platform_service or self._build_platform_service()
        
        # Create context
        ctx = PlatformContext(
            execution_id=execution_id,
            intent=intent,
            tenant_id=intent.tenant_id,
            session_id=intent.session_id,
            solution_id=intent.solution_id,
            state_surface=self.state_surface,
            wal=self.wal,
            artifacts=self.artifact_registry,
            platform=platform,
            governance=governance,
            reasoning=reasoning,
            experience={},  # Narrow surface for now
            metadata=metadata or {},
            created_at=self._clock.now_utc(),
        )
        
        # Validate
        is_valid, error = ctx.validate()
        if not is_valid:
            raise ValueError(f"Invalid platform context: {error}")
        
        self._logger.debug(f"Created PlatformContext: {execution_id}")
        return ctx
    
    def _build_governance_service(self) -> Optional["GovernanceService"]:
        """Build GovernanceService from available resources."""
        if not self.public_works:
            raise RuntimeError(
                "Public Works not wired; cannot build GovernanceService. Platform contract §8A."
            )
        
        try:
            from .services.governance_service import GovernanceService
            return GovernanceService(public_works=self.public_works)
        except Exception as e:
            self._logger.error(f"Failed to build GovernanceService: {e}")
            return None
    
    def _build_reasoning_service(self) -> Optional["ReasoningService"]:
        """Build ReasoningService from available resources."""
        if not self.public_works:
            raise RuntimeError(
                "Public Works not wired; cannot build ReasoningService. Platform contract §8A."
            )
        
        try:
            from .services.reasoning_service import ReasoningService
            return ReasoningService(public_works=self.public_works)
        except Exception as e:
            self._logger.error(f"Failed to build ReasoningService: {e}")
            return None
    
    def _build_platform_service(self) -> Optional["PlatformService"]:
        """Build PlatformService from available resources."""
        if not self.public_works:
            raise RuntimeError(
                "Public Works not wired; cannot build PlatformService. Platform contract §8A."
            )
        
        try:
            from .services.platform_service import PlatformService
            return PlatformService(
                public_works=self.public_works,
                state_surface=self.state_surface
            )
        except Exception as e:
            self._logger.error(f"Failed to build PlatformService: {e}")
            return None
    
    @classmethod
    def from_runtime_context(
        cls,
        execution_context: Any,
        public_works: Optional[Any] = None
    ) -> PlatformContext:
        """
        Create PlatformContext from existing Runtime ExecutionContext.
        
        This is for backward compatibility during migration.
        
        Args:
            execution_context: Runtime ExecutionContext
            public_works: Public Works foundation service
        
        Returns:
            PlatformContext
        """
        factory = cls(
            public_works=public_works,
            state_surface=getattr(execution_context, 'state_surface', None),
            wal=getattr(execution_context, 'wal', None),
        )
        
        return factory.create_context(
            intent=execution_context.intent,
            execution_id=execution_context.execution_id,
            metadata=getattr(execution_context, 'metadata', {})
        )
