"""
Ingestion Handlers - File Ingestion
"""

from typing import Dict, Any, Optional

from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.artifact_registry import (
    ProducedBy,
    SemanticDescriptor,
    Materialization,
    LifecycleState
)
from symphainy_platform.foundations.public_works.protocols.ingestion_protocol import (
    IngestionRequest,
    IngestionType
)
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact
from .base_handler import BaseContentHandler


class IngestionHandlers(BaseContentHandler):
    """
    Handlers for ingestion intents:
    - ingest_file
    """
    
    async def handle_ingest_file(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle ingest_file intent - unified ingestion from multiple sources (artifact-centric).
        
        Supports:
        - UPLOAD: Direct file upload (hex-encoded bytes)
        - EDI: EDI protocol (AS2, SFTP, etc.)
        - API: REST/GraphQL API payloads
        
        Intent parameters:
        - ingestion_type: str (REQUIRED) - "upload", "edi", or "api" (defaults to "upload")
        - file_content: bytes (hex-encoded) - For UPLOAD type (REQUIRED for upload)
        - edi_data: bytes (hex-encoded) - For EDI type (REQUIRED for edi)
        - api_payload: Dict - For API type (REQUIRED for api)
        - ui_name: str (REQUIRED) - User-friendly filename
        - file_type: str - File type (e.g., "pdf", "csv")
        - mime_type: str - MIME type (e.g., "application/pdf")
        - filename: str - Original filename (defaults to ui_name)
        - user_id: str - User identifier (optional, from context if not provided)
        - source_metadata: Dict - Source-specific metadata
        - ingestion_options: Dict - Ingestion-specific options
        
        Returns:
        - artifact_id: File artifact identifier
        - artifact_type: "file"
        - lifecycle_state: "PENDING" (Working Material until save_materialization)
        """
        # CRITICAL: Files are NEVER ingested directly. A boundary contract is required.
        boundary_contract_id = context.metadata.get("boundary_contract_id")
        materialization_type = context.metadata.get("materialization_type", "full_artifact")
        materialization_backing_store = context.metadata.get("materialization_backing_store", "gcs")
        
        if not boundary_contract_id:
            raise ValueError(
                "boundary_contract_id is required for ingest_file intent. "
                "This indicates a bug in ExecutionLifecycleManager - boundary contracts should "
                "always be created (permissive MVP contracts are acceptable)."
            )
        
        self.logger.info(f"✅ Using boundary contract: {boundary_contract_id}")
        
        # Get ingestion abstraction from Public Works
        if not self.public_works:
            raise RuntimeError("Public Works not initialized - cannot access IngestionAbstraction")
        
        ingestion_abstraction = self.public_works.get_ingestion_abstraction()
        if not ingestion_abstraction:
            raise RuntimeError("IngestionAbstraction not available - Public Works not configured")
        
        # Determine ingestion type
        ingestion_type_str = intent.parameters.get("ingestion_type", "upload").lower()
        try:
            ingestion_type = IngestionType(ingestion_type_str)
        except ValueError:
            raise ValueError(f"Invalid ingestion_type: {ingestion_type_str}. Must be 'upload', 'edi', or 'api'")
        
        # Extract common metadata
        ui_name = intent.parameters.get("ui_name")
        if not ui_name:
            raise ValueError("ui_name is required for ingest_file intent")
        
        file_type = intent.parameters.get("file_type", "unstructured")
        mime_type = intent.parameters.get("mime_type", "application/octet-stream")
        filename = intent.parameters.get("filename", ui_name)
        user_id = intent.parameters.get("user_id") or context.metadata.get("user_id", "system")
        source_metadata = intent.parameters.get("source_metadata", {})
        ingestion_options = intent.parameters.get("ingestion_options", {})
        
        # Prepare source metadata
        source_metadata.update({
            "ui_name": ui_name,
            "file_type": file_type,
            "mime_type": mime_type,
            "user_id": user_id,
            "filename": filename,
            "status": "uploaded"
        })
        
        # Prepare ingestion request based on type
        if ingestion_type == IngestionType.UPLOAD:
            file_content_hex = intent.parameters.get("file_content")
            if not file_content_hex:
                raise ValueError("file_content is required for upload ingestion_type")
            
            try:
                file_data = bytes.fromhex(file_content_hex)
            except ValueError as e:
                raise ValueError(f"Invalid file_content (must be hex-encoded): {e}")
            
            ingestion_request = IngestionRequest(
                ingestion_type=IngestionType.UPLOAD,
                tenant_id=context.tenant_id,
                session_id=context.session_id,
                source_metadata=source_metadata,
                data=file_data,
                options=ingestion_options
            )
        
        elif ingestion_type == IngestionType.EDI:
            edi_data_hex = intent.parameters.get("edi_data")
            if not edi_data_hex:
                raise ValueError("edi_data is required for edi ingestion_type")
            
            try:
                edi_data = bytes.fromhex(edi_data_hex)
            except ValueError as e:
                raise ValueError(f"Invalid edi_data (must be hex-encoded): {e}")
            
            partner_id = intent.parameters.get("partner_id")
            if not partner_id:
                raise ValueError("partner_id is required for edi ingestion_type")
            
            source_metadata["partner_id"] = partner_id
            source_metadata["edi_protocol"] = intent.parameters.get("edi_protocol", "as2")
            
            ingestion_request = IngestionRequest(
                ingestion_type=IngestionType.EDI,
                tenant_id=context.tenant_id,
                session_id=context.session_id,
                source_metadata=source_metadata,
                data=edi_data,
                options=ingestion_options
            )
        
        elif ingestion_type == IngestionType.API:
            api_payload = intent.parameters.get("api_payload")
            if not api_payload:
                raise ValueError("api_payload is required for api ingestion_type")
            
            endpoint = intent.parameters.get("endpoint")
            api_type = intent.parameters.get("api_type", "rest")
            
            source_metadata["endpoint"] = endpoint
            source_metadata["api_type"] = api_type
            
            ingestion_request = IngestionRequest(
                ingestion_type=IngestionType.API,
                tenant_id=context.tenant_id,
                session_id=context.session_id,
                source_metadata=source_metadata,
                api_payload=api_payload,
                options=ingestion_options
            )
        
        # Execute ingestion via IngestionAbstraction
        ingestion_result = await ingestion_abstraction.ingest_data(ingestion_request)
        
        if not ingestion_result.success:
            raise RuntimeError(f"Ingestion failed: {ingestion_result.error}")
        
        artifact_id = ingestion_result.file_id  # artifact_id is the file_id from ingestion
        file_reference = ingestion_result.file_reference
        file_metadata = ingestion_result.ingestion_metadata
        
        # Register artifact in State Surface (artifact-centric pattern)
        semantic_descriptor = SemanticDescriptor(
            schema="file_v1",
            record_count=None,
            parser_type=None,
            embedding_model=None
        )
        
        produced_by = ProducedBy(
            intent="ingest_file",
            execution_id=context.execution_id
        )
        
        # Register artifact with lifecycle_state: PENDING (Working Material)
        artifact_registered = await context.state_surface.register_artifact(
            artifact_id=artifact_id,
            artifact_type="file",
            tenant_id=context.tenant_id,
            produced_by=produced_by,
            semantic_descriptor=semantic_descriptor,
            parent_artifacts=[],
            lifecycle_state=LifecycleState.PENDING.value  # PENDING until save_materialization
        )
        
        if not artifact_registered:
            raise RuntimeError(f"Failed to register artifact in Artifact Registry: {artifact_id}")
        
        # Add GCS materialization
        materialization = Materialization(
            materialization_id=f"mat_{artifact_id}",
            storage_type="gcs",
            uri=ingestion_result.storage_location,
            format=mime_type or "binary",
            compression=None
        )
        
        await context.state_surface.add_materialization(
            artifact_id=artifact_id,
            tenant_id=context.tenant_id,
            materialization=materialization
        )
        
        # Index in Artifact Index (discovery layer)
        await self._index_artifact(
            artifact_id=artifact_id,
            artifact_type="file",
            tenant_id=context.tenant_id,
            lifecycle_state=LifecycleState.PENDING.value,
            semantic_descriptor=semantic_descriptor,
            produced_by=produced_by,
            parent_artifacts=[],
            context=context
        )
        
        self.logger.info(f"✅ Artifact registered: {artifact_id} (file, lifecycle_state: PENDING)")
        
        # Create structured artifact for response
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
        
        structured_artifact = create_structured_artifact(
            result_type="artifact",
            semantic_payload=semantic_payload,
            renderings={}
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
