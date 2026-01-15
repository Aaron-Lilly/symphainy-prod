# Holistic Parsing Implementation Plan for `symphainy_source_code`

**Date:** January 10, 2026  
**Status:** 📋 **READY FOR IMPLEMENTATION**  
**Goal:** Create separate parsing services aligned with frontend patterns, bringing forward all parsing capabilities

---

## ✅ Architecture Compliance - Three Critical Requirements

This plan **explicitly addresses** all three requirements:

### 1. ✅ Mainframe Parsing Gold Standard

**Fully Integrated:**
- ✅ **Custom parser** - Production-ready implementation (from `MAINFRAME_PARSING_IMPLEMENTATION_PLAN.md`)
- ✅ **Cobrix parser** - Gold standard, simplified (~200 lines vs 1400+)
  - Extract 88-level metadata BEFORE cleaning
  - Minimal preprocessing (trust Cobrix capabilities)
  - Use Cobrix options (file_start_offset, file_trailer_length)
  - No workarounds, no manual field fixes
- ✅ **Unified adapter** - Strategy pattern with auto-selection
- ✅ **88-level metadata** - Extracted BEFORE cleaning, passed to insights pillar
- ✅ **State Surface integration** - File references, not bytes

**Location:** Structured Parsing Service → `binary_parser.py` module

**Reference:** See `MAINFRAME_PARSING_IMPLEMENTATION_PLAN.md` and `COBRIX_GOLD_STANDARD_FIX.md`

---

### 2. ✅ State Surface Architecture for All Parsing

**All Parsing Services Use State Surface:**
- ✅ **State Surface extended** - File storage methods (`store_file()`, `get_file()`, `get_file_metadata()`)
- ✅ **All services** - Use file references, not bytes
- ✅ **All abstractions** - Updated to retrieve files from State Surface
- ✅ **All adapters** - Work with bytes (retrieved by abstractions)
- ✅ **No bytes passed** - Through service layers (only references)

**Pattern Applied Everywhere:**
```python
# OLD (old repo):
async def parse_file(self, file_data: bytes, ...) -> Dict

# NEW (symphainy_source_code):
async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
    file_data = await self.state_surface.get_file(request.file_reference)
    # ... parse ...
```

**Updated Abstractions:**
- PdfProcessingAbstraction ✅
- WordProcessingAbstraction ✅
- ExcelProcessingAbstraction ✅
- CsvProcessingAbstraction ✅
- JsonProcessingAbstraction ✅
- TextProcessingAbstraction ✅
- HtmlProcessingAbstraction ✅
- ImageProcessingAbstraction ✅
- MainframeProcessingAbstraction ✅ (from mainframe plan)
- KreuzbergProcessingAbstraction ✅

---

### 3. ✅ All Parsing Pattern Abstractions Properly Implemented

**All Abstractions Updated for New Architecture:**
- ✅ **Protocol compliance** - All implement `FileParsingProtocol`
- ✅ **Request/Result pattern** - All use `FileParsingRequest` / `FileParsingResult`
- ✅ **State Surface integration** - All retrieve files from State Surface
- ✅ **Consistent interface** - Same pattern across all parsing types
- ✅ **Proper abstraction layer** - Lightweight coordination, not business logic

**Abstraction Pattern:**
```python
class ProcessingAbstraction:
    """All abstractions follow this pattern."""
    
    def __init__(self, adapter, state_surface):
        self.adapter = adapter  # Layer 0 (raw technology)
        self.state_surface = state_surface  # State Surface for files
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        # 1. Retrieve file from State Surface
        file_data = await self.state_surface.get_file(request.file_reference)
        
        # 2. Parse using adapter (adapter works with bytes)
        result = await self.adapter.parse(file_data)
        
        # 3. Return FileParsingResult
        return FileParsingResult(success=True, ...)
```

**All Abstractions Available:**
- ✅ PDF, Word, Excel, CSV, JSON, Text, HTML, Image processing abstractions
- ✅ Mainframe processing abstraction (custom + Cobrix strategies)
- ✅ Kreuzberg processing abstraction (hybrid files)
- ✅ All registered in Public Works Foundation
- ✅ All accessible via Platform Gateway

---

## 🎯 Executive Summary

This document provides a comprehensive plan to:
1. **Split parsing into 4 separate services** aligned with frontend patterns:
   - **Structured Parsing Service** - Excel, CSV, JSON, Binary + Copybook
   - **Unstructured Parsing Service** - PDF, Word, Text, Images
   - **Hybrid Parsing Service** - Files with both structured and unstructured content
   - **Workflow/SOP Parsing Service** - BPMN, Draw.io, SOP documents

