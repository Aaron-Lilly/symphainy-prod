"""
Save Materialization Intent Service

Implements the save_materialization intent for the Content Realm.

Contract: docs/intent_contracts/journey_content_file_upload_materialization/intent_save_materialization.md

Purpose: Explicitly authorize and register materialization of a file that was uploaded via
ingest_file. Transitions file artifact from Working Material (PENDING) to Records of Fact (READY).
Creates pending parsing journey with ingest type and file type stored in intent context.

WHAT (Intent Service Role): I handle materialization registration and lifecycle transitions
HOW (Intent Service Implementation): I execute the save_materialization intent, register
    materialization via Public Works, create pending parsing journey, transition lifecycle,
    and report telemetry
"""

from typing import Dict, Any, Optional

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.artifact_registry import LifecycleState


class SaveMaterializationService(BaseIntentService):
    """
    Intent service for saving file materialization.
    
    This is the second step after upload:
    1. Upload → creates boundary contract (pending materialization)
    2. Save → authorizes materialization (active), registers in index, creates pending parsing journey
    
    Contract Compliance:
    - Parameters: Section 2 of intent contract
    - Returns: Section 3 of intent contract
    - Artifact Lifecycle Transition: Section 4 of intent contract
    - Idempotency: Section 5 of intent contract
    - Error Handling: Section 8 of intent contract
    """
    
    def __init__(self, public_works, state_surface):
        """
        Initialize SaveMaterializationService.
        
        Args:
            public_works: Public Works Foundation Service for infrastructure access
            state_surface: State Surface for artifact registration and lifecycle management
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
        
        Intent Flow (from contract):
        1. User clicks "Save File"
        2. save_materialization intent executes
        3. File artifact lifecycle transition: PENDING → READY
        4. Materialization registered in materialization index
        5. Pending parsing journey created (intent_executions table, status: PENDING)
        6. Ingest type and file type stored in pending intent context
        7. Returns materialization_id, available_for_parsing: true
        
        Args:
            context: Execution context with intent, tenant, session information
            params: Optional additional parameters (merged with intent.parameters)
        
        Returns:
            Dictionary with artifacts and events per contract Section 3
        
        Raises:
            ValueError: For validation errors (Section 8)
            RuntimeError: For runtime errors (Section 8)
        """
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
            # Get intent parameters
            intent_params = context.intent.parameters or {}
            if params:
                intent_params = {**intent_params, **params}
            
            # === VALIDATION (Contract Section 2) ===
            
            boundary_contract_id = intent_params.get("boundary_contract_id")
            file_id = intent_params.get("file_id")
            
            if not boundary_contract_id:
                raise ValueError("boundary_contract_id is required for save_materialization intent")
            if not file_id:
                raise ValueError("file_id is required for save_materialization intent")
            
            # Get materialization metadata from context
            materialization_type = context.metadata.get("materialization_type", "full_artifact")
            materialization_scope = context.metadata.get("materialization_scope", {})
            materialization_backing_store = context.metadata.get("materialization_backing_store", "gcs")
            user_id = context.metadata.get("user_id") or "system"
            
            # Build file reference
            file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
            
            self.logger.info(f"Processing save_materialization for file: {file_id}")
            
            # === GET FILE METADATA (Optional) ===
            
            file_metadata = await self._get_file_metadata(
                file_reference=file_reference,
                context=context
            )
            
            # Get file type for pending parsing journey (from metadata if available)
            file_type = None
            ingestion_profile = None
            if file_metadata:
                file_type = file_metadata.get("file_type")
                ingestion_profile = file_metadata.get("ingestion_type", "upload")
            
            # === REGISTER MATERIALIZATION (Contract Section 4) ===
            
            await self._register_materialization(
                file_id=file_id,
                boundary_contract_id=boundary_contract_id,
                materialization_type=materialization_type,
                materialization_scope=materialization_scope,
                materialization_backing_store=materialization_backing_store,
                tenant_id=context.tenant_id,
                user_id=user_id,
                session_id=context.session_id,
                file_reference=file_reference,
                metadata=file_metadata or {}
            )
            
            # === TRANSITION ARTIFACT LIFECYCLE (Contract Section 4) ===
            
            await self._transition_artifact_lifecycle(
                artifact_id=file_id,
                tenant_id=context.tenant_id,
                from_state=LifecycleState.PENDING.value,
                to_state=LifecycleState.READY.value
            )
            
            # === CREATE PENDING PARSING JOURNEY (Contract Section 4) ===
            
            pending_intent_id = await self._create_pending_parsing_journey(
                file_id=file_id,
                tenant_id=context.tenant_id,
                session_id=context.session_id,
                file_type=file_type,
                ingestion_profile=ingestion_profile,
                context=context
            )
            
            self.logger.info(f"✅ Materialization saved: {file_id} (contract: {boundary_contract_id})")
            
            # === BUILD RESPONSE (Contract Section 3) ===
            
            semantic_payload = {
                "boundary_contract_id": boundary_contract_id,
                "file_id": file_id,
                "file_reference": file_reference,
                "materialization_type": materialization_type,
                "materialization_scope": materialization_scope,
                "materialization_backing_store": materialization_backing_store,
                "status": "saved",
                "available_for_parsing": True
            }
            
            # Include pending intent ID if created
            if pending_intent_id:
                semantic_payload["pending_parsing_intent_id"] = pending_intent_id
            
            structured_artifact = {
                "result_type": "materialization",
                "semantic_payload": semantic_payload,
                "renderings": {
                    "message": "File saved and available for parsing"
                }
            }
            
            # Record telemetry (success)
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute",
                    "status": "completed",
                    "execution_id": context.execution_id,
                    "intent_type": self.intent_type,
                    "file_id": file_id,
                    "boundary_contract_id": boundary_contract_id,
                    "pending_intent_created": pending_intent_id is not None
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "materialization": structured_artifact
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
            
        except Exception as e:
            # Record telemetry (failure)
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute",
                    "status": "failed",
                    "execution_id": context.execution_id,
                    "intent_type": self.intent_type,
                    "error": str(e)
                },
                tenant_id=context.tenant_id
            )
            raise
    
    async def _get_file_metadata(
        self,
        file_reference: str,
        context: ExecutionContext
    ) -> Optional[Dict[str, Any]]:
        """
        Get file metadata from State Surface.
        
        Non-blocking - failures are logged but don't fail the intent.
        
        Args:
            file_reference: File reference string
            context: Execution context
        
        Returns:
            File metadata dictionary if found, None otherwise
        """
        try:
            if self.state_surface and hasattr(self.state_surface, 'get_file_metadata'):
                file_metadata = await self.state_surface.get_file_metadata(
                    session_id=context.session_id,
                    tenant_id=context.tenant_id,
                    file_reference=file_reference
                )
                return file_metadata
            
            self.logger.debug(f"State Surface get_file_metadata not available")
            return None
            
        except Exception as e:
            self.logger.warning(f"Could not retrieve file metadata from state surface: {e}")
            return None
    
    async def _register_materialization(
        self,
        file_id: str,
        boundary_contract_id: str,
        materialization_type: str,
        materialization_scope: Dict[str, Any],
        materialization_backing_store: str,
        tenant_id: str,
        user_id: str,
        session_id: str,
        file_reference: str,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Register materialization in the materialization index.
        
        Non-blocking - failures are logged but don't fail the intent.
        
        Args:
            file_id: File artifact identifier
            boundary_contract_id: Boundary contract identifier
            materialization_type: Type of materialization
            materialization_scope: Materialization scope
            materialization_backing_store: Backing store (e.g., "gcs")
            tenant_id: Tenant identifier
            user_id: User identifier
            session_id: Session identifier
            file_reference: File reference string
            metadata: File metadata
        """
        try:
            if self.public_works:
                file_storage = self.public_works.get_file_storage_abstraction()
                if file_storage and hasattr(file_storage, 'register_materialization'):
                    await file_storage.register_materialization(
                        file_id=file_id,
                        boundary_contract_id=boundary_contract_id,
                        materialization_type=materialization_type,
                        materialization_scope=materialization_scope,
                        materialization_backing_store=materialization_backing_store,
                        tenant_id=tenant_id,
                        user_id=user_id,
                        session_id=session_id,
                        file_reference=file_reference,
                        metadata=metadata
                    )
                    self.logger.info(f"✅ Materialization registered: {file_id} (contract: {boundary_contract_id})")
                    return
                else:
                    self.logger.warning("FileStorageAbstraction not available or missing register_materialization method")
            else:
                self.logger.warning("Public Works not available, skipping materialization registration")
                
        except Exception as e:
            # Non-blocking - log but don't fail
            self.logger.error(f"Failed to register materialization: {e}", exc_info=True)
    
    async def _transition_artifact_lifecycle(
        self,
        artifact_id: str,
        tenant_id: str,
        from_state: str,
        to_state: str
    ) -> None:
        """
        Transition artifact lifecycle state.
        
        Updates the artifact registry to transition from PENDING to READY.
        
        Args:
            artifact_id: Artifact identifier
            tenant_id: Tenant identifier
            from_state: Expected current state
            to_state: Target state
        """
        try:
            if self.state_surface and hasattr(self.state_surface, 'artifact_registry'):
                success = await self.state_surface.artifact_registry.update_artifact_lifecycle(
                    artifact_id=artifact_id,
                    tenant_id=tenant_id,
                    new_state=to_state,
                    reason=f"save_materialization: {from_state} → {to_state}"
                )
                
                if success:
                    self.logger.info(f"Artifact lifecycle updated: {artifact_id} {from_state} → {to_state}")
                else:
                    self.logger.warning(f"Failed to update artifact lifecycle: {artifact_id}")
            else:
                self.logger.warning("State Surface artifact_registry not available, skipping lifecycle transition")
                
        except Exception as e:
            # Log but don't fail - materialization is still saved
            self.logger.error(f"Failed to transition artifact lifecycle: {e}", exc_info=True)
    
    async def _create_pending_parsing_journey(
        self,
        file_id: str,
        tenant_id: str,
        session_id: str,
        file_type: Optional[str],
        ingestion_profile: Optional[str],
        context: ExecutionContext
    ) -> Optional[str]:
        """
        Create pending parsing journey.
        
        Creates a pending intent record in intent_executions table with:
        - Intent type: parse_content
        - Status: PENDING
        - Context: ingest_profile, file_type, parse_options
        
        This enables resumable parsing workflow.
        
        Args:
            file_id: File artifact identifier
            tenant_id: Tenant identifier
            session_id: Session identifier
            file_type: File type (e.g., "pdf", "csv")
            ingestion_profile: Ingestion profile (e.g., "upload", "edi", "api")
            context: Execution context
        
        Returns:
            Pending intent ID if created, None otherwise
        """
        try:
            # Try to get intent registry from Public Works or context
            intent_registry = None
            
            if self.public_works:
                intent_registry = getattr(self.public_works, 'intent_registry', None)
            
            if not intent_registry and self.state_surface:
                intent_registry = getattr(self.state_surface, 'intent_registry', None)
            
            if intent_registry and hasattr(intent_registry, 'create_pending_intent'):
                # Build pending intent context with ingest/file type
                pending_context = {
                    "ingestion_profile": ingestion_profile or "upload",
                    "file_type": file_type or "unstructured",
                    "parse_options": {},
                    "source_file_id": file_id,
                    "source_execution_id": context.execution_id
                }
                
                pending_intent_id = await intent_registry.create_pending_intent(
                    intent_type="parse_content",
                    target_artifact_id=file_id,
                    tenant_id=tenant_id,
                    session_id=session_id,
                    context=pending_context
                )
                
                self.logger.info(f"Created pending parsing journey: {pending_intent_id} for file: {file_id}")
                return pending_intent_id
            
            # Fallback: Try to register directly in registry abstraction
            if self.public_works:
                registry_abstraction = getattr(self.public_works, 'registry_abstraction', None)
                if registry_abstraction and hasattr(registry_abstraction, 'register_pending_intent'):
                    pending_context = {
                        "ingestion_profile": ingestion_profile or "upload",
                        "file_type": file_type or "unstructured",
                        "parse_options": {},
                        "source_file_id": file_id,
                        "source_execution_id": context.execution_id
                    }
                    
                    pending_intent_id = await registry_abstraction.register_pending_intent(
                        intent_type="parse_content",
                        target_artifact_id=file_id,
                        tenant_id=tenant_id,
                        session_id=session_id,
                        context=pending_context
                    )
                    
                    self.logger.info(f"Created pending parsing journey (via registry): {pending_intent_id}")
                    return pending_intent_id
            
            self.logger.warning("Intent registry not available, skipping pending parsing journey creation")
            return None
            
        except Exception as e:
            # Non-blocking - log but don't fail
            self.logger.warning(f"Failed to create pending parsing journey: {e}")
            return None
