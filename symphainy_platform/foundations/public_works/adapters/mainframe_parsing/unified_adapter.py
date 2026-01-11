"""
Unified Mainframe Processing Adapter

Unified adapter with automatic strategy selection (Custom or Cobrix).

WHAT (Infrastructure): I provide mainframe parsing with automatic strategy selection
HOW (Adapter): I coordinate between Custom and Cobrix strategies
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from symphainy_platform.foundations.public_works.protocols.file_parsing_protocol import (
    FileParsingResult
)
from .base import MainframeParsingStrategy
from .custom_strategy import CustomMainframeStrategy
from .cobrix_strategy import CobrixMainframeStrategy

logger = logging.getLogger(__name__)


class MainframeProcessingAdapter:
    """
    Unified Mainframe Processing Adapter.
    
    Provides mainframe parsing with automatic strategy selection:
    - Custom strategy (pure Python, faster for small files)
    - Cobrix strategy (industry standard, better for complex/large files)
    """
    
    def __init__(
        self,
        state_surface: Any,
        cobrix_service_url: Optional[str] = None,
        prefer_cobrix: bool = False
    ):
        """
        Initialize Unified Mainframe Processing Adapter.
        
        Args:
            state_surface: State Surface instance for file retrieval
            cobrix_service_url: Cobrix service URL (optional)
            prefer_cobrix: Whether to prefer Cobrix over Custom (default: False)
        """
        self.state_surface = state_surface
        self.cobrix_service_url = cobrix_service_url
        self.prefer_cobrix = prefer_cobrix
        self.logger = logger
        
        # Initialize strategies
        self.custom_strategy = CustomMainframeStrategy(state_surface)
        self.cobrix_strategy = None
        if cobrix_service_url:
            self.cobrix_strategy = CobrixMainframeStrategy(state_surface, cobrix_service_url)
        
        self.logger.info("✅ Unified Mainframe Processing Adapter initialized")
    
    async def parse_file(
        self,
        file_reference: str,
        copybook_reference: str,
        options: Dict[str, Any]
    ) -> FileParsingResult:
        """
        Parse mainframe file with automatic strategy selection.
        
        Strategy selection logic:
        1. User preference (prefer_cobrix, prefer_custom)
        2. File size (>10MB → Cobrix)
        3. Copybook complexity (OCCURS, REDEFINES → Cobrix)
        4. Default: Custom (simpler, faster for most cases)
        
        Args:
            file_reference: State Surface reference to binary file
            copybook_reference: State Surface reference to copybook file
            options: Parsing options (encoding, record_format, etc.)
        
        Returns:
            FileParsingResult with parsed records and validation_rules
        """
        try:
            # Select strategy (with async checks)
            strategy = await self._select_strategy(file_reference, copybook_reference, options)
            
            if not strategy:
                return FileParsingResult(
                    success=False,
                    error="No suitable strategy available",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Parse using selected strategy
            return await strategy.parse_file(file_reference, copybook_reference, options)
        
        except Exception as e:
            self.logger.error(f"❌ Mainframe parsing failed: {e}", exc_info=True)
            return FileParsingResult(
                success=False,
                error=f"Mainframe parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def _select_strategy(
        self,
        file_reference: str,
        copybook_reference: str,
        options: Dict[str, Any]
    ) -> Optional[MainframeParsingStrategy]:
        """
        Select appropriate strategy based on file characteristics.
        
        Args:
            file_reference: State Surface reference to binary file
            copybook_reference: State Surface reference to copybook file
            options: Parsing options
        
        Returns:
            Selected strategy or None
        """
        # Check user preference
        if options.get("prefer_cobrix") and self.cobrix_strategy:
            self.logger.info("📊 Strategy selection: User prefers Cobrix")
            return self.cobrix_strategy
        
        if options.get("prefer_custom"):
            self.logger.info("📊 Strategy selection: User prefers Custom")
            return self.custom_strategy
        
        # Check file size (>10MB → Cobrix)
        try:
            file_metadata = await self.state_surface.get_file_metadata(file_reference)
            if file_metadata:
                file_size = file_metadata.get("size", 0)
                if file_size > 10 * 1024 * 1024:  # 10MB
                    if self.cobrix_strategy:
                        self.logger.info(f"📊 Strategy selection: Large file ({file_size} bytes) → Cobrix")
                        return self.cobrix_strategy
        except Exception as e:
            self.logger.warning(f"Failed to get file metadata: {e}")
        
        # Check copybook complexity (OCCURS, REDEFINES → Cobrix)
        try:
            copybook_data = await self.state_surface.get_file(copybook_reference)
            if copybook_data:
                copybook_content = copybook_data.decode('utf-8')
                if 'OCCURS' in copybook_content.upper() or 'REDEFINES' in copybook_content.upper():
                    if self.cobrix_strategy:
                        self.logger.info("📊 Strategy selection: Complex copybook (OCCURS/REDEFINES) → Cobrix")
                        return self.cobrix_strategy
        except Exception as e:
            self.logger.warning(f"Failed to check copybook complexity: {e}")
        
        # Default: Custom (simpler, faster for most cases)
        self.logger.info("📊 Strategy selection: Default → Custom")
        return self.custom_strategy