2. **Bring forward all parsing capabilities** from old repo with **NEW ARCHITECTURE**:
   - PDF processing (pdfplumber, PyPDF2) - **Updated to use State Surface**
   - Word processing (python-docx) - **Updated to use State Surface**
   - Excel processing (openpyxl, pandas) - **Updated to use State Surface**
   - CSV processing - **Updated to use State Surface**
   - JSON processing - **Updated to use State Surface**
   - Text processing - **Updated to use State Surface**
   - Image processing (OCR with Tesseract, OpenCV) - **Updated to use State Surface**
   - HTML processing (BeautifulSoup) - **Updated to use State Surface**
   - **Mainframe parsing (Custom + Cobrix) - GOLD STANDARD implementation** (see `MAINFRAME_PARSING_IMPLEMENTATION_PLAN.md`)
   - Workflow parsing (BPMN, Draw.io, JSON) - **Updated to use State Surface**
   - SOP parsing (structure extraction) - **Updated to use State Surface**

3. **Evaluate Kreuzeberg** for hybrid file handling

4. **Ensure all abstractions use new architecture:**
   - ✅ State Surface for file references (not passing bytes)
   - ✅ Updated protocols for new architecture
   - ✅ All adapters updated to use State Surface
   - ✅ All abstractions updated to use State Surface
   - ✅ Mainframe parsers aligned to gold standard (Cobrix simplified, Custom production-ready)

---

## 📊 Current State Analysis

### Old Repo Structure

**Single Service Approach:**
- `FileParserService` - One service handling all parsing types
- Modules: `structured_parsing.py`, `unstructured_parsing.py`, `hybrid_parsing.py`, `workflow_parsing.py`, `sop_parsing.py`
- All parsing logic in one place (monolithic)

**Abstractions (Public Works Foundation):**
- `PdfProcessingAbstraction` - PDF processing
- `WordProcessingAbstraction` - Word document processing
- `ExcelProcessingAbstraction` - Excel processing
- `CsvProcessingAbstraction` - CSV processing
- `JsonProcessingAbstraction` - JSON processing
- `TextProcessingAbstraction` - Text processing
- `HtmlProcessingAbstraction` - HTML processing
- `ImageProcessingAbstraction` - Image/OCR processing
- `MainframeProcessingAbstraction` - Mainframe parsing

**Adapters (Layer 0):**
- `pdfplumber_adapter`, `pypdf2_adapter` - PDF
- `python_docx_adapter` - Word
- `excel_processing_adapter` - Excel
- `csv_processing_adapter` - CSV
- `json_processing_adapter` - JSON
- `text_processing_adapter` - Text
- `beautifulsoup_html_adapter` - HTML
- `pytesseract_ocr_adapter`, `opencv_image_processor` - Images
- `mainframe_processing_adapter`, `cobrix_service_adapter` - Mainframe

### Current Hybrid Parsing Implementation

**Location:** `hybrid_parsing.py`

**Current Approach:**
1. Calls `StructuredParsing.parse()` - Gets structured data
2. Calls `UnstructuredParsing.parse()` - Gets unstructured chunks
3. Creates correlation map (simple round-robin mapping)
4. Returns 3 JSON files: structured, unstructured, correlation map

**Limitations:**
- Simple correlation mapping (not semantic)
- No intelligent extraction of structured data from unstructured context
- No understanding of relationships between tables and text
- Manual coordination between two separate parsing calls

---

## 🔍 Kreuzeberg Evaluation

### What is Kreuzeberg?

**Kreuzberg** is a high-performance document intelligence platform that:
- Extracts text, tables, and metadata from 56+ file formats
- Converts documents to clean Markdown or JSON
- Preserves table structure and metadata
- Supports streaming parsers for large files (constant memory)
- Multi-engine OCR (Tesseract, EasyOCR, PaddleOCR)
- Plugin ecosystem for post-processors and validators

### Kreuzeberg for Hybrid Files

**Strengths:**
- ✅ **Native hybrid support** - Extracts both structured (tables) and unstructured (text) in one pass
- ✅ **Intelligent extraction** - Understands relationships between tables and surrounding text
- ✅ **Preserves structure** - Maintains table formatting and metadata
- ✅ **Performance** - Streaming parsers for large files
- ✅ **Format support** - 56+ formats including PDF, Office docs, images
- ✅ **Clean output** - Markdown or JSON with structured data

**Use Cases:**
- PDFs with embedded tables
- Word documents with tables and text
- Excel files with text annotations
- Scanned documents (OCR + table extraction)
- Complex documents requiring both structured and unstructured extraction

### Recommendation: **YES - Use Kreuzeberg for Hybrid Parsing**

**Rationale:**
1. **Native hybrid capability** - Designed for this exact use case
2. **Better correlation** - Understands relationships between tables and text
3. **Simpler architecture** - One parsing call instead of two separate calls
4. **Better performance** - Streaming parsers, optimized for large files
5. **Future-proof** - Plugin ecosystem allows customization

**Implementation Strategy:**
- Use Kreuzeberg as the primary hybrid parser
- Keep current approach as fallback for formats Kreuzeberg doesn't support
- Integrate Kreuzeberg as an adapter in Public Works Foundation

---

