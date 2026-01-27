# Parsing Standardization - Summary of Special Cases

**Date:** January 24, 2026  
**Status:** ✅ **ANALYSIS COMPLETE**

---

## Special Cases Identified & Addressed

### 1. ✅ Data Model/Extraction Config Parsing Type

**Status:** Added to standardization plan

**Details:**
- **File Type:** `DATA_MODEL` (`.json`, `.yaml`, `.yml`)
- **Parsing Type:** `"data_model"` (special type)
- **Purpose:** Target data model schemas for source-to-target matching
- **Templates:** AAR, PSO, variable_life_policy_rules
- **Downstream:** `StructuredExtractionService.create_extraction_config_from_target_model()`

**Standardized Format:**
```python
{
    "parsing_type": "data_model",
    "text_content": None,
    "structured_data": {
        "format": "data_model",
        "schema": Dict,  # JSON Schema or YAML schema
        "schema_type": str,  # "json_schema" | "yaml_schema" | "openapi"
        "target_model_name": Optional[str]  # AAR, PSO, variable_life_policies
    },
    "metadata": {
        "parsing_type": "data_model",
        "structure": {
            "schema": {
                "type": str,
                "properties": Dict,
                "required": List[str],
                "definitions": Dict
            }
        },
        "file_type": "json" or "yaml",
        "schema_type": str,
        "target_model_name": Optional[str]
    }
}
```

**Action Required:**
- Add `"data_model"` to `FileParserService._determine_parsing_type()`
- Create `DataModelProcessingAbstraction` (or extend JSON/YAML processing)
- Ensure structure metadata includes schema structure

---

### 2. ✅ Workflow/SOP Files in Journey Realm

**Status:** Integration strategy defined

**Current State:**
- Journey realm uses `FileParserService.get_parsed_file()` to retrieve workflow/SOP files
- `WorkflowConversionService` parses BPMN XML from parsed content
- `CoexistenceAnalysisService` uses keyword heuristics (not semantic)
- `VisualGenerationService` generates workflow/SOP visuals

**Issues:**
- ❌ Not using deterministic chunks
- ❌ Not using semantic embeddings
- ❌ Coexistence analysis uses keyword matching instead of semantic understanding

**Standardized Format:**

**Workflow (BPMN, DrawIO):**
```python
{
    "parsing_type": "workflow",
    "text_content": str,  # BPMN XML as text
    "structured_data": {
        "format": "workflow",
        "bpmn_xml": str,  # Raw XML for WorkflowConversionService
        "tasks": List[Dict],
        "gateways": List[Dict],
        "flows": List[Dict]
    },
    "metadata": {
        "parsing_type": "workflow",
        "structure": {
            "workflow": {
                "tasks": [...],
                "gateways": [...],
                "flows": [...]
            }
        },
        "file_type": "bpmn" or "drawio",
        "task_count": int,
        "gateway_count": int
    }
}
```

**SOP (Markdown):**
```python
{
    "parsing_type": "sop",
    "text_content": str,  # Markdown text
    "structured_data": {
        "format": "sop",
        "sections": List[Dict],
        "steps": List[Dict]
    },
    "metadata": {
        "parsing_type": "sop",
        "structure": {
            "sections": [...],
            "steps": [...]
        },
        "file_type": "markdown",
        "section_count": int,
        "step_count": int
    }
}
```

**Integration Strategy:**

**Option 1: Use Deterministic Chunks (Future Enhancement)**
- Chunk workflows by tasks, gateways, flows
- Extract semantic meaning of tasks (AI-suitable vs human-required)
- Use semantic signals for coexistence analysis

**Option 2: Direct Structure Usage (Recommended for Now)**
- Use `metadata.structure` directly from parsed file
- No chunking needed (structure is already extracted)
- Semantic signals can be extracted from structure if needed

**Recommendation:** Start with Option 2, migrate to Option 1 when semantic pipeline is ready

---

## Other Downstream Use Cases

### Structured Extraction Service
- **Impact:** Needs consistent parsed content format
- **Status:** ✅ Addressed (standardized format ensures compatibility)

### Visual Generation
- **Impact:** Needs structure metadata in consistent format
- **Status:** ✅ Addressed (workflow/SOP structure extraction added)

### Coexistence Analysis
- **Impact:** Could use semantic signals instead of keywords
- **Status:** ⚠️ Future enhancement (Option 1 integration strategy)

---

## Updated Parser Count

**Original:** 8 parsers  
**Updated:** 11 parsers

1. PDF Processing
2. CSV Processing
3. Excel Processing
4. Word Processing
5. Kreuzberg Processing
6. Mainframe Processing
7. Text Processing
8. JSON Processing
9. **Data Model Processing** (NEW)
10. **Workflow Processing** (NEW - BPMN, DrawIO)
11. **SOP Processing** (NEW - Markdown)

---

## Action Items

### Immediate (Phase 2)
1. ✅ Add `"data_model"` parsing type to `FileParserService`
2. ✅ Create `DataModelProcessingAbstraction`
3. ✅ Add structure extraction to Workflow/SOP parsers
4. ✅ Update Journey realm to use standardized structure

### Future (Phase 3+)
1. ⏳ Integrate semantic pipeline for Workflow/SOP (Option 1)
2. ⏳ Use semantic signals for coexistence analysis
3. ⏳ Chunk workflows by tasks for semantic search

---

**Last Updated:** January 24, 2026  
**Status:** ✅ **READY FOR IMPLEMENTATION**
