"""
Create Deterministic Embeddings Intent Service (New Architecture)

Creates deterministic embeddings (schema fingerprints + pattern signatures) from parsed content.

Contract: docs/intent_contracts/journey_content_deterministic_embedding/intent_create_deterministic_embeddings.md

WHAT (Service Role): I create deterministic embeddings from parsed content
HOW (Service Implementation): I use ctx.platform.create_deterministic_embeddings()

This is a REBUILD of realms/content/intent_services/create_deterministic_embeddings_service.py
using the new PlatformIntentService architecture.

Key Changes from Legacy:
- Extends PlatformIntentService (not BaseIntentService)
- Receives PlatformContext (ctx) instead of (intent, context)
- Uses ctx.platform.get_parsed_file() to retrieve parsed content
- Uses ctx.platform.create_deterministic_embeddings() for embedding creation
- Uses ctx.governance.telemetry for telemetry

Deterministic Embeddings:
- Schema Fingerprint: Hash of column structure (names, types, positions, constraints)
- Pattern Signature: Statistical signature of data patterns (distributions, formats, ranges)
- Idempotent: Same input always produces same output
- Use Case: Schema matching, data profiling, structural similarity
"""

from typing import Dict, Any, Optional

from utilities import get_logger, generate_event_id
from symphainy_platform.civic_systems.platform_sdk import PlatformIntentService, PlatformContext
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact


class CreateDeterministicEmbeddingsService(PlatformIntentService):
    """
    Create Deterministic Embeddings Intent Service (New Architecture).
    
    Handles the `create_deterministic_embeddings` intent:
    - Validates parsed_file_id parameter
    - Retrieves parsed content via ctx.platform.get_parsed_file()
    - Creates deterministic embeddings via ctx.platform.create_deterministic_embeddings()
    - Returns deterministic_embedding_id, schema_fingerprint, pattern_signature
    
    Deterministic embeddings are idempotent - same input always produces same output.
    They capture structural patterns (schema) rather than semantic meaning.
    """
    
    intent_type = "create_deterministic_embeddings"
    
    def __init__(self, service_id: Optional[str] = None):
        """
        Initialize Create Deterministic Embeddings Service.
        
        Args:
            service_id: Optional service identifier
        """
        super().__init__(
            service_id=service_id or "create_deterministic_embeddings_service",
            intent_type="create_deterministic_embeddings"
        )
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute create_deterministic_embeddings intent.
        
        Args:
            ctx: PlatformContext with full platform access
        
        Returns:
            Dict with artifacts containing deterministic embedding info
        
        Raises:
            ValueError: If parsed_file_id not provided
        """
        self.logger.info(f"🔢 CreateDeterministicEmbeddingsService executing with PlatformContext")
        
        # Validate parameters
        parsed_file_id = ctx.intent.parameters.get("parsed_file_id")
        is_valid, error = self.validate_params(
            ctx.intent.parameters,
            required_params=["parsed_file_id"],
            param_types={"parsed_file_id": str}
        )
        if not is_valid:
            raise ValueError(error)
        
        # Validate platform service is available
        if not ctx.platform:
            raise RuntimeError("Platform service not available")
        
        # Record telemetry (start)
        await self.record_telemetry(ctx, {
            "action": "create_deterministic_embeddings",
            "status": "started",
            "parsed_file_id": parsed_file_id
        })
        
        try:
            # Get execution context for library calls (maintains audit trail)
            # DISPOSABLE WRAPPER PATTERN: Pass execution context to preserve audit trail
            exec_ctx = ctx.to_execution_context()
            
            # Get parsed file content via ctx.platform
            self.logger.info(f"🔢 Getting parsed file: {parsed_file_id}")
            parsed_content = await ctx.platform.get_parsed_file(
                parsed_file_id=parsed_file_id,
                tenant_id=ctx.tenant_id,
                session_id=ctx.session_id,
                execution_context=exec_ctx
            )
            
            if not parsed_content:
                raise ValueError(f"Parsed file not found: {parsed_file_id}")
            
            # Create deterministic embeddings via ctx.platform
            self.logger.info(f"🔢 Creating deterministic embeddings for: {parsed_file_id}")
            result = await ctx.platform.create_deterministic_embeddings(
                parsed_file_id=parsed_file_id,
                parsed_content=parsed_content,
                tenant_id=ctx.tenant_id,
                session_id=ctx.session_id,
                execution_context=exec_ctx
            )
            
            if result.get("status") == "failed":
                raise RuntimeError(f"Deterministic embedding creation failed: {result.get('error')}")
            
            deterministic_embedding_id = result.get("deterministic_embedding_id")
            schema_fingerprint = result.get("schema_fingerprint")
            pattern_signature = result.get("pattern_signature")
            schema = result.get("schema")
            
            # Create structured artifact
            semantic_payload = {
                "deterministic_embedding_id": deterministic_embedding_id,
                "parsed_file_id": parsed_file_id,
                "schema_fingerprint": schema_fingerprint,
                "pattern_signature": pattern_signature,
                "schema": schema
            }
            
            embedding_artifact = create_structured_artifact(
                result_type="deterministic_embeddings",
                semantic_payload=semantic_payload,
                renderings={
                    "fingerprint": schema_fingerprint,
                    "column_count": len(schema) if schema else 0
                }
            )
            
            # Record telemetry (success)
            await self.record_telemetry(ctx, {
                "action": "create_deterministic_embeddings",
                "status": "completed",
                "parsed_file_id": parsed_file_id,
                "deterministic_embedding_id": deterministic_embedding_id,
                "column_count": len(schema) if schema else 0
            })
            
            # Create event
            event = {
                "type": "deterministic_embeddings_created",
                "event_id": generate_event_id(),
                "parsed_file_id": parsed_file_id,
                "deterministic_embedding_id": deterministic_embedding_id
            }
            
            self.logger.info(f"✅ Deterministic embeddings created: {deterministic_embedding_id}")
            
            return {
                "artifacts": {
                    "deterministic_embedding": embedding_artifact
                },
                "events": [event]
            }
            
        except Exception as e:
            # Record telemetry (failure)
            await self.record_telemetry(ctx, {
                "action": "create_deterministic_embeddings",
                "status": "failed",
                "parsed_file_id": parsed_file_id,
                "error": str(e)
            })
            raise
