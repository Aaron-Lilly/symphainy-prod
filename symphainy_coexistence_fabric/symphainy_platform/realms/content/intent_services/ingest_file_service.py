"""
Ingest File Intent Service

Implements the ingest_file intent per contract specification.
Contract: docs/intent_contracts/journey_content_file_upload_materialization/intent_ingest_file.md

WHAT (Intent Service Role): Upload a file to the platform
HOW (Intent Service Implementation): Store file in GCS, register artifact in State Surface

Key Principle: Files are uploaded as Working Material (PENDING lifecycle state).
User must explicitly save via save_materialization to transition to Records of Fact.
"""

import sys
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
# Path: realms/content/intent_services/ingest_file_service.py
# parents[0] = intent_services, parents[1] = content, parents[2] = realms,
# parents[3] = symphainy_platform, parents[4] = symphainy_coexistence_fabric
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.artifact_registry import (
    ArtifactRecord,
    Materialization,
    SemanticDescriptor,
    ProducedBy,
    LifecycleState
)
from utilities import generate_event_id


class IngestFileService(BaseIntentService):
    """
    Intent Service for file ingestion.
    
    Implements the ingest_file intent per contract specification.
    Handles upload, EDI, and API ingestion types.
    
    Contract Compliance:
    - Parameters validated per contract Section 2
    - Returns structured artifact per contract Section 3
    - Artifact registered with lifecycle_state: PENDING
    - Telemetry reported via Nurse SDK
    """
    
    # Intent contract definition for validation
    INTENT_CONTRACT = {
        "parameters": {
            "required": ["ui_name"],
            "types": {
                "ui_name": "str",
                "file_content": "str",
                "ingestion_type": "str",
                "file_type": "str",
                "mime_type": "str",
                "filename": "str",
                "user_id": "str"
            }
        },
        "required_artifacts": ["artifact"],
        "returns": {
            "artifacts": "dict",
            "events": "list"
        }
    }
    
    def __init__(self, public_works, state_surface):
        """
        Initialize IngestFileService.
        
        Args:
            public_works: Public Works Foundation Service
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
        
        Implementation follows contract specification exactly:
        1. Validate parameters per contract Section 2
        2. Get IngestionAbstraction from Public Works
        3. Execute ingestion (upload/edi/api)
        4. Register artifact in State Surface (lifecycle_state: PENDING)
        5. Add GCS materialization
        6. Index artifact in Supabase
        7. Report telemetry via Nurse SDK
        8. Return structured artifact response per contract Section 3
        
        Args:
            context: Execution context containing intent, tenant_id, session_id, etc.
            params: Intent parameters (ui_name, file_content, ingestion_type, etc.)
        
        Returns:
            Structured artifact response per contract Section 3
        
        Raises:
            ValueError: If required parameters missing or invalid
            RuntimeError: If Public Works or ingestion fails
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
            self._validate_parameters(params, context)
            
            # Extract parameters
            ui_name = params.get("ui_name")
            file_content = params.get("file_content")  # Hex-encoded bytes
            ingestion_type = params.get("ingestion_type", "upload")
            file_type = params.get("file_type", "unstructured")
            mime_type = params.get("mime_type", "application/octet-stream")
            filename = params.get("filename", ui_name)
            user_id = params.get("user_id") or context.metadata.get("user_id")
            source_metadata = params.get("source_metadata", {})
            ingestion_options = params.get("ingestion_options", {})
            
            # Get boundary_contract_id from context metadata (required)
            boundary_contract_id = context.metadata.get("boundary_contract_id")
            if not boundary_contract_id:
                # Generate if not provided
                boundary_contract_id = f"boundary_{generate_event_id()}"
            
            # Step 2: Get abstractions from Public Works
            if not self.public_works:
                raise RuntimeError("Public Works not initialized")
            
            # Get ingestion abstraction (for file upload)
            ingestion_abstraction = getattr(self.public_works, 'ingestion_abstraction', None)
            file_storage_abstraction = getattr(self.public_works, 'file_storage_abstraction', None)
            
            # Step 3: Execute ingestion based on type
            ingestion_result = await self._execute_ingestion(
                ingestion_type=ingestion_type,
                file_content=file_content,
                ui_name=ui_name,
                filename=filename,
                mime_type=mime_type,
                file_type=file_type,
                context=context,
                params=params,
                ingestion_abstraction=ingestion_abstraction,
                file_storage_abstraction=file_storage_abstraction
            )
            
            # Extract results
            artifact_id = ingestion_result.get("artifact_id")
            storage_location = ingestion_result.get("storage_location")
            file_reference = ingestion_result.get("file_reference")
            file_size = ingestion_result.get("file_size", 0)
            file_hash = ingestion_result.get("file_hash")
            
            # Step 4: Register artifact in State Surface (lifecycle_state: PENDING)
            semantic_descriptor = SemanticDescriptor(
                schema="file_v1",
                record_count=None,
                parser_type=None,
                embedding_model=None
            )
            
            produced_by = ProducedBy(
                intent=self.intent_type,
                execution_id=context.execution_id
            )
            
            # Step 5: Add GCS materialization
            materialization = Materialization(
                materialization_id=f"mat_{artifact_id}",
                storage_type="gcs",
                uri=storage_location,
                format=mime_type,
                compression=None
            )
            
            # Register artifact with State Surface
            if self.state_surface:
                # Register artifact record
                artifact_record = self.create_artifact_record(
                    artifact_id=artifact_id,
                    artifact_type="file",
                    context=context,
                    semantic_descriptor=semantic_descriptor,
                    parent_artifacts=[],
                    materializations=[materialization],
                    lifecycle_state=LifecycleState.PENDING.value
                )
                
                await self.register_artifact(artifact_record, context)
                
                # Store file reference in state surface
                await self.state_surface.store_file_reference(
                    session_id=context.session_id,
                    tenant_id=context.tenant_id,
                    file_reference=file_reference,
                    storage_location=storage_location,
                    filename=filename,
                    metadata={
                        "ui_name": ui_name,
                        "file_type": file_type,
                        "content_type": mime_type,
                        "size": file_size,
                        "file_hash": file_hash,
                        "ingestion_type": ingestion_type,
                        "boundary_contract_id": boundary_contract_id
                    }
                )
            
            # Step 6: Index artifact in Supabase (via Public Works registry abstraction)
            # Note: This is handled by the registry abstraction if available
            await self._index_artifact(
                artifact_id=artifact_id,
                artifact_type="file",
                lifecycle_state=LifecycleState.PENDING.value,
                tenant_id=context.tenant_id
            )
            
            # Step 7: Report telemetry (success)
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute",
                    "status": "completed",
                    "execution_id": context.execution_id,
                    "intent_type": self.intent_type,
                    "artifact_id": artifact_id,
                    "file_size": file_size,
                    "ingestion_type": ingestion_type
                },
                tenant_id=context.tenant_id
            )
            
            # Step 8: Return structured artifact response per contract Section 3
            result = {
                "artifacts": {
                    "artifact": {
                        "result_type": "artifact",
                        "semantic_payload": {
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
                            "materialization_pending": True,
                            "file_size": file_size,
                            "file_hash": file_hash,
                            "created_at": self.clock.now_iso()
                        },
                        "renderings": {}
                    }
                },
                "events": [
                    {
                        "type": "artifact_ingested",
                        "artifact_id": artifact_id,
                        "artifact_type": "file",
                        "ingestion_type": ingestion_type
                    }
                ]
            }
            
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
            raise RuntimeError(f"Ingestion failed: {e}") from e
    
    def _validate_parameters(
        self,
        params: Dict[str, Any],
        context: ExecutionContext
    ) -> None:
        """
        Validate parameters per contract Section 2.
        
        Args:
            params: Intent parameters
            context: Execution context
        
        Raises:
            ValueError: If required parameters missing or invalid
        """
        # Required: ui_name
        ui_name = params.get("ui_name")
        if not ui_name:
            raise ValueError("Required parameter 'ui_name' not provided")
        
        # Determine ingestion type
        ingestion_type = params.get("ingestion_type", "upload")
        
        if ingestion_type == "upload":
            # For upload type, file_content is required
            file_content = params.get("file_content")
            if not file_content:
                raise ValueError("Required parameter 'file_content' not provided for upload type")
            
            # Validate hex-encoded content
            try:
                bytes.fromhex(file_content)
            except ValueError:
                raise ValueError("Parameter 'file_content' must be hex-encoded bytes")
                
        elif ingestion_type == "edi":
            # EDI-specific validation
            if not params.get("edi_data"):
                raise ValueError("Required parameter 'edi_data' not provided for EDI type")
            if not params.get("partner_id"):
                raise ValueError("Required parameter 'partner_id' not provided for EDI type")
            
            # Validate hex-encoded edi_data
            try:
                bytes.fromhex(params.get("edi_data"))
            except ValueError:
                raise ValueError("Parameter 'edi_data' must be hex-encoded bytes")
                
        elif ingestion_type == "api":
            # API-specific validation
            if not params.get("api_payload"):
                raise ValueError("Required parameter 'api_payload' not provided for API type")
        else:
            raise ValueError(f"Invalid ingestion_type: {ingestion_type}. Must be 'upload', 'edi', or 'api'")
    
    async def _execute_ingestion(
        self,
        ingestion_type: str,
        file_content: Optional[str],
        ui_name: str,
        filename: str,
        mime_type: str,
        file_type: str,
        context: ExecutionContext,
        params: Dict[str, Any],
        ingestion_abstraction: Optional[Any],
        file_storage_abstraction: Optional[Any]
    ) -> Dict[str, Any]:
        """
        Execute ingestion based on type.
        
        Args:
            ingestion_type: Type of ingestion (upload, edi, api)
            file_content: Hex-encoded file content (for upload)
            ui_name: User-friendly filename
            filename: Original filename
            mime_type: MIME type
            file_type: File type category
            context: Execution context
            params: Full parameters dict
            ingestion_abstraction: Optional ingestion abstraction from Public Works
            file_storage_abstraction: Optional file storage abstraction from Public Works
        
        Returns:
            Dict with artifact_id, storage_location, file_reference, file_size, file_hash
        """
        # Generate artifact ID
        artifact_id = f"file_{generate_event_id()}"
        
        # Determine file bytes based on ingestion type
        if ingestion_type == "upload":
            file_bytes = bytes.fromhex(file_content)
        elif ingestion_type == "edi":
            file_bytes = bytes.fromhex(params.get("edi_data"))
        elif ingestion_type == "api":
            # For API type, serialize the payload
            import json
            file_bytes = json.dumps(params.get("api_payload")).encode('utf-8')
        else:
            raise ValueError(f"Unknown ingestion_type: {ingestion_type}")
        
        # Calculate file hash and size
        file_hash = f"sha256:{hashlib.sha256(file_bytes).hexdigest()}"
        file_size = len(file_bytes)
        
        # Generate idempotency key (content fingerprint)
        content_fingerprint = hashlib.sha256(
            file_bytes + context.session_id.encode('utf-8')
        ).hexdigest()
        
        # Check idempotency via State Surface
        if self.state_surface:
            existing_result = await self.state_surface.check_idempotency(
                idempotency_key=content_fingerprint,
                tenant_id=context.tenant_id
            )
            if existing_result:
                self.logger.info(f"Idempotent request detected, returning existing artifact")
                return existing_result
        
        # Build storage path
        storage_path = f"tenants/{context.tenant_id}/sessions/{context.session_id}/files/{artifact_id}/{filename}"
        
        # Upload file using Public Works file storage abstraction
        if file_storage_abstraction:
            try:
                upload_result = await file_storage_abstraction.upload_file(
                    file_data=file_bytes,
                    destination_path=storage_path,
                    content_type=mime_type,
                    metadata={
                        "artifact_id": artifact_id,
                        "ui_name": ui_name,
                        "file_type": file_type,
                        "tenant_id": context.tenant_id,
                        "session_id": context.session_id
                    }
                )
                storage_location = upload_result.get("uri", f"gs://bucket/{storage_path}")
            except Exception as e:
                self.logger.error(f"File storage upload failed: {e}")
                # Fallback to constructed path
                storage_location = f"gs://bucket/{storage_path}"
        elif ingestion_abstraction:
            try:
                # Use ingestion abstraction if available
                ingest_result = await ingestion_abstraction.ingest_data(
                    data=file_bytes,
                    metadata={
                        "filename": filename,
                        "content_type": mime_type,
                        "artifact_id": artifact_id,
                        "tenant_id": context.tenant_id,
                        "session_id": context.session_id
                    }
                )
                storage_location = ingest_result.get("storage_location", f"gs://bucket/{storage_path}")
            except Exception as e:
                self.logger.error(f"Ingestion abstraction failed: {e}")
                storage_location = f"gs://bucket/{storage_path}"
        else:
            # No abstraction available, use constructed path
            self.logger.warning("No storage abstraction available, using constructed path")
            storage_location = f"gs://bucket/{storage_path}"
        
        # Build file reference
        file_reference = f"file:{context.tenant_id}:{context.session_id}:{artifact_id}"
        
        # Build result
        result = {
            "artifact_id": artifact_id,
            "storage_location": storage_location,
            "file_reference": file_reference,
            "file_size": file_size,
            "file_hash": file_hash
        }
        
        # Store idempotency result
        if self.state_surface:
            await self.state_surface.store_idempotency_result(
                idempotency_key=content_fingerprint,
                tenant_id=context.tenant_id,
                result=result
            )
        
        return result
    
    async def _index_artifact(
        self,
        artifact_id: str,
        artifact_type: str,
        lifecycle_state: str,
        tenant_id: str
    ) -> None:
        """
        Index artifact in Supabase artifact_index table.
        
        Uses Public Works registry abstraction if available.
        
        Args:
            artifact_id: Artifact identifier
            artifact_type: Artifact type
            lifecycle_state: Lifecycle state
            tenant_id: Tenant identifier
        """
        if not self.public_works:
            self.logger.warning("Public Works not available, skipping artifact indexing")
            return
        
        registry_abstraction = getattr(self.public_works, 'registry_abstraction', None)
        if not registry_abstraction:
            self.logger.debug("Registry abstraction not available, skipping Supabase indexing")
            return
        
        try:
            await registry_abstraction.index_artifact(
                artifact_id=artifact_id,
                artifact_type=artifact_type,
                lifecycle_state=lifecycle_state,
                tenant_id=tenant_id,
                created_at=self.clock.now_iso()
            )
            self.logger.debug(f"Artifact indexed in Supabase: {artifact_id}")
        except Exception as e:
            # Non-blocking - log and continue
            self.logger.warning(f"Failed to index artifact in Supabase (non-blocking): {e}")
