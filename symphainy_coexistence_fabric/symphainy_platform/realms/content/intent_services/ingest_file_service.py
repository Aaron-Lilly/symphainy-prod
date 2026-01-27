"""
Ingest File Intent Service

Implements the ingest_file intent for the Content Realm.

Contract: docs/intent_contracts/journey_content_file_upload_materialization/intent_ingest_file.md

Purpose: Upload a file to the platform. File is stored in GCS with materialization pending
(Working Material). User must explicitly save via save_materialization to transition
to Records of Fact.

WHAT (Intent Service Role): I handle file ingestion from multiple sources
HOW (Intent Service Implementation): I execute the ingest_file intent, store files via
    Public Works abstractions, register artifacts with State Surface, and report telemetry
"""

from typing import Dict, Any, Optional

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.artifact_registry import (
    ArtifactRecord,
    Materialization,
    SemanticDescriptor,
    ProducedBy,
    LifecycleState
)
from symphainy_platform.foundations.public_works.protocols.ingestion_protocol import (
    IngestionRequest,
    IngestionType
)


class IngestFileService(BaseIntentService):
    """
    Intent service for file ingestion.
    
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
    
    def __init__(self, public_works, state_surface):
        """
        Initialize IngestFileService.
        
        Args:
            public_works: Public Works Foundation Service for infrastructure access
            state_surface: State Surface for artifact registration
        """
        super().__init__(
            service_id="ingest_file_service",
            intent_type="ingest_file",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the ingest_file intent.
        
        Intent Flow (from contract):
        1. User uploads file
        2. ingest_file intent executes
        3. File stored in GCS
        4. Artifact registered in State Surface (lifecycle_state: PENDING)
        5. Artifact indexed in Supabase
        6. Returns artifact_id, boundary_contract_id, materialization_pending: true
        
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
            
            # CRITICAL: Files are NEVER ingested directly. A boundary contract is required.
            boundary_contract_id = context.metadata.get("boundary_contract_id")
            if not boundary_contract_id:
                raise ValueError(
                    "boundary_contract_id is required for ingest_file intent. "
                    "This indicates a bug in ExecutionLifecycleManager - boundary contracts should "
                    "always be created (permissive MVP contracts are acceptable)."
                )
            
            # Get materialization metadata from context
            materialization_type = context.metadata.get("materialization_type", "full_artifact")
            materialization_backing_store = context.metadata.get("materialization_backing_store", "gcs")
            
            # Validate ui_name (required per contract)
            ui_name = intent_params.get("ui_name")
            if not ui_name:
                raise ValueError("ui_name is required for ingest_file intent")
            
            # Get Public Works abstractions
            if not self.public_works:
                raise RuntimeError("Public Works not initialized - cannot access IngestionAbstraction")
            
            ingestion_abstraction = self.public_works.get_ingestion_abstraction()
            if not ingestion_abstraction:
                raise RuntimeError("IngestionAbstraction not available - Public Works not configured")
            
            # Determine ingestion type (default: upload)
            ingestion_type_str = intent_params.get("ingestion_type", "upload").lower()
            try:
                ingestion_type = IngestionType(ingestion_type_str)
            except ValueError:
                raise ValueError(f"Invalid ingestion_type: {ingestion_type_str}. Must be 'upload', 'edi', or 'api'")
            
            # Extract common metadata
            file_type = intent_params.get("file_type", "unstructured")
            mime_type = intent_params.get("mime_type", "application/octet-stream")
            filename = intent_params.get("filename", ui_name)
            user_id = intent_params.get("user_id") or context.metadata.get("user_id", "system")
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
            
            # === PREPARE INGESTION REQUEST BASED ON TYPE ===
            
            if ingestion_type == IngestionType.UPLOAD:
                ingestion_request = await self._prepare_upload_request(
                    intent_params, context, source_metadata, ingestion_options
                )
            elif ingestion_type == IngestionType.EDI:
                ingestion_request = await self._prepare_edi_request(
                    intent_params, context, source_metadata, ingestion_options
                )
            elif ingestion_type == IngestionType.API:
                ingestion_request = await self._prepare_api_request(
                    intent_params, context, source_metadata, ingestion_options
                )
            
            # === EXECUTE INGESTION ===
            
            self.logger.info(f"Executing {ingestion_type.value} ingestion for: {ui_name}")
            ingestion_result = await ingestion_abstraction.ingest_data(ingestion_request)
            
            if not ingestion_result.success:
                raise RuntimeError(f"Ingestion failed: {ingestion_result.error}")
            
            artifact_id = ingestion_result.file_id  # artifact_id is the file_id from ingestion
            file_reference = ingestion_result.file_reference
            file_metadata = ingestion_result.ingestion_metadata
            
            # === REGISTER ARTIFACT (Contract Section 4) ===
            
            # Create semantic descriptor
            semantic_descriptor = SemanticDescriptor(
                schema="file_v1",
                record_count=None,
                parser_type=None,
                embedding_model=None
            )
            
            # Create artifact record with lifecycle_state: PENDING (Working Material)
            artifact = self.create_artifact_record(
                artifact_id=artifact_id,
                artifact_type="file",
                context=context,
                semantic_descriptor=semantic_descriptor,
                parent_artifacts=[],
                materializations=[],
                lifecycle_state=LifecycleState.PENDING.value  # PENDING until save_materialization
            )
            
            # Register artifact via State Surface
            artifact_registered = await self.register_artifact(artifact, context)
            
            if not artifact_registered:
                raise RuntimeError(f"Failed to register artifact in Artifact Registry: {artifact_id}")
            
            # Add GCS materialization to artifact
            materialization = Materialization(
                materialization_id=f"mat_{artifact_id}",
                storage_type="gcs",
                uri=ingestion_result.storage_location,
                format=mime_type or "binary",
                compression=None
            )
            
            if self.state_surface and hasattr(self.state_surface, 'artifact_registry'):
                await self.state_surface.artifact_registry.add_materialization(
                    artifact_id=artifact_id,
                    tenant_id=context.tenant_id,
                    materialization=materialization
                )
            
            # Index artifact in artifact index (discovery layer)
            await self._index_artifact(
                artifact_id=artifact_id,
                artifact_type="file",
                tenant_id=context.tenant_id,
                context=context
            )
            
            self.logger.info(f"✅ Artifact registered: {artifact_id} (file, lifecycle_state: PENDING)")
            
            # === BUILD RESPONSE (Contract Section 3) ===
            
            semantic_payload = {
                "artifact_id": artifact_id,
                "artifact_type": "file",
                "lifecycle_state": LifecycleState.PENDING.value,
                "file_reference": file_reference,
                "storage_location": ingestion_result.storage_location,
                "ui_name": ui_name,
                "file_type": file_type,
                "mime_type": mime_type,
                "ingestion_type": ingestion_type.value,
                "boundary_contract_id": boundary_contract_id,
                "materialization_pending": True,  # Working Material
                "file_size": file_metadata.get("size") if file_metadata else None,
                "file_hash": file_metadata.get("file_hash") if file_metadata else None,
                "created_at": file_metadata.get("created_at") if file_metadata else None
            }
            
            structured_artifact = {
                "result_type": "artifact",
                "semantic_payload": semantic_payload,
                "renderings": {}
            }
            
            # Record telemetry (success)
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute",
                    "status": "completed",
                    "execution_id": context.execution_id,
                    "intent_type": self.intent_type,
                    "artifact_id": artifact_id,
                    "ingestion_type": ingestion_type.value
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "artifact": structured_artifact
                },
                "events": [
                    {
                        "type": "artifact_ingested",
                        "artifact_id": artifact_id,
                        "artifact_type": "file",
                        "ingestion_type": ingestion_type.value
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
    
    async def _prepare_upload_request(
        self,
        intent_params: Dict[str, Any],
        context: ExecutionContext,
        source_metadata: Dict[str, Any],
        ingestion_options: Dict[str, Any]
    ) -> IngestionRequest:
        """
        Prepare ingestion request for UPLOAD type.
        
        Args:
            intent_params: Intent parameters
            context: Execution context
            source_metadata: Source metadata
            ingestion_options: Ingestion options
        
        Returns:
            IngestionRequest configured for upload
        
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
        
        return IngestionRequest(
            ingestion_type=IngestionType.UPLOAD,
            tenant_id=context.tenant_id,
            session_id=context.session_id,
            source_metadata=source_metadata,
            data=file_data,
            options=ingestion_options
        )
    
    async def _prepare_edi_request(
        self,
        intent_params: Dict[str, Any],
        context: ExecutionContext,
        source_metadata: Dict[str, Any],
        ingestion_options: Dict[str, Any]
    ) -> IngestionRequest:
        """
        Prepare ingestion request for EDI type.
        
        Args:
            intent_params: Intent parameters
            context: Execution context
            source_metadata: Source metadata
            ingestion_options: Ingestion options
        
        Returns:
            IngestionRequest configured for EDI
        
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
        
        source_metadata["partner_id"] = partner_id
        source_metadata["edi_protocol"] = intent_params.get("edi_protocol", "as2")
        
        return IngestionRequest(
            ingestion_type=IngestionType.EDI,
            tenant_id=context.tenant_id,
            session_id=context.session_id,
            source_metadata=source_metadata,
            data=edi_data,
            options=ingestion_options
        )
    
    async def _prepare_api_request(
        self,
        intent_params: Dict[str, Any],
        context: ExecutionContext,
        source_metadata: Dict[str, Any],
        ingestion_options: Dict[str, Any]
    ) -> IngestionRequest:
        """
        Prepare ingestion request for API type.
        
        Args:
            intent_params: Intent parameters
            context: Execution context
            source_metadata: Source metadata
            ingestion_options: Ingestion options
        
        Returns:
            IngestionRequest configured for API
        
        Raises:
            ValueError: If api_payload is missing
        """
        api_payload = intent_params.get("api_payload")
        if not api_payload:
            raise ValueError("api_payload is required for api ingestion_type")
        
        endpoint = intent_params.get("endpoint")
        api_type = intent_params.get("api_type", "rest")
        
        source_metadata["endpoint"] = endpoint
        source_metadata["api_type"] = api_type
        
        return IngestionRequest(
            ingestion_type=IngestionType.API,
            tenant_id=context.tenant_id,
            session_id=context.session_id,
            source_metadata=source_metadata,
            api_payload=api_payload,
            options=ingestion_options
        )
    
    async def _index_artifact(
        self,
        artifact_id: str,
        artifact_type: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> None:
        """
        Index artifact in the artifact index (discovery layer).
        
        This enables artifact discovery via list_artifacts() queries.
        Non-blocking - failures are logged but don't fail the intent.
        
        Args:
            artifact_id: Artifact identifier
            artifact_type: Artifact type
            tenant_id: Tenant identifier
            context: Execution context
        """
        try:
            # Try to get registry abstraction from Public Works
            if self.public_works:
                registry_abstraction = getattr(self.public_works, 'registry_abstraction', None)
                if registry_abstraction and hasattr(registry_abstraction, 'index_artifact'):
                    await registry_abstraction.index_artifact(
                        artifact_id=artifact_id,
                        artifact_type=artifact_type,
                        tenant_id=tenant_id,
                        lifecycle_state=LifecycleState.PENDING.value,
                        session_id=context.session_id
                    )
                    self.logger.debug(f"Artifact indexed: {artifact_id}")
                    return
            
            self.logger.debug(f"Registry abstraction not available, skipping artifact indexing for: {artifact_id}")
            
        except Exception as e:
            # Non-blocking - log but don't fail
            self.logger.warning(f"Failed to index artifact {artifact_id}: {e}")