## 🏗️ Target Architecture

### Service Structure

```
symphainy_platform/
  realms/
    content/
      services/
        structured_parsing_service/
          structured_parsing_service.py
          modules/
            excel_parser.py
            csv_parser.py
            json_parser.py
            binary_parser.py  # Mainframe parsing
        unstructured_parsing_service/
          unstructured_parsing_service.py
          modules/
            pdf_parser.py
            word_parser.py
            text_parser.py
            image_parser.py  # OCR
        hybrid_parsing_service/
          hybrid_parsing_service.py
          modules/
            kreuzberg_parser.py  # Primary hybrid parser
            fallback_parser.py    # Current approach (structured + unstructured)
        workflow_sop_parsing_service/
          workflow_sop_parsing_service.py
          modules/
            workflow_parser.py  # BPMN, Draw.io, JSON workflows
            sop_parser.py       # SOP structure extraction
```

### Foundation Structure (Unchanged)

```
symphainy_platform/
  foundations/
    public_works/
      adapters/
        # All existing adapters (PDF, Word, Excel, etc.)
        # + New: kreuzberg_adapter.py
      abstractions/
        # All existing abstractions
        # + New: kreuzberg_processing_abstraction.py
      protocols/
        # All existing protocols
        # + New: kreuzberg_processing_protocol.py
```

---

## 📋 Implementation Plan

### Phase 1: Foundation - Protocols and Abstractions (Week 1)

#### 1.1 Create Parsing Service Protocols

**File:** `symphainy_platform/foundations/public_works/protocols/parsing_service_protocol.py`

```python
"""
Parsing Service Protocols

Defines interfaces for all parsing services.
"""

from typing import Protocol, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ParsingRequest:
    """Request for parsing operations."""
    file_reference: str  # State Surface reference
    filename: str = ""
    options: Optional[Dict[str, Any]] = None

@dataclass
class ParsingResult:
    """Result of parsing operations."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str = ""

class StructuredParsingProtocol(Protocol):
    """Protocol for structured parsing service."""
    
    async def parse_structured_file(
        self,
        request: ParsingRequest
    ) -> ParsingResult:
        """Parse structured file (Excel, CSV, JSON, Binary)."""
        ...

class UnstructuredParsingProtocol(Protocol):
    """Protocol for unstructured parsing service."""
    
    async def parse_unstructured_file(
        self,
        request: ParsingRequest
    ) -> ParsingResult:
        """Parse unstructured file (PDF, Word, Text, Image)."""
        ...

class HybridParsingProtocol(Protocol):
    """Protocol for hybrid parsing service."""
    
    async def parse_hybrid_file(
        self,
        request: ParsingRequest
    ) -> ParsingResult:
        """Parse hybrid file (structured + unstructured)."""
        ...

class WorkflowSOPParsingProtocol(Protocol):
    """Protocol for workflow/SOP parsing service."""
    
    async def parse_workflow_file(
        self,
        request: ParsingRequest
    ) -> ParsingResult:
        """Parse workflow file (BPMN, Draw.io, JSON)."""
        ...
    
    async def parse_sop_file(
        self,
        request: ParsingRequest
    ) -> ParsingResult:
        """Parse SOP file (DOCX, PDF, TXT, MD)."""
        ...
```

#### 1.2 Create Kreuzeberg Adapter and Abstraction

**File:** `symphainy_platform/foundations/public_works/adapters/kreuzberg_adapter.py`

```python
"""
Kreuzberg Adapter - Layer 0

Raw technology client for Kreuzberg document intelligence platform.
"""

from typing import Dict, Any, Optional
import asyncio

class KreuzbergAdapter:
    """Adapter for Kreuzberg document intelligence platform."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "http://localhost:8080"):
        """
        Initialize Kreuzberg adapter.
        
        Args:
            api_key: Kreuzberg API key (if using hosted service)
            base_url: Kreuzberg service URL (if using local service)
        """
        self.api_key = api_key
        self.base_url = base_url
    
    async def extract_document(
        self,
        file_data: bytes,
        filename: str,
        output_format: str = "json"  # "json" or "markdown"
    ) -> Dict[str, Any]:
        """
        Extract text, tables, and metadata from document.
        
        Args:
            file_data: File data as bytes
            filename: Original filename
            output_format: Output format ("json" or "markdown")
        
        Returns:
            Dictionary with extracted content:
            {
                "text": str,  # Full text content
                "tables": List[Dict],  # Extracted tables
                "metadata": Dict,  # Document metadata
                "structure": Dict  # Document structure
            }
        """
        # Implementation: Call Kreuzberg API or SDK
        ...
```

**File:** `symphainy_platform/foundations/public_works/abstractions/kreuzberg_processing_abstraction.py`

