"""
Parsing Service Protocols

Defines interfaces for all parsing services (structured, unstructured, hybrid, workflow/SOP).
All services use State Surface for file references.

WHAT (Infrastructure Role): I define how parsing services should operate
HOW (Infrastructure Implementation): I provide the interface for parsing service logic
"""

from typing import Protocol, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ParsingRequest:
    """Request for parsing operations using State Surface."""
    file_reference: str  # State Surface reference
    filename: str = ""
    options: Optional[Dict[str, Any]] = None


@dataclass
class ParsingResult:
    """Result of parsing operations."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None  # For insights pillar
    error: Optional[str] = None
    timestamp: str = ""

    def __post_init__(self):
        """Set timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


class StructuredParsingProtocol(Protocol):
    """Protocol for structured parsing service."""
    
    async def parse_structured_file(
        self,
        request: ParsingRequest
    ) -> ParsingResult:
        """
        Parse structured file (Excel, CSV, JSON, Binary + Copybook).
        
        Args:
            request: ParsingRequest with file_reference
        
        Returns:
            ParsingResult with structured data (tables, records)
        """
        ...


class UnstructuredParsingProtocol(Protocol):
    """Protocol for unstructured parsing service."""
    
    async def parse_unstructured_file(
        self,
        request: ParsingRequest
    ) -> ParsingResult:
        """
        Parse unstructured file (PDF, Word, Text, Image).
        
        Args:
            request: ParsingRequest with file_reference
        
        Returns:
            ParsingResult with text chunks for semantic processing
        """
        ...


class HybridParsingProtocol(Protocol):
    """Protocol for hybrid parsing service."""
    
    async def parse_hybrid_file(
        self,
        request: ParsingRequest
    ) -> ParsingResult:
        """
        Parse hybrid file (structured + unstructured).
        
        Args:
            request: ParsingRequest with file_reference
        
        Returns:
            ParsingResult with both structured and unstructured data
        """
        ...


class WorkflowSOPParsingProtocol(Protocol):
    """Protocol for workflow/SOP parsing service."""
    
    async def parse_workflow_file(
        self,
        request: ParsingRequest
    ) -> ParsingResult:
        """
        Parse workflow file (BPMN, Draw.io, JSON).
        
        Args:
            request: ParsingRequest with file_reference
        
        Returns:
            ParsingResult with workflow structure (nodes, edges)
        """
        ...
    
    async def parse_sop_file(
        self,
        request: ParsingRequest
    ) -> ParsingResult:
        """
        Parse SOP file (DOCX, PDF, TXT, MD).
        
        Args:
            request: ParsingRequest with file_reference
        
        Returns:
            ParsingResult with SOP structure (sections, steps, roles)
        """
        ...
