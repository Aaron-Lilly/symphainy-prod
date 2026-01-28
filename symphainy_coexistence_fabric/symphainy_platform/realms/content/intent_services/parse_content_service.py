"""
Parse Content Intent Service

Parses uploaded files to extract structured content.

Contract: docs/intent_contracts/journey_content_file_parsing/intent_parse_content.md

WHAT (Service Role): I parse uploaded files to extract structured content
HOW (Service Implementation): I coordinate FileParserService, register artifacts, track lineage
"""

from typing import Dict, Any, Optional, List
import uuid

from utilities import get_logger, generate_event_id
from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.runtime.artifact_registry import (
    SemanticDescriptor,
    ProducedBy,
    Materialization,
    LifecycleState
)
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact


class ParseContentService(BaseIntentService):
    """
    Parse Content Intent Service.
    
    Handles the `parse_content` intent:
    - Validates file_id parameter
    - Checks for pending parsing intent context
    - Parses file via FileParserService
    - Stores parsed content in GCS
    - Registers artifact in State Surface
    - Indexes artifact for discovery
    - Updates pending intent status
    
    Contract compliance:
    - Creates artifact with lifecycle_state: PENDING (until embedding)
    - Sets parent_artifacts for lineage tracking
    - Records telemetry for observability
    """
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None,
        file_parser_service: Optional[Any] = None
    ):
        """
        Initialize Parse Content Service.
        
        Args:
            public_works: Public Works Foundation Service
            state_surface: State Surface for artifact registration
            file_parser_service: FileParserService instance (optional, created if not provided)
        """
        super().__init__(
            service_id="parse_content_service",
            intent_type="parse_content",
            public_works=public_works,
            state_surface=state_surface
        )
        
        # Initialize file parser service
        if file_parser_service:
            self.file_parser_service = file_parser_service
        else:
            from symphainy_platform.foundations.libraries.parsing.file_parser_service import FileParserService
            self.file_parser_service = FileParserService(public_works=public_works)
    
    async def execute(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Execute parse_content intent.
        
        Args:
            intent: The parse_content intent
            context: Execution context
        
        Returns:
            Dict with artifacts and events
        
        Raises:
            ValueError: If file_id not provided
        """
        # Validate parameters
        file_id = intent.parameters.get("file_id")
        is_valid, error = self.validate_params(
            intent.parameters,
            required_params=["file_id"],
            param_types={"file_id": str}
        )
        if not is_valid:
            raise ValueError(error)
        
        file_reference = intent.parameters.get("file_reference")
        
        # Construct file_reference if not provided
        if not file_reference:
            file_reference = await self._resolve_file_reference(
                file_id=file_id,
                tenant_id=context.tenant_id,
                session_id=context.session_id
            )
        
        # Check for pending parsing intent (CTO guidance: ingest type lives with intent)
        pending_intent = await self._get_pending_intent(
            file_id=file_id,
            tenant_id=context.tenant_id
        )
        
        # Extract parsing parameters from pending intent or intent parameters
        parsing_type, parse_options, copybook_reference = self._extract_parsing_params(
            intent=intent,
            pending_intent=pending_intent
        )
        
        # Update pending intent status to in_progress
        if pending_intent:
            await self._update_pending_intent_status(
                pending_intent=pending_intent,
                status="in_progress",
                tenant_id=context.tenant_id,
                execution_id=context.execution_id
            )
        
        # Parse file via FileParserService
        parsed_result = await self.file_parser_service.parse_file(
            file_id=file_id,
            tenant_id=context.tenant_id,
            context=context,
            file_reference=file_reference,
            parsing_type=parsing_type,
            parse_options=parse_options,
            copybook_reference=copybook_reference
        )
        
        parsed_file_id = parsed_result.get("parsed_file_id")
        parsed_file_reference = parsed_result.get("parsed_file_reference")
        parsing_type_result = parsed_result.get("parsing_type", parsing_type or "unknown")
        parsing_status = parsed_result.get("parsing_status", "success")
        record_count = parsed_result.get("record_count")
        
        # Track parsed result for lineage
        await self._track_parsed_result(
            parsed_file_id=parsed_file_id,
            file_id=file_id,
            parsed_file_reference=parsed_file_reference,
            parser_type=parsing_type_result,
            parser_config=parse_options,
            record_count=record_count,
            status=parsing_status,
            tenant_id=context.tenant_id,
            context=context
        )
        
        # Create structured artifact
        semantic_payload = {
            "parsed_file_id": parsed_file_id,
            "parsed_file_reference": parsed_file_reference,
            "file_id": file_id,
            "parsing_type": parsing_type_result,
            "parsing_status": parsing_status,
            "record_count": record_count,
            "parse_options": parse_options
        }
        
        # Prepare renderings (parsed data preview)
        renderings = self._prepare_renderings(parsed_result)
        
        parsed_content_artifact = create_structured_artifact(
            result_type="parsed_content",
            semantic_payload=semantic_payload,
            renderings=renderings
        )
        
        # Register artifact in State Surface
        await self._register_parsed_artifact(
            parsed_file_id=parsed_file_id,
            file_id=file_id,
            parsing_type_result=parsing_type_result,
            record_count=record_count,
            context=context
        )
        
        # Update pending intent status to completed
        if pending_intent:
            await self._update_pending_intent_status(
                pending_intent=pending_intent,
                status="completed",
                tenant_id=context.tenant_id,
                execution_id=context.execution_id
            )
        
        # Create event
        event = {
            "type": "content_parsed",
            "event_id": generate_event_id(),
            "parsed_file_id": parsed_file_id,
            "file_id": file_id,
            "parsing_type": parsing_type_result,
            "record_count": record_count
        }
        
        return {
            "artifacts": {
                "parsed_file": parsed_content_artifact
            },
            "events": [event]
        }
    
    async def _resolve_file_reference(
        self,
        file_id: str,
        tenant_id: str,
        session_id: str
    ) -> str:
        """
        Resolve file reference from file_id.
        
        Looks up file metadata to get actual session_id, constructs reference.
        """
        if self.public_works:
            try:
                # Try to get file metadata from registry
                registry = getattr(self.public_works, 'registry_abstraction', None)
                if registry:
                    file_metadata = await registry.get_file_metadata(
                        file_id=file_id,
                        tenant_id=tenant_id
                    )
                    if file_metadata:
                        actual_session_id = file_metadata.get("session_id", session_id)
                        return f"file:{tenant_id}:{actual_session_id}:{file_id}"
            except Exception as e:
                self.logger.warning(f"Failed to resolve file reference: {e}")
        
        # Fallback: construct with context session_id
        return f"file:{tenant_id}:{session_id}:{file_id}"
    
    async def _get_pending_intent(
        self,
        file_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get pending parsing intent for file.
        
        CTO guidance: ingestion_profile and file_type live with the pending intent.
        """
        if not self.public_works:
            return None
        
        registry = getattr(self.public_works, 'registry_abstraction', None)
        if not registry:
            return None
        
        try:
            pending_intents = await registry.get_pending_intents(
                tenant_id=tenant_id,
                target_artifact_id=file_id,
                intent_type="parse_content"
            )
            if pending_intents:
                pending_intent = pending_intents[0]
                self.logger.info(f"Found pending intent for file {file_id}: {pending_intent.get('intent_id')}")
                return pending_intent
        except Exception as e:
            self.logger.warning(f"Failed to get pending intents: {e}")
        
        return None
    
    def _extract_parsing_params(
        self,
        intent: Intent,
        pending_intent: Optional[Dict[str, Any]]
    ) -> tuple:
        """
        Extract parsing parameters from pending intent or intent parameters.
        
        Returns:
            Tuple of (parsing_type, parse_options, copybook_reference)
        """
        if pending_intent:
            # Extract from pending intent context (ingestion_profile lives here)
            intent_context = pending_intent.get("context", {})
            parsing_type = (
                intent_context.get("ingestion_profile") or 
                intent_context.get("parsing_type") or 
                intent.parameters.get("parsing_type")
            )
            parse_options = intent_context.get("parse_options", intent.parameters.get("parse_options", {}))
            copybook_reference = (
                intent_context.get("copybook_reference") or 
                intent.parameters.get("copybook_reference")
            )
            self.logger.info(f"Using pending intent context: ingestion_profile={parsing_type}")
        else:
            # No pending intent, use intent parameters directly
            parsing_type = intent.parameters.get("parsing_type")
            parse_options = intent.parameters.get("parse_options", {})
            copybook_reference = intent.parameters.get("copybook_reference")
        
        return parsing_type, parse_options, copybook_reference
    
    async def _update_pending_intent_status(
        self,
        pending_intent: Dict[str, Any],
        status: str,
        tenant_id: str,
        execution_id: str
    ) -> None:
        """Update pending intent status."""
        if not self.public_works:
            return
        
        registry = getattr(self.public_works, 'registry_abstraction', None)
        if not registry:
            return
        
        try:
            await registry.update_intent_status(
                intent_id=pending_intent["intent_id"],
                status=status,
                tenant_id=tenant_id,
                execution_id=execution_id
            )
        except Exception as e:
            self.logger.warning(f"Failed to update pending intent status: {e}")
    
    async def _track_parsed_result(
        self,
        parsed_file_id: str,
        file_id: str,
        parsed_file_reference: str,
        parser_type: str,
        parser_config: Dict[str, Any],
        record_count: Optional[int],
        status: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> None:
        """
        Track parsed result in Supabase for lineage.
        """
        if not self.public_works:
            return
        
        registry = getattr(self.public_works, 'registry_abstraction', None)
        if not registry:
            return
        
        try:
            await registry.track_parsed_result(
                parsed_file_id=parsed_file_id,
                file_id=file_id,
                parsed_file_reference=parsed_file_reference,
                parser_type=parser_type,
                parser_config=parser_config,
                record_count=record_count,
                status=status,
                tenant_id=tenant_id,
                session_id=context.session_id
            )
        except Exception as e:
            self.logger.warning(f"Failed to track parsed result: {e}")
    
    def _prepare_renderings(
        self,
        parsed_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare renderings from parsed result.
        
        Includes parsed data and preview for quick access.
        """
        renderings = {}
        parsed_data = parsed_result.get("parsed_data")
        
        if parsed_data:
            renderings["parsed_data"] = parsed_data
            
            # Create preview for large datasets
            if isinstance(parsed_data, list) and len(parsed_data) > 10:
                renderings["parsed_data_preview"] = parsed_data[:10]
            elif isinstance(parsed_data, dict) and len(parsed_data) > 10:
                renderings["parsed_data_preview"] = dict(list(parsed_data.items())[:10])
            else:
                renderings["parsed_data_preview"] = parsed_data
        
        return renderings
    
    async def _register_parsed_artifact(
        self,
        parsed_file_id: str,
        file_id: str,
        parsing_type_result: str,
        record_count: Optional[int],
        context: ExecutionContext
    ) -> None:
        """
        Register parsed content artifact in State Surface.
        """
        if not context.state_surface:
            self.logger.warning("State Surface not available, skipping artifact registration")
            return
        
        try:
            # GCS storage path
            parsed_file_path = f"parsed/{context.tenant_id}/{parsed_file_id}.json"
            
            # Create semantic descriptor
            semantic_descriptor = SemanticDescriptor(
                schema="parsed_content_v1",
                record_count=record_count,
                parser_type=parsing_type_result,
                embedding_model=None
            )
            
            # Create produced_by (provenance)
            produced_by = ProducedBy(
                intent="parse_content",
                execution_id=context.execution_id
            )
            
            # Register artifact (lifecycle_state = PENDING initially)
            artifact_registered = await context.state_surface.register_artifact(
                artifact_id=parsed_file_id,
                artifact_type="parsed_content",
                tenant_id=context.tenant_id,
                produced_by=produced_by,
                semantic_descriptor=semantic_descriptor,
                parent_artifacts=[file_id],  # Lineage: parsed from file
                lifecycle_state=LifecycleState.PENDING.value
            )
            
            if artifact_registered:
                # Add GCS materialization
                materialization = Materialization(
                    materialization_id=f"mat_{parsed_file_id}",
                    storage_type="gcs",
                    uri=parsed_file_path,
                    format="json",
                    compression=None
                )
                
                await context.state_surface.add_materialization(
                    artifact_id=parsed_file_id,
                    tenant_id=context.tenant_id,
                    materialization=materialization
                )
                
                # Update lifecycle state to READY
                await context.state_surface.update_artifact_lifecycle(
                    artifact_id=parsed_file_id,
                    tenant_id=context.tenant_id,
                    new_state=LifecycleState.READY.value,
                    reason="Parsed content stored in GCS"
                )
                
                self.logger.info(f"Registered parsed content artifact: {parsed_file_id}")
            else:
                self.logger.error(f"Failed to register artifact: {parsed_file_id}")
                
        except Exception as e:
            self.logger.error(f"Error registering parsed artifact: {e}", exc_info=True)
