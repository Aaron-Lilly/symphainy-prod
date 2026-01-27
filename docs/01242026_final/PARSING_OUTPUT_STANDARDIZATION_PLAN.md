# Parsing Output Standardization Plan

**Date:** January 24, 2026  
**Status:** 🔄 **IN PROGRESS**  
**Goal:** Standardize all parsing outputs to align with chunking service and downstream architecture

---

## Executive Summary

**Problem:** Parsing outputs are inconsistent across different file types:
- Structure metadata (pages, sections, paragraphs) is missing or inconsistent
- `structured_data` format varies by parser
- `metadata.structure` is not consistently populated
- Chunking service expects standardized format but receives varied inputs

**Solution:** Standardize `FileParsingResult` structure across all parsers with:
1. Consistent `metadata.structure` format (for chunking)
2. Standardized `structured_data` format (JSON-serializable)
3. Unified output format regardless of parsing type

---

## Special Cases Identified

### 1. Data Model/Extraction Config Parsing Type (MISSING FROM PLAN)

**Purpose:** Target data model schemas (JSON Schema, YAML) used for source-to-target matching in Insights pillar.

**Current State:**
- File type: `DATA_MODEL` (`.json`, `.yaml`, `.yml`)
- Parsing type: `"data_model"` (special type)
- Used for: Creating extraction configs for AAR, PSO, variable_life_policies templates
- Location: `symphainy-frontend/shared/types/file.ts` defines `parsingType: "data_model"`

**Downstream Usage:**
- `StructuredExtractionService.create_extraction_config_from_target_model()` consumes these
- Templates: AAR, PSO, variable_life_policy_rules
- Stored in: ExtractionConfigRegistry (Supabase)

**Required Changes:**
- Add `"data_model"` as parsing type in `FileParserService._determine_parsing_type()`
- Create `DataModelProcessingAbstraction` (or use JSON/YAML processing with special metadata)
- Standardize output format for data model schemas

### 2. Workflow/SOP Files in Journey Realm (NEEDS SEMANTIC INTEGRATION)

**Current Usage:**
- Journey realm uses `FileParserService.get_parsed_file()` to retrieve workflow/SOP files
- `WorkflowConversionService` parses BPMN XML from parsed content
- `CoexistenceAnalysisService` analyzes workflows for coexistence opportunities
- `VisualGenerationService` generates workflow/SOP visuals

**Current Flow:**
```
FileParserService.parse_file() → FileParsingResult
  ↓
Journey Orchestrator.get_parsed_file() → parsed_content
  ↓
WorkflowConversionService.parse_bpmn_file() → workflow structure
  ↓
CoexistenceAnalysisService.analyze_coexistence() → opportunities
  ↓
VisualGenerationService.generate_workflow_visual() → chart
```

**Issue:** Not using deterministic chunks or semantic embeddings
- Workflows/SOPs are parsed but not chunked
- No semantic meaning extraction
- Coexistence analysis uses heuristics, not semantic understanding

**Opportunity:** Use deterministic → semantic pipeline
- Chunk workflows by tasks, gateways, flows
- Extract semantic meaning of tasks (AI-suitable vs human-required)
- Use semantic signals for coexistence analysis instead of keyword matching

### 3. Other Downstream Use Cases

**Structured Extraction Service:**
- Consumes parsed files for extraction
- Uses extraction configs (from data models)
- Pattern discovery from parsed content
- **Impact:** Needs consistent parsed content format

**Visual Generation:**
- Generates charts from workflow/SOP structure
- **Impact:** Needs structure metadata in consistent format

**Coexistence Analysis:**
- Analyzes workflow tasks for AI/human suitability
- **Impact:** Could use semantic signals instead of keywords

---

## Current State Analysis

### FileParsingResult Protocol (Current)

```python
@dataclass
class FileParsingResult:
    success: bool
    text_content: str = ""
    structured_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str = ""
```

### Current Parser Outputs

#### 1. PDF Processing
```python
{
    "text_content": str,  # ✅ Present
    "structured_data": {
        "tables": List[Dict],  # ✅ Present
        "metadata": Dict  # ⚠️ Duplicate of top-level metadata
    },
    "metadata": Dict  # ❌ Missing "structure" key
}
```

