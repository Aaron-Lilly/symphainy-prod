"""
Execution Lifecycle Manager - Orchestrates Full Execution Flow

Orchestrates the complete execution lifecycle from intent acceptance to completion.

WHAT (Runtime Role): I orchestrate the full execution flow
HOW (Runtime Implementation): I coordinate intent acceptance, execution, artifact handling, and event publishing

Key Principle: Runtime owns execution. This manager ensures every step is
governed, logged, and recoverable.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from utilities import get_logger, get_clock
from .intent_model import Intent, IntentFactory
from .execution_context import ExecutionContext, ExecutionContextFactory
from .intent_registry import IntentRegistry, IntentHandler
from .wal import WriteAheadLog, WALEventType
from .state_surface import StateSurface


@dataclass
class ExecutionResult:
    """Execution result."""
    execution_id: str
    success: bool
    artifacts: Dict[str, Any] = None
    events: List[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.artifacts is None:
            self.artifacts = {}
        if self.events is None:
            self.events = []
        if self.metadata is None:
            self.metadata = {}


class ExecutionLifecycleManager:
    """
    Orchestrates the complete execution lifecycle.
    
    Manages:
    - Intent acceptance and validation
    - Execution context creation
    - Intent execution via domain services
    - Artifact handling
    - Event publishing (via transactional outbox)
    - Execution completion
    """
    
    def __init__(
        self,
        intent_registry: IntentRegistry,
        state_surface: StateSurface,
        wal: WriteAheadLog,
        transactional_outbox: Optional[Any] = None  # Will be TransactionalOutbox
    ):
        """
        Initialize execution lifecycle manager.
        
        Args:
            intent_registry: Intent registry for finding handlers
            state_surface: State surface for execution state
            wal: Write-ahead log for audit
            transactional_outbox: Optional transactional outbox for event publishing
        """
        self.intent_registry = intent_registry
        self.state_surface = state_surface
        self.wal = wal
        self.transactional_outbox = transactional_outbox
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
    
    async def execute(self, intent: Intent) -> ExecutionResult:
        """
        Execute an intent through the full lifecycle.
        
        Args:
            intent: The intent to execute
        
        Returns:
            Execution result
        """
        execution_id = None
        
        try:
            # Stage 1: Accept Intent
            self.logger.info(f"Accepting intent: {intent.intent_id} ({intent.intent_type})")
            is_valid, error = intent.validate()
            if not is_valid:
                raise ValueError(f"Invalid intent: {error}")
            
            # Log intent received
            await self.wal.append(
                WALEventType.INTENT_RECEIVED,
                intent.tenant_id,
                {
                    "intent_id": intent.intent_id,
                    "intent_type": intent.intent_type,
                    "session_id": intent.session_id,
                    "solution_id": intent.solution_id,
                }
            )
            
            # Stage 2: Create Execution Context
            self.logger.info(f"Creating execution context for intent: {intent.intent_id}")
            context = ExecutionContextFactory.create_context(
                intent=intent,
                state_surface=self.state_surface,
                wal=self.wal
            )
            execution_id = context.execution_id
            
            # Store execution state
            await self.state_surface.set_execution_state(
                execution_id,
                intent.tenant_id,
                {
                    "status": "created",
                    "intent": intent.to_dict(),
                    "created_at": self.clock.now_iso(),
                }
            )
            
            # Log execution started
            await self.wal.append(
                WALEventType.EXECUTION_STARTED,
                intent.tenant_id,
                {
                    "execution_id": execution_id,
                    "intent_id": intent.intent_id,
                    "intent_type": intent.intent_type,
                }
            )
            
            # Stage 3: Find Intent Handler
            handlers = self.intent_registry.get_intent_handlers(intent.intent_type)
            if not handlers:
                raise ValueError(f"No handler found for intent type: {intent.intent_type}")
            
            # Use first handler (can be enhanced to support multiple handlers)
            handler = handlers[0]
            self.logger.info(f"Found handler: {handler.handler_name} for intent: {intent.intent_type}")
            
            # Stage 3.5: Execute Intent Handler
            # Handler is a realm's handle_intent method
            self.logger.info(f"Executing intent via handler: {handler.handler_name}")
            
            if not handler.handler_function:
                raise ValueError(f"Handler function not available for: {handler.handler_name}")
            
            # Update execution state
            await self.state_surface.set_execution_state(
                execution_id,
                intent.tenant_id,
                {
                    "status": "executing",
                    "handler": handler.handler_name,
                    "updated_at": self.clock.now_iso(),
                }
            )
            
            # Call realm's handle_intent method
            try:
                handler_result = await handler.handler_function(intent, context)
                
                # Extract artifacts and events from realm result
                if isinstance(handler_result, dict):
                    artifacts = handler_result.get("artifacts", {})
                    events = handler_result.get("events", [])
                else:
                    # Fallback: assume result is artifacts dict
                    artifacts = handler_result if isinstance(handler_result, dict) else {}
                    events = []
            except Exception as e:
                self.logger.error(f"Handler execution failed: {e}", exc_info=True)
                raise
            
            # Stage 5: Handle Artifacts
            self.logger.info(f"Handling artifacts from execution: {execution_id}")
            # Artifacts are stored in execution state (domain services return them)
            await self.state_surface.set_execution_state(
                execution_id,
                intent.tenant_id,
                {
                    "status": "artifacts_received",
                    "artifacts": artifacts,
                    "updated_at": self.clock.now_iso(),
                }
            )
            
            # Stage 6: Publish Events (via Transactional Outbox)
            if events and self.transactional_outbox:
                self.logger.info(f"Publishing {len(events)} events via transactional outbox")
                for event in events:
                    await self.transactional_outbox.add_event(
                        execution_id,
                        event.get("event_type", "execution_event"),
                        event.get("event_data", {})
                    )
                # Publish events
                await self.transactional_outbox.publish_events(execution_id)
            elif events:
                self.logger.warning("Events generated but no transactional outbox available")
            
            # Stage 7: Complete Execution
            self.logger.info(f"Completing execution: {execution_id}")
            await self.state_surface.set_execution_state(
                execution_id,
                intent.tenant_id,
                {
                    "status": "completed",
                    "artifacts": artifacts,
                    "completed_at": self.clock.now_iso(),
                }
            )
            
            # Log execution completed
            await self.wal.append(
                WALEventType.EXECUTION_COMPLETED,
                intent.tenant_id,
                {
                    "execution_id": execution_id,
                    "intent_id": intent.intent_id,
                    "artifacts_count": len(artifacts),
                    "events_count": len(events),
                }
            )
            
            return ExecutionResult(
                execution_id=execution_id,
                success=True,
                artifacts=artifacts,
                events=events,
                metadata={"handler": handler.handler_name}
            )
            
        except Exception as e:
            self.logger.error(f"Execution failed: {e}", exc_info=True)
            
            # Log execution failed
            if execution_id:
                await self.wal.append(
                    WALEventType.EXECUTION_FAILED,
                    intent.tenant_id,
                    {
                        "execution_id": execution_id,
                        "intent_id": intent.intent_id,
                        "error": str(e),
                    }
                )
                
                # Update execution state
                await self.state_surface.set_execution_state(
                    execution_id,
                    intent.tenant_id,
                    {
                        "status": "failed",
                        "error": str(e),
                        "failed_at": self.clock.now_iso(),
                    }
                )
            
            return ExecutionResult(
                execution_id=execution_id or "unknown",
                success=False,
                error=str(e),
                artifacts={},
                events=[],
            )
    
    async def accept_intent(self, intent: Intent) -> bool:
        """
        Accept and validate an intent (without executing).
        
        Args:
            intent: The intent to accept
        
        Returns:
            True if intent accepted
        """
        is_valid, error = intent.validate()
        if not is_valid:
            self.logger.error(f"Intent validation failed: {error}")
            return False
        
        # Log intent received
        await self.wal.append(
            WALEventType.INTENT_RECEIVED,
            intent.tenant_id,
            {
                "intent_id": intent.intent_id,
                "intent_type": intent.intent_type,
                "session_id": intent.session_id,
                "solution_id": intent.solution_id,
            }
        )
        
        return True
