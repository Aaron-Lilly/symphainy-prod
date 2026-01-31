"""
Save Materialization Intent Service (New Architecture)

Implements the save_materialization intent - the second step after upload.

Contract: docs/intent_contracts/journey_content_file_upload_materialization/intent_save_materialization.md

Purpose: Explicitly authorize and register materialization of a file that was uploaded via
ingest_file. Transitions file artifact from Working Material (PENDING) to Records of Fact (READY).
Creates pending parsing journey with ingest type and file type stored in intent context.

WHAT (Intent Service Role): I handle materialization registration and lifecycle transitions
HOW (Intent Service Implementation): I use ctx.platform for materialization registration,
    ctx.state_surface for lifecycle transitions, and create pending parsing journeys

This is a REBUILD of realms/content/intent_services/save_materialization_service.py
using the new PlatformIntentService architecture.

Key Changes from Legacy:
- Extends PlatformIntentService (not BaseIntentService)
- Receives PlatformContext (ctx) instead of (intent, context)
- Uses ctx.platform.register_materialization() for materialization
- Uses ctx.platform.create_pending_intent() for pending parsing journey
- Uses ctx.state_surface for artifact lifecycle transitions
- Uses ctx.governance.telemetry for telemetry
"""

from typing import Dict, Any, Optional

from utilities import get_logger, generate_event_id
from symphainy_platform.civic_systems.platform_sdk import PlatformIntentService, PlatformContext
from symphainy_platform.runtime.artifact_registry import LifecycleState


