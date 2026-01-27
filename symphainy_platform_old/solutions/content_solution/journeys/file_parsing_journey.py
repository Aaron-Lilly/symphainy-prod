"""
File Parsing Journey Orchestrator

Composes the file parsing journey:
1. parse_content - Resume pending parsing journey, parse file using ingest type and file type
2. save_parsed_content - Save parsed content as artifact

WHAT (Journey Role): I orchestrate file parsing
HOW (Journey Implementation): I compose parse_content + save_parsed_content intents

Key Principle: This journey RESUMES a pending parsing journey created during save_materialization.
The ingest type and file type are retrieved from the pending intent context.
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
import hashlib

from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.artifact_registry import (
    ArtifactRecord,
    SemanticDescriptor,
    ProducedBy,
    Materialization,
    LifecycleState
)
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact


class FileParsingJourney:
    """
    File Parsing Journey Orchestrator.
    
    Journey Flow:
    1. User selects uploaded file from dropdown
    2. System identifies pending parsing journey for this file
    3. User clicks "Parse File"
    4. parse_content intent executes - uses ingest type and file type from pending context
    5. Parsed content artifact created with parent lineage
    6. save_parsed_content saves the parsed content
    
    Provides MCP Tools:
    - content_parse_file: Parse a file
    - content_get_parsed_content: Get parsed content
    - content_resume_parsing: Resume pending parsing journey
    """
    
    JOURNEY_ID = "file_parsing"
    JOURNEY_NAME = "File Parsing"
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        self.journey_id = self.JOURNEY_ID
        self.journey_name = self.JOURNEY_NAME
        self.telemetry_service = None
    
    async def compose_journey(
        self,
        context: ExecutionContext,
        journey_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compose the file parsing journey.
        
        Args:
            context: Execution context
            journey_params: Journey parameters including:
                - artifact_id: File artifact to parse
                - pending_journey_id: Optional pending journey to resume
                - ingest_type: Content type (if not resuming)
                - file_type: File type (if not resuming)
                - parse_options: Optional parsing options
                - auto_save: If True, automatically save after parsing (default: True)
        """
        journey_params = journey_params or {}
        self.logger.info(f"Composing journey: {self.journey_name}")
        
        journey_execution_id = generate_event_id()
        
        try:
            # Validate parameters
            validation_result = self._validate_journey_params(journey_params)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid journey parameters: {validation_result['error']}")
            
            artifact_id = journey_params.get("artifact_id")
            pending_journey_id = journey_params.get("pending_journey_id")
            
            # Step 1: Retrieve pending journey context if resuming
            pending_context = None
            if pending_journey_id:
                pending_context = await self._get_pending_journey_context(context, pending_journey_id)
                if pending_context:
                    journey_params["ingest_type"] = pending_context.get("content_type", journey_params.get("ingest_type"))
                    journey_params["file_type"] = pending_context.get("file_type", journey_params.get("file_type"))
            
            # Step 2: Execute parse_content
            parse_result = await self._execute_parse_content(context, journey_params)
            
            if not parse_result.get("success", False):
                raise RuntimeError(f"parse_content failed: {parse_result.get('error', 'Unknown error')}")
            
            parsed_artifact_id = parse_result.get("parsed_artifact_id")
            
            # Step 3: Execute save_parsed_content (if auto_save)
            auto_save = journey_params.get("auto_save", True)
            save_result = None
            
            if auto_save:
                save_result = await self._execute_save_parsed_content(
                    context,
                    parsed_artifact_id=parsed_artifact_id,
                    parent_artifact_id=artifact_id
                )
                
                if not save_result.get("success", False):
                    raise RuntimeError(f"save_parsed_content failed: {save_result.get('error', 'Unknown error')}")
            
            # Mark pending journey as completed
            if pending_journey_id:
                await self._complete_pending_journey(context, pending_journey_id)
            
            # Build result
            return self._build_journey_result(
                parse_result=parse_result,
                save_result=save_result,
                journey_execution_id=journey_execution_id,
                auto_save=auto_save
            )
            
        except Exception as e:
            self.logger.error(f"Journey failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "artifacts": {},
                "events": [{"type": "journey_failed", "journey_id": self.journey_id, "error": str(e)}]
            }
    
    def _validate_journey_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if not params.get("artifact_id"):
            return {"valid": False, "error": "artifact_id is required"}
        return {"valid": True}
    
    async def _get_pending_journey_context(self, context: ExecutionContext, pending_journey_id: str) -> Optional[Dict[str, Any]]:
        """Get pending journey context from State Surface."""
        state_surface = self.state_surface or context.state_surface
        if state_surface:
            try:
                pending_state = await state_surface.get_execution_state(
                    f"pending_journey_{pending_journey_id}",
                    context.tenant_id
                )
                return pending_state
            except Exception as e:
                self.logger.warning(f"Could not retrieve pending journey context: {e}")
        return None
    
    async def _execute_parse_content(self, context: ExecutionContext, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute parse_content intent."""
        self.logger.info(f"Executing parse_content for artifact: {params.get('artifact_id')}")
        
        try:
            artifact_id = params.get("artifact_id")
            ingest_type = params.get("ingest_type", "unstructured")
            file_type = params.get("file_type", "unknown")
            parse_options = params.get("parse_options", {})
            
            # Calculate parsing fingerprint for idempotency
            parsing_fingerprint = hashlib.sha256(
                f"{artifact_id}:{ingest_type}:{file_type}".encode('utf-8')
            ).hexdigest()
            
            # Generate parsed artifact ID
            parsed_artifact_id = generate_event_id()
            
            # Get file content from State Surface
            file_content = None
            state_surface = self.state_surface or context.state_surface
            if state_surface:
                try:
                    file_metadata = await state_surface.get_file_metadata(artifact_id, context.tenant_id)
                    if file_metadata:
                        # Get materialization location
                        materializations = file_metadata.get("materializations", [])
                        if materializations:
                            storage_location = materializations[0].get("location")
                            # Download content via Public Works
                            if self.public_works and storage_location:
                                file_storage = self.public_works.get_file_storage_abstraction()
                                if file_storage:
                                    file_content = await file_storage.download_file(storage_location)
                except Exception as e:
                    self.logger.warning(f"Could not retrieve file content: {e}")
            
            # Parse content (simplified - in real impl would use FileParserService)
            parsed_content = {
                "source_artifact_id": artifact_id,
                "ingest_type": ingest_type,
                "file_type": file_type,
                "parsed_at": self.clock.now_utc().isoformat(),
                "structure": {},
                "chunks": []
            }
            
            if file_content:
                # Simple text extraction for demo
                if isinstance(file_content, bytes):
                    try:
                        parsed_content["text_content"] = file_content.decode('utf-8')[:1000]  # First 1000 chars
                    except:
                        parsed_content["text_content"] = "[Binary content]"
            
            # Create parsed content artifact
            artifact_record = ArtifactRecord(
                artifact_id=parsed_artifact_id,
                artifact_type="parsed_content",
                semantic_descriptor=SemanticDescriptor(
                    domain="content",
                    entity_type="parsed_content",
                    description=f"Parsed content from artifact {artifact_id}",
                    tags=[ingest_type, file_type, "parsed"]
                ),
                produced_by=ProducedBy(
                    intent_type="parse_content",
                    execution_id=context.execution_id,
                    service_id="file_parsing_journey"
                ),
                lifecycle_state=LifecycleState.PENDING,
                materializations=[],
                tenant_id=context.tenant_id,
                parent_artifacts=[artifact_id]
            )
            
            # Register artifact
            if state_surface:
                await state_surface.register_artifact(artifact_record)
            
            return {
                "success": True,
                "parsed_artifact_id": parsed_artifact_id,
                "parsing_fingerprint": parsing_fingerprint,
                "parent_artifact_id": artifact_id,
                "ingest_type": ingest_type,
                "file_type": file_type,
                "parsed_content": parsed_content
            }
            
        except Exception as e:
            self.logger.error(f"parse_content failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def _execute_save_parsed_content(self, context: ExecutionContext, parsed_artifact_id: str, parent_artifact_id: str) -> Dict[str, Any]:
        """Execute save_parsed_content intent."""
        self.logger.info(f"Executing save_parsed_content for: {parsed_artifact_id}")
        
        try:
            # Update artifact lifecycle to READY
            state_surface = self.state_surface or context.state_surface
            if state_surface:
                await state_surface.update_artifact_lifecycle(
                    artifact_id=parsed_artifact_id,
                    new_state=LifecycleState.READY,
                    tenant_id=context.tenant_id
                )
            
            # Calculate fingerprint
            fingerprint = hashlib.sha256(
                f"{parsed_artifact_id}:{context.session_id}".encode('utf-8')
            ).hexdigest()
            
            return {
                "success": True,
                "parsed_artifact_id": parsed_artifact_id,
                "lifecycle_state": "READY",
                "parsed_content_fingerprint": fingerprint
            }
            
        except Exception as e:
            self.logger.error(f"save_parsed_content failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def _complete_pending_journey(self, context: ExecutionContext, pending_journey_id: str):
        """Mark pending journey as completed."""
        state_surface = self.state_surface or context.state_surface
        if state_surface:
            try:
                await state_surface.set_execution_state(
                    key=f"pending_journey_{pending_journey_id}",
                    state={
                        "status": "COMPLETED",
                        "completed_at": self.clock.now_utc().isoformat()
                    },
                    tenant_id=context.tenant_id
                )
            except Exception as e:
                self.logger.warning(f"Could not update pending journey status: {e}")
    
    def _build_journey_result(self, parse_result: Dict, save_result: Optional[Dict], journey_execution_id: str, auto_save: bool) -> Dict[str, Any]:
        parsed_artifact_id = parse_result.get("parsed_artifact_id")
        lifecycle_state = "READY" if auto_save and save_result else "PENDING"
        
        semantic_payload = {
            "parsed_artifact_id": parsed_artifact_id,
            "artifact_type": "parsed_content",
            "lifecycle_state": lifecycle_state,
            "parent_artifact_id": parse_result.get("parent_artifact_id"),
            "ingest_type": parse_result.get("ingest_type"),
            "file_type": parse_result.get("file_type"),
            "parsing_fingerprint": parse_result.get("parsing_fingerprint"),
            "journey_execution_id": journey_execution_id
        }
        
        renderings = {"parse_result": parse_result, "save_result": save_result}
        
        artifact = create_structured_artifact(
            result_type="file_parsing",
            semantic_payload=semantic_payload,
            renderings=renderings
        )
        
        events = [{"type": "file_parsed", "parsed_artifact_id": parsed_artifact_id}]
        if auto_save and save_result:
            events.append({"type": "parsed_content_saved", "parsed_artifact_id": parsed_artifact_id, "lifecycle_state": "READY"})
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "parsed_artifact_id": parsed_artifact_id,
            "lifecycle_state": lifecycle_state,
            "artifacts": {"parsed_content": artifact},
            "events": events
        }
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get SOA API definitions for MCP tool registration."""
        return {
            "parse_file": {
                "handler": self._handle_parse_file,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "artifact_id": {"type": "string", "description": "File artifact ID to parse"},
                        "ingest_type": {"type": "string", "description": "Content type (structured/unstructured/hybrid)"},
                        "file_type": {"type": "string", "description": "File type (pdf, csv, etc.)"},
                        "parse_options": {"type": "object", "description": "Optional parsing options"},
                        "user_context": {"type": "object", "description": "User context"}
                    },
                    "required": ["artifact_id"]
                },
                "description": "Parse a file and create parsed content artifact"
            },
            "resume_parsing": {
                "handler": self._handle_resume_parsing,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pending_journey_id": {"type": "string", "description": "Pending parsing journey ID"},
                        "artifact_id": {"type": "string", "description": "File artifact ID"},
                        "user_context": {"type": "object", "description": "User context"}
                    },
                    "required": ["pending_journey_id", "artifact_id"]
                },
                "description": "Resume a pending parsing journey"
            }
        }
    
    async def _handle_parse_file(self, **kwargs) -> Dict[str, Any]:
        user_context = kwargs.get("user_context", {})
        context = ExecutionContext(
            execution_id=generate_event_id(),
            tenant_id=user_context.get("tenant_id", "default"),
            session_id=user_context.get("session_id", generate_event_id()),
            solution_id=user_context.get("solution_id", "content_solution")
        )
        context.state_surface = self.state_surface
        
        return await self.compose_journey(context, {
            "artifact_id": kwargs.get("artifact_id"),
            "ingest_type": kwargs.get("ingest_type", "unstructured"),
            "file_type": kwargs.get("file_type", "unknown"),
            "parse_options": kwargs.get("parse_options"),
            "auto_save": True
        })
    
    async def _handle_resume_parsing(self, **kwargs) -> Dict[str, Any]:
        user_context = kwargs.get("user_context", {})
        context = ExecutionContext(
            execution_id=generate_event_id(),
            tenant_id=user_context.get("tenant_id", "default"),
            session_id=user_context.get("session_id", generate_event_id()),
            solution_id=user_context.get("solution_id", "content_solution")
        )
        context.state_surface = self.state_surface
        
        return await self.compose_journey(context, {
            "artifact_id": kwargs.get("artifact_id"),
            "pending_journey_id": kwargs.get("pending_journey_id"),
            "auto_save": True
        })
