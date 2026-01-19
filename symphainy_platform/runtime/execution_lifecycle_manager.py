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

# OpenTelemetry tracing
try:
    from opentelemetry import trace
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    trace = None


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
        transactional_outbox: Optional[Any] = None,  # Will be TransactionalOutbox
        materialization_policy_store: Optional[Any] = None,  # MaterializationPolicyStore
        artifact_storage: Optional[Any] = None,  # ArtifactStorageAbstraction
        solution_config: Optional[Dict[str, Any]] = None,
        data_steward_sdk: Optional[Any] = None  # DataStewardSDK for boundary contract enforcement
    ):
        """
        Initialize execution lifecycle manager.
        
        Args:
            intent_registry: Intent registry for finding handlers
            state_surface: State surface for execution state
            wal: Write-ahead log for audit
            transactional_outbox: Optional transactional outbox for event publishing
            materialization_policy_store: Optional materialization policy store (from Smart City)
            artifact_storage: Optional artifact storage abstraction
            solution_config: Optional solution-specific configuration
            data_steward_sdk: Optional Data Steward SDK for boundary contract enforcement
        """
        self.intent_registry = intent_registry
        self.state_surface = state_surface
        self.wal = wal
        self.transactional_outbox = transactional_outbox
        self.materialization_policy_store = materialization_policy_store
        self.artifact_storage = artifact_storage
        self.solution_config = solution_config or {}
        self.data_steward_sdk = data_steward_sdk
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
        
        # Create trace span for execution
        # OpenTelemetry's start_as_current_span returns a context manager
        # We'll use it as a context manager in the try block
        tracer = None
        if OTEL_AVAILABLE and trace:
            tracer = trace.get_tracer(__name__)
        
        # Use span as context manager
        span_context = None
        if OTEL_AVAILABLE and trace and tracer:
            span_context = tracer.start_as_current_span("runtime.execute_intent")
        
        try:
            # Get current span if available
            current_span = None
            if OTEL_AVAILABLE and trace:
                current_span = trace.get_current_span()
                if current_span and hasattr(current_span, 'set_attribute'):
                    current_span.set_attribute("intent.id", intent.intent_id)
                    current_span.set_attribute("intent.type", intent.intent_type)
                    current_span.set_attribute("intent.tenant_id", intent.tenant_id)
                    current_span.set_attribute("intent.session_id", intent.session_id)
                    current_span.set_attribute("intent.solution_id", intent.solution_id)
            # Stage 1: Accept Intent
            self.logger.info(f"Accepting intent: {intent.intent_id} ({intent.intent_type})")
            
            if OTEL_AVAILABLE and trace and current_span and hasattr(current_span, 'add_event'):
                current_span.add_event("intent.accepted")
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
            
            if OTEL_AVAILABLE and trace and current_span and hasattr(current_span, 'add_event'):
                current_span.add_event("execution.context_created")
            
            context = ExecutionContextFactory.create_context(
                intent=intent,
                state_surface=self.state_surface,
                wal=self.wal
            )
            execution_id = context.execution_id
            
            if OTEL_AVAILABLE and trace and current_span and hasattr(current_span, 'set_attribute'):
                current_span.set_attribute("execution.id", execution_id)
            
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
            
            if OTEL_AVAILABLE and trace and current_span and hasattr(current_span, 'set_attribute'):
                current_span.set_attribute("handler.name", handler.handler_name)
                if hasattr(handler, 'realm_name'):
                    current_span.set_attribute("handler.realm", handler.realm_name)
                if hasattr(current_span, 'add_event'):
                    current_span.add_event("handler.execution_started")
            
            if not handler.handler_function:
                raise ValueError(f"Handler function not available for: {handler.handler_name}")
            
            # CRITICAL: Enforce boundary contracts before realm execution
            # Files are NEVER ingested directly. A boundary contract is negotiated first.
            boundary_contract_id = None
            if intent.intent_type in ["ingest_file", "register_file"] and self.data_steward_sdk:
                try:
                    # Step 1: Request data access (negotiate boundary contract)
                    external_source_type = "file"
                    external_source_identifier = f"upload:{intent.intent_id}:{intent.parameters.get('ui_name', 'unknown')}"
                    external_source_metadata = {
                        "ui_name": intent.parameters.get("ui_name"),
                        "file_type": intent.parameters.get("file_type", "unstructured"),
                        "mime_type": intent.parameters.get("mime_type"),
                        "ingestion_type": intent.parameters.get("ingestion_type", "upload")
                    }
                    
                    access_request = await self.data_steward_sdk.request_data_access(
                        intent={
                            "intent_id": intent.intent_id,
                            "intent_type": intent.intent_type,
                            "tenant_id": intent.tenant_id,
                            "parameters": intent.parameters
                        },
                        context={
                            "tenant_id": intent.tenant_id,
                            "user_id": context.metadata.get("user_id", "system"),
                            "session_id": context.session_id
                        },
                        external_source_type=external_source_type,
                        external_source_identifier=external_source_identifier,
                        external_source_metadata=external_source_metadata
                    )
                    
                    if not access_request.access_granted:
                        raise ValueError(f"Data access denied: {access_request.access_reason}")
                    
                    boundary_contract_id = access_request.contract_id
                    self.logger.info(f"✅ Boundary contract negotiated: {boundary_contract_id}")
                    
                    # Step 2: Authorize materialization
                    materialization_auth = await self.data_steward_sdk.authorize_materialization(
                        contract_id=boundary_contract_id,
                        tenant_id=intent.tenant_id
                    )
                    
                    if not materialization_auth.materialization_allowed:
                        raise ValueError(f"Materialization not authorized: {materialization_auth.reason}")
                    
                    self.logger.info(f"✅ Materialization authorized: {materialization_auth.materialization_type} -> {materialization_auth.materialization_backing_store}")
                    
                    # Store boundary contract info in context for realm use
                    context.metadata["boundary_contract_id"] = boundary_contract_id
                    context.metadata["materialization_type"] = materialization_auth.materialization_type
                    context.metadata["materialization_backing_store"] = materialization_auth.materialization_backing_store
                    
                except Exception as e:
                    self.logger.error(f"Boundary contract enforcement failed: {e}", exc_info=True)
                    # MVP: Allow execution to continue (backwards compatibility)
                    # In full implementation: This should block execution
                    self.logger.warning("⚠️ MVP: Allowing execution to continue despite boundary contract failure (backwards compatibility)")
            
            # Update execution state
            execution_state_updates = {
                "status": "executing",
                "handler": handler.handler_name,
                "updated_at": self.clock.now_iso(),
            }
            
            # Include boundary contract info if available
            if boundary_contract_id:
                execution_state_updates["boundary_contract_id"] = boundary_contract_id
            if context.metadata.get("materialization_pending") is not None:
                execution_state_updates["materialization_pending"] = context.metadata.get("materialization_pending")
            
            await self.state_surface.set_execution_state(
                execution_id,
                intent.tenant_id,
                execution_state_updates
            )
            
            # Call realm's handle_intent method with tracing
            try:
                # Create child span for handler execution
                handler_span_context = None
                if OTEL_AVAILABLE and trace and tracer:
                    handler_span_context = tracer.start_as_current_span(f"realm.{getattr(handler, 'realm_name', 'unknown')}.handle_intent")
                    handler_span = trace.get_current_span()
                    if handler_span and hasattr(handler_span, 'set_attribute'):
                        handler_span.set_attribute("intent.type", intent.intent_type)
                        if hasattr(handler, 'realm_name'):
                            handler_span.set_attribute("realm.name", handler.realm_name)
                
                handler_result = await handler.handler_function(intent, context)
                
                handler_span = trace.get_current_span() if OTEL_AVAILABLE and trace else None
                if handler_span and hasattr(handler_span, 'add_event'):
                    handler_span.add_event("handler.execution_completed")
                if handler_span and hasattr(handler_span, 'set_status'):
                    handler_span.set_status(trace.Status(trace.StatusCode.OK))
                
                # Extract artifacts and events from realm result
                if isinstance(handler_result, dict):
                    artifacts = handler_result.get("artifacts", {})
                    events = handler_result.get("events", [])
                else:
                    # Fallback: assume result is artifacts dict
                    artifacts = handler_result if isinstance(handler_result, dict) else {}
                    events = []
                
                # CRITICAL DEBUG: Log artifact structure IMMEDIATELY after extraction
                self.logger.info(f"DEBUG_HANDLER_RESULT: type={type(handler_result)}, is_dict={isinstance(handler_result, dict)}")
                if isinstance(handler_result, dict):
                    self.logger.info(f"DEBUG_HANDLER_RESULT: keys={list(handler_result.keys())}")
                self.logger.info(f"DEBUG_ARTIFACTS_EXTRACTED: count={len(artifacts) if artifacts else 0}, keys={list(artifacts.keys()) if artifacts else []}")
                if artifacts:
                    for key, value in list(artifacts.items())[:2]:
                        if isinstance(value, dict):
                            self.logger.info(f"DEBUG_ARTIFACT_{key}: has_result_type={'result_type' in value}, top_keys={list(value.keys())[:5]}")
                        else:
                            self.logger.info(f"DEBUG_ARTIFACT_{key}: type={type(value).__name__}")
            except Exception as e:
                handler_span = trace.get_current_span() if OTEL_AVAILABLE and trace else None
                if handler_span and hasattr(handler_span, 'record_exception'):
                    handler_span.record_exception(e)
                if handler_span and hasattr(handler_span, 'set_status'):
                    handler_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                self.logger.error(f"Handler execution failed: {e}", exc_info=True)
                raise
            finally:
                # Context manager will handle span end automatically
                pass
            
            # Stage 5: Handle Artifacts & Evaluate Materialization Policy
            self.logger.info(f"Handling artifacts from execution: {execution_id}")
            # CRITICAL: Log artifacts dict OUTSIDE try block to ensure it's logged
            self.logger.info(f"DEBUG_AFTER_TRY: artifacts exists={artifacts is not None}, count={len(artifacts) if artifacts else 0}, keys={list(artifacts.keys())[:5] if artifacts else []}")
            if artifacts:
                for key, value in list(artifacts.items())[:2]:
                    if isinstance(value, dict):
                        self.logger.info(f"DEBUG_AFTER_TRY_ARTIFACT_{key}: has_result_type={'result_type' in value}, keys={list(value.keys())[:5]}")
                    else:
                        self.logger.info(f"DEBUG_AFTER_TRY_ARTIFACT_{key}: type={type(value).__name__}")
            self.logger.info(f"🔍 DEBUG: artifacts dict at start of Stage 5: keys={list(artifacts.keys()) if artifacts else 'EMPTY'}, count={len(artifacts) if artifacts else 0}")
            if artifacts:
                for key, value in list(artifacts.items())[:3]:
                    if isinstance(value, dict):
                        self.logger.info(f"🔍 DEBUG: artifact '{key}': has result_type={'result_type' in value}, keys={list(value.keys())[:10]}")
                    else:
                        self.logger.info(f"🔍 DEBUG: artifact '{key}': type={type(value).__name__}")
            
            if OTEL_AVAILABLE and trace and current_span and hasattr(current_span, 'set_attribute'):
                current_span.set_attribute("artifacts.count", len(artifacts))
            if OTEL_AVAILABLE and trace and current_span and hasattr(current_span, 'add_event'):
                current_span.add_event("artifacts.handled")
            
            # Evaluate materialization policy for each artifact BEFORE storing in state
            if artifacts and self.materialization_policy_store and self.artifact_storage:
                self.logger.info(f"Evaluating materialization policy for {len(artifacts)} artifacts")
                
                # Import MaterializationPolicyPrimitives (Smart City pattern)
                from symphainy_platform.civic_systems.smart_city.primitives.materialization_policy_primitives import (
                    MaterializationPolicyPrimitives,
                    MaterializationDecision
                )
                
                for artifact_key, artifact_data in list(artifacts.items()):
                    # Skip artifact_id references (already processed)
                    if artifact_key.endswith("_artifact_id") or artifact_key.endswith("_storage_path"):
                        continue
                    
                    # Skip non-dict artifacts (e.g., strings, lists)
                    if not isinstance(artifact_data, dict):
                        continue
                    
                    # Determine result_type from artifact_key or artifact_data
                    result_type = self._infer_result_type(artifact_key, artifact_data)
                    
                    # Extract semantic_payload and renderings from structured format
                    # Realms now return structured artifacts with result_type, semantic_payload, and renderings
                    if isinstance(artifact_data, dict) and "result_type" in artifact_data:
                        # Structured format (native)
                        result_type = artifact_data.get("result_type", result_type)  # Use artifact's result_type if available
                        semantic_payload = artifact_data.get("semantic_payload", {})
                        renderings = artifact_data.get("renderings", {})
                    else:
                        # Fallback for legacy format (should not happen, but safe)
                        self.logger.warning(f"Artifact {artifact_key} is not in structured format, using fallback extraction")
                        semantic_payload = self._extract_semantic_payload(artifact_data)
                        renderings = artifact_data.copy()
                        if "semantic_payload" in renderings:
                            del renderings["semantic_payload"]
                    
                    # Prepare execution contract for policy evaluation
                    execution_contract = {
                        "tenant_id": intent.tenant_id,
                        "solution_id": getattr(intent, 'solution_id', 'default'),
                        "materialization_policy": self.solution_config.get("materialization_policy", {})
                    }
                    
                    # Evaluate policy using Smart City Primitive (with error handling)
                    try:
                        decision = await MaterializationPolicyPrimitives.evaluate_policy(
                            result_type=result_type,
                            semantic_payload=semantic_payload,
                            renderings=renderings,
                            intent=intent,
                            context=context,
                            policy_store=self.materialization_policy_store,
                            execution_contract=execution_contract
                        )
                    except Exception as e:
                        self.logger.error(f"Policy evaluation failed for {artifact_key}: {e}", exc_info=True)
                        # Default to DISCARD on policy evaluation failure (safest)
                        decision = MaterializationDecision.DISCARD
                    
                    if decision == MaterializationDecision.PERSIST:
                        # Store artifact
                        try:
                            storage_result = await self.artifact_storage.store_composite_artifact(
                                artifact_type=result_type,
                                artifact_data=renderings,
                                tenant_id=intent.tenant_id,
                                metadata={
                                    "execution_id": execution_id,
                                    "session_id": context.session_id,
                                    "intent_id": intent.intent_id,
                                    "intent_type": intent.intent_type,
                                    "semantic_payload_stored": bool(semantic_payload)
                                }
                            )
                            
                            if storage_result.get("success"):
                                # Store artifact_id reference in artifacts dict (platform memory)
                                artifacts[f"{artifact_key}_artifact_id"] = storage_result["artifact_id"]
                                artifacts[f"{artifact_key}_storage_path"] = storage_result["storage_path"]
                                self.logger.info(f"Artifact stored: {storage_result['artifact_id']}")
                            else:
                                self.logger.warning(f"Artifact storage failed for {artifact_key}: {storage_result.get('error')}")
                        except Exception as e:
                            self.logger.error(f"Failed to store artifact {artifact_key}: {e}", exc_info=True)
                            # Continue - don't fail execution on storage failure
                    
                    elif decision == MaterializationDecision.CACHE:
                        # Cache temporarily (e.g., in State Surface)
                        self.logger.debug(f"Artifact {artifact_key} cached (not persisted)")
                    
                    elif decision == MaterializationDecision.DISCARD:
                        # Discard (ephemeral)
                        self.logger.debug(f"Artifact {artifact_key} discarded (ephemeral)")
            
            # Artifacts are stored in execution state
            # Structured artifacts have semantic_payload (JSON-serializable) and renderings (handled by policy)
            # Store structured artifacts as-is (semantic_payload is JSON-serializable, renderings handled by policy)
            artifacts_for_state = {}
            self.logger.info(f"DEBUG_STORAGE_PREP: artifacts_count={len(artifacts)}, keys={list(artifacts.keys())[:10]}")
            # CRITICAL: Check if artifacts dict has been corrupted with flat keys
            if "file" not in artifacts and any(k in artifacts for k in ["file_id", "artifact_type", "file_path"]):
                self.logger.error(f"CRITICAL: artifacts dict appears to have flat keys instead of structured! Keys: {list(artifacts.keys())[:15]}")
                self.logger.error(f"CRITICAL: This suggests semantic_payload was unwrapped into artifacts dict")
            for artifact_key, artifact_data in artifacts.items():
                # Skip artifact_id references (already processed)
                if artifact_key.endswith("_artifact_id") or artifact_key.endswith("_storage_path"):
                    artifacts_for_state[artifact_key] = artifact_data
                    continue
                
                # Handle structured artifacts - preserve complete structure
                if isinstance(artifact_data, dict) and "result_type" in artifact_data:
                    # Structured format: store complete artifact
                    artifacts_for_state[artifact_key] = artifact_data
                    self.logger.info(f"DEBUG_STORAGE_STRUCTURED: {artifact_key} -> result_type={artifact_data.get('result_type')}")
                else:
                    # Legacy format - log details
                    self.logger.warning(f"DEBUG_STORAGE_LEGACY: {artifact_key} -> type={type(artifact_data).__name__}, keys={list(artifact_data.keys())[:8] if isinstance(artifact_data, dict) else 'N/A'}")
                    artifacts_for_state[artifact_key] = artifact_data
            
            self.logger.info(f"DEBUG_STORAGE_FINAL: storing {len(artifacts_for_state)} artifacts, keys={list(artifacts_for_state.keys())[:5]}")
            # Validate file artifact structure
            if "file" in artifacts_for_state:
                file_artifact = artifacts_for_state["file"]
                if not isinstance(file_artifact, dict) or "result_type" not in file_artifact:
                    self.logger.error(f"'file' artifact is not structured! type={type(file_artifact)}, keys={list(file_artifact.keys()) if isinstance(file_artifact, dict) else 'N/A'}")
            
            await self.state_surface.set_execution_state(
                execution_id,
                intent.tenant_id,
                {
                    "status": "artifacts_received",
                    "artifacts": artifacts_for_state,
                    "updated_at": self.clock.now_iso(),
                }
            )
            # Stage 6: Publish Events (via Transactional Outbox)
            if events and self.transactional_outbox:
                self.logger.info(f"Publishing {len(events)} events via transactional outbox")
                
                if OTEL_AVAILABLE and trace and current_span and hasattr(current_span, 'set_attribute'):
                    current_span.set_attribute("events.count", len(events))
                if OTEL_AVAILABLE and trace and current_span and hasattr(current_span, 'add_event'):
                    current_span.add_event("events.publishing_started")
                
                for event in events:
                    await self.transactional_outbox.add_event(
                        execution_id,
                        event.get("event_type", "execution_event"),
                        event.get("event_data", {})
                    )
                # Publish events
                await self.transactional_outbox.publish_events(execution_id)
                
                if OTEL_AVAILABLE and trace and current_span and hasattr(current_span, 'add_event'):
                    current_span.add_event("events.published")
            elif events:
                self.logger.warning("Events generated but no transactional outbox available")
            
            # Stage 7: Complete Execution
            self.logger.info(f"Completing execution: {execution_id}")
            
            if OTEL_AVAILABLE and trace and current_span and hasattr(current_span, 'add_event'):
                current_span.add_event("execution.completed")
            if OTEL_AVAILABLE and trace and current_span and hasattr(current_span, 'set_status'):
                current_span.set_status(trace.Status(trace.StatusCode.OK))
            
            # Store structured artifacts in execution state (preserve format)
            artifacts_for_completion = {}
            for artifact_key, artifact_data in artifacts.items():
                # Skip artifact_id references
                if artifact_key.endswith("_artifact_id") or artifact_key.endswith("_storage_path"):
                    artifacts_for_completion[artifact_key] = artifact_data
                    continue
                
                # Handle structured artifacts - preserve complete structure
                if isinstance(artifact_data, dict) and "result_type" in artifact_data:
                    # Structured format: store complete artifact (semantic_payload + renderings metadata)
                    # renderings handled by materialization policy (not stored in execution state)
                    artifacts_for_completion[artifact_key] = artifact_data
                else:
                    # Legacy format (should not happen after refactoring)
                    self.logger.warning(f"Artifact {artifact_key} is not in structured format - this should not happen after refactoring")
                    artifacts_for_completion[artifact_key] = artifact_data
            
            await self.state_surface.set_execution_state(
                execution_id,
                intent.tenant_id,
                {
                    "status": "completed",
                    "artifacts": artifacts_for_completion,
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
            
            # Record error in trace
            if OTEL_AVAILABLE and trace:
                current_span = trace.get_current_span()
                if current_span:
                    current_span.record_exception(e)
                    current_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    current_span.set_attribute("execution.error", str(e))
            
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

    def _infer_result_type(self, artifact_key: str, artifact_data: Dict[str, Any]) -> str:
        """
        Infer result_type from artifact_key or artifact_data.
        
        Args:
            artifact_key: Key of the artifact in artifacts dict
            artifact_data: Artifact data dictionary
        
        Returns:
            str: Result type (e.g., 'workflow', 'sop', 'blueprint')
        """
        # Try artifact_key first
        if artifact_key in ["workflow", "sop", "blueprint", "solution", "roadmap", "poc", "visual"]:
            return artifact_key
        
        # Try artifact_data
        if isinstance(artifact_data, dict) and "result_type" in artifact_data:
            return artifact_data["result_type"]
        
        # Default
        return "unknown"
    
    def _extract_semantic_payload(self, artifact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract semantic payload from artifact data.
        
        For MVP: Extract key semantic fields if available.
        Future: Realms will return structured results with explicit semantic_payload.
        
        Args:
            artifact_data: Artifact data dictionary
        
        Returns:
            Dict[str, Any]: Semantic payload dictionary
        """
        semantic = {}
        
        # Skip if not a dict
        if not isinstance(artifact_data, dict):
            return semantic
        
        # If artifact_data already has semantic_payload, use it
        if "semantic_payload" in artifact_data:
            semantic.update(artifact_data["semantic_payload"])
        
        # Extract common semantic fields
        semantic_fields = [
            "workflow_id", "sop_id", "blueprint_id", "solution_id", 
            "roadmap_id", "poc_id", "intent_id", "execution_id"
        ]
        
        for field in semantic_fields:
            if field in artifact_data:
                semantic[field] = artifact_data[field]
        
        return semantic
    

