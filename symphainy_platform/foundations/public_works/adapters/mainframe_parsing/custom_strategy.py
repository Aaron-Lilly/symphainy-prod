"""
Custom Mainframe Parsing Strategy

Pure Python implementation for mainframe parsing.
Production-ready, bytes-based parsing.

WHAT (Infrastructure): I parse mainframe files using custom Python implementation
HOW (Strategy): I use pure Python logic for COBOL parsing
"""

import logging
import re
import math
import codecs
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from symphainy_platform.foundations.public_works.protocols.file_parsing_protocol import (
    FileParsingResult
)
from symphainy_platform.foundations.public_works.adapters.file_parsing.metadata_extractor import (
    MetadataExtractor
)
from .base import MainframeParsingStrategy

# Optional pandas support
try:
    import pandas as pd
    pandas_available = True
except ImportError:
    pd = None
    pandas_available = False

logger = logging.getLogger(__name__)


class CustomMainframeStrategy:
    """
    Custom Mainframe Parsing Strategy.
    
    Pure Python implementation for mainframe parsing.
    Uses State Surface for file retrieval.
    """
    
    def __init__(self, state_surface: Any):
        """
        Initialize Custom Mainframe Strategy.
        
        Args:
            state_surface: State Surface instance for file retrieval
        """
        self.state_surface = state_surface
        self.logger = logger
        self.metadata_extractor = MetadataExtractor()
        self.pandas_available = pandas_available
        
        self.logger.info("✅ Custom Mainframe Strategy initialized")
    
    async def parse_file(
        self,
        file_reference: str,
        copybook_reference: str,
        options: Dict[str, Any]
    ) -> FileParsingResult:
        """
        Parse mainframe file using custom implementation.
        
        Args:
            file_reference: State Surface reference to binary file
            copybook_reference: State Surface reference to copybook file
            options: Parsing options (encoding, record_format, codepage, etc.)
        
        Returns:
            FileParsingResult with parsed records and validation_rules
        """
        try:
            # Retrieve files from State Surface
            file_data = await self.state_surface.get_file(file_reference)
            copybook_data = await self.state_surface.get_file(copybook_reference)
            
            if not file_data:
                return FileParsingResult(
                    success=False,
                    error=f"File not found: {file_reference}",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            if not copybook_data:
                return FileParsingResult(
                    success=False,
                    error=f"Copybook not found: {copybook_reference}",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Decode copybook
            try:
                copybook_content = copybook_data.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    copybook_content = copybook_data.decode('latin-1')
                except Exception as e:
                    return FileParsingResult(
                        success=False,
                        error=f"Failed to decode copybook: {e}",
                        timestamp=datetime.utcnow().isoformat()
                    )
            
            # Extract 88-level metadata BEFORE parsing (CRITICAL for insights pillar)
            validation_rules = self.metadata_extractor.extract_all_validation_rules(copybook_content)
            
            # Parse copybook
            field_definitions = await self._parse_copybook_from_string(copybook_content)
            if not field_definitions:
                return FileParsingResult(
                    success=False,
                    error="Failed to parse copybook",
                    validation_rules=validation_rules,
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Get code page from options (default to cp037)
            codepage = options.get("codepage", "cp037")
            
            # Parse binary records
            records = await self._parse_binary_records(file_data, field_definitions, codepage)
            
            if not records:
                return FileParsingResult(
                    success=False,
                    error="No records parsed from binary data",
                    validation_rules=validation_rules,
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Convert records to text representation
            text_content = self._records_to_text(records)
            
            # Build tables structure
            tables = [{
                "data": records,
                "columns": list(records[0].keys()) if records else [],
                "row_count": len(records)
            }] if records else []
            
            # Convert to DataFrame if pandas is available
            dataframe = None
            if self.pandas_available and records:
                dataframe = pd.DataFrame(records)
            
            # Build structured_data dict
            structured_data = {
                "tables": tables,
                "records": records
            }
            if dataframe is not None:
                structured_data["dataframe"] = dataframe
            
            # Build metadata
            metadata = {
                "file_type": "mainframe",
                "record_count": len(records),
                "column_count": len(records[0].keys()) if records else 0,
                "columns": list(records[0].keys()) if records else [],
                "codepage": codepage
            }
            
            # Return FileParsingResult (mapped from legacy dict format)
            return FileParsingResult(
                success=True,
                text_content=text_content,
                structured_data=structured_data,
                metadata=metadata,
                validation_rules=validation_rules,
                timestamp=datetime.utcnow().isoformat()
            )
        
        except Exception as e:
            self.logger.error(f"❌ Custom mainframe parsing failed: {e}", exc_info=True)
            return FileParsingResult(
                success=False,
                error=f"Custom mainframe parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    # ============================================================================
    # Copybook Parsing Methods
    # ============================================================================
    
    async def _parse_copybook_from_string(self, copybook_content: str) -> List[Dict[str, Any]]:
        """Parse copybook from string content using legacy approach."""
        try:
            # Use legacy clean_cobol approach to handle continuation lines
            lines = copybook_content.split('\n')
            cleaned_lines = self._clean_cobol(lines)
            
            # COBOL pattern matching (legacy pattern)
            opt_pattern_format = "({})?"
            row_pattern_base = r"^(?P<level>\d{2})\s+(?P<name>\S+)"
            row_pattern_occurs = r"\s+OCCURS (?P<occurs>\d+) TIMES"
            row_pattern_indexed_by = r"\s+INDEXED BY\s(?P<indexed_by>\S+)"
            row_pattern_redefines = r"\s+REDEFINES\s+(?P<redefines>\S+)"
            row_pattern_pic = r"\s+PIC\s+(?P<pic>\S+)"  # Legacy uses simpler pattern
            row_pattern_comp = r"\s+COMP"  # Legacy pattern
            row_pattern_binary = r"\s+BINARY"  # Legacy pattern
            row_pattern_end = r"\.$"  # Legacy requires period at end
            
            row_pattern = re.compile(
                row_pattern_base
                + opt_pattern_format.format(row_pattern_redefines)
                + opt_pattern_format.format(row_pattern_occurs)
                + opt_pattern_format.format(row_pattern_indexed_by)
                + opt_pattern_format.format(row_pattern_pic)
                + opt_pattern_format.format(row_pattern_comp)
                + opt_pattern_format.format(row_pattern_binary)
                + row_pattern_end
            )
            
            field_definitions = []
            
            # Process cleaned lines (like legacy parse_cobol)
            for line_num, line in enumerate(cleaned_lines, 1):
                # Extract OCCURS count manually (legacy approach - before pattern matching)
                occurs_count = 0
                if "OCCURS " in line and " TIMES" in line:
                    occurs_index = line.find("OCCURS ")
                    whitespace_index = occurs_index - 1
                    while whitespace_index >= 0 and line[whitespace_index] == " ":
                        whitespace_index -= 1
                    times_index = line.find(" TIMES", occurs_index)
                    if times_index > occurs_index:
                        try:
                            occurs_count = int(line[occurs_index + len("OCCURS "):times_index])
                            # Remove OCCURS clause from line (legacy approach)
                            string_to_replace = (
                                " " * (occurs_index - whitespace_index - 1)
                                + line[occurs_index:times_index + len(" TIMES")]
                            )
                            line = line.replace(string_to_replace, "")
                        except ValueError:
                            self.logger.warning(f"⚠️ Could not parse OCCURS count in line {line_num}: {line}")
                
                # Check for COMP-3 before pattern matching (legacy approach)
                is_comp3 = " COMP-3" in line or " COMP-3." in line
                if is_comp3:
                    line = line.replace(" COMP-3", "").replace(" COMP-3.", ".")
                
                # CRITICAL FIX: Also check for COMP (without -3) before pattern matching
                is_comp = False
                if not is_comp3 and (" COMP" in line or " COMP." in line):
                    is_comp = True
                    # Don't remove COMP from line - let regex capture it
                
                match = row_pattern.match(line.strip())
                if match:
                    field_def = self._parse_field_definition(match, line_num, is_comp3=is_comp3, occurs_count=occurs_count, is_comp_manual=is_comp)
                    if field_def:
                        # Handle REDEFINES (legacy approach - remove redefined field)
                        redefines = field_def.get("redefines")
                        if redefines:
                            try:
                                # Find the field being redefined
                                redefined_item_index = None
                                for idx, item in enumerate(field_definitions):
                                    if item.get("name") == redefines:
                                        redefined_item_index = idx
                                        break
                                
                                if redefined_item_index is not None:
                                    redefined_item = field_definitions[redefined_item_index]
                                    # Get subgroup (all fields with higher level)
                                    related_group = self._get_subgroup(
                                        redefined_item.get("level", 0),
                                        field_definitions[redefined_item_index + 1:]
                                    )
                                    # Remove redefined field and its subgroup
                                    field_definitions = (
                                        field_definitions[:redefined_item_index]
                                        + field_definitions[redefined_item_index + len(related_group) + 1:]
                                    )
                                    # Clear redefines flag (field is now replacing the redefined one)
                                    field_def["redefines"] = None
                                    self.logger.debug(f"✅ REDEFINES: Replaced {redefines} with {field_def.get('name')}")
                                else:
                                    self.logger.warning(f"⚠️ Could not find field to be redefined ({redefines}) for line {line_num}")
                            except Exception as e:
                                self.logger.warning(f"⚠️ Error handling REDEFINES for {redefines}: {e}")
                        
                        field_definitions.append(field_def)
                # Legacy code continues even if no match (just skips the line)
            
            # Denormalize OCCURS (flatten OCCURS clauses)
            fields_before_denorm = len(field_definitions)
            field_definitions = self._denormalize_cobol(field_definitions)
            fields_after_denorm = len(field_definitions)
            
            # Rename FILLER fields to avoid duplicates
            field_definitions = self._rename_filler_fields(field_definitions)
            
            self.logger.info(f"✅ Parsed {fields_before_denorm} fields before OCCURS denormalization, {fields_after_denorm} fields after (expansion factor: {fields_after_denorm / fields_before_denorm if fields_before_denorm > 0 else 0:.2f}x)")
            
            # WARNING: If OCCURS expansion created too many fields, parsing will be very slow
            if fields_after_denorm > 1000:
                self.logger.warning(f"⚠️ WARNING: OCCURS expansion created {fields_after_denorm} fields. This may cause very slow parsing. Consider optimizing OCCURS handling.")
            
            return field_definitions
            
        except Exception as e:
            self.logger.error(f"❌ Copybook parsing from string failed: {e}", exc_info=True)
            return []
    
    def _clean_cobol(self, lines: List[str]) -> List[str]:
        """
        Clean COBOL lines by handling continuation lines (legacy clean_cobol function).
        COBOL allows fields to span multiple physical lines (columns 6-72).
        Lines are joined until a period is found.
        """
        holder = []
        output = []
        
        for row in lines:
            # Legacy approach: directly slice columns 6-72 (COBOL standard)
            # This works even if row is shorter than 72 chars (slices to end)
            row = row[6:72].rstrip() if len(row) > 6 else row.rstrip()
            
            # Skip empty lines and comments (legacy pattern)
            if row == "" or (row and row[0] in ("*", "/")):
                continue
            
            # Add to holder (join continuation lines)
            holder.append(row if len(holder) == 0 else row.strip())
            
            # If line ends with period, we have a complete statement
            if row and row[-1] == ".":
                output.append(" ".join(holder))
                holder = []
        
        # Warn if there are unfinished lines (legacy behavior)
        if len(holder) > 0:
            self.logger.warning(f"[WARNING] probably invalid COBOL - found unfinished line: {' '.join(holder)}")
            # Legacy doesn't add unfinished lines to output
        
        return output
    
    def _get_subgroup(self, parent_level: int, lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get all fields that have a higher level than parent_level until
        a field with equal or lower level is encountered.
        """
        output = []
        for row in lines:
            level = row.get("level", 0)
            # Skip level 77 (working storage) and 88 (condition names)
            if level == 77 or level == 88:
                continue
            elif level > parent_level:
                output.append(row)
            else:
                return output
        return output
    
    def _handle_occurs(self, lines: List[Dict[str, Any]], occurs: int, level_diff: int = 0, name_postfix: str = "") -> List[Dict[str, Any]]:
        """
        Denormalize COBOL by handling OCCURS clauses.
        Recursively flattens OCCURS into multiple field instances.
        """
        if not lines:
            return []
        
        output = []
        
        try:
            for i in range(1, occurs + 1):
                skipTill = 0
                # If occurs > 1, add postfix like "-1", "-2", etc.
                new_name_postfix = name_postfix if occurs == 1 else name_postfix + "-" + str(i)
                
                for index, row in enumerate(lines):
                    if index < skipTill:
                        continue
                    
                    if not isinstance(row, dict):
                        self.logger.warning(f"⚠️ Skipping invalid row at index {index}: {type(row)}")
                        continue
                    
                    new_row = row.copy()
                    new_row["level"] = new_row.get("level", 0) + level_diff
                    
                    # Remove indexed_by when flattened (not needed)
                    new_row["indexed_by"] = None
                    
                    occurs_count = row.get("occurs")
                    if occurs_count is None:
                        # Field doesn't have OCCURS - just add postfix to name
                        field_name = row.get("name", "")
                        new_row["name"] = field_name + new_name_postfix
                        output.append(new_row)
                    else:
                        # Field has OCCURS
                        # Check if field has PIC (legacy checks row["pic"], we check pic_info)
                        pic_info = row.get("pic_info")
                        pic_string = pic_info.get("pic_string", "") if pic_info else ""
                        has_pic = pic_string != "" or (pic_info and pic_info.get("field_length", 0) > 0)
                        
                        if has_pic:
                            # Field has PIC - repeat the field multiple times
                            new_row["occurs"] = None  # Clear occurs after expansion
                            field_name = row.get("name", "")
                            for j in range(1, occurs_count + 1):
                                row_to_add = new_row.copy()
                                # Legacy naming: row["name"] + new_name_postfix + "-" + str(j)
                                row_to_add["name"] = field_name + new_name_postfix + "-" + str(j)
                                output.append(row_to_add)
                        else:
                            # Field has OCCURS but no PIC - get subgroup and recurse
                            occur_lines = self._get_subgroup(row.get("level", 0), lines[index + 1:])
                            if occur_lines and len(occur_lines) > 0:
                                # Calculate new level difference
                                first_occur_level = occur_lines[0].get("level")
                                if first_occur_level is not None:
                                    new_level_diff = level_diff + row.get("level", 0) - first_occur_level
                                    output += self._handle_occurs(occur_lines, occurs_count, new_level_diff, new_name_postfix)
                                    skipTill = index + len(occur_lines) + 1
                                else:
                                    # Invalid level - skip
                                    self.logger.warning(f"⚠️ Invalid level in occur_lines[0], skipping OCCURS expansion")
                                    new_row["occurs"] = None
                                    new_row["name"] = row.get("name", "") + new_name_postfix
                                    output.append(new_row)
                            else:
                                # No subgroup found - just add the field (shouldn't happen, but handle gracefully)
                                self.logger.warning(f"⚠️ OCCURS field {row.get('name')} has no subgroup, treating as regular field")
                                new_row["occurs"] = None
                                new_row["name"] = row.get("name", "") + new_name_postfix
                                output.append(new_row)
        except Exception as e:
            self.logger.error(f"❌ Error in _handle_occurs: {e}", exc_info=True)
            # Return what we have so far
            return output
        
        return output
    
    def _denormalize_cobol(self, lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Denormalize COBOL by flattening OCCURS clauses.
        """
        try:
            return self._handle_occurs(lines, 1)
        except Exception as e:
            self.logger.error(f"❌ OCCURS denormalization failed: {e}", exc_info=True)
            # Return original lines if denormalization fails
            return lines
    
    def _rename_filler_fields(self, field_definitions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rename FILLER fields to FILLER_1, FILLER_2, etc. to avoid duplicate names.
        """
        filler_counter = 1
        for field_def in field_definitions:
            field_name = field_def.get("name", "")
            if field_name.upper() == "FILLER":
                field_def["name"] = f"FILLER_{filler_counter}"
                filler_counter += 1
        return field_definitions
    
    def _parse_field_definition(self, match: re.Match, line_num: int, is_comp3: bool = False, occurs_count: int = 0, is_comp_manual: bool = False) -> Optional[Dict[str, Any]]:
        """Parse individual field definition from regex match."""
        try:
            level = int(match.group('level'))
            name = match.group('name')
            
            # Extract optional components (use get() to handle missing groups safely)
            redefines = match.group('redefines') if 'redefines' in match.groupdict() else None
            # Use manually extracted occurs_count (legacy approach) instead of regex group
            indexed_by = match.group('indexed_by') if 'indexed_by' in match.groupdict() else None
            pic = match.group('pic') if 'pic' in match.groupdict() else None
            comp = match.group('comp') if 'comp' in match.groupdict() else None
            binary = match.group('binary') if 'binary' in match.groupdict() else None
            
            # CRITICAL FIX: Use manually detected COMP if regex didn't capture it
            if is_comp_manual and comp is None:
                comp = "COMP"  # Set comp so the logic below works
            
            field_def = {
                "level": level,
                "name": name,
                "line_number": line_num,
                "redefines": redefines,
                "occurs": occurs_count if occurs_count > 0 else None,  # Use manually extracted count
                "indexed_by": indexed_by,
                "is_comp": comp is not None and not is_comp3,  # COMP but not COMP-3
                "is_binary": binary is not None
            }
            
            # Parse PIC clause
            if pic:
                pic_info = self._parse_pic_clause(pic)
                # Mark as BCD/COMP-3 if detected (COMP-3 is packed decimal)
                pic_info["is_bcd"] = is_comp3
                field_def["pic_info"] = pic_info
            else:
                field_def["pic_info"] = {
                    "pic_string": "",
                    "expanded_pic": "",
                    "field_length": 0,
                    "data_type": "unknown",
                    "has_sign": False,
                    "is_bcd": is_comp3,
                    "is_comp": comp is not None and not is_comp3,
                    "is_binary": binary is not None,
                    "precision": 0
                }
            
            return field_def
            
        except Exception as e:
            self.logger.error(f"❌ Field definition parsing failed at line {line_num}: {e}")
            return None
    
    def _parse_pic_clause(self, pic_str: str) -> Dict[str, Any]:
        """Parse PIC clause to extract field information."""
        try:
            # Remove parentheses and expand repeats
            pic_pattern_repeats = re.compile(r"(.)\((\d+)\)")
            expanded_pic = pic_pattern_repeats.sub(lambda m: m.group(1) * int(m.group(2)), pic_str)
            
            # Determine data type
            pic_pattern_float = re.compile(r"[+-S]?[9Z]*[.V][9Z]+")
            pic_pattern_integer = re.compile(r"S?[9Z]+")
            
            if pic_pattern_float.match(expanded_pic):
                data_type = "float"
            elif pic_pattern_integer.match(expanded_pic):
                data_type = "integer"
            else:
                data_type = "string"
            
            # Calculate field length
            field_length = len(expanded_pic)
            
            # Check for sign
            has_sign = 'S' in expanded_pic
            
            # Calculate precision (digits after decimal point)
            precision = 0
            if 'V' in expanded_pic:
                parts = expanded_pic.split('V')
                if len(parts) > 1:
                    precision = len(parts[1])
            
            return {
                "pic_string": pic_str,
                "expanded_pic": expanded_pic,
                "field_length": field_length,
                "data_type": data_type,
                "has_sign": has_sign,
                "precision": precision,
                "is_bcd": False,  # Will be set by caller if COMP-3
                "is_comp": False,  # Will be set by caller if COMP
                "is_binary": False  # Will be set by caller if BINARY
            }
            
        except Exception as e:
            self.logger.error(f"❌ PIC clause parsing failed: {e}")
            return {
                "pic_string": pic_str,
                "expanded_pic": pic_str,
                "field_length": 0,
                "data_type": "unknown",
                "has_sign": False,
                "precision": 0,
                "is_bcd": False,
                "is_comp": False,
                "is_binary": False
            }
    
    # ============================================================================
    # Binary Record Parsing Methods
    # ============================================================================
    
    async def _parse_binary_records(self, binary_data: bytes, field_definitions: List[Dict[str, Any]], codepage: str = 'cp037') -> List[Dict[str, Any]]:
        """
        Parse binary records using field definitions.
        Uses proven approach from legacy cobol2csv.py implementation.
        Reads fields sequentially like legacy: for each record, read all fields in order.
        """
        try:
            # Build parseable fields list with adjusted lengths
            parseable_fields = []
            record_length = 0
            
            for field_def in field_definitions:
                level = field_def.get('level', 0)
                if level == 1:  # Skip record level (01)
                    continue
                
                pic_info = field_def.get('pic_info', {})
                field_length = pic_info.get('field_length', 0)
                field_name = field_def.get('name', 'unknown')
                
                # Adjust length for COMP-3 (packed decimal) - use math.ceil like legacy
                if pic_info.get('is_bcd'):
                    # CRITICAL: For COMP-3, count only digits (9s), not sign character (S) or V
                    expanded_pic = pic_info.get('expanded_pic', '')
                    digit_count = len([c for c in expanded_pic if c in '9Z'])
                    if digit_count > 0:
                        field_length = int(math.ceil((digit_count + 1) / 2))
                    else:
                        field_length = int(math.ceil((field_length + 1) / 2)) if field_length > 0 else 0
                # Adjust length for COMP/BINARY
                elif field_def.get('is_comp') or field_def.get('is_binary'):
                    # CRITICAL: For COMP/BINARY, count only digits (9s), not sign character (S)
                    expanded_pic = pic_info.get('expanded_pic', '')
                    digit_count = len([c for c in expanded_pic if c in '9Z'])
                    if digit_count > 0:
                        field_length = self._get_len_for_comp_binary(digit_count)
                    else:
                        field_length = self._get_len_for_comp_binary(field_length)
                
                # Include ALL fields that have PIC clauses
                if field_length > 0:
                    record_length += field_length
                
                parseable_fields.append({
                    **field_def,
                    'actual_length': field_length,
                    'field_type': pic_info.get('data_type', 'string'),
                    'tag': 'BCD' if pic_info.get('is_bcd') else ('Comp' if pic_info.get('is_comp') else ('Binary' if pic_info.get('is_binary') else None))
                })
            
            if record_length == 0:
                self.logger.error("❌ No valid fields found or record length is 0")
                return []
            
            self.logger.info(f"📏 Calculated record length: {record_length} bytes, {len(parseable_fields)} fields")
            
            # WARNING: If too many fields, parsing will be extremely slow
            if len(parseable_fields) > 500:
                self.logger.warning(f"⚠️ WARNING: {len(parseable_fields)} parseable fields detected. This will cause very slow parsing. Estimated time: {len(parseable_fields) * 0.001:.1f} seconds per record.")
            
            # Detect ASCII vs EBCDIC
            is_ascii_file = False
            if len(binary_data) > 100:
                ascii_bytes = sum(1 for b in binary_data[:100] if 0x20 <= b <= 0x7E)
                if ascii_bytes / 100 > 0.8:  # >80% ASCII printable
                    is_ascii_file = True
            
            record_prefix_length = 0
            if is_ascii_file or codepage in ['ascii', 'utf-8'] or codepage is None:
                # Normalize ASCII file (remove newlines, find data start, strip prefixes)
                normalized_data, normalization_metadata = self._normalize_ascii_file(
                    binary_data, 
                    record_length, 
                    parseable_fields
                )
                
                # Update offset based on normalization
                offset = 0  # Normalized data starts at 0
                record_prefix_length = normalization_metadata.get('record_prefix_length', 0)
                
                # Use normalized data for parsing
                original_binary_data_size = len(binary_data)
                binary_data = normalized_data
                self.logger.info(f"📊 Using normalized data: {len(normalized_data)} bytes (was {original_binary_data_size} bytes before normalization)")
            
            # Read fields sequentially until EOF
            MAX_RECORDS = 1000000  # 1 million records max
            MAX_MISALIGNMENT_COUNT = 10  # Stop after 10 consecutive misalignments
            misalignment_count = 0
            
            # Performance warning
            if len(parseable_fields) > 10000:
                self.logger.error(f"❌ Too many parseable fields ({len(parseable_fields)}). This will likely cause extremely slow parsing or timeout. OCCURS expansion may have created too many fields. Aborting to prevent timeout.")
                return []
            elif len(parseable_fields) > 1000:
                estimated_time_per_record = len(parseable_fields) * 0.001  # Rough estimate: 1ms per field
                self.logger.warning(f"⚠️ Large number of parseable fields ({len(parseable_fields)}). Estimated time: ~{estimated_time_per_record:.2f} seconds per record. This may be slow but will proceed.")
            
            records = []
            offset = 0
            record_number = 0
            
            while offset < len(binary_data) and record_number < MAX_RECORDS:
                # Read all fields for one record
                record_start = offset
                record = {}
                bytes_read = 0
                
                for field_idx, field_def in enumerate(parseable_fields):
                    field_name = field_def.get('name', 'unknown')
                    field_length = field_def.get('actual_length', 0)
                    pic_info = field_def.get('pic_info', {})
                    
                    # Skip 0-length fields (they don't consume bytes)
                    if field_length == 0:
                        continue
                    
                    # Check bounds
                    if offset + field_length > len(binary_data):
                        # Incomplete record - stop parsing
                        break
                    
                    # Read field data
                    field_data = binary_data[offset:offset + field_length]
                    offset += field_length
                    bytes_read += field_length
                    
                    # Parse field value
                    value = self._parse_field_value(field_data, field_def, pic_info, codepage, is_ascii_file=is_ascii_file)
                    record[field_name] = value
                
                # Validate record length
                if bytes_read != record_length:
                    misalignment_count += 1
                    if misalignment_count >= MAX_MISALIGNMENT_COUNT:
                        self.logger.warning(f"⚠️ Too many misaligned records ({misalignment_count}). Stopping parsing.")
                        break
                    # For EBCDIC files, use actual bytes_read as record length if misaligned
                    if not is_ascii_file:
                        # Try to continue with actual bytes_read
                        self.logger.warning(f"⚠️ Record {record_number}: Expected {record_length} bytes, got {bytes_read} bytes. Using actual bytes_read.")
                        record_length = bytes_read
                else:
                    misalignment_count = 0
                
                # Skip comment/metadata records using extensible pattern detection
                is_header = False
                if record_number < 20:
                    first_field_name = parseable_fields[0].get('name', '') if parseable_fields else ''
                    first_value = str(record.get(first_field_name, ''))
                    
                    # Check for comment markers
                    has_comment_marker = False
                    if record_number < 10:
                        for field_name in list(record.keys()):
                            field_value = str(record.get(field_name, ''))
                            if '#' in field_value:
                                has_comment_marker = True
                                break
                    
                    # Skip records with comment markers
                    if first_value.startswith('#') or '\n' in first_value or has_comment_marker:
                        is_header = True
                
                if not is_header:
                    records.append(record)
                
                record_number += 1
                
                # Progress logging for large files
                if record_number % 10000 == 0:
                    self.logger.info(f"📊 Processed {record_number} records, {len(records)} valid records, offset: {offset}/{len(binary_data)} bytes")
            
            if record_number >= MAX_RECORDS:
                self.logger.warning(f"⚠️ Reached maximum record count ({MAX_RECORDS}). Stopping to prevent infinite loop.")
            
            self.logger.info(f"✅ Parsed {len(records)} records from {len(binary_data)} bytes")
            return records
            
        except Exception as e:
            self.logger.error(f"❌ Binary records parsing failed: {e}", exc_info=True)
            return []
    
    def _parse_field_value(self, field_data: bytes, field_def: Dict[str, Any], pic_info: Dict[str, Any], codepage: str = 'cp037', is_ascii_file: bool = False) -> Any:
        """Parse field value using proven legacy approach."""
        data_type = pic_info.get('data_type', 'string')
        is_comp = pic_info.get('is_comp', False) or field_def.get('is_comp', False)
        is_binary = pic_info.get('is_binary', False) or field_def.get('is_binary', False)
        is_bcd = pic_info.get('is_bcd', False)
        has_sign = pic_info.get('has_sign', False)
        
        # Normalize data_type for matching
        data_type_normalized = data_type.lower()
        is_integer = 'integer' in data_type_normalized
        is_float = 'float' in data_type_normalized
        
        # Handle Binary/COMP fields (NO character translation - these are binary)
        if is_binary or (is_comp and is_integer):
            return self._unpack_hex_array(field_data)
        
        # Handle COMP-3 (packed decimal / BCD) - NO character translation
        if is_bcd:
            precision = pic_info.get('precision', 0)
            pic_length = pic_info.get('field_length', 0)  # Original PIC length
            left_digits = pic_length - precision  # Digits before decimal point
            return self._unpack_comp3_number(field_data, left_digits, precision)
        
        # Handle COMP float
        if is_comp and is_float:
            int_val = self._unpack_hex_array(field_data)
            precision = pic_info.get('precision', 0)
            return float(int_val) / (10 ** precision) if precision > 0 else float(int_val)
        
        # Handle Integer (display format - ASCII or EBCDIC)
        if is_integer:
            if is_ascii_file or codepage in ['ascii', 'utf-8']:
                # ASCII numeric field - decode as ASCII and parse
                try:
                    decoded = field_data.decode('ascii', errors='ignore').strip()
                    digits_only = ''.join(c for c in decoded if c.isdigit())
                    if digits_only:
                        return int(digits_only)
                    else:
                        self.logger.warning(f"⚠️ No digits found in numeric field (ASCII): {repr(decoded)}, raw_hex: {field_data.hex()}")
                        return 0
                except (ValueError, UnicodeDecodeError) as e:
                    self.logger.warning(f"⚠️ Failed to parse ASCII numeric field: {e}, raw: {field_data.hex()}")
                    return 0
            else:
                # EBCDIC numeric field - use EBCDIC-to-decimal conversion
                value = self._ebcdic_to_decimal(field_data)
                return value
        
        # Handle Float (display format - ASCII or EBCDIC)
        if is_float:
            if is_ascii_file or codepage in ['ascii', 'utf-8']:
                # ASCII float field - decode as ASCII and parse
                try:
                    decoded = field_data.decode('ascii', errors='ignore').strip()
                    cleaned = ''.join(c for c in decoded if c.isdigit() or c == '.' or c == '-' or c == '+')
                    if cleaned:
                        return float(cleaned)
                    else:
                        self.logger.warning(f"⚠️ No numeric value found in float field (ASCII): {repr(decoded)}, raw_hex: {field_data.hex()}")
                        return 0.0
                except (ValueError, UnicodeDecodeError) as e:
                    self.logger.warning(f"⚠️ Failed to parse ASCII float field: {e}, raw: {field_data.hex()}")
                    return 0.0
            else:
                # EBCDIC float field - use EBCDIC-to-decimal then convert to float
                int_val = self._ebcdic_to_decimal(field_data)
                precision = pic_info.get('precision', 0)
                return float(int_val) / (10 ** precision) if precision > 0 else float(int_val)
        
        # Handle String/Char - apply encoding conversion (EBCDIC→ASCII/Unicode)
        try:
            # Quick encoding detection: check first 10 bytes
            sample_size = min(10, len(field_data)) if field_data else 0
            is_ascii = False
            if sample_size > 0:
                ascii_count = sum(1 for b in field_data[:sample_size] if 0x20 <= b <= 0x7E)
                ascii_ratio = ascii_count / sample_size if sample_size > 0 else 0
                
                if ascii_ratio > 0.8:
                    # ASCII
                    is_ascii = True
                    original_str = field_data.decode('ascii', errors='ignore')
                else:
                    # EBCDIC - apply code page conversion
                    try:
                        original_str = codecs.decode(field_data, codepage, errors='ignore')
                    except LookupError:
                        self.logger.warning(f"Unknown code page {codepage}, falling back to cp037")
                        original_str = codecs.decode(field_data, "cp037", errors='ignore')
            else:
                # Empty field
                original_str = ""
            
            # Apply different cleaning for ASCII vs EBCDIC
            if is_ascii:
                # ASCII-specific cleaning for FIXED-WIDTH fields
                cleaned = original_str
                # Filter out non-printable control characters
                cleaned = ''.join(c if (32 <= ord(c) <= 126) or c in [' ', '\t'] else '' for c in cleaned)
                cleaned = cleaned.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                cleaned = cleaned.rstrip()  # Only strip trailing whitespace
                return cleaned
            else:
                # EBCDIC: use custom encoder (handles @ symbols, etc.)
                return self._custom_encoder(original_str.strip())
        except Exception:
            return ""
    
    def _get_len_for_comp_binary(self, elem_length: int) -> int:
        """Calculate byte length for COMP/BINARY fields."""
        if elem_length >= 1 and elem_length <= 4:
            return 2
        elif elem_length >= 5 and elem_length <= 9:
            return 4
        elif elem_length >= 10 and elem_length <= 18:
            return 8
        else:
            return 0
    
    def _ebcdic_to_decimal(self, byte_sequence: bytes) -> int:
        """
        Convert EBCDIC-encoded byte sequence to decimal.
        
        Handles EBCDIC display format numeric fields which may contain:
        - EBCDIC digits (0xF0-0xF9)
        - Spaces (0x40 in EBCDIC)
        - Sign indicators (0x4E for +, 0x60 for -)
        """
        ebcdic_to_digit = {
            0xF0: '0', 0xF1: '1', 0xF2: '2', 0xF3: '3', 0xF4: '4',
            0xF5: '5', 0xF6: '6', 0xF7: '7', 0xF8: '8', 0xF9: '9'
        }
        
        digits = []
        is_negative = False
        
        for byte in byte_sequence:
            if byte in ebcdic_to_digit:
                digits.append(ebcdic_to_digit[byte])
            elif byte == 0x60:  # EBCDIC minus sign
                is_negative = True
            # Ignore spaces (0x40 EBCDIC, 0x20 ASCII), plus signs (0x4E EBCDIC), and other non-digits
        
        if not digits:
            return 0
        
        value = int(''.join(digits))
        return -value if is_negative else value
    
    def _unpack_hex_array(self, byte_sequence: bytes) -> int:
        """Unpack binary/COMP field."""
        if not byte_sequence:
            return 0
        # Check if negative (starts with 0xFF)
        if byte_sequence[0] == 0xFF:
            v = 0
            for b in byte_sequence:
                v = v * 256 + (255 - b)
            return -(v + 1)
        else:
            v = 0
            for b in byte_sequence:
                v = v * 256 + b
            return int(v)
    
    def _unpack_comp3_number(self, byte_sequence: bytes, left_digits: int, right_digits: int) -> float:
        """Unpack COMP-3 (packed decimal) number."""
        if not byte_sequence:
            return 0.0
        result = 0
        sign = 1
        # Process all bytes except the last one
        for byte in byte_sequence[:-1]:
            high_nibble = (byte >> 4) & 0x0F
            low_nibble = byte & 0x0F
            result = (result * 100) + (high_nibble * 10) + low_nibble
        # Handle last byte which contains last digit and sign
        last_byte = byte_sequence[-1]
        last_digit = (last_byte >> 4) & 0x0F
        sign_nibble = last_byte & 0x0F
        result = (result * 10) + last_digit
        # Check sign nibble: 0x0D = negative, 0x0C = positive
        if sign_nibble == 0x0D:
            sign = -1
        return sign * (result / (10 ** right_digits))
    
    def _custom_encoder(self, my_string: str) -> str:
        """
        Replace non-ASCII characters with spaces.
        Also removes excessive @ symbols that are EBCDIC fillers.
        """
        # First, replace non-ASCII (>127) with spaces
        # Also replace control characters (0x00-0x1F) except common whitespace
        cleaned = "".join([
            i if (ord(i) < 128 and (ord(i) >= 32 or i in ['\n', '\r', '\t'])) else " " 
            for i in my_string
        ])
        # Remove excessive @ symbols (EBCDIC filler character)
        cleaned = re.sub(r'@{2,}', ' ', cleaned)  # Replace 2+ @ with space
        cleaned = cleaned.rstrip('@')  # Remove trailing @
        # Remove any remaining control characters
        cleaned = ''.join(c if c.isprintable() or c in ['\n', '\r', '\t', ' '] else ' ' for c in cleaned)
        # Collapse multiple spaces to single space
        cleaned = re.sub(r' +', ' ', cleaned)
        # Strip leading/trailing whitespace
        cleaned = cleaned.strip()
        return cleaned
    
    # ============================================================================
    # ASCII File Normalization Methods
    # ============================================================================
    
    def _normalize_ascii_file(self, binary_data: bytes, record_length: int, parseable_fields: List[Dict[str, Any]]) -> Tuple[bytes, dict]:
        """
        Normalize ASCII file using extensible patterns.
        
        Steps:
        1. Remove newlines (convert text to binary)
        2. Find first valid data record using pattern matching (extensible)
        3. Detect and strip record prefixes using spacing detection (extensible)
        
        Returns:
            Tuple of (normalized_bytes, metadata_dict)
        """
        metadata = {
            'original_size': len(binary_data),
            'newlines_removed': 0,
            'header_bytes': 0,
            'record_prefix_length': 0,
            'normalized_size': 0
        }
        
        # Step 1: Remove newlines
        original_size = len(binary_data)
        normalized = binary_data.replace(b'\n', b'').replace(b'\r', b'')
        newlines_removed = original_size - len(normalized)
        metadata['newlines_removed'] = newlines_removed
        self.logger.info(f"📊 Removed {newlines_removed} newlines from ASCII file (original: {original_size} bytes, after: {len(normalized)} bytes)")
        
        # Step 2: Find first valid data record using extensible pattern matching
        data_start_offset = self._find_ascii_data_start_extensible(normalized, parseable_fields, record_length)
        
        if data_start_offset > 0:
            normalized = normalized[data_start_offset:]
            metadata['header_bytes'] = data_start_offset
            self.logger.info(f"📊 Removed {data_start_offset} bytes of header/comments")
        
        # Step 3: Detect and strip record prefixes using spacing-based detection
        prefix_length = self._detect_and_strip_prefix_extensible(normalized, record_length, parseable_fields)
        
        if prefix_length > 0:
            normalized = self._strip_record_prefixes_extensible(normalized, prefix_length, record_length)
            metadata['record_prefix_length'] = prefix_length
            self.logger.info(f"📊 Stripped {prefix_length}-byte prefix from all records")
        else:
            self.logger.info(f"📊 No prefix detected - using data as-is")
        
        metadata['normalized_size'] = len(normalized)
        return normalized, metadata
    
    def _find_ascii_data_start_extensible(self, binary_data: bytes, parseable_fields: List[Dict[str, Any]], record_length: int, max_scan: int = 2000) -> int:
        """
        Extensible method to find where actual fixed-width data starts in ASCII files.
        
        Uses pattern matching based on first field from copybook (extensible for any file type).
        """
        # Extract first field pattern from copybook
        first_field = parseable_fields[0] if parseable_fields else None
        first_field_name = first_field.get('name', '').upper() if first_field else ''
        
        # Try to infer pattern from first field name
        first_field_pattern = None
        if first_field_name:
            if 'POLICY' in first_field_name or 'POL' in first_field_name:
                first_field_pattern = r'POL\d{3}'  # Matches "POL001", "POL002", etc.
            elif 'RECORD' in first_field_name or 'REC' in first_field_name:
                first_field_pattern = r'REC\d{3}'  # Matches "REC001", "REC002", etc.
        
        # Strategy 1: Pattern-based search
        if first_field_pattern:
            try:
                pattern_regex = re.compile(first_field_pattern.encode('ascii', errors='ignore'))
                matches = list(pattern_regex.finditer(binary_data[:max_scan]))
                
                if len(matches) >= 3:
                    # Check spacing between matches
                    spacings = []
                    for i in range(1, min(4, len(matches))):
                        spacing = matches[i].start() - matches[i-1].start()
                        spacings.append(spacing)
                    
                    if len(set(spacings)) == 1:
                        # Consistent spacing detected
                        detected_spacing = spacings[0]
                        self.logger.info(f"📊 Detected consistent spacing: {detected_spacing} bytes between patterns")
                        return matches[0].start()
            except Exception as e:
                self.logger.warning(f"⚠️ Pattern matching failed: {e}, falling back to heuristics")
        
        # Strategy 2: Use heuristics (simplified version)
        return self._find_ascii_data_start(binary_data, parseable_fields, record_length, max_scan)
    
    def _find_ascii_data_start(self, binary_data: bytes, parseable_fields: List[Dict[str, Any]], record_length: int, max_scan: int = 2000) -> int:
        """
        Extensible method to find where actual fixed-width data starts in ASCII files.
        
        Strategy:
        1. Skip common comment markers (#, *, /, //, REM, etc.)
        2. Detect header row by matching copybook field names
        3. Validate data records by checking field types match expected patterns
        """
        # Common comment markers
        comment_markers = [b'#', b'*', b'/', b'//', b'REM', b'REM ', b'C ', b'C\t', b';', b'!']
        
        # Extract field names from copybook
        field_names = [field.get('name', '').upper() for field in parseable_fields if field.get('name')]
        
        # Strategy 1: Find header row by matching field names
        normalized_field_names = []
        for name in field_names[:10]:  # Check first 10 field names
            if not name or name.startswith('FILLER'):
                continue
            normalized_field_names.append(name)
            normalized_field_names.append(name.replace('_', '-'))
            normalized_field_names.append(name.replace('_', ' '))
            normalized_field_names.append(name.replace('-', '_'))
            normalized_field_names.append(name.replace('-', ' '))
        
        for field_name in normalized_field_names:
            if not field_name:
                continue
            field_name_bytes = field_name.upper().encode('ascii', errors='ignore')
            marker_pos = binary_data.find(field_name_bytes, 0, max_scan)
            if marker_pos != -1:
                # Found a field name, check if this is a header row
                for offset_adjust in range(-10, 11):
                    test_offset = marker_pos + offset_adjust
                    if test_offset < 0 or test_offset + record_length > len(binary_data):
                        continue
                    
                    test_record_bytes = binary_data[test_offset:test_offset + record_length]
                    try:
                        test_record_text = test_record_bytes.decode('ascii', errors='ignore')
                        test_record_upper = test_record_text.upper()
                        
                        # Check if this record contains multiple field names
                        matching_fields = 0
                        for name in field_names[:10]:
                            if not name or name.startswith('FILLER'):
                                continue
                            if (name in test_record_upper or 
                                name.replace('_', '-') in test_record_upper or
                                name.replace('_', ' ') in test_record_upper or
                                name.replace('-', '_') in test_record_upper or
                                name.replace('-', ' ') in test_record_upper):
                                matching_fields += 1
                        
                        if matching_fields >= 3:  # Found header row
                            next_record_offset = test_offset + record_length
                            self.logger.info(f"📍 Found header row at offset {test_offset}, starting data at {next_record_offset}")
                            return next_record_offset
                    except:
                        continue
        
        # Strategy 2: Skip comment lines and find first valid data record
        start_scan = 0
        for marker in comment_markers:
            if binary_data.startswith(marker):
                start_scan = len(marker)
                break
        
        for i in range(start_scan, min(max_scan - record_length, len(binary_data) - record_length), 1):
            test_record_bytes = binary_data[i:i+record_length]
            try:
                test_record_text = test_record_bytes.decode('ascii', errors='ignore')
                
                # Skip if it's a comment line
                is_comment = False
                for marker in comment_markers:
                    if test_record_text.startswith(marker.decode('ascii', errors='ignore')):
                        is_comment = True
                        break
                if is_comment:
                    continue
                
                # Skip if it contains newlines in the middle
                if '\n' in test_record_text[:-2] or '\r' in test_record_text[:-2]:
                    continue
                
                # Skip if it contains comment keywords
                comment_keywords = ['comment', 'note', 'format', 'char', 'record', 'file', 'contains', 'description']
                test_record_lower = test_record_text.lower()
                if any(keyword in test_record_lower for keyword in comment_keywords):
                    continue
                
                # Validate: Check if first few fields match expected types
                offset = 0
                valid_fields = 0
                first_field_valid = False
                
                for idx, field in enumerate(parseable_fields[:5]):  # Check first 5 fields
                    field_length = field.get('actual_length', 0)
                    if field_length == 0 or offset + field_length > len(test_record_bytes):
                        break
                    
                    field_data = test_record_bytes[offset:offset + field_length]
                    field_type = field.get('field_type', 'string')
                    
                    try:
                        field_text = field_data.decode('ascii', errors='ignore').strip()
                        
                        if idx == 0:
                            if any(keyword in field_text.lower() for keyword in comment_keywords):
                                break
                            if len(field_text.strip()) < 3:
                                break
                        
                        # Validate based on expected type
                        if field_type == 'integer':
                            if field_text.isdigit() and len(field_text) >= 3:
                                valid_fields += 1
                                if idx == 0:
                                    first_field_valid = True
                        elif field_type == 'float':
                            if (field_text.replace('.', '').replace('-', '').isdigit() and len(field_text.replace('.', '').replace('-', '')) >= 3):
                                valid_fields += 1
                                if idx == 0:
                                    first_field_valid = True
                        elif field_type == 'string':
                            if len(field_text) > 2 and not any(keyword in field_text.lower() for keyword in comment_keywords):
                                valid_fields += 1
                                if idx == 0:
                                    first_field_valid = True
                    except:
                        pass
                    
                    offset += field_length
                
                # Require first field to be valid AND at least 3 fields total
                if first_field_valid and valid_fields >= 3:
                    # Verify next record also looks valid
                    if i + record_length * 2 <= len(binary_data):
                        next_record_bytes = binary_data[i+record_length:i+record_length*2]
                        try:
                            next_record_text = next_record_bytes.decode('ascii', errors='ignore')
                            first_field = parseable_fields[0] if parseable_fields else None
                            if first_field:
                                first_field_length = first_field.get('actual_length', 0)
                                if first_field_length > 0:
                                    first_field_data = next_record_bytes[:first_field_length]
                                    first_field_text = first_field_data.decode('ascii', errors='ignore').strip()
                                    
                                    if any(keyword in first_field_text.lower() for keyword in comment_keywords):
                                        continue
                                    
                                    # Quick validation
                                    first_field_type = first_field.get('field_type', 'string')
                                    next_valid = False
                                    if first_field_type == 'integer' and first_field_text.isdigit() and len(first_field_text) >= 3:
                                        next_valid = True
                                    elif first_field_type == 'float' and (first_field_text.replace('.', '').replace('-', '').isdigit() and len(first_field_text.replace('.', '').replace('-', '')) >= 3):
                                        next_valid = True
                                    elif first_field_type == 'string' and len(first_field_text) > 2 and not any(keyword in first_field_text.lower() for keyword in comment_keywords):
                                        next_valid = True
                                    
                                    if next_valid:
                                        self.logger.info(f"📍 Found valid data start at offset {i}")
                                        return i
                        except:
                            pass
                    else:
                        # Can't verify next record, but this one looks valid
                        self.logger.info(f"📍 Found likely data start at offset {i} (couldn't verify next record)")
                        return i
            except:
                continue
        
        # If no valid start found, return 0 (start from beginning)
        return 0
    
    def _detect_and_strip_prefix_extensible(self, normalized_data: bytes, record_length: int, parseable_fields: List[Dict[str, Any]]) -> int:
        """
        Detect record prefix using extensible spacing-based detection.
        
        Strategy: Find patterns like "POL001", "POL002" and calculate spacing.
        If spacing > record_length, infer prefix length = spacing - record_length.
        
        Returns:
            Prefix length in bytes (0 if no prefix detected)
        """
        if len(normalized_data) < record_length * 2:
            return 0
        
        # Try to find pattern in first few records
        first_field = parseable_fields[0] if parseable_fields else None
        first_field_name = first_field.get('name', '').upper() if first_field else ''
        
        # Infer pattern from field name (extensible)
        pattern = None
        if 'POLICY' in first_field_name or 'POL' in first_field_name:
            pattern = b'POL'
        elif 'RECORD' in first_field_name or 'REC' in first_field_name:
            pattern = b'REC'
        
        if pattern:
            # Search for pattern occurrences
            matches = []
            search_limit = min(len(normalized_data), record_length * 10)
            search_start = 0
            
            while search_start < search_limit:
                pos = normalized_data.find(pattern, search_start, search_limit)
                if pos == -1:
                    break
                matches.append(pos)
                search_start = pos + 1
            
            if len(matches) >= 3:
                # Calculate spacing between matches
                spacings = []
                for i in range(1, min(4, len(matches))):
                    spacing = matches[i] - matches[i-1]
                    spacings.append(spacing)
                
                if len(set(spacings)) == 1:
                    # Consistent spacing detected
                    detected_spacing = spacings[0]
                    self.logger.info(f"📊 Detected record spacing: {detected_spacing} bytes")
                    
                    if detected_spacing > record_length:
                        # Spacing is larger than record length - there's a prefix
                        prefix_length = detected_spacing - record_length
                        self.logger.info(f"📊 Inferred {prefix_length}-byte prefix (spacing {detected_spacing} - record {record_length})")
                        return prefix_length
        
        return 0
    
    def _strip_record_prefixes_extensible(self, content: bytes, prefix_length: int, record_length: int) -> bytes:
        """
        Strip record prefixes from all records.
        
        Args:
            content: Normalized file content (no newlines, data start found)
            prefix_length: Length of prefix to strip from each record
            record_length: Expected record length after stripping prefix
            
        Returns:
            Content with prefixes stripped
        """
        if prefix_length == 0:
            return content
        
        # Split into records using actual record size (record_length + prefix_length)
        actual_record_size = record_length + prefix_length
        record_count = len(content) // actual_record_size
        
        self.logger.info(f"🔍 [prefix_strip] Splitting {len(content)} bytes into records: actual_record_size={actual_record_size}, record_count={record_count}")
        
        result = bytearray()
        for i in range(record_count):
            record_start = i * actual_record_size
            record_end = record_start + actual_record_size
            
            if record_end > len(content):
                break
            
            # Extract record and strip prefix from start
            full_record = content[record_start:record_end]
            record_without_prefix = full_record[prefix_length:]
            
            result.extend(record_without_prefix)
        
        self.logger.info(f"📊 Stripped {prefix_length}-byte prefix from {record_count} records")
        return bytes(result)
    
    # ============================================================================
    # Field Validation Methods
    # ============================================================================
    
    def _validate_field_against_copybook(
        self, field_name: str, field_data: bytes, expected_length: int,
        pic_info: Dict[str, Any], offset: int, record_number: int, is_ascii_file: bool
    ) -> List[str]:
        """
        Extensible validation: Detect copybook/file mismatches for individual fields.
        
        This method validates that the actual field data matches the copybook specification.
        It does NOT try to "fix" the data - it only reports data quality issues.
        
        Returns:
            List of validation error messages (empty if no issues)
        """
        errors = []
        actual_length = len(field_data)
        
        # Validation 1: Field length mismatch
        if actual_length != expected_length:
            errors.append(
                f"Record {record_number}, Field '{field_name}': "
                f"Copybook specifies {expected_length} bytes, but file has {actual_length} bytes. "
                f"Offset: {offset}. This is a DATA QUALITY ISSUE - the file doesn't match the copybook."
            )
        
        # Validation 2: For numeric fields, check if data type matches
        if pic_info.get('data_type') in ['integer', 'float']:
            try:
                if is_ascii_file:
                    # ASCII numeric field - should contain only digits, spaces, decimal point, and signs
                    field_text = field_data.decode('ascii', errors='ignore').strip()
                    cleaned = ''.join(c for c in field_text if c.isdigit() or c in [' ', '.', '-', '+'])
                    if field_text and len(cleaned) < len(field_text.replace(' ', '').replace('.', '').replace('-', '').replace('+', '')):
                        errors.append(
                            f"Record {record_number}, Field '{field_name}': "
                            f"Expected numeric data (PIC {pic_info.get('pic_string', '?')}), "
                            f"but found non-numeric characters: {repr(field_text[:20])}. "
                            f"This may indicate field misalignment."
                        )
                else:
                    # EBCDIC numeric field - check if field contains valid EBCDIC numeric bytes
                    ebcdic_digits = [b for b in field_data if 0xF0 <= b <= 0xF9]
                    ebcdic_space = 0x40
                    ebcdic_plus = 0x4E
                    ebcdic_minus = 0x60
                    
                    valid_bytes = sum(1 for b in field_data 
                                     if (0xF0 <= b <= 0xF9) or b == ebcdic_space or b == ebcdic_plus or b == ebcdic_minus)
                    
                    if len(field_data) > 0 and valid_bytes / len(field_data) < 0.8:
                        field_text = field_data.decode('cp037', errors='ignore').strip()
                        errors.append(
                            f"Record {record_number}, Field '{field_name}': "
                            f"Expected EBCDIC numeric data (PIC {pic_info.get('pic_string', '?')}), "
                            f"but found many non-numeric bytes. Decoded: {repr(field_text[:20])}. "
                            f"This may indicate field misalignment."
                        )
            except Exception:
                pass  # Ignore decode errors
        
        return errors
    
    def _validate_record_length(
        self, record_number: int, bytes_read: int, expected_length: int,
        record: Dict[str, Any], parseable_fields: List[Dict[str, Any]],
        record_start: int, current_offset: int
    ) -> List[str]:
        """
        Extensible validation: Detect record length mismatches.
        
        This method validates that the actual record length matches the copybook specification.
        It provides detailed diagnostics to help identify the root cause.
        
        Returns:
            List of validation error messages (empty if no issues)
        """
        errors = []
        
        if bytes_read != expected_length:
            # Calculate expected length from field definitions
            total_field_lengths = sum(f.get('actual_length', 0) for f in parseable_fields)
            
            error_msg = (
                f"Record {record_number}: Record length mismatch. "
                f"Copybook specifies {expected_length} bytes, but file has {bytes_read} bytes "
                f"(difference: {bytes_read - expected_length} bytes). "
            )
            
            if total_field_lengths != expected_length:
                error_msg += (
                    f"Sum of field lengths from copybook: {total_field_lengths} bytes. "
                    f"This suggests a copybook definition issue."
                )
            else:
                error_msg += (
                    f"Sum of field lengths matches copybook ({total_field_lengths} bytes). "
                    f"This suggests the file structure doesn't match the copybook."
                )
            
            error_msg += (
                f" Record start: {record_start}, Current offset: {current_offset}. "
                f"This is a DATA QUALITY ISSUE - the file doesn't match the copybook."
            )
            
            errors.append(error_msg)
            
            # Additional diagnostic: Show field breakdown for first few records
            if record_number < 3:
                field_breakdown = []
                current_pos = record_start
                for field_def in parseable_fields[:5]:  # First 5 fields
                    field_name = field_def.get('name', 'unknown')
                    field_length = field_def.get('actual_length', 0)
                    field_breakdown.append(
                        f"{field_name}({field_length} bytes @ {current_pos}-{current_pos+field_length-1})"
                    )
                    current_pos += field_length
                errors.append(
                    f"Record {record_number} field breakdown: {', '.join(field_breakdown)}"
                )
        
        return errors
    
    # ============================================================================
    # Utility Methods
    # ============================================================================
    
    def _records_to_text(self, records: List[Dict[str, Any]]) -> str:
        """Convert records to text representation."""
        if not records:
            return ""
        
        # Create text representation
        text_lines = []
        for i, record in enumerate(records, 1):
            record_str = f"Record {i}: " + ", ".join(f"{k}: {v}" for k, v in record.items())
            text_lines.append(record_str)
        
        return "\n".join(text_lines)
    
    def supports_feature(self, feature: str) -> bool:
        """
        Check if custom strategy supports a COBOL feature.
        
        Args:
            feature: Feature name
        
        Returns:
            True if feature is supported
        """
        # Custom strategy supports most features (when fully implemented)
        supported_features = {
            "OCCURS": True,
            "REDEFINES": True,
            "COMP-3": True,
            "BINARY": True,
            "88-level": True,  # Via metadata extraction
            "VALUE": True,  # Via metadata extraction
            "large_files": False,  # May be slow for very large files
            "parallel": False  # Single-threaded
        }
        
        return supported_features.get(feature, False)
