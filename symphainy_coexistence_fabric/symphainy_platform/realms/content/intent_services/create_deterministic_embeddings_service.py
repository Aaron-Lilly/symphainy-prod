"""
Create Deterministic Embeddings Intent Service

Creates deterministic embeddings from parsed file content.

Contract: docs/intent_contracts/journey_content_deterministic_embedding/intent_create_deterministic_embeddings.md

WHAT (Service Role): I create deterministic embeddings from parsed content
HOW (Service Implementation): I coordinate DeterministicEmbeddingService to create schema fingerprints
"""

from typing import Dict, Any, Optional

from utilities import get_logger, generate_event_id
from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.intent_model import Intent


class CreateDeterministicEmbeddingsService(BaseIntentService):
    """
    Create Deterministic Embeddings Intent Service.
    
    Handles the `create_deterministic_embeddings` intent:
    - Validates parsed_file_id parameter
    - Retrieves parsed content via FileParserService
    - Creates deterministic embeddings via DeterministicEmbeddingService
    - Returns deterministic_embedding_id, schema_fingerprint, pattern_signature
    
    Deterministic embeddings are idempotent - same input always produces same output.
    They capture structural patterns (schema) rather than semantic meaning.
    """
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None,
        file_parser_service: Optional[Any] = None,
        deterministic_embedding_service: Optional[Any] = None
    ):
        """
        Initialize Create Deterministic Embeddings Service.
        
        Args:
            public_works: Public Works Foundation Service
            state_surface: State Surface
            file_parser_service: FileParserService instance
            deterministic_embedding_service: DeterministicEmbeddingService instance
        """
        super().__init__(
            service_id="create_deterministic_embeddings_service",
            intent_type="create_deterministic_embeddings",
            public_works=public_works,
            state_surface=state_surface
        )
        
        # Initialize file parser service
        if file_parser_service:
            self.file_parser_service = file_parser_service
        else:
            from symphainy_platform.foundations.libraries.parsing.file_parser_service import FileParserService
            self.file_parser_service = FileParserService(public_works=public_works)
        
        # Initialize deterministic embedding service
        if deterministic_embedding_service:
            self.deterministic_embedding_service = deterministic_embedding_service
        else:
            from symphainy_platform.foundations.libraries.embeddings.deterministic_embedding_service import DeterministicEmbeddingService
            self.deterministic_embedding_service = DeterministicEmbeddingService(public_works=public_works)
    
    async def execute(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Execute create_deterministic_embeddings intent.
        
        Args:
            intent: The create_deterministic_embeddings intent
            context: Execution context
        
        Returns:
            Dict with artifacts containing deterministic embedding info
        
        Raises:
            ValueError: If parsed_file_id not provided
        """
        # Validate parameters
        parsed_file_id = intent.parameters.get("parsed_file_id")
        is_valid, error = self.validate_params(
            intent.parameters,
            required_params=["parsed_file_id"],
            param_types={"parsed_file_id": str}
        )
        if not is_valid:
            raise ValueError(error)
        
        # Get parsed file content
        parsed_file = await self.file_parser_service.get_parsed_file(
            parsed_file_id=parsed_file_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        # Create deterministic embeddings
        result = await self.deterministic_embedding_service.create_deterministic_embeddings(
            parsed_file_id=parsed_file_id,
            parsed_content=parsed_file,
            context=context
        )
        
        # Create event
        event = {
            "type": "deterministic_embeddings_created",
            "event_id": generate_event_id(),
            "parsed_file_id": parsed_file_id,
            "deterministic_embedding_id": result.get("deterministic_embedding_id")
        }
        
        return {
            "artifacts": {
                "deterministic_embeddings_created": True,
                "parsed_file_id": parsed_file_id,
                "deterministic_embedding_id": result.get("deterministic_embedding_id"),
                "schema_fingerprint": result.get("schema_fingerprint"),
                "pattern_signature": result.get("pattern_signature")
            },
            "events": [event]
        }