#### 2. CSV Processing
```python
{
    "text_content": "",  # ❌ Empty (should be None or omitted)
    "structured_data": {
        "rows": List[Dict],  # ✅ Present
        "columns": List[str],  # ✅ Present
        "metadata": Dict  # ⚠️ Duplicate
    },
    "metadata": Dict  # ❌ Missing "structure" key
}
```

#### 3. Excel Processing
```python
{
    "text_content": "",  # ❌ Empty
    "structured_data": {
        "sheets": List[Dict],  # ✅ Present
        "tables": List[Dict],  # ✅ Present
        "metadata": Dict  # ⚠️ Duplicate
    },
    "metadata": Dict  # ❌ Missing "structure" key
}
```

#### 4. Word Processing
```python
{
    "text_content": str,  # ✅ Present
    "structured_data": List[Dict],  # ⚠️ Just tables, not wrapped
    "metadata": Dict  # ❌ Missing "structure" key
}
```

#### 5. Kreuzberg Processing (Hybrid PDFs)
```python
{
    "text_content": str,  # ✅ Present
    "structured_data": {
        "tables": List[Dict],  # ✅ Present
        "metadata": Dict,  # ⚠️ Duplicate
        "structure": Dict  # ✅ Present! (pages, sections, paragraphs)
    },
    "metadata": Dict  # ⚠️ Should have "structure" here too
}
```

#### 6. Mainframe Processing
```python
{
    "text_content": str,  # ✅ Present (parsed records as text?)
    "structured_data": Dict,  # ✅ Present (parsed records)
    "metadata": Dict,  # ❌ Missing "structure"
    "validation_rules": Dict  # ✅ Present (88-level fields, level-01)
}
```

#### 7. Text Processing
```python
{
    "text_content": str,  # ✅ Present
    "structured_data": None,  # ✅ Correct
    "metadata": Dict  # ❌ Missing "structure"
}
```

#### 8. JSON Processing
```python
{
    "text_content": "",  # ❌ Should be None
    "structured_data": Dict,  # ✅ Present
    "metadata": Dict  # ❌ Missing "structure"
}
```

---

## Issues Identified

### 1. Structure Metadata Missing
- **Problem:** Most parsers don't populate `metadata.structure`
- **Impact:** Chunking service can't use parser structure, falls back to heuristics
- **Exception:** Kreuzberg returns `structure` in `structured_data`, not `metadata`

### 2. Inconsistent structured_data Format
- **Problem:** Some parsers wrap in dict, others return list directly
- **Impact:** Chunking service needs complex normalization logic

### 3. Duplicate Metadata
- **Problem:** `structured_data.metadata` duplicates top-level `metadata`
- **Impact:** Confusion, potential inconsistencies

### 4. Empty text_content for Structured Files
- **Problem:** CSV/Excel return empty string instead of None
- **Impact:** Chunking service treats empty string as valid text

### 5. Missing parsing_type
- **Problem:** FileParsingResult doesn't include `parsing_type`
- **Impact:** Chunking service must infer from file extension or metadata

### 6. Data Model Parsing Type Missing
- **Problem:** `"data_model"` parsing type not handled in FileParserService
- **Impact:** Target data model schemas not properly parsed/standardized

### 7. Workflow/SOP Not Using Semantic Pipeline
- **Problem:** Journey realm uses parsed files but not deterministic chunks or semantic embeddings
- **Impact:** Coexistence analysis uses heuristics instead of semantic understanding

---

## Proposed Standardized Format

### Standardized FileParsingResult

```python
@dataclass
class FileParsingResult:
    success: bool
    text_content: Optional[str] = None  # None if no text (not empty string)
    structured_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None  # MUST include "structure" and "parsing_type"
    validation_rules: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str = ""
    
    # NEW: Explicit parsing type
    parsing_type: Optional[str] = None  # "structured", "unstructured", "hybrid", "mainframe", "workflow", "sop"
```

### Standardized metadata.structure Format

