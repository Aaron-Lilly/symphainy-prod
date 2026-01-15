"""
Runtime Execution Engine

The single execution authority for the platform.

Owns:
- Intent acceptance and validation
- Execution lifecycle
- Session & tenant context
- Write-ahead log (WAL)
- Saga orchestration
- Retries & failure recovery
- Deterministic replay
- State transitions
- Runtime-native data cognition (Data Brain)
"""

# Core Runtime Components
from .intent_model import Intent, IntentType, IntentFactory
from .intent_registry import IntentRegistry, IntentHandler
from .execution_context import ExecutionContext, ExecutionContextFactory
from .execution_lifecycle_manager import ExecutionLifecycleManager, ExecutionResult
from .transactional_outbox import TransactionalOutbox, OutboxEvent
from .data_brain import DataBrain, DataReference, ProvenanceEntry
from .state_surface import StateSurface
from .wal import WriteAheadLog, WALEvent, WALEventType

__all__ = [
    # Intent Model
    "Intent",
    "IntentType",
    "IntentFactory",
    # Intent Registry
    "IntentRegistry",
    "IntentHandler",
    # Execution Context
    "ExecutionContext",
    "ExecutionContextFactory",
    # Execution Lifecycle
    "ExecutionLifecycleManager",
    "ExecutionResult",
    # Transactional Outbox
    "TransactionalOutbox",
    "OutboxEvent",
    # Data Brain
    "DataBrain",
    "DataReference",
    "ProvenanceEntry",
    # State Surface
    "StateSurface",
    # WAL
    "WriteAheadLog",
    "WALEvent",
    "WALEventType",
]