```python
"""
Kreuzberg Processing Abstraction - Layer 1

Lightweight coordination layer for Kreuzberg processing operations.
"""

from typing import Dict, Any, Optional
from ..adapters.kreuzberg_adapter import KreuzbergAdapter
from ..protocols.file_parsing_protocol import FileParsingRequest, FileParsingResult

class KreuzbergProcessingAbstraction:
    """Abstraction for Kreuzberg document processing."""
    
    def __init__(self, kreuzberg_adapter: KreuzbergAdapter, state_surface):
        self.kreuzberg_adapter = kreuzberg_adapter
        self.state_surface = state_surface  # State Surface for file retrieval
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse file using Kreuzberg.
        
        Returns both structured (tables) and unstructured (text) content.
        Uses State Surface for file retrieval.
        """
        # Get file from State Surface
        file_data = await self.state_surface.get_file(request.file_reference)
        
        # Extract using Kreuzberg
        result = await self.kreuzberg_adapter.extract_document(
            file_data=file_data,
            filename=request.filename,
            output_format="json"
        )
        
        # Convert to FileParsingResult
        return FileParsingResult(
            success=True,
            text_content=result.get("text", ""),
            structured_data={
                "tables": result.get("tables", []),
                "metadata": result.get("metadata", {}),
                "structure": result.get("structure", {})
            },
            metadata=result.get("metadata", {})
        )
```

---

### Phase 2: Structured Parsing Service (Week 1-2)

#### 2.1 Create Structured Parsing Service

**File:** `symphainy_platform/realms/content/services/structured_parsing_service/structured_parsing_service.py`

**Responsibilities:**
- Excel parsing (XLSX, XLS)
- CSV parsing
- JSON parsing
- **Binary + Copybook parsing (mainframe) - GOLD STANDARD**
- State Surface integration
- Validation rules extraction (88-level fields)

**Modules:**
- `excel_parser.py` - Excel parsing logic (uses ExcelProcessingAbstraction via State Surface)
- `csv_parser.py` - CSV parsing logic (uses CsvProcessingAbstraction via State Surface)
- `json_parser.py` - JSON parsing logic (uses JsonProcessingAbstraction via State Surface)
- `binary_parser.py` - **Mainframe parsing (uses unified adapter from MAINFRAME_PARSING_IMPLEMENTATION_PLAN.md)**

**Key Integration Points:**
- **Mainframe Parsing:** Uses implementation from `MAINFRAME_PARSING_IMPLEMENTATION_PLAN.md`:
  - Custom strategy (production-ready)
  - Cobrix strategy (gold standard, simplified)
  - Unified adapter with auto-selection
  - 88-level metadata extraction (BEFORE cleaning)
  - State Surface integration (file references, not bytes)

**State Surface Integration:**
```python
async def parse_structured_file(
    self,
    file_reference: str,
    filename: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Parse structured file using State Surface reference.
    """
    # Retrieve file from State Surface
    file_data = await self.state_surface.get_file(file_reference)
    
    # Get file type
    file_type = self._get_file_type(filename)
    
    # Route to appropriate parser
    if file_type in ["bin", "binary"]:
        # Mainframe parsing - use unified adapter
        copybook_ref = options.get("copybook_reference") if options else None
        return await self.binary_parser.parse(
            file_reference=file_reference,
            copybook_reference=copybook_ref,
            options=options or {}
        )
    elif file_type in ["xlsx", "xls"]:
        # Excel parsing - use abstraction
        return await self.excel_parser.parse(file_reference, options)
    # ... etc
```

**Implementation:**
- Use existing abstractions (ExcelProcessingAbstraction, CsvProcessingAbstraction, etc.)
- Integrate with State Surface
- Extract validation rules for binary files
- Return structured data (tables, records)

---

### Phase 3: Unstructured Parsing Service (Week 2)

#### 3.1 Create Unstructured Parsing Service

**File:** `symphainy_platform/realms/content/services/unstructured_parsing_service/unstructured_parsing_service.py`

**Responsibilities:**
- PDF parsing (text + tables)
- Word parsing (DOCX, DOC)
- Text parsing (TXT, MD)
- Image parsing (OCR with Tesseract)
- HTML parsing
- State Surface integration
- Text chunking for semantic processing

**Modules:**
- `pdf_parser.py` - PDF parsing logic
- `word_parser.py` - Word parsing logic
- `text_parser.py` - Text parsing logic
- `image_parser.py` - Image/OCR parsing logic
- `html_parser.py` - HTML parsing logic

**Implementation:**
- Use existing abstractions (PdfProcessingAbstraction, WordProcessingAbstraction, etc.)
- Integrate with State Surface
- Text chunking (paragraphs → sentences → fixed size)
- Return text chunks for semantic processing

---

### Phase 4: Hybrid Parsing Service (Week 2-3)

#### 4.1 Create Hybrid Parsing Service with Kreuzeberg

**File:** `symphainy_platform/realms/content/services/hybrid_parsing_service/hybrid_parsing_service.py`