```python
metadata = {
    "parsing_type": str,  # REQUIRED
    "structure": {  # REQUIRED for chunking
        "pages": [  # For PDFs, DOCX, etc.
            {
                "page_number": int,
                "text": str,
                "byte_offset": Optional[int],
                "sections": [  # Optional
                    {
                        "section_index": int,
                        "text": str,
                        "byte_offset": Optional[int],
                        "paragraphs": [  # Optional
                            {
                                "paragraph_index": int,
                                "text": str,
                                "byte_offset": Optional[int]
                            }
                        ]
                    }
                ]
            }
        ],
        "sections": [  # For documents without pages
            {
                "section_index": int,
                "text": str,
                "paragraphs": [...]
            }
        ],
        "paragraphs": [  # For simple text files
            {
                "paragraph_index": int,
                "text": str
            }
        ]
    },
    # Other metadata...
    "file_type": str,
    "page_count": Optional[int],
    "table_count": Optional[int],
    # etc.
}
```

### Standardized structured_data Format

**For Structured Files (CSV, Excel, JSON):**
```python
structured_data = {
    "format": "structured",  # REQUIRED
    "rows": List[Dict[str, Any]],  # For CSV, Excel rows
    "columns": List[str],  # Column names
    "sheets": List[Dict],  # For Excel (optional)
    "tables": List[Dict],  # For Excel tables (optional)
    # NO nested "metadata" - use top-level metadata
}
```

**For Hybrid Files (PDF with tables, Excel with text):**
```python
structured_data = {
    "format": "hybrid",  # REQUIRED
    "tables": List[Dict],
    "text_sections": List[Dict],  # Optional
    # NO nested "metadata"
}
```

**For Unstructured Files (PDF, DOCX, TXT):**
```python
structured_data = {
    "format": "unstructured",  # REQUIRED
    "tables": List[Dict],  # Extracted tables (if any)
    # NO nested "metadata"
}
```

**For Mainframe Files:**
```python
structured_data = {
    "format": "mainframe",  # REQUIRED
    "records": List[Dict[str, Any]],  # Parsed records
    "schema": Dict,  # Copybook schema
    # NO nested "metadata"
}
```

**For Data Model Files (JSON Schema, YAML):**
```python
structured_data = {
    "format": "data_model",  # REQUIRED
    "schema": Dict,  # JSON Schema or YAML schema structure
    "schema_type": str,  # "json_schema" | "yaml_schema" | "openapi" | etc.
    "target_model_name": Optional[str],  # If known (AAR, PSO, variable_life_policies)
    # NO nested "metadata"
}
```

**For Workflow Files (BPMN, DrawIO):**
```python
structured_data = {
    "format": "workflow",  # REQUIRED
    "bpmn_xml": Optional[str],  # Raw BPMN XML if available
    "tasks": List[Dict],  # Extracted tasks
    "gateways": List[Dict],  # Decision points
    "flows": List[Dict],  # Sequence flows
    # NO nested "metadata"
}
```

**For SOP Files (Markdown):**
```python
structured_data = {
    "format": "sop",  # REQUIRED
    "sections": List[Dict],  # Markdown sections
    "steps": List[Dict],  # SOP steps if structured
    # NO nested "metadata"
}
```

---

## Implementation Plan

### Phase 1: Update FileParsingResult Protocol

**File:** `symphainy_platform/foundations/public_works/protocols/file_parsing_protocol.py`

**Changes:**
1. Add `parsing_type` field to `FileParsingResult`
2. Change `text_content` default from `""` to `None`
3. Document required `metadata.structure` format
4. Document standardized `structured_data` format

### Phase 2: Update All Parsing Abstractions

**Priority Order:**
1. **PDF Processing** - Add structure extraction (pages, sections, paragraphs)
2. **Word Processing** - Add structure extraction
3. **Text Processing** - Add paragraph extraction
4. **CSV Processing** - Standardize structured_data format, remove empty text_content
5. **Excel Processing** - Standardize structured_data format, remove empty text_content
6. **JSON Processing** - Standardize structured_data format, remove empty text_content
7. **Kreuzberg Processing** - Move structure from structured_data to metadata.structure
8. **Mainframe Processing** - Add structure extraction, standardize format
9. **Data Model Processing** - NEW: Create abstraction for JSON Schema/YAML schemas
10. **Workflow Processing** - Add structure extraction (tasks, gateways, flows)
11. **SOP Processing** - Add structure extraction (sections, steps)

### Phase 3: Update FileParserService

**File:** `symphainy_platform/realms/content/enabling_services/file_parser_service.py`

