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
from datetime import datetime

from utilities import get_logger, get_clock, generate_event_id
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
        
        # Debug: Log data_steward_sdk state at initialization
        self.logger.info(f"🔍 ExecutionLifecycleManager.__init__: data_steward_sdk type={type(data_steward_sdk)}, is None={data_steward_sdk is None}")
    
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
            self.logger.info(f"🔍 BOUNDARY_CONTRACT_CHECK: intent_type={intent.intent_type}, has_data_steward_sdk={hasattr(self, 'data_steward_sdk') and self.data_steward_sdk is not None}")
            boundary_contract_id = None
            
            # Debug: Always log for ingest_file to verify code path
            self.logger.info(f"🔍 DEBUG: Processing intent_type={intent.intent_type}, data_steward_sdk={self.data_steward_sdk is not None}")
            
            # Debug: Check if we're processing ingest_file
            if intent.intent_type == "ingest_file":
                self.logger.info(f"🔍 Processing ingest_file intent - data_steward_sdk available: {self.data_steward_sdk is not None}")
            
            # Phase 1: For ingest_file - always create boundary contract (permissive MVP if needed)
            if intent.intent_type == "ingest_file":
                boundary_contract_id = None
                
                # Try to get boundary contract via Data Steward SDK first
                if self.data_steward_sdk:
                    try:
                        self.logger.info(f"🔍 Enforcing boundary contract for ingest_file intent (data_steward_sdk available)")
                        # Step 1: Request data access (negotiate boundary contract, pending materialization)
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
                        
                        if access_request.access_granted:
                            boundary_contract_id = access_request.contract_id
                            self.logger.info(f"✅ Boundary contract negotiated: {boundary_contract_id} (materialization pending)")
                        else:
                            # Access denied - create permissive MVP contract as fallback
                            self.logger.warning(f"⚠️ Data access denied: {access_request.access_reason}, creating permissive MVP contract")
                            boundary_contract_id = await self._create_permissive_mvp_contract(intent, context)
                        
                    except Exception as e:
                        # Boundary contract negotiation failed - create permissive MVP contract
                        self.logger.warning(f"⚠️ Boundary contract negotiation failed: {e}, creating permissive MVP contract")
                        boundary_contract_id = await self._create_permissive_mvp_contract(intent, context)
                else:
                    # No Data Steward SDK - create permissive MVP contract
                    self.logger.info("⚠️ Data Steward SDK not available - creating permissive MVP boundary contract")
                    boundary_contract_id = await self._create_permissive_mvp_contract(intent, context)
                
                # ALWAYS set boundary contract in context (required - no exceptions)
                if not boundary_contract_id:
                    raise RuntimeError("Failed to create boundary contract - this should never happen")
                
                context.metadata["boundary_contract_id"] = boundary_contract_id
                context.metadata["materialization_pending"] = True
                self.logger.info(f"✅ Boundary contract set in context: {boundary_contract_id} (MVP permissive)")
            
            # Phase 2: For save_materialization - authorize materialization with workspace scope
            elif intent.intent_type == "save_materialization" and self.data_steward_sdk:
                try:
                    contract_id = intent.parameters.get("boundary_contract_id")
                    if not contract_id:
                        raise ValueError("boundary_contract_id is required for save_materialization intent")
                    
                    # Step 2: Authorize materialization with workspace scope
                    materialization_auth = await self.data_steward_sdk.authorize_materialization(
                        contract_id=contract_id,
                        tenant_id=intent.tenant_id,
                        context={
                            "tenant_id": intent.tenant_id,
                            "user_id": context.metadata.get("user_id", "system"),
                            "session_id": context.session_id,
                            "solution_id": context.metadata.get("solution_id")
                        },
                        materialization_policy=self.materialization_policy_store
                    )
                    
                    if not materialization_auth.materialization_allowed:
                        raise ValueError(f"Materialization not authorized: {materialization_auth.reason}")
                    
                    self.logger.info(f"✅ Materialization authorized: {materialization_auth.materialization_type} -> {materialization_auth.materialization_backing_store} (workspace-scoped)")
                    
                    # Store materialization info in context for realm use
                    context.metadata["boundary_contract_id"] = contract_id
                    context.metadata["materialization_type"] = materialization_auth.materialization_type
                    context.metadata["materialization_scope"] = materialization_auth.materialization_scope
                    context.metadata["materialization_backing_store"] = materialization_auth.materialization_backing_store
                    context.metadata["materialization_pending"] = False  # Materialization now authorized
                    
                except Exception as e:
                    self.logger.error(f"Materialization authorization failed: {e}", exc_info=True)
                    raise  # Don't allow save to continue if authorization fails
            
            # For register_file (legacy) - keep existing behavior for now
            elif intent.intent_type == "register_file" and self.data_steward_sdk:
                try:
                    # For register_file, we still do both steps (backwards compatibility)
                    # TODO: Consider making register_file also two-phase in future
                    external_source_type = "file"
                    external_source_identifier = f"register:{intent.parameters.get('file_id', 'unknown')}"
                    external_source_metadata = {
                        "ui_name": intent.parameters.get("ui_name"),
                        "file_type": intent.parameters.get("file_type", "unstructured"),
                        "mime_type": intent.parameters.get("mime_type")
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
                    
                    # Authorize materialization immediately for register_file (legacy behavior)
                    materialization_auth = await self.data_steward_sdk.authorize_materialization(
                        contract_id=boundary_contract_id,
                        tenant_id=intent.tenant_id,
                        context={
                            "tenant_id": intent.tenant_id,
                            "user_id": context.metadata.get("user_id", "system"),
                            "session_id": context.session_id,
                            "solution_id": context.metadata.get("solution_id")
                        },
                        materialization_policy=self.materialization_policy_store
                    )
                    
                    if not materialization_auth.materialization_allowed:
                        raise ValueError(f"Materialization not authorized: {materialization_auth.reason}")
                    
                    context.metadata["boundary_contract_id"] = boundary_contract_id
                    context.metadata["materialization_type"] = materialization_auth.materialization_type
                    context.metadata["materialization_scope"] = materialization_auth.materialization_scope
                    context.metadata["materialization_backing_store"] = materialization_auth.materialization_backing_store
                    context.metadata["materialization_pending"] = False
                    
                except Exception as e:
                    self.logger.error(f"Boundary contract enforcement failed: {e}", exc_info=True)
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
            
            # Store artifact references only in execution state (Phase 4.3)
            # Full artifacts are in Artifact Plane
            artifacts_for_completion = {}
            for artifact_key, artifact_data in artifacts.items():
                # Skip artifact_id references (already processed)
                if artifact_key.endswith("_artifact_id") or artifact_key.endswith("_storage_path"):
                    artifacts_for_completion[artifact_key] = artifact_data
                    continue
                
                # Extract artifact_id from artifact metadata (if registered in Artifact Plane)
                artifact_id = None
                if isinstance(artifact_data, dict):
                    metadata = artifact_data.get("metadata", {})
                    artifact_id = metadata.get("artifact_id") or artifact_data.get("artifact_id")
                
                # Store only artifact_id reference
                if artifact_id:
                    artifacts_for_completion[f"{artifact_key}_artifact_id"] = artifact_id
                else:
                    # Backward compatibility: minimal reference
                    if isinstance(artifact_data, dict) and "result_type" in artifact_data:
                        minimal_reference = {
                            "result_type": artifact_data.get("result_type"),
                            "semantic_payload": {
                                k: v for k, v in artifact_data.get("semantic_payload", {}).items()
                                if k.endswith("_id") or k == "id"
                            }
                        }
                        artifacts_for_completion[artifact_key] = minimal_reference
                    else:
                        # Legacy format
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
    
    async def _create_permissive_mvp_contract(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> str:
        """
        Create permissive MVP boundary contract.
        
        This method ensures that boundary contracts are ALWAYS created, even if
        Data Steward SDK is unavailable or access is denied. MVP uses permissive
        policies that allow all operations.
        
        ARCHITECTURAL PRINCIPLE: "Data stays at door" - boundary contracts are
        always required, but MVP policies are permissive.
        
        Args:
            intent: The intent being executed
            context: Execution context
            
        Returns:
            Boundary contract ID (always succeeds)
        """
        # Get MVP permissive policy
        policy = None
        if self.materialization_policy_store:
            try:
                policy = await self.materialization_policy_store.get_policy(
                    tenant_id=intent.tenant_id
                )
            except Exception as e:
                self.logger.debug(f"Could not get policy from store: {e}")
        
        # Fallback: Use hardcoded MVP permissive policy
        if not policy:
            policy = {
                "allow_all_types": True,
                "allowed_types": [
                    "reference",
                    "partial_extraction",
                    "deterministic",
                    "semantic_embedding",
                    "full_artifact"
                ],
                "default_ttl_days": 30,
                "default_backing_store": "gcs",
                "no_restrictions": True,
                "policy_version": "mvp_1.0"
            }
        
        # Generate contract ID
        contract_id = generate_event_id()
        
        # Create contract data
        contract_data = {
            "contract_id": contract_id,
            "tenant_id": intent.tenant_id,
            "external_source_type": "file",
            "external_source_identifier": f"upload:{intent.intent_id}:{intent.parameters.get('ui_name', 'unknown')}",
            "materialization_policy": policy,
            "access_granted": True,
            "policy_basis": "mvp_permissive_policy",
            "created_at": datetime.utcnow().isoformat(),
            "created_by": "system",
            "mvp_permissive": True
        }
        
        # Try to store contract via Data Steward SDK if available
        if self.data_steward_sdk:
            try:
                # Check if Data Steward SDK has create_boundary_contract method
                if hasattr(self.data_steward_sdk, 'create_boundary_contract'):
                    stored_id = await self.data_steward_sdk.create_boundary_contract(contract_data)
                    if stored_id:
                        self.logger.info(f"✅ MVP permissive boundary contract stored: {stored_id}")
                        return stored_id
            except Exception as e:
                self.logger.debug(f"Could not store contract via SDK: {e}, using in-memory contract")
        
        # MVP: Store contract data in context metadata if SDK not available
        # This ensures contract exists even if storage fails
        if "mvp_boundary_contracts" not in context.metadata:
            context.metadata["mvp_boundary_contracts"] = {}
        context.metadata["mvp_boundary_contracts"][contract_id] = contract_data
        
        self.logger.info(f"✅ MVP permissive boundary contract created: {contract_id} (stored in context)")
        return contract_id
    