**Primary Strategy: Kreuzeberg**
- Use `KreuzbergProcessingAbstraction` for hybrid files
- Single parsing call extracts both structured and unstructured
- Intelligent correlation between tables and text
- Preserves document structure

**Fallback Strategy: Current Approach**
- If Kreuzeberg doesn't support format, use current approach:
  1. Call StructuredParsingService
  2. Call UnstructuredParsingService
  3. Create correlation map

**Modules:**
- `kreuzberg_parser.py` - Primary hybrid parser (Kreuzberg)
- `fallback_parser.py` - Fallback parser (structured + unstructured)

**Implementation:**
```python
async def parse_hybrid_file(
    self,
    file_reference: str,
    filename: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Parse hybrid file using Kreuzeberg (primary) or fallback approach.
    """
    # Try Kreuzeberg first
    if self._should_use_kreuzberg(filename, options):
        return await self._parse_with_kreuzberg(file_reference, filename, options)
    
    # Fallback to structured + unstructured
    return await self._parse_with_fallback(file_reference, filename, options)
```

**Kreuzberg Integration:**
- Add Kreuzberg adapter to Public Works Foundation
- Create Kreuzberg abstraction
- Integrate with Hybrid Parsing Service
- Test with various hybrid file formats

---

### Phase 5: Workflow/SOP Parsing Service (Week 3)

#### 5.1 Create Workflow/SOP Parsing Service

**File:** `symphainy_platform/realms/content/services/workflow_sop_parsing_service/workflow_sop_parsing_service.py`

**Responsibilities:**
- Workflow parsing (BPMN, Draw.io, JSON workflows)
- SOP parsing (structure extraction from DOCX, PDF, TXT, MD)
- State Surface integration
- Workflow structure extraction (nodes, edges, gateways)
- SOP structure extraction (sections, steps, roles)

**Modules:**
- `workflow_parser.py` - Workflow parsing logic
- `sop_parser.py` - SOP parsing logic

**Implementation:**
- Use existing BPMN abstraction (if available)
- Use unstructured parsing for SOP text extraction
- Extract workflow structure (nodes, edges)
- Extract SOP structure (sections, steps, roles)

---

### Phase 6: Update All Abstractions for New Architecture (Week 3)

#### 6.1 Update All Processing Abstractions

**Goal:** Update all existing abstractions to use State Surface instead of accepting bytes directly.

**Abstractions to Update:**
- `PdfProcessingAbstraction` - Update `parse_file()` to use State Surface
- `WordProcessingAbstraction` - Update `parse_file()` to use State Surface
- `ExcelProcessingAbstraction` - Update `parse_file()` to use State Surface
- `CsvProcessingAbstraction` - Update `parse_file()` to use State Surface
- `JsonProcessingAbstraction` - Update `parse_file()` to use State Surface
- `TextProcessingAbstraction` - Update `parse_file()` to use State Surface
- `HtmlProcessingAbstraction` - Update `parse_file()` to use State Surface
- `ImageProcessingAbstraction` - Update `parse_file()` to use State Surface
- `MainframeProcessingAbstraction` - **Already updated in MAINFRAME_PARSING_IMPLEMENTATION_PLAN.md**

**Pattern for All Abstractions:**
```python
class PdfProcessingAbstraction:
    """Updated to use State Surface and new architecture."""
    
    def __init__(self, pdfplumber_adapter, pypdf2_adapter, state_surface):
        self.pdfplumber_adapter = pdfplumber_adapter  # Layer 0 (raw technology)
        self.pypdf2_adapter = pypdf2_adapter  # Layer 0 (raw technology)
        self.state_surface = state_surface  # NEW: State Surface dependency
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse PDF file using State Surface reference.
        
        OLD (old repo): async def parse_file(self, file_data: bytes, filename: str, ...) -> Dict
        NEW (symphainy_source_code): async def parse_file(self, request: FileParsingRequest) -> FileParsingResult
        
        Architecture:
        - Uses State Surface for file retrieval (not accepting bytes)
        - Implements FileParsingProtocol
        - Returns FileParsingResult (not raw dict)
        """
        # 1. Retrieve file from State Surface
        file_data = await self.state_surface.get_file(request.file_reference)
        
        if not file_data:
            return FileParsingResult(
                success=False,
                error=f"File not found: {request.file_reference}",
                timestamp=datetime.utcnow().isoformat()
            )
        
        # 2. Parse using adapter (adapter still works with bytes - Layer 0)
        result = await self.pdfplumber_adapter.parse_pdf(file_data)
        
        # 3. Return FileParsingResult (standardized format)
        return FileParsingResult(
            success=True,
            text_content=result.get("text", ""),
            structured_data={"tables": result.get("tables", [])},
            metadata=result.get("metadata", {}),
            timestamp=datetime.utcnow().isoformat()
        )
```

