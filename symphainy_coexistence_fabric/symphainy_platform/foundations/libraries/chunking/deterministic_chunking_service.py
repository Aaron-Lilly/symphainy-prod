"""
Deterministic Chunking Service - Chunk-Level Deterministic Identity

Enabling service for creating deterministic chunks from parsed content.

WHAT (Enabling Service Role): I create deterministic chunks (stable, reproducible, content-addressed)
HOW (Enabling Service Implementation): I extract structural elements from parsed content and generate stable chunk IDs

Key Principle: Deterministic = identity + structure + locality signals
CTO Principle: Chunking based on parser structure, not heuristics
CIO Requirement: Chunk boundaries must be deterministic and replayable
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
import hashlib
import json
import re

from utilities import get_logger, generate_event_id
from symphainy_platform.runtime.execution_context import ExecutionContext


@dataclass
class DeterministicChunk:
    """
    Deterministic chunk identity - stable, reproducible, content-addressed.
    
    CTO Principle: Deterministic = identity + structure + locality signals
    CIO Requirement: Chunk boundaries must be deterministic and replayable
    """
    chunk_id: str  # Stable, content-addressed (SHA256-based)
    chunk_index: int
    source_path: str  # file → page → section → paragraph
    text_hash: str  # Normalized hash for re-embedding detection
    structural_type: str  # page | section | paragraph | table | cell | heading | list_item
    byte_offset: Optional[int] = None
    logical_offset: Optional[int] = None
    text: str = ""
    # ENHANCEMENT: Link to schema-level deterministic
    schema_fingerprint: Optional[str] = None  # Links to schema-level
    pattern_hints: Optional[Dict[str, Any]] = None  # From pattern signature
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize metadata if not provided."""
        if self.metadata is None:
            self.metadata = {}


