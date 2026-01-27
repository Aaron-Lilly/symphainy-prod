"""
Metadata Extractor

Extracts 88-level fields and level-01 metadata records from copybooks.
Used by both custom and Cobrix implementations.

WHAT (Infrastructure): I extract validation rules from copybook metadata
HOW (Utility): I parse COBOL copybook to find 88-level fields and metadata records
"""

import re
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """
    Extracts validation rules from copybook metadata.
    
    Extracts:
    - 88-level fields (condition names with VALUE clauses)
    - Level-01 metadata records (validation rules, allowed values)
    """
    
    def __init__(self):
        """Initialize Metadata Extractor."""
        self.logger = logger
    
    def extract_88_level_fields(self, copybook_content: str) -> List[Dict[str, Any]]:
        """
        Extract 88-level field validation rules.
        
        Args:
            copybook_content: COBOL copybook text
        
        Returns:
            List of 88-level field rules:
            [
                {
                    "field_name": "STATUS-CODE",
                    "condition_name": "ACTIVE",
                    "value": "A",
                    "line_number": 123
                },
                ...
            ]
        """
        rules = []
        lines = copybook_content.split('\n')
        cleaned_lines = self._clean_cobol_lines(lines)
        
        # Pattern for 88-level fields (condition names)
        # Example: "    88  ACTIVE      VALUE 'A'."
        pattern_88 = re.compile(r'^\s+88\s+(\S+)\s+VALUE\s+[\'"]?([^\'"]+)[\'"]?\.', re.IGNORECASE)
        
        # Track current parent field for 88-level fields
        current_parent = None
        current_level = 0
        
        for line_num, line in enumerate(cleaned_lines, 1):
            line = line.strip()
            if not line or line.startswith('*'):
                continue
            
            # Check for level number (01-49, 77, 88)
            level_match = re.match(r'^(\d{2})\s+', line)
            if level_match:
                level = int(level_match.group(1))
                
                # Track parent field for 88-level fields
                if level < 88:
                    # This is a data field (not 88-level)
                    field_match = re.match(r'^\d{2}\s+(\S+)', line)
                    if field_match:
                        current_parent = field_match.group(1)
                        current_level = level
                elif level == 88:
                    # This is an 88-level field
                    match = pattern_88.match(line)
                    if match and current_parent:
                        condition_name = match.group(1)
                        value = match.group(2).strip()
                        
                        rules.append({
                            "field_name": current_parent,
                            "condition_name": condition_name,
                            "value": value,
                            "line_number": line_num
                        })
        
        return rules
    
    def extract_level_01_metadata(self, copybook_content: str) -> List[Dict[str, Any]]:
        """
        Extract level-01 metadata record validation rules.
        
        Args:
            copybook_content: COBOL copybook text
        
        Returns:
            List of metadata record rules:
            [
                {
                    "record_name": "POLICY-TYPES",
                    "field_name": "TERM-LIFE",
                    "value": "Term Life",
                    "target_field": "POLICY-TYPE",
                    "line_number": 456
                },
                ...
            ]
        """
        rules = []
        lines = copybook_content.split('\n')
        cleaned_lines = self._clean_cobol_lines(lines)
        
        # Pattern for level-01 metadata records
        # Example: "01  POLICY-TYPES."
        pattern_01 = re.compile(r'^01\s+(\S+)\.', re.IGNORECASE)
        
        # Pattern for fields within metadata records with VALUE clauses
        # Example: "    05  TERM-LIFE    PIC X(10) VALUE 'Term Life  '."
        pattern_metadata_field = re.compile(
            r'^\s+\d{2}\s+(\S+)\s+.*?VALUE\s+[\'"]?([^\'"]+)[\'"]?\.',
            re.IGNORECASE
        )
        
        current_metadata_record = None
        in_metadata_record = False
        
        for line_num, line in enumerate(cleaned_lines, 1):
            line = line.strip()
            if not line or line.startswith('*'):
                continue
            
            # Check for level-01 metadata record
            match_01 = pattern_01.match(line)
            if match_01:
                record_name = match_01.group(1)
                # Check if this is a metadata record (not a data record)
                # Metadata records typically have names like "POLICY-TYPES", "VALIDATION-RULES", etc.
                if any(keyword in record_name.upper() for keyword in ['TYPE', 'VALIDATION', 'RULE', 'THRESHOLD', 'FLAG', 'METADATA']):
                    current_metadata_record = record_name
                    in_metadata_record = True
                    continue
                else:
                    # This is a data record, not metadata
                    in_metadata_record = False
                    current_metadata_record = None
                    continue
            
            # Extract fields within metadata records
            if in_metadata_record and current_metadata_record:
                match_field = pattern_metadata_field.match(line)
                if match_field:
                    field_name = match_field.group(1)
                    value = match_field.group(2).strip()
                    
                    # Try to infer target field from field name
                    # Example: "TERM-LIFE" in "POLICY-TYPES" record → target field is "POLICY-TYPE"
                    target_field = self._infer_target_field(field_name, current_metadata_record)
                    
                    rules.append({
                        "record_name": current_metadata_record,
                        "field_name": field_name,
                        "value": value,
                        "target_field": target_field,
                        "line_number": line_num
                    })
        
        return rules
    
    def _infer_target_field(self, field_name: str, record_name: str) -> str:
        """
        Infer target field name from metadata field name.
        
        Example:
        - "TERM-LIFE" in "POLICY-TYPES" → "POLICY-TYPE"
        - "MIN-AGE" in "AGE-VALIDATION" → "AGE"
        """
        # Simple heuristic: remove plural suffix and use record name pattern
        if record_name.upper().endswith('S'):
            # Remove 'S' suffix
            base = record_name[:-1]
            return base.replace('-TYPE', '-TYPE').replace('-VALIDATION', '').replace('-RULES', '')
        
        return record_name
    
    def extract_all_validation_rules(self, copybook_content: str) -> Dict[str, Any]:
        """
        Extract all validation rules (88-level + level-01 metadata).
        
        Args:
            copybook_content: COBOL copybook text
        
        Returns:
            {
                "88_level_fields": [...],
                "metadata_records": [...]
            }
        """
        return {
            "88_level_fields": self.extract_88_level_fields(copybook_content),
            "metadata_records": self.extract_level_01_metadata(copybook_content)
        }
    
    def _clean_cobol_lines(self, lines: List[str]) -> List[str]:
        """
        Clean COBOL lines (remove comments, handle continuation lines).
        
        Args:
            lines: List of COBOL lines
        
        Returns:
            List of cleaned lines
        """
        cleaned = []
        continuation = False
        current_line = ""
        
        for line in lines:
            # Remove sequence numbers (columns 1-6) and line numbers (columns 73-80)
            if len(line) > 6:
                line = line[6:]  # Remove columns 1-6
            if len(line) > 72:
                line = line[:72]  # Remove columns 73-80
            
            line = line.rstrip()
            
            # Handle continuation lines (line ends with -)
            if line.endswith('-'):
                continuation = True
                current_line += line[:-1]  # Remove trailing -
                continue
            elif continuation:
                current_line += line.lstrip()  # Remove leading spaces on continuation
                continuation = False
                cleaned.append(current_line)
                current_line = ""
            else:
                # Regular line
                if line and not line.startswith('*'):
                    cleaned.append(line)
        
        if current_line:
            cleaned.append(current_line)
        
        return cleaned