**Key Changes for ALL Abstractions:**
- ✅ **Accept `FileParsingRequest`** (not `file_data: bytes`)
- ✅ **Retrieve file from State Surface** using `file_reference`
- ✅ **Return `FileParsingResult`** (not raw dict)
- ✅ **Include `state_surface`** in `__init__`
- ✅ **Implement `FileParsingProtocol`** (consistent interface)
- ✅ **No bytes passed** through abstraction layer

**This pattern applies to:**
- PdfProcessingAbstraction ✅
- WordProcessingAbstraction ✅
- ExcelProcessingAbstraction ✅
- CsvProcessingAbstraction ✅
- JsonProcessingAbstraction ✅
- TextProcessingAbstraction ✅
- HtmlProcessingAbstraction ✅
- ImageProcessingAbstraction ✅
- MainframeProcessingAbstraction ✅ (from mainframe plan)
- KreuzbergProcessingAbstraction ✅

#### 6.2 Update All Adapters (If Needed)

**Adapters (Layer 0) remain unchanged:**
- Adapters still work with bytes (raw technology layer)
- Abstractions handle State Surface ↔ bytes conversion
- No changes needed to adapters themselves

**Exception: Mainframe Adapters**
- Custom and Cobrix adapters updated in `MAINFRAME_PARSING_IMPLEMENTATION_PLAN.md`
- Both use State Surface for file references
- Cobrix adapter handles temp files internally (Cobrix requires file paths)

---

### Phase 7: Integration and Migration (Week 3-4)

#### 7.1 Update Content Orchestrator

**File:** `symphainy_platform/realms/content/orchestrators/content_orchestrator/content_orchestrator.py`

**Changes:**
- Route parsing requests to appropriate service:
  - `structured` → StructuredParsingService
  - `unstructured` → UnstructuredParsingService
  - `hybrid` → HybridParsingService
  - `workflow` → WorkflowSOPParsingService
  - `sop` → WorkflowSOPParsingService

**Implementation:**
```python
async def parse_file(
    self,
    file_id: str,
    parse_options: Optional[Dict[str, Any]] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Route to appropriate parsing service using State Surface.
    
    Flow:
    1. Store uploaded file in State Surface (if not already stored)
    2. Get file reference
    3. Route to appropriate parsing service
    4. Service retrieves file from State Surface
    5. Service parses and returns result
    """
    # Get session/tenant from user_context
    session_id = user_context.get("session_id") if user_context else None
    tenant_id = user_context.get("tenant_id") if user_context else "default"
    
    # Get file reference (if file already in State Surface, use it)
    # Otherwise, retrieve from file storage and store in State Surface
    file_reference = await self._get_or_store_file_reference(
        file_id=file_id,
        session_id=session_id,
        tenant_id=tenant_id
    )
    
    # Get parsing type
    parsing_type = self._determine_parsing_type(file_id, parse_options)
    
    # Route to service (services use State Surface internally)
    if parsing_type == "structured":
        return await self.structured_parsing_service.parse_structured_file(
            file_reference=file_reference,
            filename=file_id,
            options=parse_options
        )
    elif parsing_type == "unstructured":
        return await self.unstructured_parsing_service.parse_unstructured_file(
            file_reference=file_reference,
            filename=file_id,
            options=parse_options
        )
    elif parsing_type == "hybrid":
        return await self.hybrid_parsing_service.parse_hybrid_file(
            file_reference=file_reference,
            filename=file_id,
            options=parse_options
        )
    elif parsing_type in ["workflow", "sop"]:
        return await self.workflow_sop_parsing_service.parse_workflow_or_sop_file(
            file_reference=file_reference,
            filename=file_id,
            options=parse_options,
            parsing_type=parsing_type
        )
```

#### 7.2 Migrate Existing Capabilities with Architecture Updates

**From Old Repo - All Updated for New Architecture:**

1. **PDF Processing:**
   - `PdfProcessingAbstraction` → **Update to use State Surface**
   - `pdfplumber_adapter`, `pypdf2_adapter` → Keep as-is (work with bytes)

2. **Word Processing:**
   - `WordProcessingAbstraction` → **Update to use State Surface**
   - `python_docx_adapter` → Keep as-is (work with bytes)

3. **Excel Processing:**
   - `ExcelProcessingAbstraction` → **Update to use State Surface**
   - `excel_processing_adapter` → Keep as-is (work with bytes)

4. **CSV/JSON/Text Processing:**
   - `CsvProcessingAbstraction` → **Update to use State Surface**
   - `JsonProcessingAbstraction` → **Update to use State Surface**
   - `TextProcessingAbstraction` → **Update to use State Surface**
   - Adapters → Keep as-is (work with bytes)

5. **Image Processing:**
   - `ImageProcessingAbstraction` → **Update to use State Surface**
   - `pytesseract_ocr_adapter`, `opencv_image_processor` → Keep as-is (work with bytes)

6. **HTML Processing:**
   - `HtmlProcessingAbstraction` → **Update to use State Surface**
   - `beautifulsoup_html_adapter` → Keep as-is (work with bytes)

