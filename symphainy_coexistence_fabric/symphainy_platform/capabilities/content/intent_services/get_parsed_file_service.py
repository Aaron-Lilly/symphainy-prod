"""
Get Parsed File Service (Platform SDK)

Retrieves parsed file content by parsed_file_id.

Uses ctx.platform.get_parsed_file() for retrieval.

Contract: docs/intent_contracts/journey_content_file_parsing/intent_get_parsed_file.md
"""

from typing import Dict, Any

from utilities import get_logger

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class GetParsedFileService(PlatformIntentService):
    """
    Get Parsed File Service using Platform SDK.
    
    Handles the `get_parsed_file` intent:
    - Validates parsed_file_id parameter
    - Retrieves parsed file via ctx.platform.get_parsed_file()
    - Returns parsed content artifact
    
    This is a read-only query intent.
    """
    
    intent_type = "get_parsed_file"
    
    def __init__(self, service_id: str = "get_parsed_file_service"):
        """Initialize Get Parsed File Service."""
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute get_parsed_file intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with artifacts containing parsed file content
        """
        self.logger.info(f"Executing get_parsed_file: {ctx.execution_id}")
        
        # Validate parameters
        parsed_file_id = ctx.intent.parameters.get("parsed_file_id")
        if not parsed_file_id:
            raise ValueError("parsed_file_id is required")
        
        # Get parsed file via ctx.platform
        parsed_file = await ctx.platform.get_parsed_file(
            parsed_file_id=parsed_file_id,
            tenant_id=ctx.tenant_id,
            session_id=ctx.session_id
        )
        
        if not parsed_file:
            raise ValueError(f"Parsed file not found: {parsed_file_id}")
        
        self.logger.info(f"✅ Retrieved parsed file: {parsed_file_id}")
        
        return {
            "artifacts": {
                "parsed_file": parsed_file
            },
            "events": []
        }
