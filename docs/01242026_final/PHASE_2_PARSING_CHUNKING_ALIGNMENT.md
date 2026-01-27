# Phase 2: Parsing & Chunking Service Alignment Review

**Date:** January 24, 2026  
**Status:** ✅ **REVIEWED - ALIGNMENT NEEDED**

---

## Key Insight

**Embeddings are only created from parsed files** - this simplifies the patterns/formats we need to address.

---

## Current State Analysis

### FileParserService Output Structure

**From `parse_file()`:**
```python
{
    "parsed_file_id": str,
    "parsed_file_reference": str,
    "file_id": str,
    "parsing_type": str,  # "structured", "unstructured", "hybrid", "workflow", "sop"
    "parsed_data": Any,  # Can be structured_data (dict/list) or text_content (str)
    "record_count": Optional[int],
    "metadata": {
        "text_content_length": int,
        "has_structured_data": bool,
        "has_validation_rules": bool
    }
}
```

**From `get_parsed_file()`:**
```python
{
    "parsed_file_id": str,
    "parsed_content": Any,  # Actual parsed content (dict, list, str, etc.)
    "metadata": Dict[str, Any]
}
```

**FileParsingResult (from parsing abstractions):**
```python
{
    "success": bool,
    "text_content": str,
    "structured_data": Optional[Dict[str, Any]],  # Tables, records, etc.
    "metadata": Optional[Dict[str, Any]],  # May contain structure info
    "validation_rules": Optional[Dict[str, Any]],
    "error": Optional[str],
    "timestamp": str
}
```

### DeterministicChunkingService Expected Input

**Current expectation:**
```python
parsed_content: Dict[str, Any] = {
    "parser_type": str,  # ❌ MISMATCH: FileParserService uses "parsing_type"
    "structure": Dict[str, Any],  # ❌ UNCLEAR: Where does this come from?
    "text": str,  # ❌ MISMATCH: FileParsingResult uses "text_content"
    "data": List[Any]  # ❌ MISMATCH: FileParsingResult uses "structured_data"
}
```

---

## Issues Identified

### 1. Field Name Mismatches
- `parser_type` vs `parsing_type`
- `text` vs `text_content`
- `data` vs `structured_data`

### 2. Structure Metadata Location
- DeterministicChunkingService expects `structure` dict
- FileParsingResult has `metadata` dict (may contain structure)
- Need to clarify: Does `metadata` contain structure info (pages, sections, paragraphs)?

### 3. Parsed Content Format
- FileParserService stores parsed result in GCS as JSON
- When retrieved, `parsed_content` is the actual parsed data (not the FileParsingResult structure)
- Need to handle both:
  - Direct FileParsingResult (from parsing abstraction)
  - Retrieved parsed file (from GCS via get_parsed_file)

---

## Recommended Alignment

### Option 1: Normalize in DeterministicChunkingService (RECOMMENDED)

**Accept both formats and normalize internally:**

```python
async def create_chunks(
    self,
    parsed_content: Dict[str, Any],  # Can be FileParsingResult or retrieved parsed file
    file_id: str,
    tenant_id: str,
    parsed_file_id: Optional[str] = None
) -> List[DeterministicChunk]:
    # Normalize input format
    normalized = self._normalize_parsed_content(parsed_content)
    
    # Use normalized fields
    parsing_type = normalized.get("parsing_type")
    text_content = normalized.get("text_content", "")
    structured_data = normalized.get("structured_data")
    structure_metadata = normalized.get("structure", {})
    
    # Extract chunks...
```