7. **Mainframe Processing:**
   - **Use implementation from `MAINFRAME_PARSING_IMPLEMENTATION_PLAN.md`**
   - **Custom strategy** - Production-ready, bytes-based, State Surface integrated
   - **Cobrix strategy** - Gold standard, simplified (~200 lines), State Surface integrated
   - **Unified adapter** - Auto-selection, State Surface integrated
   - **88-level metadata extraction** - BEFORE cleaning, for insights pillar
   - **All aligned to gold standard vision**

8. **Workflow/SOP Processing:**
   - Migrate workflow parsing logic → **Update to use State Surface**
   - Migrate SOP structure extraction logic → **Update to use State Surface**

**Migration Pattern for All Abstractions:**
```python
# OLD (old repo):
async def parse_file(self, file_data: bytes, filename: str, ...) -> Dict[str, Any]:
    # Work with bytes directly
    result = await self.adapter.parse(file_data)
    return result

# NEW (symphainy_source_code):
async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
    # Retrieve from State Surface
    file_data = await self.state_surface.get_file(request.file_reference)
    # Work with bytes (adapter unchanged)
    result = await self.adapter.parse(file_data)
    # Return FileParsingResult
    return FileParsingResult(success=True, ...)
```

---

## 📊 Service Comparison

| Aspect | Old Approach | New Approach |
|--------|-------------|--------------|
| **Architecture** | Single service (monolithic) | 4 separate services (modular) |
| **Hybrid Parsing** | Manual coordination (2 calls) | Kreuzeberg (1 call, intelligent) |
| **Maintainability** | All parsing in one place | Separated by concern |
| **Scalability** | Single service bottleneck | Independent scaling |
| **Testing** | Complex (all types together) | Simpler (isolated services) |
| **State Management** | Files passed as bytes | State Surface references |

---

## 🎯 Kreuzeberg Integration Details

### When to Use Kreuzeberg

**Primary Use Cases:**
- PDFs with embedded tables
- Word documents with tables and text
- Excel files with text annotations
- Scanned documents (OCR + table extraction)
- Complex documents requiring both structured and unstructured extraction

**Supported Formats:**
- PDF, DOCX, DOC, XLSX, XLS, PPTX, PPT
- Images (JPG, PNG, TIFF) with OCR
- HTML, XML
- And 40+ more formats

### When to Use Fallback

**Fallback Cases:**
- Formats not supported by Kreuzeberg
- Custom binary formats (mainframe files)
- When Kreuzeberg service is unavailable
- When explicit separation is needed (structured vs unstructured)

### Implementation Strategy

1. **Phase 1:** Integrate Kreuzeberg adapter and abstraction
2. **Phase 2:** Use Kreuzeberg as primary hybrid parser
3. **Phase 3:** Keep fallback for edge cases
4. **Phase 4:** Monitor performance and accuracy
5. **Phase 5:** Expand Kreuzeberg usage if successful

---

## 📝 Implementation Checklist

### Phase 1: Foundation (Week 1)
- [ ] **Extend State Surface for file storage**
  - [ ] Add `store_file()` method
  - [ ] Add `get_file()` method
  - [ ] Add `get_file_metadata()` method
  - [ ] Add `delete_file()` method
  - [ ] Test file storage and retrieval
- [ ] Create parsing service protocols (updated for State Surface)
- [ ] Create Kreuzberg adapter
- [ ] Create Kreuzberg abstraction (uses State Surface)
- [ ] Add Kreuzberg to Public Works Foundation
- [ ] Test Kreuzberg integration

### Phase 2: Structured Parsing Service (Week 1-2)
- [ ] Create StructuredParsingService
- [ ] Create excel_parser module
- [ ] Create csv_parser module
- [ ] Create json_parser module
- [ ] Create binary_parser module (mainframe)
- [ ] Integrate with State Surface
- [ ] Test all structured formats

### Phase 3: Unstructured Parsing Service (Week 2)
- [ ] Create UnstructuredParsingService
- [ ] Create pdf_parser module
- [ ] Create word_parser module
- [ ] Create text_parser module
- [ ] Create image_parser module (OCR)
- [ ] Create html_parser module
- [ ] Integrate with State Surface
- [ ] Test all unstructured formats

### Phase 4: Hybrid Parsing Service (Week 2-3)
- [ ] Create HybridParsingService
- [ ] Create kreuzberg_parser module
- [ ] Create fallback_parser module
- [ ] Integrate Kreuzberg as primary parser
- [ ] Implement fallback logic
- [ ] Test hybrid file formats
- [ ] Compare Kreuzeberg vs fallback results

### Phase 5: Workflow/SOP Parsing Service (Week 3)
- [ ] Create WorkflowSOPParsingService
- [ ] Create workflow_parser module
- [ ] Create sop_parser module
- [ ] Integrate with State Surface
- [ ] Test workflow formats (BPMN, Draw.io, JSON)
- [ ] Test SOP formats (DOCX, PDF, TXT, MD)

