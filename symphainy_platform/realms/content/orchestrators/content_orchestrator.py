"""
Content Orchestrator - Coordinates Content Operations

Coordinates enabling services for content processing.

WHAT (Orchestrator Role): I coordinate content operations
HOW (Orchestrator Implementation): I route intents to enabling services and compose results

⚠️ CRITICAL: Orchestrators coordinate within a single intent only.
They may NOT spawn long-running sagas, manage retries, or track cross-intent progress.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional

from utilities import get_logger
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.runtime.execution_context import ExecutionContext
from ..enabling_services.file_parser_service import FileParserService


class ContentOrchestrator:
    """
    Content Orchestrator - Coordinates content operations.
    
    Coordinates:
    - File parsing
    - Embedding creation
    - Semantic storage
    """
    
    def __init__(self):
        """Initialize Content Orchestrator."""
        self.logger = get_logger(self.__class__.__name__)
        
        # Initialize enabling services
        # In production, these would be injected via DI
        self.file_parser_service = FileParserService()
    
    async def handle_intent(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle intent by coordinating enabling services.
        
        Args:
            intent: The intent to handle
            context: Runtime execution context
        
        Returns:
            Dict with "artifacts" and "events" keys
        """
        intent_type = intent.intent_type
        
        if intent_type == "ingest_file":
            return await self._handle_ingest_file(intent, context)
        elif intent_type == "parse_content":
            return await self._handle_parse_content(intent, context)
        elif intent_type == "extract_embeddings":
            return await self._handle_extract_embeddings(intent, context)
        elif intent_type == "get_parsed_file":
            return await self._handle_get_parsed_file(intent, context)
        elif intent_type == "get_semantic_interpretation":
            return await self._handle_get_semantic_interpretation(intent, context)
        else:
            raise ValueError(f"Unknown intent type: {intent_type}")
    
    async def _handle_ingest_file(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle ingest_file intent."""
        file_id = intent.parameters.get("file_id")
        
        if not file_id:
            raise ValueError("file_id is required for ingest_file intent")
        
        # Parse file
        parsed_result = await self.file_parser_service.parse_file(
            file_id=file_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        return {
            "artifacts": {
                "parsed_file_id": parsed_result.get("parsed_file_id"),
                "file_id": file_id,
                "parsing_status": "completed"
            },
            "events": [
                {
                    "type": "file_parsed",
                    "file_id": file_id,
                    "parsed_file_id": parsed_result.get("parsed_file_id")
                }
            ]
        }
    
    async def _handle_parse_content(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle parse_content intent."""
        # Similar to ingest_file, but for content that's already uploaded
        content_id = intent.parameters.get("content_id")
        
        if not content_id:
            raise ValueError("content_id is required for parse_content intent")
        
        parsed_result = await self.file_parser_service.parse_file(
            file_id=content_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        return {
            "artifacts": {
                "parsed_file_id": parsed_result.get("parsed_file_id"),
                "content_id": content_id
            },
            "events": [
                {
                    "type": "content_parsed",
                    "content_id": content_id
                }
            ]
        }
    
    async def _handle_extract_embeddings(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle extract_embeddings intent."""
        parsed_file_id = intent.parameters.get("parsed_file_id")
        
        if not parsed_file_id:
            raise ValueError("parsed_file_id is required for extract_embeddings intent")
        
        # For MVP: Return placeholder
        # In full implementation: Create embeddings via EmbeddingService
        return {
            "artifacts": {
                "embeddings_created": True,
                "parsed_file_id": parsed_file_id
            },
            "events": [
                {
                    "type": "embeddings_created",
                    "parsed_file_id": parsed_file_id
                }
            ]
        }
    
    async def _handle_get_parsed_file(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle get_parsed_file intent."""
        parsed_file_id = intent.parameters.get("parsed_file_id")
        
        if not parsed_file_id:
            raise ValueError("parsed_file_id is required for get_parsed_file intent")
        
        # Get parsed file via FileParserService
        parsed_file = await self.file_parser_service.get_parsed_file(
            parsed_file_id=parsed_file_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        return {
            "artifacts": {
                "parsed_file": parsed_file
            },
            "events": []
        }
    
    async def _handle_get_semantic_interpretation(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle get_semantic_interpretation intent."""
        parsed_file_id = intent.parameters.get("parsed_file_id")
        
        if not parsed_file_id:
            raise ValueError("parsed_file_id is required for get_semantic_interpretation intent")
        
        # For MVP: Return placeholder
        # In full implementation: Get semantic interpretation from SemanticDataAbstraction
        return {
            "artifacts": {
                "semantic_interpretation": {
                    "parsed_file_id": parsed_file_id,
                    "interpretation": "Semantic interpretation (3-layer pattern)"
                }
            },
            "events": []
        }
