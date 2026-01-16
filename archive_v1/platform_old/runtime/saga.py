"""
Saga Skeleton - Async Workflow Coordination

SagaCoordinator manages saga lifecycle.
SagaStep interface for saga steps.
SagaState tracked via state surface.

No retries yet. No compensation logic yet. Just structure.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional

from utilities import generate_saga_id, get_clock


class SagaState(str, Enum):
    """Saga state enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


@dataclass
class SagaStep:
    """Saga step structure."""
    step_id: str
    step_name: str
    step_type: str  # e.g., "realm_action", "agent_reasoning"
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Optional[Dict[str, Any]] = None
    status: str = "pending"  # "pending", "running", "completed", "failed"
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


def _get_now():
    """Get current time using clock abstraction."""
    return get_clock().now()


@dataclass
class Saga:
    """Saga structure."""
    saga_id: str
    tenant_id: str
    session_id: str
    saga_name: str
    state: SagaState
    steps: List[SagaStep] = field(default_factory=list)
    created_at: datetime = field(default_factory=_get_now)
    updated_at: datetime = field(default_factory=_get_now)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert saga to dictionary."""
        return {
            "saga_id": self.saga_id,
            "tenant_id": self.tenant_id,
            "session_id": self.session_id,
            "saga_name": self.saga_name,
            "state": self.state.value,
            "steps": [
                {
                    "step_id": s.step_id,
                    "step_name": s.step_name,
                    "step_type": s.step_type,
                    "inputs": s.inputs,
                    "outputs": s.outputs,
                    "status": s.status,
                    "error": s.error,
                    "started_at": s.started_at.isoformat() if s.started_at else None,
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                }
                for s in self.steps
            ],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "context": self.context,
        }


class SagaStepInterface(ABC):
    """
    Interface for saga steps.
    
    Saga steps are executed by the Runtime Plane.
    Steps register themselves, Runtime executes them.
    """
    
    @abstractmethod
    async def execute(
        self,
        inputs: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute saga step.
        
        Args:
            inputs: Step inputs
            context: Execution context
        
        Returns:
            Step outputs
        
        Raises:
            Exception: If step fails
        """
        pass
    
    @abstractmethod
    def get_step_name(self) -> str:
        """Get step name."""
        pass
    
    @abstractmethod
    def get_step_type(self) -> str:
        """Get step type."""
        pass


class SagaCoordinator:
    """
    Saga coordinator.
    
    Manages saga lifecycle and state.
    Tracks saga state via state surface.
    """
    
    def __init__(self, state_surface: Any):
        """
        Initialize saga coordinator.
        
        Args:
            state_surface: State surface for saga state storage
        """
        self.state_surface = state_surface
        self._active_sagas: Dict[str, Saga] = {}
    
    async def create_saga(
        self,
        tenant_id: str,
        session_id: str,
        saga_name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Saga:
        """
        Create a new saga.
        
        Args:
            tenant_id: Tenant identifier
            session_id: Session identifier
            saga_name: Saga name
            context: Optional saga context
        
        Returns:
            Created saga
        """
        clock = get_clock()
        now = clock.now()
        saga = Saga(
            saga_id=generate_saga_id(),
            tenant_id=tenant_id,
            session_id=session_id,
            saga_name=saga_name,
            state=SagaState.PENDING,
            steps=[],
            created_at=now,
            updated_at=now,
            context=context or {}
        )
        
        self._active_sagas[saga.saga_id] = saga
        
        # Store in state surface
        await self.state_surface.set_execution_state(
            execution_id=saga.saga_id,
            tenant_id=tenant_id,
            state=saga.to_dict()
        )
        
        return saga
    
    async def get_saga(
        self,
        saga_id: str,
        tenant_id: str
    ) -> Optional[Saga]:
        """
        Get saga by ID.
        
        Args:
            saga_id: Saga identifier
            tenant_id: Tenant identifier
        
        Returns:
            Saga or None if not found
        """
        # Check active sagas first
        if saga_id in self._active_sagas:
            saga = self._active_sagas[saga_id]
            if saga.tenant_id == tenant_id:
                return saga
        
        # Load from state surface
        state = await self.state_surface.get_execution_state(saga_id, tenant_id)
        if state:
            # Reconstruct saga from state
            saga = Saga(
                saga_id=state["saga_id"],
                tenant_id=state["tenant_id"],
                session_id=state["session_id"],
                saga_name=state["saga_name"],
                state=SagaState(state["state"]),
                steps=[],  # Steps would be reconstructed from state
                created_at=datetime.fromisoformat(state["created_at"]),
                updated_at=datetime.fromisoformat(state["updated_at"]),
                context=state.get("context", {})
            )
            return saga
        
        return None
    
    async def add_step(
        self,
        saga_id: str,
        tenant_id: str,
        step_name: str,
        step_type: str,
        inputs: Dict[str, Any]
    ) -> SagaStep:
        """
        Add step to saga.
        
        Args:
            saga_id: Saga identifier
            tenant_id: Tenant identifier
            step_name: Step name
            step_type: Step type
            inputs: Step inputs
        
        Returns:
            Created saga step
        """
        saga = await self.get_saga(saga_id, tenant_id)
        if not saga:
            raise ValueError(f"Saga {saga_id} not found")
        
        from utilities import generate_execution_id
        
        step = SagaStep(
            step_id=generate_execution_id(),
            step_name=step_name,
            step_type=step_type,
            inputs=inputs,
            status="pending"
        )
        
        saga.steps.append(step)
        saga.updated_at = get_clock().now()
        
        # Update state surface
        await self.state_surface.set_execution_state(
            execution_id=saga_id,
            tenant_id=tenant_id,
            state=saga.to_dict()
        )
        
        return step
    
    async def update_saga_state(
        self,
        saga_id: str,
        tenant_id: str,
        state: SagaState
    ) -> bool:
        """
        Update saga state.
        
        Args:
            saga_id: Saga identifier
            tenant_id: Tenant identifier
            state: New state
        
        Returns:
            True if successful
        """
        saga = await self.get_saga(saga_id, tenant_id)
        if not saga:
            return False
        
        saga.state = state
        saga.updated_at = get_clock().now()
        
        # Update state surface
        await self.state_surface.set_execution_state(
            execution_id=saga_id,
            tenant_id=tenant_id,
            state=saga.to_dict()
        )
        
        return True
