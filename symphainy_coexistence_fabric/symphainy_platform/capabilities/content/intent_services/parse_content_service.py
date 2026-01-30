"""
Parse Content Intent Service (New Architecture)

Parses uploaded files to extract structured content.

Contract: docs/intent_contracts/journey_content_file_parsing/intent_parse_content.md

WHAT (Service Role): I parse uploaded files to extract structured content
HOW (Service Implementation): I use ctx.platform.parse() and track lineage

This is a REBUILD of realms/content/intent_services/parse_content_service.py
using the new PlatformIntentService architecture.

Key Changes from Legacy:
- Extends PlatformIntentService (not BaseIntentService)
- Receives PlatformContext (ctx) instead of (intent, context)
- Uses ctx.platform.parse() for parsing
- Uses ctx.platform registry helpers for pending intents and lineage
- Uses ctx.state_surface for artifact registration
- Uses ctx.governance.telemetry for telemetry
"""

from typing import Dict, Any, Optional, List
import uuid

from utilities import get_logger, generate_event_id
from symphainy_platform.civic_systems.platform_sdk import PlatformIntentService, PlatformContext
from symphainy_platform.runtime.artifact_registry import (
    SemanticDescriptor,
    ProducedBy,
    Materialization,
    LifecycleState
)
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact


class ParseContentService(PlatformIntentService):
    """
    Parse Content Intent Service (New Architecture).
    
    Handles the `parse_content` intent:
    - Validates file_id parameter
    - Checks for pending parsing intent context
    - Parses file via ctx.platform.parse()
    - Stores parsed content
    - Registers artifact in State Surface
    - Updates pending intent status
    
    Contract compliance:
    - Creates artifact with lifecycle_state: PENDING (until embedding)
    - Sets parent_artifacts for lineage tracking
    - Records telemetry for observability
    """
    
    intent_type = "parse_content"
    
    def __init__(self, service_id: Optional[str] = None):
        """
        Initialize Parse Content Service.
        
        Args:
            service_id: Optional service identifier
        """
        super().__init__(
            service_id=service_id or "parse_content_service",
            intent_type="parse_content"
        )
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute parse_content intent.
        
        Args:
            ctx: PlatformContext with full platform access
        
        Returns:
            Dict with artifacts and events
        
        Raises:
            ValueError: If file_id not provided
        """
        self.logger.info(f"📄 ParseContentService executing with PlatformContext")
        
        # Validate parameters
        file_id = ctx.intent.parameters.get("file_id")
        is_valid, error = self.validate_params(
            ctx.intent.parameters,
            required_params=["file_id"],
            param_types={"file_id": str}
        )
        if not is_valid:
            raise ValueError(error)
        
        file_reference = ctx.intent.parameters.get("file_reference")
        
        # Construct file_reference if not provided
        if not file_reference:
            file_reference = await self._resolve_file_reference(
                ctx=ctx,
                file_id=file_id
            )
        
        # Check for pending parsing intent (CTO guidance: ingest type lives with intent)
        pending_intent = await self._get_pending_intent(
            ctx=ctx,
            file_id=file_id
        )
        
        # Extract parsing parameters from pending intent or intent parameters
        parsing_type, parse_options, copybook_reference = self._extract_parsing_params(
            ctx=ctx,
            pending_intent=pending_intent
        )
        
        # Update pending intent status to in_progress
        if pending_intent:
            await self._update_pending_intent_status(
                ctx=ctx,
                pending_intent=pending_intent,
                status="in_progress"
            )
        
        # Parse file via ctx.platform.parse()
        self.logger.info(f"📄 Parsing file {file_id} with type {parsing_type or 'auto'}")
        
        # Determine file type for parsing
        file_type = parsing_type or ctx.intent.parameters.get("file_type", "text")
        
        # Use ctx.platform.parse() - the new architecture way
        if ctx.platform:
            if copybook_reference and file_type == "mainframe":
                parsed_result = await ctx.platform.parse_mainframe(
                    file_reference=file_reference,
                    copybook_reference=copybook_reference,
                    options=parse_options
                )
            else:
                parsed_result = await ctx.platform.parse(
                    file_reference=file_reference,
                    file_type=file_type,
                    options=parse_options
                )
        else:
            # Fallback if platform service not available
            self.logger.warning("ctx.platform not available, using fallback")
            parsed_result = {
                "status": "failed",
                "error": "Platform service not available"
            }
        
        # Handle parsing failure
        if parsed_result.get("status") == "failed":
            self.logger.error(f"Parsing failed: {parsed_result.get('error')}")
            # Record telemetry for failure
            await self.record_telemetry(ctx, {
                "action": "parse_content",
                "status": "failed",
                "error": parsed_result.get("error"),
                "file_id": file_id
            })
            return {
                "artifacts": {},
                "events": [{
                    "type": "content_parsing_failed",
                    "event_id": generate_event_id(),
                    "file_id": file_id,
                    "error": parsed_result.get("error")
                }]
            }
        
        # Extract parsed content details
        parsed_file_id = f"parsed_{file_id}_{uuid.uuid4().hex[:8]}"
        parsed_file_reference = f"parsed:{ctx.tenant_id}:{ctx.session_id}:{parsed_file_id}"
        parsing_type_result = parsed_result.get("file_type", parsing_type or "unknown")
        parsed_content = parsed_result.get("parsed_content", {})
        record_count = None
        
        # Calculate record count if applicable
        if isinstance(parsed_content, list):
            record_count = len(parsed_content)
        elif isinstance(parsed_content, dict) and "records" in parsed_content:
            record_count = len(parsed_content["records"])
        
        # Track parsed result for lineage
        await self._track_parsed_result(
            ctx=ctx,
            parsed_file_id=parsed_file_id,
            file_id=file_id,
            parsed_file_reference=parsed_file_reference,
            parser_type=parsing_type_result,
            parser_config=parse_options or {},
            record_count=record_count
        )
        
        # Create structured artifact
        semantic_payload = {
            "parsed_file_id": parsed_file_id,
            "parsed_file_reference": parsed_file_reference,
            "file_id": file_id,
            "parsing_type": parsing_type_result,
            "parsing_status": "success",
            "record_count": record_count,
            "parse_options": parse_options
        }
        
        # Prepare renderings (parsed data preview)
        renderings = self._prepare_renderings(parsed_content)
        
        parsed_content_artifact = create_structured_artifact(
            result_type="parsed_content",
            semantic_payload=semantic_payload,
            renderings=renderings
        )
        
        # Register artifact in State Surface
        await self._register_parsed_artifact(
            ctx=ctx,
            parsed_file_id=parsed_file_id,
            file_id=file_id,
            parsing_type_result=parsing_type_result,
            record_count=record_count
        )
        
        # Update pending intent status to completed
        if pending_intent:
            await self._update_pending_intent_status(
                ctx=ctx,
                pending_intent=pending_intent,
                status="completed"
            )
        
        # Record telemetry
        await self.record_telemetry(ctx, {
            "action": "parse_content",
            "status": "success",
            "file_id": file_id,
            "parsed_file_id": parsed_file_id,
            "parsing_type": parsing_type_result,
            "record_count": record_count
        })
        
        # Create event
        event = {
            "type": "content_parsed",
            "event_id": generate_event_id(),
            "parsed_file_id": parsed_file_id,
            "file_id": file_id,
            "parsing_type": parsing_type_result,
            "record_count": record_count
        }
        
        self.logger.info(f"✅ ParseContentService completed: {parsed_file_id}")
        
        return {
            "artifacts": {
                "parsed_file": parsed_content_artifact
            },
            "events": [event]
        }
    
    async def _resolve_file_reference(
        self,
        ctx: PlatformContext,
        file_id: str
    ) -> str:
        """
        Resolve file reference from file_id.
        
        Uses ctx.platform.get_file_metadata() to lookup actual session_id.
        """
        if ctx.platform:
            file_metadata = await ctx.platform.get_file_metadata(
                file_id=file_id,
                tenant_id=ctx.tenant_id
            )
            if file_metadata:
                actual_session_id = file_metadata.get("session_id", ctx.session_id)
                return f"file:{ctx.tenant_id}:{actual_session_id}:{file_id}"
        
        # Fallback: construct with context session_id
        return f"file:{ctx.tenant_id}:{ctx.session_id}:{file_id}"
    
    async def _get_pending_intent(
        self,
        ctx: PlatformContext,
        file_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get pending parsing intent for file.
        
        CTO guidance: ingestion_profile and file_type live with the pending intent.
        """
        if not ctx.platform:
            return None
        
        pending_intents = await ctx.platform.get_pending_intents(
            tenant_id=ctx.tenant_id,
            target_artifact_id=file_id,
            intent_type="parse_content"
        )
        
        if pending_intents:
            pending_intent = pending_intents[0]
            self.logger.info(f"Found pending intent for file {file_id}: {pending_intent.get('intent_id')}")
            return pending_intent
        
        return None
    
    def _extract_parsing_params(
        self,
        ctx: PlatformContext,
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
                ctx.intent.parameters.get("parsing_type")
            )
            parse_options = intent_context.get("parse_options", ctx.intent.parameters.get("parse_options", {}))
            copybook_reference = (
                intent_context.get("copybook_reference") or 
                ctx.intent.parameters.get("copybook_reference")
            )
            self.logger.info(f"Using pending intent context: ingestion_profile={parsing_type}")
        else:
            # No pending intent, use intent parameters directly
            parsing_type = ctx.intent.parameters.get("parsing_type")
            parse_options = ctx.intent.parameters.get("parse_options", {})
            copybook_reference = ctx.intent.parameters.get("copybook_reference")
        
        return parsing_type, parse_options, copybook_reference
    
    async def _update_pending_intent_status(
        self,
        ctx: PlatformContext,
        pending_intent: Dict[str, Any],
        status: str
    ) -> None:
        """Update pending intent status."""
        if not ctx.platform:
            return
        
        await ctx.platform.update_intent_status(
            intent_id=pending_intent["intent_id"],
            status=status,
            tenant_id=ctx.tenant_id,
            execution_id=ctx.execution_id
        )
    
    async def _track_parsed_result(
        self,
        ctx: PlatformContext,
        parsed_file_id: str,
        file_id: str,
        parsed_file_reference: str,
        parser_type: str,
        parser_config: Dict[str, Any],
        record_count: Optional[int]
    ) -> None:
        """
        Track parsed result for lineage.
        """
        if not ctx.platform:
            return
        
        await ctx.platform.track_parsed_result(
            parsed_file_id=parsed_file_id,
            file_id=file_id,
            parsed_file_reference=parsed_file_reference,
            parser_type=parser_type,
            parser_config=parser_config,
            record_count=record_count,
            status="success",
            tenant_id=ctx.tenant_id,
            session_id=ctx.session_id
        )
    
    def _prepare_renderings(
        self,
        parsed_content: Any
    ) -> Dict[str, Any]:
        """
        Prepare renderings from parsed content.
        
        Includes parsed data and preview for quick access.
        """
        renderings = {}
        
        if parsed_content:
            renderings["parsed_data"] = parsed_content
            
            # Create preview for large datasets
            if isinstance(parsed_content, list) and len(parsed_content) > 10:
                renderings["parsed_data_preview"] = parsed_content[:10]
            elif isinstance(parsed_content, dict) and len(parsed_content) > 10:
                renderings["parsed_data_preview"] = dict(list(parsed_content.items())[:10])
            else:
                renderings["parsed_data_preview"] = parsed_content
        
        return renderings
    
    async def _register_parsed_artifact(
        self,
        ctx: PlatformContext,
        parsed_file_id: str,
        file_id: str,
        parsing_type_result: str,
        record_count: Optional[int]
    ) -> None:
        """
        Register parsed content artifact in State Surface.
        """
        if not ctx.state_surface:
            self.logger.warning("State Surface not available, skipping artifact registration")
            return
        
        try:
            # GCS storage path
            parsed_file_path = f"parsed/{ctx.tenant_id}/{parsed_file_id}.json"
            
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
                execution_id=ctx.execution_id
            )
            
            # Register artifact (lifecycle_state = PENDING initially)
            artifact_registered = await ctx.state_surface.register_artifact(
                artifact_id=parsed_file_id,
                artifact_type="parsed_content",
                tenant_id=ctx.tenant_id,
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
                
                await ctx.state_surface.add_materialization(
                    artifact_id=parsed_file_id,
                    tenant_id=ctx.tenant_id,
                    materialization=materialization
                )
                
                # Update lifecycle state to READY
                await ctx.state_surface.update_artifact_lifecycle(
                    artifact_id=parsed_file_id,
                    tenant_id=ctx.tenant_id,
                    new_state=LifecycleState.READY.value,
                    reason="Parsed content stored"
                )
                
                self.logger.info(f"Registered parsed content artifact: {parsed_file_id}")
            else:
                self.logger.error(f"Failed to register artifact: {parsed_file_id}")
                
        except Exception as e:
            self.logger.error(f"Error registering parsed artifact: {e}", exc_info=True)
