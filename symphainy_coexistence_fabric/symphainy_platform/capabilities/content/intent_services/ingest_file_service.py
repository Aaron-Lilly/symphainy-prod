"""
Ingest File Intent Service (New Architecture)

Implements the ingest_file intent for file uploads.

Contract: docs/intent_contracts/journey_content_file_upload_materialization/intent_ingest_file.md

Purpose: Upload a file to the platform. File is stored in GCS with materialization pending
(Working Material). User must explicitly save via save_materialization to transition
to Records of Fact.

WHAT (Intent Service Role): I handle file ingestion from multiple sources
HOW (Intent Service Implementation): I use ctx.platform.ingest_file() to store files,
    register artifacts with ctx.state_surface, and report telemetry

This is a REBUILD of realms/content/intent_services/ingest_file_service.py
using the new PlatformIntentService architecture.

Key Changes from Legacy:
- Extends PlatformIntentService (not BaseIntentService)
- Receives PlatformContext (ctx) instead of (intent, context)
- Uses ctx.platform.ingest_file/edi/api() for ingestion
- Uses ctx.state_surface for artifact registration
- Uses ctx.governance.telemetry for telemetry
"""

from typing import Dict, Any, Optional

from utilities import get_logger, generate_event_id
from symphainy_platform.civic_systems.platform_sdk import PlatformIntentService, PlatformContext
from symphainy_platform.runtime.artifact_registry import (
    ArtifactRecord,
    Materialization,
    SemanticDescriptor,
    ProducedBy,
    LifecycleState
)


