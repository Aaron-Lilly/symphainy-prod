"""
Copybook Preprocessing

Minimal preprocessing for Cobrix (gold standard approach).
Extracts 88-level metadata BEFORE cleaning (CRITICAL for insights pillar).

WHAT (Infrastructure): I prepare copybooks for Cobrix parsing
HOW (Preprocessor): I do minimal cleaning (trust Cobrix capabilities)
"""

import re
from typing import Dict, Any, Optional
import logging

from .metadata_extractor import MetadataExtractor

logger = logging.getLogger(__name__)


class CopybookPreprocessor:
    """
    Minimal copybook preprocessing for Cobrix.
    
    Gold standard approach: Trust Cobrix to do what it's designed to do.
    Only minimal, correct preprocessing.
    """
    
    def __init__(self):
        """Initialize Copybook Preprocessor."""
        self.logger = logger
        self.metadata_extractor = MetadataExtractor()
    
    def extract_88_level_metadata(self, copybook_text: str) -> Dict[str, Any]:
        """
        Extract 88-level metadata BEFORE cleaning (CRITICAL for insights pillar).
        
        Args:
            copybook_text: Original copybook text
        
        Returns:
            {
                "88_level_fields": [...],
                "metadata_records": [...]
            }
        """
        return self.metadata_extractor.extract_all_validation_rules(copybook_text)
    
    def clean_copybook_for_cobrix(self, copybook_text: str) -> str:
        """
        Clean copybook for Cobrix (minimal preprocessing).
        
        Cobrix needs:
        - Remove 88-level fields (Cobrix doesn't support them)
        - Remove VALUE clauses (runtime initialization, not structure)
        - Remove identifiers/sequence numbers (if present)
        - Standard COBOL format (columns 6-72) OR free-form (level at column 0)
        
        Args:
            copybook_text: Original copybook text
        
        Returns:
            Cleaned copybook text
        """
        lines = copybook_text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove sequence numbers (columns 1-6) if present
            if len(line) > 6 and line[6:7].isdigit():
                # Standard COBOL format - use columns 6-72
                line = line[6:72] if len(line) > 72 else line[6:]
            elif len(line) > 0 and line[0].isdigit():
                # Free-form COBOL - level at column 0
                # No change needed
                pass
            
            line = line.rstrip()
            
            # Skip empty lines and comments
            if not line or line.startswith('*') or line.startswith('/'):
                continue
            
            # Remove 88-level fields (Cobrix doesn't support them)
            if re.match(r'^\s*88\s+', line, re.IGNORECASE):
                continue
            
            # Remove VALUE clauses (runtime initialization, not structure)
            # Pattern: "VALUE 'something'." or "VALUE 123."
            line = re.sub(r'\s+VALUE\s+[\'"]?[^\'"]+[\'"]?\.', '', line, flags=re.IGNORECASE)
            
            # Remove identifiers if they're before level numbers
            # Pattern: "IDENTIFIER  01  FIELD-NAME"
            if re.match(r'^[A-Z0-9]{2,8}\s+\d{2}\s+', line):
                line = re.sub(r'^[A-Z0-9]{2,8}\s+', '', line)
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def normalize_file_for_cobrix(
        self,
        file_data: bytes,
        record_size: Optional[int] = None
    ) -> tuple[bytes, int, int]:
        """
        Normalize file for Cobrix (calculate offsets).
        
        Cobrix has built-in options:
        - `file_start_offset` - Skip header bytes
        - `file_trailer_length` - Skip trailer bytes
        - `record_format="F"` - Fixed-length records
        
        Args:
            file_data: File data as bytes
            record_size: Record size (if known)
        
        Returns:
            (normalized_data, file_start_offset, file_trailer_length)
        """
        # Simple header detection (first few bytes are often headers)
        # For now, assume no header (can be enhanced)
        file_start_offset = 0
        
        # Simple trailer detection (last few bytes are often trailers)
        # For now, assume no trailer (can be enhanced)
        file_trailer_length = 0
        
        # If record_size is known, calculate trailer
        if record_size and record_size > 0:
            total_size = len(file_data)
            # Calculate how many complete records fit
            complete_records = total_size // record_size
            # Trailer is the remainder
            file_trailer_length = total_size - (complete_records * record_size)
        
        return file_data, file_start_offset, file_trailer_length
