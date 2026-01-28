"""
Get Parsed File Intent Service

Retrieves parsed file content by parsed_file_id.

Contract: docs/intent_contracts/journey_content_file_parsing/intent_get_parsed_file.md

WHAT (Service Role): I retrieve parsed file content
HOW (Service Implementation): I delegate to FileParserService to retrieve parsed content
"""

from typing import Dict, Any, Optional

from utilities import get_logger
from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.intent_model import Intent


class GetParsedFileService(BaseIntentService):
    """
    Get Parsed File Intent Service.
    
    Handles the `get_parsed_file` intent:
    - Validates parsed_file_id parameter
    - Retrieves parsed file via FileParserService
    - Returns parsed content artifact
    
    This is a read-only query intent - no artifact registration required.
    """
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None,
        file_parser_service: Optional[Any] = None
    ):
        """
        Initialize Get Parsed File Service.
        
        Args:
            public_works: Public Works Foundation Service
            state_surface: State Surface
            file_parser_service: FileParserService instance
        """
        super().__init__(
            service_id="get_parsed_file_service",
            intent_type="get_parsed_file",
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
        Execute get_parsed_file intent.
        
        Args:
            intent: The get_parsed_file intent
            context: Execution context
        
        Returns:
            Dict with artifacts containing parsed file content
        
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