class IngestFileService(PlatformIntentService):
    """
    Intent service for file ingestion (New Architecture).
    
    Supports multiple ingestion types:
    - UPLOAD: Direct file upload (hex-encoded bytes)
    - EDI: EDI protocol (AS2, SFTP, etc.)
    - API: REST/GraphQL API payloads
    
    Contract Compliance:
    - Parameters: Section 2 of intent contract
    - Returns: Section 3 of intent contract
    - Artifact Registration: Section 4 of intent contract
    - Idempotency: Section 5 of intent contract
    - Error Handling: Section 8 of intent contract
    """
    
    intent_type = "ingest_file"
    
    def __init__(self, service_id: Optional[str] = None):
        """
        Initialize IngestFileService.
        
        Args:
            service_id: Optional service identifier
        """
        super().__init__(
            service_id=service_id or "ingest_file_service",
            intent_type="ingest_file"
        )
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute the ingest_file intent.
        
        Intent Flow (from contract):
        1. User uploads file
        2. ingest_file intent executes
        3. File stored in GCS via ctx.platform.ingest_file()
        4. Artifact registered in State Surface (lifecycle_state: PENDING)
        5. Artifact indexed for discovery
        6. Returns artifact_id, boundary_contract_id, materialization_pending: true
        
        Args:
            ctx: PlatformContext with full platform access
        
        Returns:
            Dictionary with artifacts and events per contract Section 3
        
        Raises:
            ValueError: For validation errors (Section 8)
            RuntimeError: For runtime errors (Section 8)
        """
        self.logger.info(f"📥 IngestFileService executing with PlatformContext")
        
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
            
            # CRITICAL: Files are NEVER ingested directly. A boundary contract is required.
            boundary_contract_id = ctx.metadata.get("boundary_contract_id")
            if not boundary_contract_id:
                raise ValueError(
                    "boundary_contract_id is required for ingest_file intent. "
                    "This indicates a bug in ExecutionLifecycleManager - boundary contracts should "
                    "always be created (permissive MVP contracts are acceptable)."
                )
            
            # Get materialization metadata from context
            materialization_type = ctx.metadata.get("materialization_type", "full_artifact")
            materialization_backing_store = ctx.metadata.get("materialization_backing_store", "gcs")
            
            # Validate ui_name (required per contract)
            ui_name = intent_params.get("ui_name")
            if not ui_name:
                raise ValueError("ui_name is required for ingest_file intent")
            
            # Validate platform service is available
            if not ctx.platform:
                raise RuntimeError("Platform service not available - cannot access ingestion")
            
            # Determine ingestion type (default: upload)
            ingestion_type = intent_params.get("ingestion_type", "upload").lower()
            if ingestion_type not in ["upload", "edi", "api"]:
                raise ValueError(f"Invalid ingestion_type: {ingestion_type}. Must be 'upload', 'edi', or 'api'")
            
            # Extract common metadata
            file_type = intent_params.get("file_type", "unstructured")
            mime_type = intent_params.get("mime_type", "application/octet-stream")
            filename = intent_params.get("filename", ui_name)
            user_id = intent_params.get("user_id") or ctx.metadata.get("user_id", "system")
            source_metadata = intent_params.get("source_metadata", {})
            ingestion_options = intent_params.get("ingestion_options", {})
            
            # Prepare source metadata
            source_metadata.update({
                "ui_name": ui_name,
                "file_type": file_type,
                "mime_type": mime_type,
                "user_id": user_id,
                "filename": filename,
                "status": "uploaded"
            })
            
            # === EXECUTE INGESTION VIA ctx.platform ===
            
            self.logger.info(f"📥 Executing {ingestion_type} ingestion for: {ui_name}")
            
            if ingestion_type == "upload":
                ingestion_result = await self._execute_upload_ingestion(
                    ctx, intent_params, source_metadata, ingestion_options
                )
            elif ingestion_type == "edi":
                ingestion_result = await self._execute_edi_ingestion(
                    ctx, intent_params, source_metadata, ingestion_options
                )
            elif ingestion_type == "api":
                ingestion_result = await self._execute_api_ingestion(
                    ctx, intent_params, source_metadata, ingestion_options
                )
            
            if not ingestion_result.get("success"):
                raise RuntimeError(f"Ingestion failed: {ingestion_result.get('error')}")
            
            artifact_id = ingestion_result["file_id"]
            file_reference = ingestion_result["file_reference"]
            storage_location = ingestion_result["storage_location"]
            file_metadata = ingestion_result.get("ingestion_metadata", {})
            
            # === REGISTER ARTIFACT (Contract Section 4) ===
            
            await self._register_artifact(
                ctx=ctx,
                artifact_id=artifact_id,
                storage_location=storage_location,
                mime_type=mime_type
            )
            
            # Index artifact for discovery
            await self._index_artifact(
                ctx=ctx,
                artifact_id=artifact_id,
                artifact_type="file"
            )
            
            self.logger.info(f"✅ Artifact registered: {artifact_id} (file, lifecycle_state: PENDING)")
            
            # === BUILD RESPONSE (Contract Section 3) ===
            
            semantic_payload = {
                "artifact_id": artifact_id,
                "artifact_type": "file",
                "lifecycle_state": LifecycleState.PENDING.value,
                "file_reference": file_reference,
                "storage_location": storage_location,
                "ui_name": ui_name,
                "file_type": file_type,
                "mime_type": mime_type,
                "ingestion_type": ingestion_type,
                "boundary_contract_id": boundary_contract_id,
                "materialization_pending": True,  # Working Material
                "file_size": file_metadata.get("size"),
                "file_hash": file_metadata.get("file_hash"),
                "created_at": file_metadata.get("created_at")
            }
            
            structured_artifact = {
                "result_type": "artifact",
                "semantic_payload": semantic_payload,
                "renderings": {}
            }
            
            # Record telemetry (success)
            await self.record_telemetry(ctx, {
                "action": "execute",
                "status": "completed",
                "intent_type": self.intent_type,
                "artifact_id": artifact_id,
                "ingestion_type": ingestion_type
            })
            
            return {
                "artifacts": {
                    "artifact": structured_artifact
                },
                "events": [
                    {
                        "type": "artifact_ingested",
                        "event_id": generate_event_id(),
                        "artifact_id": artifact_id,
                        "artifact_type": "file",
                        "ingestion_type": ingestion_type
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
    
    async def _execute_upload_ingestion(
        self,
        ctx: PlatformContext,
        intent_params: Dict[str, Any],
        source_metadata: Dict[str, Any],
        ingestion_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute upload ingestion via ctx.platform.ingest_file().
        
        Args:
            ctx: Platform context
            intent_params: Intent parameters
            source_metadata: Source metadata
            ingestion_options: Ingestion options
        
        Returns:
            Ingestion result dict
        
        Raises:
            ValueError: If file_content is missing or invalid
        """
        file_content_hex = intent_params.get("file_content")
        if not file_content_hex:
            raise ValueError("file_content is required for upload ingestion_type")
        
        try:
            file_data = bytes.fromhex(file_content_hex)
        except ValueError as e:
            raise ValueError(f"Invalid file_content (must be hex-encoded): {e}")
        
        return await ctx.platform.ingest_file(
            file_data=file_data,
            tenant_id=ctx.tenant_id,
            session_id=ctx.session_id,
            source_metadata=source_metadata,
            options=ingestion_options
        )
    
    async def _execute_edi_ingestion(
        self,
        ctx: PlatformContext,
        intent_params: Dict[str, Any],
        source_metadata: Dict[str, Any],
        ingestion_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute EDI ingestion via ctx.platform.ingest_edi().
        
        Args:
            ctx: Platform context
            intent_params: Intent parameters
            source_metadata: Source metadata
            ingestion_options: Ingestion options
        
        Returns:
            Ingestion result dict
        
        Raises:
            ValueError: If edi_data or partner_id is missing
        """
        edi_data_hex = intent_params.get("edi_data")
        if not edi_data_hex:
            raise ValueError("edi_data is required for edi ingestion_type")
        
        try:
            edi_data = bytes.fromhex(edi_data_hex)
        except ValueError as e:
            raise ValueError(f"Invalid edi_data (must be hex-encoded): {e}")
        
        partner_id = intent_params.get("partner_id")
        if not partner_id:
            raise ValueError("partner_id is required for edi ingestion_type")
        
        source_metadata["edi_protocol"] = intent_params.get("edi_protocol", "as2")
        
        return await ctx.platform.ingest_edi(
            edi_data=edi_data,
            tenant_id=ctx.tenant_id,
            session_id=ctx.session_id,
            partner_id=partner_id,
            source_metadata=source_metadata,
            options=ingestion_options
        )
    
    async def _execute_api_ingestion(
        self,
        ctx: PlatformContext,
        intent_params: Dict[str, Any],
        source_metadata: Dict[str, Any],
        ingestion_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute API ingestion via ctx.platform.ingest_api().
        
        Args:
            ctx: Platform context
            intent_params: Intent parameters
            source_metadata: Source metadata
            ingestion_options: Ingestion options
        
        Returns:
            Ingestion result dict
        
        Raises:
            ValueError: If api_payload is missing
        """
        api_payload = intent_params.get("api_payload")
        if not api_payload:
            raise ValueError("api_payload is required for api ingestion_type")
        
        source_metadata["endpoint"] = intent_params.get("endpoint")
        source_metadata["api_type"] = intent_params.get("api_type", "rest")
        
        return await ctx.platform.ingest_api(
            api_payload=api_payload,
            tenant_id=ctx.tenant_id,
            session_id=ctx.session_id,
            source_metadata=source_metadata,
            options=ingestion_options
        )
    
    async def _register_artifact(
        self,
        ctx: PlatformContext,
        artifact_id: str,
        storage_location: str,
        mime_type: str
    ) -> None:
        """
        Register artifact in State Surface.
        
        Creates artifact record with lifecycle_state: PENDING (Working Material).
        """
        if not ctx.state_surface:
            self.logger.warning("State Surface not available, skipping artifact registration")
            return
        
        try:
            # Create semantic descriptor
            semantic_descriptor = SemanticDescriptor(
                schema="file_v1",
                record_count=None,
                parser_type=None,
                embedding_model=None
            )
            
            # Create produced_by (provenance)
            produced_by = ProducedBy(
                intent="ingest_file",
                execution_id=ctx.execution_id
            )
            
            # Create artifact record with lifecycle_state: PENDING (Working Material)
            artifact = ArtifactRecord(
                artifact_id=artifact_id,
                artifact_type="file",
                tenant_id=ctx.tenant_id,
                produced_by=produced_by,
                parent_artifacts=[],
                lifecycle_state=LifecycleState.PENDING.value,
                semantic_descriptor=semantic_descriptor,
                materializations=[]
            )
            
            # Register artifact via State Surface
            artifact_registered = await ctx.state_surface.artifact_registry.register_artifact(
                artifact=artifact,
                tenant_id=ctx.tenant_id
            )
            
            if not artifact_registered:
                raise RuntimeError(f"Failed to register artifact in Artifact Registry: {artifact_id}")
            
            # Add GCS materialization to artifact
            materialization = Materialization(
                materialization_id=f"mat_{artifact_id}",
                storage_type="gcs",
                uri=storage_location,
                format=mime_type or "binary",
                compression=None
            )
            
            await ctx.state_surface.artifact_registry.add_materialization(
                artifact_id=artifact_id,
                tenant_id=ctx.tenant_id,
                materialization=materialization
            )
            
        except Exception as e:
            self.logger.error(f"Error registering artifact: {e}", exc_info=True)
            raise
    
    async def _index_artifact(
        self,
        ctx: PlatformContext,
        artifact_id: str,
        artifact_type: str
    ) -> None:
        """
        Index artifact for discovery.
        
        Non-blocking - failures are logged but don't fail the intent.
        """
        if not ctx.platform or not ctx.platform.registry:
            self.logger.debug("Registry not available, skipping artifact indexing")
            return
        
        try:
            registry = ctx.platform.registry
            if hasattr(registry, 'index_artifact'):
                await registry.index_artifact(
                    artifact_id=artifact_id,
                    artifact_type=artifact_type,
                    tenant_id=ctx.tenant_id,
                    lifecycle_state=LifecycleState.PENDING.value,
                    session_id=ctx.session_id
                )
                self.logger.debug(f"Artifact indexed: {artifact_id}")
        except Exception as e:
            # Non-blocking - log but don't fail
            self.logger.warning(f"Failed to index artifact {artifact_id}: {e}")