**Normalization logic:**
```python
def _normalize_parsed_content(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize parsed content to standard format.
    
    Handles:
    - FileParsingResult (from parsing abstraction)
    - Retrieved parsed file (from GCS via get_parsed_file)
    """
    normalized = {}
    
    # Handle FileParsingResult format
    if "text_content" in parsed_content:
        normalized["text_content"] = parsed_content["text_content"]
        normalized["structured_data"] = parsed_content.get("structured_data")
        normalized["parsing_type"] = parsed_content.get("parsing_type", "unstructured")
        normalized["structure"] = parsed_content.get("metadata", {}).get("structure", {})
    
    # Handle retrieved parsed file format
    elif "parsed_content" in parsed_content:
        content = parsed_content["parsed_content"]
        metadata = parsed_content.get("metadata", {})
        
        # Determine parsing type from metadata
        normalized["parsing_type"] = metadata.get("parsing_type", "unstructured")
        
        # Extract text_content and structured_data
        if isinstance(content, str):
            normalized["text_content"] = content
            normalized["structured_data"] = None
        elif isinstance(content, (dict, list)):
            normalized["text_content"] = ""
            normalized["structured_data"] = content
        else:
            normalized["text_content"] = str(content)
            normalized["structured_data"] = None
        
        # Extract structure from metadata
        normalized["structure"] = metadata.get("structure", {})
    
    # Handle direct parsed_data format (from parse_file result)
    elif "parsed_data" in parsed_content:
        parsed_data = parsed_content["parsed_data"]
        normalized["parsing_type"] = parsed_content.get("parsing_type", "unstructured")
        
        if isinstance(parsed_data, str):
            normalized["text_content"] = parsed_data
            normalized["structured_data"] = None
        elif isinstance(parsed_data, (dict, list)):
            normalized["text_content"] = ""
            normalized["structured_data"] = parsed_data
        else:
            normalized["text_content"] = str(parsed_data)
            normalized["structured_data"] = None
        
        normalized["structure"] = parsed_content.get("metadata", {}).get("structure", {})
    
    # Fallback: assume it's already normalized
    else:
        normalized = parsed_content.copy()
    
    return normalized
```

### Option 2: Standardize FileParserService Output

**Make FileParserService always return a consistent structure** that includes structure metadata.

**Pros:**
- Single source of truth
- Clearer contract

**Cons:**
- Requires changes to FileParserService
- May break existing code

---

## Simplifications (Since We Only Work with Parsed Files)

### 1. Remove Raw File Handling
- ✅ Already done - DeterministicChunkingService only accepts parsed content

### 2. Simplify Structure Extraction
- Focus on what parsers actually return:
  - **Unstructured (PDF/DOCX):** May have `metadata.structure` with pages/sections/paragraphs
  - **Structured (CSV/Excel):** Has `structured_data` (list of rows)
  - **Hybrid:** Has both `text_content` and `structured_data`

### 3. Clarify Structure Metadata
- Need to check: Do parsing abstractions populate `metadata.structure`?
- If not, we may need to infer structure from `text_content` or `structured_data`

---

## Action Items

1. ✅ **Update DeterministicChunkingService** to normalize input formats
2. ✅ **Update field names** to match FileParserService (`parsing_type`, `text_content`, `structured_data`)
3. ⚠️ **Clarify structure metadata** - Check if parsing abstractions provide structure info
4. ✅ **Simplify extraction logic** - Remove assumptions about raw file handling

---

## Updated Implementation Pattern

```python
async def create_chunks(
    self,
    parsed_content: Dict[str, Any],  # Accepts multiple formats
    file_id: str,
    tenant_id: str,
    parsed_file_id: Optional[str] = None
) -> List[DeterministicChunk]:
    # Normalize input to standard format
    normalized = self._normalize_parsed_content(parsed_content)
    
    # Extract fields (using correct names)
    parsing_type = normalized.get("parsing_type", "unstructured")
    text_content = normalized.get("text_content", "")
    structured_data = normalized.get("structured_data")
    structure_metadata = normalized.get("structure", {})
    
    # Extract chunks based on parsing_type
    if parsing_type == "structured" and structured_data:
        # Chunk by rows
        elements = self._extract_from_structured_data(structured_data, parsing_type)
    elif parsing_type in ["unstructured", "pdf", "docx", "txt"]:
        # Chunk by structure metadata or paragraphs
        if structure_metadata:
            elements = self._extract_from_structure_metadata(structure_metadata, text_content)
        elif text_content:
            elements = self._extract_paragraphs_from_text(text_content)
        else:
            elements = []
    elif parsing_type == "hybrid":
        # Handle both structured and unstructured
        elements = []
        if structure_metadata and text_content:
            elements.extend(self._extract_from_structure_metadata(structure_metadata, text_content))
        if structured_data:
            elements.extend(self._extract_from_structured_data(structured_data, parsing_type))
    else:
        elements = []
    
    # Create chunks...
```

---

**Last Updated:** January 24, 2026  
**Status:** ✅ **READY FOR IMPLEMENTATION**
