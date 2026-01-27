"""
Mainframe Parsing Strategy Protocol

Base protocol for mainframe parsing strategies (Custom and Cobrix).

WHAT (Infrastructure): I define how mainframe files should be parsed
HOW (Protocol): I provide the interface for mainframe parsing strategies
"""

from typing import Protocol, Dict, Any
from symphainy_platform.foundations.public_works.protocols.file_parsing_protocol import (
    FileParsingResult
)


class MainframeParsingStrategy(Protocol):
    """
    Protocol for mainframe parsing strategies.
    
    All strategies must:
    - Use State Surface for file retrieval (not accept bytes directly)
    - Return FileParsingResult with proper structure
    - Extract validation rules for insights pillar (where applicable)
    """
    
    async def parse_file(
        self,
        file_reference: str,  # State Surface reference
        copybook_reference: str,  # State Surface reference
        options: Dict[str, Any]
    ) -> FileParsingResult:
        """
        Parse mainframe file using copybook.
        
        Args:
            file_reference: State Surface reference to binary file
            copybook_reference: State Surface reference to copybook file
            options: Parsing options (encoding, record_format, etc.)
        
        Returns:
            FileParsingResult with parsed records and validation_rules
        """
        ...
    
    def supports_feature(self, feature: str) -> bool:
        """
        Check if strategy supports a COBOL feature.
        
        Features: "OCCURS", "REDEFINES", "COMP-3", "88-level", "VALUE",
                  "large_files", "parallel"
        
        Args:
            feature: Feature name
        
        Returns:
            True if feature is supported
        """
        ...