### Phase 6: Update All Abstractions (Week 3)
- [ ] Update PdfProcessingAbstraction (State Surface)
- [ ] Update WordProcessingAbstraction (State Surface)
- [ ] Update ExcelProcessingAbstraction (State Surface)
- [ ] Update CsvProcessingAbstraction (State Surface)
- [ ] Update JsonProcessingAbstraction (State Surface)
- [ ] Update TextProcessingAbstraction (State Surface)
- [ ] Update HtmlProcessingAbstraction (State Surface)
- [ ] Update ImageProcessingAbstraction (State Surface)
- [ ] **MainframeProcessingAbstraction** - Already updated in mainframe plan
- [ ] Test all abstractions with State Surface

### Phase 7: Integration (Week 3-4)
- [ ] Update Content Orchestrator routing (State Surface)
- [ ] Migrate all existing capabilities (with architecture updates)
- [ ] **Integrate mainframe parsing (gold standard)**
- [ ] Update frontend integration
- [ ] End-to-end testing (all parsing types)
- [ ] Performance testing
- [ ] Documentation

---

## 🎯 Success Criteria

### Functional
- ✅ All 4 parsing services working independently
- ✅ Kreuzeberg integrated and working for hybrid files
- ✅ All existing parsing capabilities migrated
- ✅ **State Surface used for ALL file references (not passing bytes)**
- ✅ **All abstractions updated to use State Surface**
- ✅ **Mainframe parsing aligned to gold standard (Cobrix simplified, Custom production-ready)**
- ✅ Validation rules extracted (88-level fields) for insights pillar
- ✅ **All parsing pattern abstractions properly implemented in new architecture**

### Architecture Compliance
- ✅ **State Surface integration** - All services use file references
- ✅ **Protocol compliance** - All abstractions implement FileParsingProtocol
- ✅ **Abstraction pattern** - All use State Surface, not direct bytes
- ✅ **Mainframe gold standard** - Cobrix simplified, Custom production-ready
- ✅ **88-level metadata** - Extracted BEFORE cleaning, passed to insights pillar

### Quality
- ✅ Services are modular and maintainable
- ✅ Clear separation of concerns
- ✅ Comprehensive testing
- ✅ Documentation complete
- ✅ **Architecture consistency** - All services follow same patterns

### Performance
- ✅ Kreuzeberg provides better hybrid parsing
- ✅ Services can scale independently
- ✅ No performance regressions
- ✅ **State Surface efficient** - Files stored once, referenced multiple times

---

## 📝 Next Steps

1. **Review this plan** - Confirm approach and priorities
2. **Evaluate Kreuzeberg** - Test with sample hybrid files
3. **Start Phase 1** - Create protocols and Kreuzeberg integration
4. **Implement services** - One service at a time
5. **Migrate capabilities** - Bring forward from old repo
6. **Test thoroughly** - All formats and edge cases

---

---

## 📋 Architecture Compliance Checklist

### ✅ State Surface Integration
- [ ] State Surface extended with file storage methods
- [ ] All parsing services use State Surface for file references
- [ ] All abstractions retrieve files from State Surface
- [ ] No bytes passed through service layers
- [ ] File references passed through layers

### ✅ Mainframe Parsing Gold Standard
- [ ] Custom parser implemented (production-ready)
- [ ] Cobrix parser implemented (gold standard, simplified)
- [ ] Unified adapter with auto-selection
- [ ] 88-level metadata extracted BEFORE cleaning
- [ ] State Surface integration complete
- [ ] Validation rules passed to insights pillar

### ✅ All Abstractions Updated
- [ ] PdfProcessingAbstraction uses State Surface
- [ ] WordProcessingAbstraction uses State Surface
- [ ] ExcelProcessingAbstraction uses State Surface
- [ ] CsvProcessingAbstraction uses State Surface
- [ ] JsonProcessingAbstraction uses State Surface
- [ ] TextProcessingAbstraction uses State Surface
- [ ] HtmlProcessingAbstraction uses State Surface
- [ ] ImageProcessingAbstraction uses State Surface
- [ ] MainframeProcessingAbstraction uses State Surface (from mainframe plan)
- [ ] All return FileParsingResult (not raw dicts)

### ✅ Protocol Compliance
- [ ] All abstractions implement FileParsingProtocol
- [ ] All accept FileParsingRequest (not bytes)
- [ ] All return FileParsingResult (not raw dicts)
- [ ] Consistent interface across all parsing types

---

**Status:** Ready for implementation  
**Estimated Effort:** 4 weeks  
**Priority:** High (needed for production parsing architecture)

**Key Integration Points:**
- ✅ Mainframe parsing: See `MAINFRAME_PARSING_IMPLEMENTATION_PLAN.md`
- ✅ Cobrix gold standard: See `COBRIX_GOLD_STANDARD_FIX.md`
- ✅ State Surface: Extended for file storage
- ✅ All abstractions: Updated for new architecture