class DeterministicChunkingService:
    """
    Creates deterministic chunks from parsed content.
    
    CIO Requirement: Chunking must be deterministic and reversible
    CTO Principle: Chunking based on parser structure, not heuristics
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Deterministic Chunking Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        
        # Get Deterministic Embedding Service for schema-level linking
        self.deterministic_embedding_service = None
        if public_works:
            from .deterministic_embedding_service import DeterministicEmbeddingService
            self.deterministic_embedding_service = DeterministicEmbeddingService(public_works=public_works)
    
    async def create_chunks(
        self,
        parsed_content: Dict[str, Any],
        file_id: str,
        tenant_id: str,
        parsed_file_id: Optional[str] = None
    ) -> List[DeterministicChunk]:
        """
        Create deterministic chunks from parsed content.
        
        CIO Requirement: Same input → same chunks (deterministic)
        CTO Principle: Use parser structure, not heuristics
        
        Args:
            parsed_content: Parsed file content (from FileParserService)
            file_id: File identifier
            tenant_id: Tenant identifier
            parsed_file_id: Optional parsed file ID (for linking to schema-level deterministic)
        
        Returns:
            List of DeterministicChunk objects
        """
        self.logger.info(f"Creating deterministic chunks for file_id: {file_id}")
        
        # Get schema-level deterministic (if exists) - ENHANCEMENT: Dual-layer deterministic
        schema_fingerprint = None
        pattern_signature = None
        if parsed_file_id and self.deterministic_embedding_service:
            try:
                context = ExecutionContext(tenant_id=tenant_id)
                # Try to get deterministic embedding by parsed_file_id
                # Note: We may need to search by parsed_file_id, not embedding_id
                # For now, we'll try to get it if we have the embedding_id stored
                # This is a placeholder - actual implementation may need to query by parsed_file_id
                deterministic_embedding = await self._get_deterministic_embedding_by_parsed_file_id(
                    parsed_file_id=parsed_file_id,
                    context=context
                )
                if deterministic_embedding:
                    schema_fingerprint = deterministic_embedding.get("schema_fingerprint")
                    pattern_signature = deterministic_embedding.get("pattern_signature")
                    self.logger.debug(f"Linked chunks to schema fingerprint: {schema_fingerprint[:16] if schema_fingerprint else None}")
            except Exception as e:
                self.logger.debug(f"Could not link to schema-level deterministic: {e}")
                # Schema-level may not exist yet - that's okay
        
        # Normalize input to standard format (handles multiple input formats)
        normalized = self._normalize_parsed_content(parsed_content)
        
        # Extract fields using correct names (aligned with FileParserService)
        parsing_type = normalized.get("parsing_type", "unstructured")
        text_content = normalized.get("text_content", "")
        structured_data = normalized.get("structured_data")
        structure_metadata = normalized.get("structure", {})
        
        # Extract structural elements based on parsing type
        structural_elements = self._extract_structural_elements(
            structure=structure_metadata,
            text_content=text_content,
            structured_data=structured_data,
            parsing_type=parsing_type
        )
        
        chunks = []
        for idx, element in enumerate(structural_elements):
            # Generate stable chunk ID (content-addressed)
            chunk_id = self._generate_chunk_id(
                file_id=file_id,
                element_path=element["path"],
                text_hash=element["text_hash"]
            )
            
            chunks.append(DeterministicChunk(
                chunk_id=chunk_id,
                chunk_index=idx,
                source_path=f"{file_id}:{element['path']}",
                text_hash=element["text_hash"],
                structural_type=element["type"],
                byte_offset=element.get("byte_offset"),
                logical_offset=element.get("logical_offset"),
                text=element["text"],
                schema_fingerprint=schema_fingerprint,
                pattern_hints=pattern_signature,
                metadata={
                    "file_id": file_id,
                    "parsed_file_id": parsed_file_id,
                    "tenant_id": tenant_id,
                    "parsing_type": parsing_type,  # Use parsing_type (aligned with FileParserService)
                    "created_at": datetime.utcnow().isoformat()
                }
            ))
        
        self.logger.info(f"✅ Created {len(chunks)} deterministic chunks for file_id: {file_id}")
        
        return chunks
    
    def _normalize_parsed_content(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize parsed content to standard format.
        
        Now that parsers are standardized, this is simpler - mainly handles legacy formats
        and ensures parsing_type and structure are always present.
        
        Args:
            parsed_content: Parsed content in any supported format
        
        Returns:
            Normalized dict with: parsing_type, text_content, structured_data, structure
        """
        normalized = {}
        
        # Handle FileParsingResult format (from parsing abstraction) - NOW STANDARDIZED
        if "text_content" in parsed_content or "structured_data" in parsed_content:
            normalized["text_content"] = parsed_content.get("text_content")
            normalized["structured_data"] = parsed_content.get("structured_data")
            # parsing_type is now always set in FileParsingResult
            normalized["parsing_type"] = parsed_content.get("parsing_type") or parsed_content.get("metadata", {}).get("parsing_type", "unstructured")
            # structure is now always in metadata.structure
            normalized["structure"] = parsed_content.get("metadata", {}).get("structure", {})
        
        # Handle retrieved parsed file format (from GCS via get_parsed_file)
        elif "parsed_content" in parsed_content:
            content = parsed_content["parsed_content"]
            metadata = parsed_content.get("metadata", {})
            
            normalized["parsing_type"] = metadata.get("parsing_type", "unstructured")
            
            # Extract text_content and structured_data
            if isinstance(content, str):
                normalized["text_content"] = content
                normalized["structured_data"] = None
            elif isinstance(content, (dict, list)):
                normalized["text_content"] = None
                normalized["structured_data"] = content
            else:
                normalized["text_content"] = str(content) if content else None
                normalized["structured_data"] = None
            
            # Extract structure from metadata (now standardized)
            normalized["structure"] = metadata.get("structure", {})
        
        # Handle direct parsed_data format (from parse_file result)
        elif "parsed_data" in parsed_content:
            parsed_data = parsed_content["parsed_data"]
            normalized["parsing_type"] = parsed_content.get("parsing_type") or parsed_content.get("metadata", {}).get("parsing_type", "unstructured")
            
            if isinstance(parsed_data, str):
                normalized["text_content"] = parsed_data
                normalized["structured_data"] = None
            elif isinstance(parsed_data, (dict, list)):
                normalized["text_content"] = None
                normalized["structured_data"] = parsed_data
            else:
                normalized["text_content"] = str(parsed_data) if parsed_data else None
                normalized["structured_data"] = None
            
            # Extract structure from metadata (now standardized)
            metadata = parsed_content.get("metadata", {})
            normalized["structure"] = metadata.get("structure", {})
        
        # Fallback: assume it's already normalized or try to infer
        else:
            normalized = parsed_content.copy()
            # Ensure required fields exist
            if "parsing_type" not in normalized:
                normalized["parsing_type"] = normalized.get("metadata", {}).get("parsing_type", "unstructured")
            if "text_content" not in normalized:
                normalized["text_content"] = None
            if "structured_data" not in normalized:
                normalized["structured_data"] = None
            if "structure" not in normalized:
                normalized["structure"] = normalized.get("metadata", {}).get("structure", {})
        
        return normalized
    
    def _extract_structural_elements(
        self,
        structure: Dict[str, Any],
        text_content: str,
        structured_data: Optional[Any],
        parsing_type: str
    ) -> List[Dict[str, Any]]:
        """
        Extract structural elements from parsed content.
        
        CTO Principle: Use parser structure, not heuristics
        CIO Requirement: Deterministic extraction (same input → same output)
        
        Args:
            structure: Structure metadata from parser (now standardized - always in metadata.structure)
            text_content: Raw text content
            structured_data: Structured data (now standardized format)
            parsing_type: Type of parser used (aligned with FileParserService)
        
        Returns:
            List of structural elements with path, type, text, offsets
        """
        elements = []
        
        # Handle structured data (CSV, Excel, JSON, Mainframe)
        if parsing_type == "structured" and structured_data:
            # structured_data is now standardized dict with "format": "structured"
            if isinstance(structured_data, dict):
                # Extract rows from standardized format
                rows = structured_data.get("rows") or structured_data.get("data", [])
                if rows:
                    elements.extend(self._extract_from_structured_data(rows, parsing_type))
                # Handle sheets (Excel)
                sheets = structured_data.get("sheets", [])
                for sheet in sheets:
                    sheet_rows = sheet.get("rows", [])
                    if sheet_rows:
                        elements.extend(self._extract_from_structured_data(sheet_rows, parsing_type))
        
        # Handle unstructured text (PDF, DOCX, TXT, etc.)
        elif parsing_type in ["unstructured", "pdf", "docx", "txt", "text"]:
            if structure:
                # Use structure metadata (now standardized - always in metadata.structure)
                elements.extend(self._extract_from_structure_metadata(structure, text_content))
            elif text_content:
                # Fallback: Extract paragraphs from raw text
                elements.extend(self._extract_paragraphs_from_text(text_content))
        
        # Handle hybrid content (PDF with tables, Word with tables)
        elif parsing_type == "hybrid":
            if structure and text_content:
                # Extract from structure metadata (pages, sections, paragraphs)
                elements.extend(self._extract_from_structure_metadata(structure, text_content))
            if structured_data:
                # Extract tables from standardized format
                tables = structured_data.get("tables", [])
                if tables:
                    # Treat tables as structured data
                    for table in tables:
                        if isinstance(table, list):
                            elements.extend(self._extract_from_structured_data(table, parsing_type))
        
        # Handle workflow files (BPMN, DrawIO)
        elif parsing_type == "workflow":
            if structure:
                workflow_structure = structure.get("workflow", {})
                tasks = workflow_structure.get("tasks", [])
                gateways = workflow_structure.get("gateways", [])
                
                # Chunk by tasks (primary structure)
                for task in tasks:
                    task_text = f"Task: {task.get('task_name', '')} - {task.get('documentation', '')}"
                    text_hash = self._normalize_and_hash(task_text)
                    elements.append({
                        "path": f"task_{task.get('task_index', 0)}",
                        "type": "task",
                        "text": task_text,
                        "text_hash": text_hash,
                        "logical_offset": task.get("task_index")
                    })
                
                # Chunk by gateways (decision points)
                for gateway in gateways:
                    gateway_text = f"Gateway: {gateway.get('gateway_name', '')}"
                    text_hash = self._normalize_and_hash(gateway_text)
                    elements.append({
                        "path": f"gateway_{gateway.get('gateway_index', 0)}",
                        "type": "gateway",
                        "text": gateway_text,
                        "text_hash": text_hash,
                        "logical_offset": gateway.get("gateway_index")
                    })
        
        # Handle SOP files (Markdown)
        elif parsing_type == "sop":
            if structure:
                sections = structure.get("sections", [])
                steps = structure.get("steps", [])
                
                # Chunk by sections
                for section in sections:
                    section_text = f"{section.get('section_title', '')}\n{section.get('text', '')}"
                    text_hash = self._normalize_and_hash(section_text)
                    elements.append({
                        "path": f"section_{section.get('section_index', 0)}",
                        "type": "section",
                        "text": section_text,
                        "text_hash": text_hash,
                        "logical_offset": section.get("section_index")
                    })
                
                # Chunk by steps
                for step in steps:
                    step_text = step.get("step_text", "")
                    text_hash = self._normalize_and_hash(step_text)
                    elements.append({
                        "path": f"step_{step.get('step_index', 0)}",
                        "type": "step",
                        "text": step_text,
                        "text_hash": text_hash,
                        "logical_offset": step.get("step_index")
                    })
        
        # Handle mainframe files
        elif parsing_type == "mainframe":
            if structure:
                records = structure.get("records", [])
                for record in records:
                    record_data = record.get("data", {})
                    record_text = json.dumps(record_data, sort_keys=True) if isinstance(record_data, dict) else str(record_data)
                    text_hash = self._normalize_and_hash(record_text)
                    elements.append({
                        "path": f"record_{record.get('record_index', 0)}",
                        "type": "record",
                        "text": record_text,
                        "text_hash": text_hash,
                        "logical_offset": record.get("record_index")
                    })
        
        # Handle data model files (JSON Schema, YAML)
        elif parsing_type == "data_model":
            if structure:
                schema_structure = structure.get("schema", {})
                schema_text = json.dumps(schema_structure, sort_keys=True)
                text_hash = self._normalize_and_hash(schema_text)
                elements.append({
                    "path": "schema",
                    "type": "schema",
                    "text": schema_text,
                    "text_hash": text_hash,
                    "logical_offset": 0
                })
        
        return elements
    
    def _extract_from_structured_data(
        self,
        data: List[Any],
        parsing_type: str
    ) -> List[Dict[str, Any]]:
        """
        Extract chunks from structured data (CSV, Excel, JSON rows, etc.).
        
        Each row becomes a chunk (deterministic - same rows → same chunks).
        """
        elements = []
        
        if not isinstance(data, list) or len(data) == 0:
            return elements
        
        for row_idx, row in enumerate(data):
            # Convert row to text representation (deterministic)
            if isinstance(row, dict):
                row_text = json.dumps(row, sort_keys=True)
            elif isinstance(row, (list, tuple)):
                row_text = json.dumps(row, sort_keys=True)
            else:
                row_text = str(row)
            
            text_hash = self._normalize_and_hash(row_text)
            
            elements.append({
                "path": f"row_{row_idx}",
                "type": "row",
                "text": row_text,
                "text_hash": text_hash,
                "logical_offset": row_idx
            })
        
        return elements
    
    def _extract_from_structure_metadata(
        self,
        structure: Dict[str, Any],
        text_content: str
    ) -> List[Dict[str, Any]]:
        """
        Extract chunks from structure metadata (pages, sections, paragraphs).
        
        CTO Principle: Use parser structure, not heuristics
        """
        elements = []
        
        # Handle pages
        pages = structure.get("pages", [])
        if pages:
            for page_idx, page in enumerate(pages):
                page_text = page.get("text", "")
                if page_text:
                    text_hash = self._normalize_and_hash(page_text)
                    elements.append({
                        "path": f"page_{page_idx}",
                        "type": "page",
                        "text": page_text,
                        "text_hash": text_hash,
                        "logical_offset": page_idx,
                        "byte_offset": page.get("byte_offset")
                    })
                
                # Extract sections within page
                sections = page.get("sections", [])
                for section_idx, section in enumerate(sections):
                    section_text = section.get("text", "")
                    if section_text:
                        text_hash = self._normalize_and_hash(section_text)
                        elements.append({
                            "path": f"page_{page_idx}/section_{section_idx}",
                            "type": "section",
                            "text": section_text,
                            "text_hash": text_hash,
                            "logical_offset": (page_idx, section_idx),
                            "byte_offset": section.get("byte_offset")
                        })
                    
                    # Extract paragraphs within section
                    paragraphs = section.get("paragraphs", [])
                    for para_idx, para in enumerate(paragraphs):
                        para_text = para.get("text", "")
                        if para_text:
                            text_hash = self._normalize_and_hash(para_text)
                            elements.append({
                                "path": f"page_{page_idx}/section_{section_idx}/paragraph_{para_idx}",
                                "type": "paragraph",
                                "text": para_text,
                                "text_hash": text_hash,
                                "logical_offset": (page_idx, section_idx, para_idx),
                                "byte_offset": para.get("byte_offset")
                            })
        
        # Handle sections (if not nested in pages)
        sections = structure.get("sections", [])
        if sections and not pages:
            for section_idx, section in enumerate(sections):
                section_text = section.get("text", "")
                if section_text:
                    text_hash = self._normalize_and_hash(section_text)
                    elements.append({
                        "path": f"section_{section_idx}",
                        "type": "section",
                        "text": section_text,
                        "text_hash": text_hash,
                        "logical_offset": section_idx,
                        "byte_offset": section.get("byte_offset")
                    })
                
                # Extract paragraphs within section
                paragraphs = section.get("paragraphs", [])
                for para_idx, para in enumerate(paragraphs):
                    para_text = para.get("text", "")
                    if para_text:
                        text_hash = self._normalize_and_hash(para_text)
                        elements.append({
                            "path": f"section_{section_idx}/paragraph_{para_idx}",
                            "type": "paragraph",
                            "text": para_text,
                            "text_hash": text_hash,
                            "logical_offset": (section_idx, para_idx),
                            "byte_offset": para.get("byte_offset")
                        })
        
        # Handle paragraphs (if not nested in sections/pages)
        paragraphs = structure.get("paragraphs", [])
        if paragraphs and not pages and not sections:
            for para_idx, para in enumerate(paragraphs):
                para_text = para.get("text", "") if isinstance(para, dict) else str(para)
                if para_text:
                    text_hash = self._normalize_and_hash(para_text)
                    elements.append({
                        "path": f"paragraph_{para_idx}",
                        "type": "paragraph",
                        "text": para_text,
                        "text_hash": text_hash,
                        "logical_offset": para_idx,
                        "byte_offset": para.get("byte_offset") if isinstance(para, dict) else None
                    })
        
        return elements
    
    def _extract_paragraphs_from_text(
        self,
        text_content: str
    ) -> List[Dict[str, Any]]:
        """
        Fallback: Extract paragraphs from raw text (when no structure metadata).
        
        This is a deterministic fallback - splits on double newlines.
        """
        elements = []
        
        if not text_content:
            return elements
        
        # Split on double newlines (paragraph boundaries)
        paragraphs = re.split(r'\n\s*\n', text_content)
        
        for para_idx, para_text in enumerate(paragraphs):
            para_text = para_text.strip()
            if para_text:
                text_hash = self._normalize_and_hash(para_text)
                elements.append({
                    "path": f"paragraph_{para_idx}",
                    "type": "paragraph",
                    "text": para_text,
                    "text_hash": text_hash,
                    "logical_offset": para_idx
                })
        
        return elements
    
    def _normalize_and_hash(self, text: str) -> str:
        """
        Normalize text and create hash for re-embedding detection.
        
        CIO Requirement: Deterministic and replayable
        """
        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', text.strip())
        
        # Create hash
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    
    def _generate_chunk_id(
        self,
        file_id: str,
        element_path: str,
        text_hash: str
    ) -> str:
        """
        Generate stable, content-addressed chunk ID.
        
        CIO Requirement: Deterministic and replayable
        CTO Principle: Stable identity
        
        Args:
            file_id: File identifier
            element_path: Structural path (e.g., "page_0/section_1/paragraph_2")
            text_hash: Normalized text hash
        
        Returns:
            16-character hex chunk ID
        """
        # Create content-addressed ID
        content = f"{file_id}:{element_path}:{text_hash}"
        full_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        # Use first 16 characters for shorter ID (still collision-resistant for our use case)
        return full_hash[:16]
    
    async def _get_deterministic_embedding_by_parsed_file_id(
        self,
        parsed_file_id: str,
        context: ExecutionContext
    ) -> Optional[Dict[str, Any]]:
        """
        Get deterministic embedding by parsed_file_id.
        
        This is a helper to link chunks to schema-level deterministic.
        The actual implementation may need to query by parsed_file_id.
        
        For now, this is a placeholder - we may need to add a method to
        DeterministicEmbeddingService to query by parsed_file_id.
        """
        # TODO: Implement query by parsed_file_id
        # For now, return None (schema-level may not exist yet)
        return None
