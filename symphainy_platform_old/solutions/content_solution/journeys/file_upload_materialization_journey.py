"""
File Upload & Materialization Journey Orchestrator

Composes the file upload and materialization journey:
1. ingest_file - Upload file to storage (Working Material, materialization pending)
2. save_materialization - User explicitly saves file (Working Material → Records of Fact)

WHAT (Journey Role): I orchestrate file upload and materialization
HOW (Journey Implementation): I compose ingest_file + save_materialization intents

Key Principle: Journey orchestrators compose intent services into journeys.
They use BaseOrchestrator.compose_journey() pattern.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
import hashlib

from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.intent_model import Intent, IntentFactory
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.artifact_registry import (
    ArtifactRecord,
    SemanticDescriptor,
    ProducedBy,
    Materialization,
    LifecycleState
)
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact


class FileUploadMaterializationJourney:
    """
    File Upload & Materialization Journey Orchestrator.
    
    Journey Flow:
    1. User selects content type and file type
    2. User uploads file (ingest_file intent)
    3. File artifact created with lifecycle_state: "PENDING"
    4. User clicks "Save File" (save_materialization intent)
    5. File artifact lifecycle transitions to "READY"
    6. Pending parsing journey created
    
    Provides MCP Tools:
    - content_upload_file: Upload a file
    - content_save_materialization: Save file materialization
    - content_upload_and_materialize: Complete journey in one step
    """
    
    JOURNEY_ID = "file_upload_materialization"
    JOURNEY_NAME = "File Upload & Materialization"
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        """
        Initialize File Upload & Materialization Journey.
        
        Args:
            public_works: Public Works Foundation Service
            state_surface: State Surface for artifact management
        """
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        
        # Journey configuration
        self.journey_id = self.JOURNEY_ID
        self.journey_name = self.JOURNEY_NAME
        
        # Telemetry
        self.telemetry_service = None
        self.health_monitor = None
    
    async def compose_journey(
        self,
        context: ExecutionContext,
        journey_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compose the file upload and materialization journey.
        
        This method orchestrates the complete journey:
        1. Validate journey parameters
        2. Execute ingest_file intent
        3. Execute save_materialization intent
        4. Return journey result with artifacts and events
        
        Args:
            context: Execution context
            journey_params: Journey parameters including:
                - file_content: File content (bytes or base64)
                - file_name: Original file name
                - content_type: Content type (structured/unstructured/hybrid)
                - file_type: File type category (pdf, csv, binary, etc.)
                - copybook_content: Optional copybook for binary files
                - auto_save: If True, automatically save after upload (default: True)
        
        Returns:
            Journey result with artifacts and events
        """
        journey_params = journey_params or {}
        
        self.logger.info(f"Composing journey: {self.journey_name}")
        
        # Initialize telemetry if needed
        await self._ensure_telemetry()
        
        # Record journey start
        journey_execution_id = generate_event_id()
        await self._record_telemetry({
            "action": "journey_started",
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id
        }, context.tenant_id)
        
        try:
            # Step 1: Validate journey parameters
            validation_result = self._validate_journey_params(journey_params)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid journey parameters: {validation_result['error']}")
            
            # Step 2: Execute ingest_file
            ingest_result = await self._execute_ingest_file(context, journey_params)
            
            if not ingest_result.get("success", False):
                raise RuntimeError(f"ingest_file failed: {ingest_result.get('error', 'Unknown error')}")
            
            artifact_id = ingest_result.get("artifact_id")
            
            # Step 3: Execute save_materialization (if auto_save is True, default)
            auto_save = journey_params.get("auto_save", True)
            materialization_result = None
            
            if auto_save:
                materialization_result = await self._execute_save_materialization(
                    context,
                    artifact_id=artifact_id,
                    boundary_contract_id=ingest_result.get("boundary_contract_id"),
                    content_type=journey_params.get("content_type"),
                    file_type=journey_params.get("file_type")
                )
                
                if not materialization_result.get("success", False):
                    raise RuntimeError(f"save_materialization failed: {materialization_result.get('error', 'Unknown error')}")
            
            # Build journey result
            journey_result = self._build_journey_result(
                ingest_result=ingest_result,
                materialization_result=materialization_result,
                journey_execution_id=journey_execution_id,
                auto_save=auto_save
            )
            
            # Record journey completion
            await self._record_telemetry({
                "action": "journey_completed",
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "artifact_id": artifact_id,
                "auto_save": auto_save
            }, context.tenant_id)
            
            return journey_result
            
        except Exception as e:
            self.logger.error(f"Journey failed: {e}", exc_info=True)
            
            # Record journey failure
            await self._record_telemetry({
                "action": "journey_failed",
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "error": str(e)
            }, context.tenant_id)
            
            return {
                "success": False,
                "error": str(e),
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "artifacts": {},
                "events": [
                    {
                        "type": "journey_failed",
                        "journey_id": self.journey_id,
                        "error": str(e)
                    }
                ]
            }
    
    def _validate_journey_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate journey parameters."""
        # Required parameters
        if not params.get("file_content"):
            return {"valid": False, "error": "file_content is required"}
        
        if not params.get("file_name"):
            return {"valid": False, "error": "file_name is required"}
        
        # Optional parameters with defaults
        content_type = params.get("content_type", "unstructured")
        if content_type not in ["structured", "unstructured", "hybrid"]:
            return {"valid": False, "error": f"Invalid content_type: {content_type}"}
        
        # Binary files require copybook
        file_type = params.get("file_type", "").lower()
        if file_type in ["binary", "cobol", "ebcdic"] and not params.get("copybook_content"):
            return {"valid": False, "error": "copybook_content is required for binary files"}
        
        return {"valid": True}
    
    async def _execute_ingest_file(
        self,
        context: ExecutionContext,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute ingest_file intent.
        
        Creates file artifact with lifecycle_state: "PENDING"
        """
        self.logger.info("Executing ingest_file intent")
        
        try:
            # Get file content and metadata
            file_content = params.get("file_content")
            file_name = params.get("file_name")
            content_type = params.get("content_type", "unstructured")
            file_type = params.get("file_type", "unknown")
            copybook_content = params.get("copybook_content")
            
            # Calculate content fingerprint for idempotency
            if isinstance(file_content, str):
                content_bytes = file_content.encode('utf-8')
            else:
                content_bytes = file_content
            
            content_fingerprint = hashlib.sha256(
                content_bytes + context.session_id.encode('utf-8')
            ).hexdigest()
            
            # Generate artifact ID
            artifact_id = generate_event_id()
            boundary_contract_id = generate_event_id()
            
            # Create artifact record
            artifact_record = ArtifactRecord(
                artifact_id=artifact_id,
                artifact_type="file",
                semantic_descriptor=SemanticDescriptor(
                    domain="content",
                    entity_type="file",
                    description=f"Uploaded file: {file_name}",
                    tags=[content_type, file_type]
                ),
                produced_by=ProducedBy(
                    intent_type="ingest_file",
                    execution_id=context.execution_id,
                    service_id="file_upload_materialization_journey"
                ),
                lifecycle_state=LifecycleState.PENDING,
                materializations=[],
                tenant_id=context.tenant_id
            )
            
            # Store file via Public Works
            storage_location = None
            if self.public_works:
                try:
                    file_storage = self.public_works.get_file_storage_abstraction()
                    if file_storage:
                        upload_result = await file_storage.upload_file(
                            file_content=content_bytes,
                            file_name=file_name,
                            content_type=self._get_mime_type(file_type),
                            tenant_id=context.tenant_id,
                            metadata={
                                "artifact_id": artifact_id,
                                "content_type": content_type,
                                "file_type": file_type,
                                "content_fingerprint": content_fingerprint
                            }
                        )
                        storage_location = upload_result.get("storage_location") or upload_result.get("file_path")
                except Exception as e:
                    self.logger.warning(f"File storage upload failed: {e}")
            
            # Add materialization
            materialization = Materialization(
                materialization_type="gcs",
                location=storage_location or f"gs://bucket/{context.tenant_id}/{artifact_id}/{file_name}",
                format=file_type,
                is_primary=True
            )
            artifact_record.materializations.append(materialization)
            
            # Register artifact in State Surface
            if self.state_surface:
                await self.state_surface.register_artifact(artifact_record)
            elif context.state_surface:
                await context.state_surface.register_artifact(artifact_record)
            
            return {
                "success": True,
                "artifact_id": artifact_id,
                "boundary_contract_id": boundary_contract_id,
                "content_fingerprint": content_fingerprint,
                "storage_location": storage_location,
                "lifecycle_state": "PENDING",
                "file_name": file_name,
                "content_type": content_type,
                "file_type": file_type
            }
            
        except Exception as e:
            self.logger.error(f"ingest_file failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def _execute_save_materialization(
        self,
        context: ExecutionContext,
        artifact_id: str,
        boundary_contract_id: str,
        content_type: str,
        file_type: str
    ) -> Dict[str, Any]:
        """
        Execute save_materialization intent.
        
        Transitions file artifact lifecycle_state: "PENDING" → "READY"
        Creates pending parsing journey.
        """
        self.logger.info(f"Executing save_materialization for artifact: {artifact_id}")
        
        try:
            # Calculate materialization fingerprint
            materialization_fingerprint = hashlib.sha256(
                f"{artifact_id}:{boundary_contract_id}:{context.session_id}".encode('utf-8')
            ).hexdigest()
            
            # Update artifact lifecycle state
            state_surface = self.state_surface or context.state_surface
            if state_surface:
                await state_surface.update_artifact_lifecycle(
                    artifact_id=artifact_id,
                    new_state=LifecycleState.READY,
                    tenant_id=context.tenant_id
                )
            
            # Create pending parsing journey
            pending_journey_id = generate_event_id()
            pending_intent_context = {
                "artifact_id": artifact_id,
                "content_type": content_type,
                "file_type": file_type,
                "boundary_contract_id": boundary_contract_id
            }
            
            # Store pending journey in State Surface
            if state_surface:
                await state_surface.set_execution_state(
                    key=f"pending_journey_{pending_journey_id}",
                    state={
                        "journey_type": "file_parsing",
                        "status": "PENDING",
                        "artifact_id": artifact_id,
                        "content_type": content_type,
                        "file_type": file_type,
                        "created_at": self.clock.now_utc().isoformat()
                    },
                    tenant_id=context.tenant_id
                )
            
            return {
                "success": True,
                "artifact_id": artifact_id,
                "lifecycle_state": "READY",
                "materialization_fingerprint": materialization_fingerprint,
                "pending_journey_id": pending_journey_id,
                "pending_journey_type": "file_parsing",
                "pending_intent_context": pending_intent_context
            }
            
        except Exception as e:
            self.logger.error(f"save_materialization failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _build_journey_result(
        self,
        ingest_result: Dict[str, Any],
        materialization_result: Optional[Dict[str, Any]],
        journey_execution_id: str,
        auto_save: bool
    ) -> Dict[str, Any]:
        """Build structured journey result."""
        artifact_id = ingest_result.get("artifact_id")
        
        # Determine lifecycle state
        if auto_save and materialization_result:
            lifecycle_state = "READY"
        else:
            lifecycle_state = "PENDING"
        
        # Build semantic payload
        semantic_payload = {
            "artifact_id": artifact_id,
            "artifact_type": "file",
            "lifecycle_state": lifecycle_state,
            "file_name": ingest_result.get("file_name"),
            "content_type": ingest_result.get("content_type"),
            "file_type": ingest_result.get("file_type"),
            "content_fingerprint": ingest_result.get("content_fingerprint"),
            "journey_execution_id": journey_execution_id
        }
        
        # Add materialization info if saved
        if materialization_result:
            semantic_payload["materialization_fingerprint"] = materialization_result.get("materialization_fingerprint")
            semantic_payload["pending_journey_id"] = materialization_result.get("pending_journey_id")
        
        # Build renderings
        renderings = {
            "ingest_result": ingest_result,
            "materialization_result": materialization_result
        }
        
        # Create structured artifact
        artifact = create_structured_artifact(
            result_type="file_upload_materialization",
            semantic_payload=semantic_payload,
            renderings=renderings
        )
        
        # Build events
        events = [
            {
                "type": "file_ingested",
                "artifact_id": artifact_id,
                "journey_execution_id": journey_execution_id
            }
        ]
        
        if auto_save and materialization_result:
            events.append({
                "type": "file_materialized",
                "artifact_id": artifact_id,
                "lifecycle_state": "READY",
                "pending_journey_id": materialization_result.get("pending_journey_id")
            })
            events.append({
                "type": "pending_journey_created",
                "journey_type": "file_parsing",
                "pending_journey_id": materialization_result.get("pending_journey_id"),
                "artifact_id": artifact_id
            })
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifact_id": artifact_id,
            "lifecycle_state": lifecycle_state,
            "artifacts": {
                "file": artifact
            },
            "events": events
        }
    
    def _get_mime_type(self, file_type: str) -> str:
        """Get MIME type from file type."""
        mime_types = {
            "pdf": "application/pdf",
            "csv": "text/csv",
            "json": "application/json",
            "xml": "application/xml",
            "txt": "text/plain",
            "binary": "application/octet-stream",
            "cobol": "application/octet-stream",
            "ebcdic": "application/octet-stream",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xls": "application/vnd.ms-excel"
        }
        return mime_types.get(file_type.lower(), "application/octet-stream")
    
    async def _ensure_telemetry(self):
        """Ensure telemetry service is initialized."""
        if not self.telemetry_service and self.public_works:
            try:
                from symphainy_platform.civic_systems.agentic.telemetry.agentic_telemetry_service import AgenticTelemetryService
                self.telemetry_service = AgenticTelemetryService()
            except Exception as e:
                self.logger.debug(f"Telemetry service not available: {e}")
    
    async def _record_telemetry(self, data: Dict[str, Any], tenant_id: str):
        """Record telemetry data."""
        if self.telemetry_service:
            try:
                await self.telemetry_service.record_event(
                    event_type="journey_telemetry",
                    event_data={"journey_id": self.journey_id, **data},
                    tenant_id=tenant_id
                )
            except Exception as e:
                self.logger.debug(f"Telemetry recording failed: {e}")
    
    # ========================================
    # SOA API Handlers (for MCP Tool exposure)
    # ========================================
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """
        Get SOA API definitions for this journey.
        
        These will be registered as MCP tools by ContentSolutionMCPServer.
        
        Returns:
            Dict of SOA API definitions
        """
        return {
            "upload_file": {
                "handler": self._handle_upload_file,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_content": {
                            "type": "string",
                            "description": "File content (base64 encoded)"
                        },
                        "file_name": {
                            "type": "string",
                            "description": "Original file name"
                        },
                        "content_type": {
                            "type": "string",
                            "enum": ["structured", "unstructured", "hybrid"],
                            "description": "Content type category"
                        },
                        "file_type": {
                            "type": "string",
                            "description": "File type (pdf, csv, json, etc.)"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "User context (tenant_id, session_id)"
                        }
                    },
                    "required": ["file_content", "file_name"]
                },
                "description": "Upload a file to the platform (creates PENDING artifact)"
            },
            "save_materialization": {
                "handler": self._handle_save_materialization,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "artifact_id": {
                            "type": "string",
                            "description": "Artifact ID from upload"
                        },
                        "boundary_contract_id": {
                            "type": "string",
                            "description": "Boundary contract ID"
                        },
                        "content_type": {
                            "type": "string",
                            "description": "Content type"
                        },
                        "file_type": {
                            "type": "string",
                            "description": "File type"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "User context (tenant_id, session_id)"
                        }
                    },
                    "required": ["artifact_id"]
                },
                "description": "Save file materialization (transitions PENDING → READY, creates pending parsing journey)"
            },
            "upload_and_materialize": {
                "handler": self._handle_upload_and_materialize,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_content": {
                            "type": "string",
                            "description": "File content (base64 encoded)"
                        },
                        "file_name": {
                            "type": "string",
                            "description": "Original file name"
                        },
                        "content_type": {
                            "type": "string",
                            "enum": ["structured", "unstructured", "hybrid"],
                            "description": "Content type category"
                        },
                        "file_type": {
                            "type": "string",
                            "description": "File type (pdf, csv, json, etc.)"
                        },
                        "copybook_content": {
                            "type": "string",
                            "description": "Copybook content for binary files"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "User context (tenant_id, session_id)"
                        }
                    },
                    "required": ["file_content", "file_name"]
                },
                "description": "Complete file upload and materialization journey (upload + save in one step)"
            }
        }
    
    async def _handle_upload_file(self, **kwargs) -> Dict[str, Any]:
        """SOA API handler for upload_file."""
        user_context = kwargs.get("user_context", {})
        
        context = ExecutionContext(
            execution_id=generate_event_id(),
            tenant_id=user_context.get("tenant_id", "default"),
            session_id=user_context.get("session_id", generate_event_id()),
            solution_id=user_context.get("solution_id", "content_solution")
        )
        context.state_surface = self.state_surface
        
        return await self._execute_ingest_file(context, {
            "file_content": kwargs.get("file_content"),
            "file_name": kwargs.get("file_name"),
            "content_type": kwargs.get("content_type", "unstructured"),
            "file_type": kwargs.get("file_type", "unknown")
        })
    
    async def _handle_save_materialization(self, **kwargs) -> Dict[str, Any]:
        """SOA API handler for save_materialization."""
        user_context = kwargs.get("user_context", {})
        
        context = ExecutionContext(
            execution_id=generate_event_id(),
            tenant_id=user_context.get("tenant_id", "default"),
            session_id=user_context.get("session_id", generate_event_id()),
            solution_id=user_context.get("solution_id", "content_solution")
        )
        context.state_surface = self.state_surface
        
        return await self._execute_save_materialization(
            context,
            artifact_id=kwargs.get("artifact_id"),
            boundary_contract_id=kwargs.get("boundary_contract_id", generate_event_id()),
            content_type=kwargs.get("content_type", "unstructured"),
            file_type=kwargs.get("file_type", "unknown")
        )
    
    async def _handle_upload_and_materialize(self, **kwargs) -> Dict[str, Any]:
        """SOA API handler for upload_and_materialize (complete journey)."""
        user_context = kwargs.get("user_context", {})
        
        context = ExecutionContext(
            execution_id=generate_event_id(),
            tenant_id=user_context.get("tenant_id", "default"),
            session_id=user_context.get("session_id", generate_event_id()),
            solution_id=user_context.get("solution_id", "content_solution")
        )
        context.state_surface = self.state_surface
        
        return await self.compose_journey(context, {
            "file_content": kwargs.get("file_content"),
            "file_name": kwargs.get("file_name"),
            "content_type": kwargs.get("content_type", "unstructured"),
            "file_type": kwargs.get("file_type", "unknown"),
            "copybook_content": kwargs.get("copybook_content"),
            "auto_save": True
        })
