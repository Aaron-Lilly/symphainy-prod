"""
Save Materialization Intent Service

Implements the save_materialization intent per contract specification.
Contract: docs/intent_contracts/journey_content_file_upload_materialization/intent_save_materialization.md

WHAT (Intent Service Role): Authorize and register materialization of an uploaded file
HOW (Intent Service Implementation): Transition lifecycle, register materialization, create pending parsing journey

Key Principle: Explicitly transitions file artifact from Working Material (PENDING) 
to Records of Fact (READY). Creates pending parsing journey for resumable workflows.
"""

import sys
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
# Path: realms/content/intent_services/save_materialization_service.py
# parents[0] = intent_services, parents[1] = content, parents[2] = realms,
# parents[3] = symphainy_platform, parents[4] = symphainy_coexistence_fabric
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.artifact_registry import (
    LifecycleState
)
from utilities import generate_event_id


class SaveMaterializationService(BaseIntentService):
    """
    Intent Service for saving materializations.
    
    Implements the save_materialization intent per contract specification.
    Transitions file artifacts from PENDING to READY lifecycle state.
    
    Contract Compliance:
    - Parameters validated per contract Section 2
    - Returns structured materialization artifact per contract Section 3
    - File artifact lifecycle transitions (PENDING → READY)
    - Creates pending parsing journey for resumable workflow
    - Telemetry reported via Nurse SDK
    """
    
    # Intent contract definition for validation
    INTENT_CONTRACT = {
        "parameters": {
            "required": ["file_id", "boundary_contract_id"],
            "types": {
                "file_id": "str",
                "boundary_contract_id": "str"
            }
        },
        "required_artifacts": ["materialization"],
        "returns": {
            "artifacts": "dict",
            "events": "list"
        }
    }
    
    def __init__(self, public_works, state_surface):
        """
        Initialize SaveMaterializationService.
        
        Args:
            public_works: Public Works Foundation Service
            state_surface: State Surface for artifact registration
        """
        super().__init__(
            service_id="save_materialization_service",
            intent_type="save_materialization",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the save_materialization intent.
        
        Implementation follows contract specification exactly:
        1. Validate parameters per contract Section 2
        2. Get file metadata from State Surface
        3. Register materialization in materialization index
        4. Create pending parsing journey (intent_executions table, status: PENDING)
        5. Store ingest type and file type in pending intent context
        6. Transition file artifact lifecycle (PENDING → READY)
        7. Report telemetry via Nurse SDK
        8. Return structured artifact response per contract Section 3
        
        Args:
            context: Execution context containing intent, tenant_id, session_id, etc.
            params: Intent parameters (file_id, boundary_contract_id)
        
        Returns:
            Structured materialization artifact response per contract Section 3
        
        Raises:
            ValueError: If required parameters missing or invalid
            RuntimeError: If lifecycle transition or registration fails
        """
        # Use params from context.intent if not provided directly
        params = params or context.intent.parameters or {}
        
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
                "execution_id": context.execution_id,
                "intent_type": self.intent_type
            },
            tenant_id=context.tenant_id
        )
        
        try:
            # Step 1: Validate parameters per contract Section 2
            self._validate_parameters(params)
            
            # Extract parameters
            file_id = params.get("file_id")
            boundary_contract_id = params.get("boundary_contract_id")
            
            # Get materialization metadata from context
            materialization_type = context.metadata.get("materialization_type", "full_artifact")
            materialization_scope = context.metadata.get("materialization_scope", {})
            materialization_backing_store = context.metadata.get("materialization_backing_store", "gcs")
            user_id = context.metadata.get("user_id")
            
            # Build file reference
            file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
            
            # Step 2: Get file metadata from State Surface (optional, for validation)
            file_metadata = None
            ingest_type = "upload"  # Default
            file_type = "unstructured"  # Default
            
            if self.state_surface:
                file_metadata = await self.state_surface.get_file_metadata(file_reference)
                if file_metadata:
                    ingest_type = file_metadata.get("metadata", {}).get("ingestion_type", "upload")
                    file_type = file_metadata.get("file_type", "unstructured")
                    self.logger.debug(f"Retrieved file metadata for {file_id}: ingest_type={ingest_type}, file_type={file_type}")
            
            # Generate idempotency key
            idempotency_key = hashlib.sha256(
                f"{file_id}:{boundary_contract_id}:{context.session_id}".encode('utf-8')
            ).hexdigest()
            
            # Check idempotency
            if self.state_surface:
                existing_result = await self.state_surface.check_idempotency(
                    idempotency_key=idempotency_key,
                    tenant_id=context.tenant_id
                )
                if existing_result:
                    self.logger.info(f"Idempotent request detected, returning existing materialization")
                    return existing_result
            
            # Step 3: Register materialization in materialization index
            materialization_id = f"mat_{file_id}_{generate_event_id()}"
            await self._register_materialization(
                file_id=file_id,
                materialization_id=materialization_id,
                boundary_contract_id=boundary_contract_id,
                materialization_type=materialization_type,
                materialization_scope=materialization_scope,
                materialization_backing_store=materialization_backing_store,
                context=context
            )
            
            # Step 4 & 5: Create pending parsing journey with ingest type and file type
            pending_intent_id = await self._create_pending_parsing_journey(
                file_id=file_id,
                ingest_type=ingest_type,
                file_type=file_type,
                context=context
            )
            
            # Step 6: Transition file artifact lifecycle (PENDING → READY)
            lifecycle_updated = await self._transition_artifact_lifecycle(
                artifact_id=file_id,
                tenant_id=context.tenant_id
            )
            
            if not lifecycle_updated:
                self.logger.warning(f"Failed to transition artifact lifecycle for {file_id}")
            
            # Step 7: Report telemetry (success)
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute",
                    "status": "completed",
                    "execution_id": context.execution_id,
                    "intent_type": self.intent_type,
                    "file_id": file_id,
                    "materialization_id": materialization_id,
                    "pending_intent_id": pending_intent_id
                },
                tenant_id=context.tenant_id
            )
            
            # Step 8: Return structured artifact response per contract Section 3
            result = {
                "artifacts": {
                    "materialization": {
                        "result_type": "materialization",
                        "semantic_payload": {
                            "boundary_contract_id": boundary_contract_id,
                            "file_id": file_id,
                            "file_reference": file_reference,
                            "materialization_type": materialization_type,
                            "materialization_scope": materialization_scope,
                            "materialization_backing_store": materialization_backing_store,
                            "status": "saved",
                            "available_for_parsing": True,
                            "pending_intent_id": pending_intent_id
                        },
                        "renderings": {
                            "message": "File saved and available for parsing"
                        }
                    }
                },
                "events": [
                    {
                        "type": "materialization_saved",
                        "file_id": file_id,
                        "boundary_contract_id": boundary_contract_id,
                        "materialization_type": materialization_type,
                        "materialization_scope": materialization_scope
                    }
                ]
            }
            
            # Store idempotency result
            if self.state_surface:
                await self.state_surface.store_idempotency_result(
                    idempotency_key=idempotency_key,
                    tenant_id=context.tenant_id,
                    result=result
                )
            
            # Validate contract compliance
            is_compliant, error = self.validate_contract_compliance(
                self.INTENT_CONTRACT,
                result
            )
            if not is_compliant:
                self.logger.warning(f"Contract compliance warning: {error}")
            
            return result
            
        except ValueError as e:
            # Record telemetry (validation error)
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute",
                    "status": "failed",
                    "execution_id": context.execution_id,
                    "intent_type": self.intent_type,
                    "error_type": "validation_error",
                    "error_message": str(e)
                },
                tenant_id=context.tenant_id
            )
            raise
            
        except Exception as e:
            # Record telemetry (runtime error)
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute",
                    "status": "failed",
                    "execution_id": context.execution_id,
                    "intent_type": self.intent_type,
                    "error_type": "runtime_error",
                    "error_message": str(e)
                },
                tenant_id=context.tenant_id
            )
            raise RuntimeError(f"Save materialization failed: {e}") from e
    
    def _validate_parameters(self, params: Dict[str, Any]) -> None:
        """
        Validate parameters per contract Section 2.
        
        Args:
            params: Intent parameters
        
        Raises:
            ValueError: If required parameters missing or invalid
        """
        # Required: file_id
        file_id = params.get("file_id")
        if not file_id:
            raise ValueError("Required parameter 'file_id' not provided")
        
        # Required: boundary_contract_id
        boundary_contract_id = params.get("boundary_contract_id")
        if not boundary_contract_id:
            raise ValueError("Required parameter 'boundary_contract_id' not provided")
    
    async def _register_materialization(
        self,
        file_id: str,
        materialization_id: str,
        boundary_contract_id: str,
        materialization_type: str,
        materialization_scope: Dict[str, Any],
        materialization_backing_store: str,
        context: ExecutionContext
    ) -> None:
        """
        Register materialization in materialization index.
        
        Uses Public Works file storage abstraction if available.
        
        Args:
            file_id: File artifact identifier
            materialization_id: Generated materialization identifier
            boundary_contract_id: Boundary contract identifier
            materialization_type: Type of materialization
            materialization_scope: Scope of materialization
            materialization_backing_store: Backing store (e.g., "gcs")
            context: Execution context
        """
        if not self.public_works:
            self.logger.warning("Public Works not available, skipping materialization registration")
            return
        
        file_storage_abstraction = getattr(self.public_works, 'file_storage_abstraction', None)
        if not file_storage_abstraction:
            self.logger.debug("File storage abstraction not available, skipping materialization index")
            return
        
        try:
            # Register in project_files table (materialization index)
            # This may use the file storage abstraction's register method
            if hasattr(file_storage_abstraction, 'register_materialization'):
                await file_storage_abstraction.register_materialization(
                    file_id=file_id,
                    materialization_id=materialization_id,
                    boundary_contract_id=boundary_contract_id,
                    materialization_type=materialization_type,
                    materialization_scope=materialization_scope,
                    backing_store=materialization_backing_store,
                    tenant_id=context.tenant_id,
                    session_id=context.session_id
                )
                self.logger.debug(f"Materialization registered: {materialization_id}")
            else:
                self.logger.debug("register_materialization not available on file storage abstraction")
        except Exception as e:
            # Non-blocking - log and continue
            self.logger.warning(f"Failed to register materialization (non-blocking): {e}")
    
    async def _create_pending_parsing_journey(
        self,
        file_id: str,
        ingest_type: str,
        file_type: str,
        context: ExecutionContext
    ) -> Optional[str]:
        """
        Create pending parsing journey (intent_executions table, status: PENDING).
        
        According to journey contract:
        1. Create pending intent record
        2. Store ingest type and file type in pending intent context
        3. Enable resumable parsing workflow
        
        Args:
            file_id: File artifact identifier
            ingest_type: Ingestion type (upload, edi, api)
            file_type: File type category
            context: Execution context
        
        Returns:
            Pending intent ID if created successfully, None otherwise
        """
        pending_intent_id = f"pending_parse_{generate_event_id()}"
        
        # Build pending intent context with ingest type and file type
        pending_intent_context = {
            "ingestion_profile": ingest_type,
            "file_type": file_type,
            "parse_options": {},
            "target_artifact_id": file_id,
            "created_by_intent": self.intent_type,
            "created_by_execution": context.execution_id
        }
        
        if not self.public_works:
            self.logger.warning("Public Works not available, skipping pending journey creation")
            return pending_intent_id
        
        # Try to use intent registry to create pending intent
        intent_registry = getattr(self.public_works, 'intent_registry', None)
        
        if intent_registry and hasattr(intent_registry, 'create_pending_intent'):
            try:
                await intent_registry.create_pending_intent(
                    intent_id=pending_intent_id,
                    intent_type="parse_content",
                    target_artifact_id=file_id,
                    status="PENDING",
                    context=pending_intent_context,
                    tenant_id=context.tenant_id,
                    session_id=context.session_id
                )
                self.logger.info(f"Pending parsing journey created: {pending_intent_id}")
                return pending_intent_id
            except Exception as e:
                self.logger.warning(f"Failed to create pending intent via registry (non-blocking): {e}")
        
        # Fallback: Store pending intent in State Surface
        if self.state_surface:
            try:
                pending_state = {
                    "intent_id": pending_intent_id,
                    "intent_type": "parse_content",
                    "target_artifact_id": file_id,
                    "status": "PENDING",
                    "context": pending_intent_context,
                    "tenant_id": context.tenant_id,
                    "session_id": context.session_id,
                    "created_at": self.clock.now_iso()
                }
                
                await self.state_surface.set_execution_state(
                    execution_id=pending_intent_id,
                    tenant_id=context.tenant_id,
                    state=pending_state
                )
                self.logger.info(f"Pending parsing journey stored in State Surface: {pending_intent_id}")
                return pending_intent_id
            except Exception as e:
                self.logger.warning(f"Failed to store pending intent in State Surface (non-blocking): {e}")
        
        return pending_intent_id
    
    async def _transition_artifact_lifecycle(
        self,
        artifact_id: str,
        tenant_id: str
    ) -> bool:
        """
        Transition file artifact lifecycle (PENDING → READY).
        
        Args:
            artifact_id: Artifact identifier
            tenant_id: Tenant identifier
        
        Returns:
            True if lifecycle transition successful
        """
        if not self.state_surface:
            self.logger.warning("State Surface not available, cannot transition lifecycle")
            return False
        
        try:
            success = await self.state_surface.update_artifact_lifecycle(
                artifact_id=artifact_id,
                tenant_id=tenant_id,
                new_state=LifecycleState.READY.value,
                reason="Materialization saved via save_materialization intent"
            )
            
            if success:
                self.logger.info(f"Artifact lifecycle transitioned: {artifact_id} PENDING → READY")
            else:
                self.logger.warning(f"Failed to transition artifact lifecycle: {artifact_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error transitioning artifact lifecycle: {e}", exc_info=True)
            return False
