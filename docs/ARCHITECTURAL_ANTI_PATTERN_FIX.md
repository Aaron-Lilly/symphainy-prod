# Architectural Anti-Pattern Fix: File Retrieval

**Date:** January 2026  
**Status:** 🔴 **CRITICAL FIX IN PROGRESS**  
**Issue:** `state_surface.retrieve_file()` is an architectural anti-pattern

---

## The Problem

**Anti-Pattern:**
```python
# ❌ WRONG - Agents/Realms directly accessing state_surface for file retrieval
parsed_data = await context.state_surface.retrieve_file(parsed_file_id)
```

**Why This Is Wrong:**
1. **Collapses governance boundaries** - Bypasses Data Steward (Smart City)
2. **Dissolves data mash boundaries** - Runtime shouldn't hold client data
3. **Gives agents ambient access** - No policy evaluation
4. **Breaks architectural layers:**
   - Runtime should **observe** (not retrieve)
   - Smart City should **govern** (not retrieve)
   - Content Realm should **retrieve** (with governance)

---

## The Correct Pattern

**Correct Flow:**
1. **Agent expresses intent** (needs parsed file X)
2. **Runtime routes intent** (records request)
3. **Data Steward evaluates policy** (Smart City - is access allowed?)
4. **Content Realm retrieves** (if allowed, with policy constraints)
5. **Runtime records event** (logs access)

**Correct Implementation:**
```python
# ✅ CORRECT - Use Content Realm service
from symphainy_platform.realms.content.enabling_services.file_parser_service import FileParserService

file_parser_service = FileParserService(public_works=public_works)
parsed_file = await file_parser_service.get_parsed_file(
    parsed_file_id=parsed_file_id,
    tenant_id=context.tenant_id,
    context=context
)
```

---

## Files to Fix

### Critical (Code):
1. ✅ `symphainy_platform/civic_systems/agentic/agents/structured_extraction_agent.py`
   - Line 441: `_prepare_data_context()` - uses `state_surface.retrieve_file()`
   - Line 644: `generate_config_from_target_model()` - uses `state_surface.retrieve_file()`

2. ✅ `symphainy_platform/realms/insights/enabling_services/data_quality_service.py`
   - Line 194: `_get_parsed_data()` - uses `state_surface.retrieve_file()`

3. ⚠️ `symphainy_platform/realms/insights/enabling_services/unstructured_analysis_service.py`
   - Line 153: May use `state_surface.retrieve_file()` (needs verification)

4. ⚠️ `symphainy_platform/realms/insights/enabling_services/structured_analysis_service.py`
   - Line 138: May use `state_surface.retrieve_file()` (needs verification)

### Documentation (Update):
- `docs/FIXES_IMPLEMENTED.md` - Update to reflect correct pattern
- `docs/CRITICAL_ISSUE_EXTRACTION_DATA_RETRIEVAL.md` - Update examples
- `docs/IMPLEMENTATION_STATUS_CORRECTED.md` - Update examples

---

## Implementation Plan

1. ✅ **Implement `FileParserService.get_parsed_file()` properly**
   - Use FileManagementAbstraction (not state_surface)
   - Add governance checks (if needed)
   - Return parsed content

2. ✅ **Fix `StructuredExtractionAgent`**
   - Replace `state_surface.retrieve_file()` with `FileParserService.get_parsed_file()`
   - Update both methods

3. ✅ **Fix `DataQualityService`**
   - Replace `state_surface.retrieve_file()` with `FileParserService.get_parsed_file()`

4. ✅ **Audit other services**
   - Check `unstructured_analysis_service.py`
   - Check `structured_analysis_service.py`
   - Fix any found instances

5. ✅ **Deprecate `state_surface.retrieve_file()`**
   - Add deprecation warning
   - Document correct pattern
   - Mark for removal

---

## One-Sentence Rule

> **Runtime records reality. Smart City governs access. Realms touch data. Agents never retrieve files directly.**