class SaveMaterializationService(PlatformIntentService):
    """
    Intent service for saving file materialization (New Architecture).
    
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
    
    intent_type = "save_materialization"
    
    def __init__(self, service_id: Optional[str] = None):
        """
        Initialize SaveMaterializationService.
        
        Args:
            service_id: Optional service identifier
        """
        super().__init__(
            service_id=service_id or "save_materialization_service",
            intent_type="save_materialization"
        )
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute the save_materialization intent.
        
        Intent Flow (from contract):
        1. User clicks "Save File"
        2. save_materialization intent executes
        3. File artifact lifecycle transition: PENDING → READY
        4. Materialization registered in materialization index
        5. Pending parsing journey created (status: PENDING)
        6. Ingest type and file type stored in pending intent context
        7. Returns materialization_id, available_for_parsing: true
        
        Args:
            ctx: PlatformContext with full platform access
        
        Returns:
            Dictionary with artifacts and events per contract Section 3
        
        Raises:
            ValueError: For validation errors (Section 8)
            RuntimeError: For runtime errors (Section 8)
        """
        self.logger.info(f"💾 SaveMaterializationService executing with PlatformContext")
        
        # Record telemetry (start)
        await self.record_telemetry(ctx, {
            "action": "execute",
            "status": "started",
            "intent_type": self.intent_type
        })
        
        try:
            # Get intent parameters
            intent_params = ctx.intent.parameters or {}
            
            # === VALIDATION (Contract Section 2) ===
            
            boundary_contract_id = intent_params.get("boundary_contract_id")
            file_id = intent_params.get("file_id")
            
            if not boundary_contract_id:
                raise ValueError("boundary_contract_id is required for save_materialization intent")
            if not file_id:
                raise ValueError("file_id is required for save_materialization intent")
            
            # Get materialization metadata from context
            materialization_type = ctx.metadata.get("materialization_type", "full_artifact")
            materialization_scope = ctx.metadata.get("materialization_scope", {})
            materialization_backing_store = ctx.metadata.get("materialization_backing_store", "gcs")
            user_id = ctx.metadata.get("user_id") or "system"
            
            # Build file reference
            file_reference = f"file:{ctx.tenant_id}:{ctx.session_id}:{file_id}"
            
            self.logger.info(f"💾 Processing save_materialization for file: {file_id}")
            
            # === GET FILE METADATA (Optional) ===
            
            file_metadata = await self._get_file_metadata(ctx, file_reference)
            
            # Get file type for pending parsing journey (from metadata if available)
            file_type = None
            ingestion_profile = None
            if file_metadata:
                file_type = file_metadata.get("file_type")
                ingestion_profile = file_metadata.get("ingestion_type", "upload")
            
            # === REGISTER MATERIALIZATION (Contract Section 4) ===
            
            if ctx.platform:
                await ctx.platform.register_materialization(
                    file_id=file_id,
                    boundary_contract_id=boundary_contract_id,
                    tenant_id=ctx.tenant_id,
                    session_id=ctx.session_id,
                    user_id=user_id,
                    file_reference=file_reference,
                    materialization_type=materialization_type,
                    materialization_scope=materialization_scope,
                    materialization_backing_store=materialization_backing_store,
                    metadata=file_metadata or {}
                )
            
            # === TRANSITION ARTIFACT LIFECYCLE (Contract Section 4) ===
            
            await self._transition_artifact_lifecycle(
                ctx=ctx,
                artifact_id=file_id,
                from_state=LifecycleState.PENDING.value,
                to_state=LifecycleState.READY.value
            )
            
            # === CREATE PENDING PARSING JOURNEY (Contract Section 4) ===
            
            pending_intent_id = await self._create_pending_parsing_journey(
                ctx=ctx,
                file_id=file_id,
                file_type=file_type,
                ingestion_profile=ingestion_profile
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
            await self.record_telemetry(ctx, {
                "action": "execute",
                "status": "completed",
                "intent_type": self.intent_type,
                "file_id": file_id,
                "boundary_contract_id": boundary_contract_id,
                "pending_intent_created": pending_intent_id is not None
            })
            
            return {
                "artifacts": {
                    "materialization": structured_artifact
                },
                "events": [
                    {
                        "type": "materialization_saved",
                        "event_id": generate_event_id(),
                        "file_id": file_id,
                        "boundary_contract_id": boundary_contract_id,
                        "materialization_type": materialization_type,
                        "materialization_scope": materialization_scope
                    }
                ]
            }
            
        except Exception as e:
            # Record telemetry (failure)
            await self.record_telemetry(ctx, {
                "action": "execute",
                "status": "failed",
                "intent_type": self.intent_type,
                "error": str(e)
            })
            raise
    
    async def _get_file_metadata(
        self,
        ctx: PlatformContext,
        file_reference: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get file metadata from State Surface.
        
        Non-blocking - failures are logged but don't fail the intent.
        """
        try:
            if ctx.state_surface and hasattr(ctx.state_surface, 'get_file_metadata'):
                file_metadata = await ctx.state_surface.get_file_metadata(
                    session_id=ctx.session_id,
                    tenant_id=ctx.tenant_id,
                    file_reference=file_reference
                )
                return file_metadata
            
            self.logger.debug("State Surface get_file_metadata not available")
            return None
            
        except Exception as e:
            self.logger.warning(f"Could not retrieve file metadata: {e}")
            return None
    
    async def _transition_artifact_lifecycle(
        self,
        ctx: PlatformContext,
        artifact_id: str,
        from_state: str,
        to_state: str
    ) -> None:
        """
        Transition artifact lifecycle state.
        
        Updates the artifact registry to transition from PENDING to READY.
        """
        try:
            if ctx.state_surface and hasattr(ctx.state_surface, 'artifact_registry'):
                success = await ctx.state_surface.artifact_registry.update_artifact_lifecycle(
                    artifact_id=artifact_id,
                    tenant_id=ctx.tenant_id,
                    new_state=to_state,
                    reason=f"save_materialization: {from_state} → {to_state}"
                )
                
                if success:
                    self.logger.info(f"Artifact lifecycle updated: {artifact_id} {from_state} → {to_state}")
                else:
                    self.logger.warning(f"Failed to update artifact lifecycle: {artifact_id}")
            else:
                self.logger.warning("State Surface artifact_registry not available")
                
        except Exception as e:
            # Log but don't fail - materialization is still saved
            self.logger.error(f"Failed to transition artifact lifecycle: {e}", exc_info=True)
    
    async def _create_pending_parsing_journey(
        self,
        ctx: PlatformContext,
        file_id: str,
        file_type: Optional[str],
        ingestion_profile: Optional[str]
    ) -> Optional[str]:
        """
        Create pending parsing journey.
        
        Creates a pending intent record with:
        - Intent type: parse_content
        - Status: PENDING
        - Context: ingest_profile, file_type, parse_options
        
        This enables resumable parsing workflow.
        """
        if not ctx.platform:
            self.logger.warning("Platform service not available for pending intent creation")
            return None
        
        try:
            # Build pending intent context with ingest/file type
            pending_context = {
                "ingestion_profile": ingestion_profile or "upload",
                "file_type": file_type or "unstructured",
                "parse_options": {},
                "source_file_id": file_id,
                "source_execution_id": ctx.execution_id
            }
            
            pending_intent_id = await ctx.platform.create_pending_intent(
                intent_type="parse_content",
                target_artifact_id=file_id,
                tenant_id=ctx.tenant_id,
                session_id=ctx.session_id,
                context=pending_context
            )
            
            if pending_intent_id:
                self.logger.info(f"Created pending parsing journey: {pending_intent_id} for file: {file_id}")
            
            return pending_intent_id
            
        except Exception as e:
            # Non-blocking - log but don't fail
            self.logger.warning(f"Failed to create pending parsing journey: {e}")
            return None