**Changes:**
1. Ensure `parsing_type` is passed through to FileParsingResult
2. Normalize outputs before storing in GCS
3. Ensure stored JSON includes all required fields

### Phase 4: Update DeterministicChunkingService

**File:** `symphainy_platform/realms/content/enabling_services/deterministic_chunking_service.py`

**Changes:**
1. Simplify normalization (now that outputs are standardized)
2. Remove workarounds for inconsistent formats
3. Rely on `metadata.structure` for all structure-based chunking

---

## Detailed Parser Updates

### 1. PDF Processing Abstraction

**Current Issues:**
- No structure metadata (pages, sections, paragraphs)
- Duplicate metadata in structured_data

**Required Changes:**
```python
# Extract structure from PDF adapter
pages = result.get("pages", [])  # If adapter provides pages
sections = result.get("sections", [])  # If adapter provides sections
paragraphs = result.get("paragraphs", [])  # If adapter provides paragraphs

# Build metadata.structure
structure = {}
if pages:
    structure["pages"] = [
        {
            "page_number": page.get("page_number", idx),
            "text": page.get("text", ""),
            "byte_offset": page.get("byte_offset"),
            "sections": page.get("sections", [])
        }
        for idx, page in enumerate(pages)
    ]
elif sections:
    structure["sections"] = [...]
elif paragraphs:
    structure["paragraphs"] = [...]

metadata = {
    "parsing_type": "unstructured",  # or "hybrid" if tables present
    "structure": structure,
    "file_type": "pdf",
    "page_count": len(pages) if pages else None,
    "table_count": len(result.get("tables", [])),
    **result.get("metadata", {})
}

# Clean structured_data (remove nested metadata)
structured_data = {
    "format": "hybrid" if result.get("tables") else "unstructured",
    "tables": result.get("tables", [])
}
```

### 2. CSV Processing Abstraction

**Current Issues:**
- Empty text_content (should be None)
- Missing parsing_type
- Missing structure (rows should be in structure)

**Required Changes:**
```python
# Build structure from rows
structure = {
    "rows": [
        {
            "row_index": idx,
            "data": row  # Dict or List
        }
        for idx, row in enumerate(result.get("rows", []))
    ]
}

metadata = {
    "parsing_type": "structured",
    "structure": structure,
    "file_type": "csv",
    "row_count": len(result.get("rows", [])),
    "column_count": len(result.get("columns", [])),
    **result.get("metadata", {})
}

structured_data = {
    "format": "structured",
    "rows": result.get("rows", []),
    "columns": result.get("columns", [])
}

# text_content should be None, not ""
text_content = None
```

### 3. Excel Processing Abstraction

**Similar to CSV, but with sheets:**
```python
structure = {
    "sheets": [
        {
            "sheet_name": sheet.get("name"),
            "sheet_index": idx,
            "rows": [
                {
                    "row_index": row_idx,
                    "data": row
                }
                for row_idx, row in enumerate(sheet.get("rows", []))
            ]
        }
        for idx, sheet in enumerate(result.get("sheets", []))
    ]
}

metadata = {
    "parsing_type": "structured",
    "structure": structure,
    "file_type": "excel",
    "sheet_count": len(result.get("sheets", [])),
    **result.get("metadata", {})
}

structured_data = {
    "format": "structured",
    "sheets": result.get("sheets", []),
    "tables": result.get("tables", [])
}
```

### 4. Word Processing Abstraction

**Similar to PDF:**
```python
# Extract structure from Word adapter
paragraphs = result.get("paragraphs", [])
sections = result.get("sections", [])

structure = {}
if sections:
    structure["sections"] = [...]
elif paragraphs:
    structure["paragraphs"] = [...]

metadata = {
    "parsing_type": "unstructured",  # or "hybrid" if tables
    "structure": structure,
    "file_type": "docx",
    **result.get("metadata", {})
}

structured_data = {
    "format": "hybrid" if result.get("tables") else "unstructured",
    "tables": result.get("tables", [])
}
```

### 5. Kreuzberg Processing Abstraction

**Current Issue:**
- Structure is in `structured_data.structure`, should be in `metadata.structure`

**Required Changes:**
```python
# Move structure from structured_data to metadata
structure = result.get("structured_data", {}).get("structure", {})

metadata = {
    "parsing_type": "hybrid",
    "structure": structure,  # Move here
    "file_type": "pdf",  # or from result
    **result.get("metadata", {})
}

structured_data = {
    "format": "hybrid",
    "tables": result.get("tables", [])
    # Remove "structure" and "metadata" from here
}
```

### 6. Mainframe Processing Abstraction

**Required Changes:**
```python
# Build structure from records
structure = {
    "records": [
        {
            "record_index": idx,
            "record_type": record.get("record_type"),
            "data": record
        }
        for idx, record in enumerate(result.get("records", []))
    ]
}

metadata = {
    "parsing_type": "mainframe",
    "structure": structure,
    "file_type": "binary",
    "record_count": len(result.get("records", [])),
    "copybook_name": result.get("copybook_name"),
    **result.get("metadata", {})
}

structured_data = {
    "format": "mainframe",
    "records": result.get("records", []),
    "schema": result.get("schema", {})
}

validation_rules = result.get("validation_rules", {})  # 88-level fields, level-01
```

### 7. Text Processing Abstraction

**Required Changes:**
```python
# Extract paragraphs from text
paragraphs = self._extract_paragraphs(result.get("text", ""))

structure = {
    "paragraphs": [
        {
            "paragraph_index": idx,
            "text": para
        }
        for idx, para in enumerate(paragraphs)
    ]
}

metadata = {
    "parsing_type": "unstructured",
    "structure": structure,
    "file_type": "txt",
    "paragraph_count": len(paragraphs),
    **result.get("metadata", {})
}

structured_data = None  # No structured data for plain text
```

### 8. JSON Processing Abstraction

**Required Changes:**
```python
# JSON structure depends on content
# For arrays: treat as rows
# For objects: treat as single record or nested structure

json_data = result.get("data")
if isinstance(json_data, list):
    structure = {
        "rows": [
            {
                "row_index": idx,
                "data": row
            }
            for idx, row in enumerate(json_data)
        ]
    }
elif isinstance(json_data, dict):
    structure = {
        "object": {
            "data": json_data
        }
    }
else:
    structure = {}

metadata = {
    "parsing_type": "structured",
    "structure": structure,
    "file_type": "json",
    **result.get("metadata", {})
}

structured_data = {
    "format": "structured",
    "data": json_data
}

text_content = None  # JSON has no text content
```

---

## Testing Strategy

### Unit Tests
1. Test each parser returns standardized format
2. Test `metadata.structure` is populated correctly
3. Test `structured_data` format matches spec
4. Test `parsing_type` is set correctly

### Integration Tests
1. Test FileParserService stores standardized format
2. Test DeterministicChunkingService can consume standardized format
3. Test end-to-end: parse → chunk → embed

### Validation Tests
1. Verify all parsers return JSON-serializable output
2. Verify structure metadata is deterministic (same input → same structure)
3. Verify no duplicate metadata

---

## Migration Strategy

### Backward Compatibility
- Keep old format support in DeterministicChunkingService normalization
- Gradually migrate parsers (one at a time)
- Add feature flag to enable new format

### Rollout Plan
1. **Week 1:** Update protocol and PDF parser (highest priority)
2. **Week 2:** Update CSV, Excel, Word parsers
3. **Week 3:** Update Text, JSON, Kreuzberg parsers
4. **Week 4:** Update Mainframe parser, remove backward compatibility

---

## Success Criteria

✅ All parsers return standardized `FileParsingResult`  
✅ All parsers populate `metadata.structure`  
✅ All parsers use consistent `structured_data` format  
✅ DeterministicChunkingService can rely on structure metadata  
✅ All outputs are JSON-serializable  
✅ No duplicate metadata  
✅ `parsing_type` is always set  
✅ Data model parsing type supported (for AAR, PSO, variable_life_policies)  
✅ Workflow/SOP structure extracted and available for Journey realm  
✅ Journey realm integration designed for semantic pipeline (future-ready)  
✅ Semantic signals format documented for Journey realm usage  
✅ Coexistence analysis can use semantic signals (when Phase 2 ready)  

---

**Last Updated:** January 24, 2026  
**Status:** 🔄 **READY FOR IMPLEMENTATION**
