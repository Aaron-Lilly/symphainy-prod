# 🚨 CRITICAL ISSUE: Policy Rules Extraction - Missing Data Retrieval

**Date:** January 2026  
**Status:** 🔴 **BLOCKER**  
**Severity:** **CRITICAL** - Extraction will NOT work without this fix

---

## Problem Summary

The `StructuredExtractionAgent._prepare_data_context()` method is a **PLACEHOLDER** that does NOT retrieve actual parsed file content. The LLM is being called with only a `parsed_file_id` and a placeholder string `"Data available"`, meaning **NO ACTUAL POLICY DATA** is being extracted.

---

## Current Implementation (BROKEN)

**File:** `symphainy_platform/civic_systems/agentic/agents/structured_extraction_agent.py`

**Lines 415-423:**
```python
def _prepare_data_context(self, data_source: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare data context for extraction."""
    # Extract relevant data from data_source
    # For MVP, return data_source as-is (will be enhanced with actual data retrieval)
    return {
        "parsed_file_id": data_source.get("parsed_file_id"),
        "data_preview": data_source.get("data_preview", "Data available"),
        "metadata": data_source.get("metadata", {})
    }
```

**Problem:**
- ❌ Does NOT retrieve actual parsed file content
- ❌ Only passes `parsed_file_id` (a string ID)
- ❌ Passes placeholder string `"Data available"` instead of real data
- ❌ LLM receives NO actual policy data to extract from

**Result:**
- ❌ Extraction will FAIL or return empty/hallucinated results
- ❌ Policy rules extraction will NOT work
- ❌ LLM has no data to analyze

---

## What Should Happen

The method should:
1. ✅ Extract `parsed_file_id` from `data_source`
2. ✅ Retrieve actual parsed file content using `context.state_surface.retrieve_file(parsed_file_id)`
3. ✅ Parse the retrieved content (JSON decode if needed)
4. ✅ Return actual data content (not just file ID)

**Reference Implementation:**
Other services DO retrieve parsed data correctly:
- `data_quality_service.py` line 194: `parsed_data = await context.state_surface.retrieve_file(parsed_file_id)`
- `unstructured_analysis_service.py` line 153: `parsed_data = await context.state_surface.retrieve_file(parsed_file_id)`

---

## Impact

### Affected Features:
1. ❌ **Policy Rules Extraction** - Will NOT extract actual rules
2. ❌ **AAR Pattern Extraction** - Will NOT extract actual AAR data
3. ❌ **PSO Pattern Extraction** - Will NOT extract actual permit data
4. ❌ **Custom Pattern Extraction** - Will NOT extract actual data
5. ❌ **Pattern Discovery** - Will NOT discover patterns from actual data

### What Works:
- ✅ Extraction configs are loaded correctly
- ✅ LLM calls are made (but with no data)
- ✅ JSON parsing works (but parses empty/hallucinated responses)
- ✅ Confidence calculation works (but on empty data)

---

## Required Fix

**File:** `symphainy_platform/civic_systems/agentic/agents/structured_extraction_agent.py`

**Method:** `_prepare_data_context()`

**Fix:**
```python
async def _prepare_data_context(
    self, 
    data_source: Dict[str, Any],
    context: ExecutionContext
) -> Dict[str, Any]:
    """Prepare data context for extraction."""
    parsed_file_id = data_source.get("parsed_file_id")
    
    if not parsed_file_id:
        # If no parsed_file_id, return data_source as-is (for other data sources)
        return data_source
    
    # Retrieve actual parsed file content
    try:
        if context and hasattr(context, 'state_surface') and context.state_surface:
            parsed_data = await context.state_surface.retrieve_file(parsed_file_id)
            
            # Parse JSON if needed
            if isinstance(parsed_data, bytes):
                parsed_data = json.loads(parsed_data.decode('utf-8'))
            elif isinstance(parsed_data, str):
                try:
                    parsed_data = json.loads(parsed_data)
                except json.JSONDecodeError:
                    # If not JSON, return as string
                    pass
            
            return {
                "parsed_file_id": parsed_file_id,
                "parsed_content": parsed_data,
                "data_preview": str(parsed_data)[:500] if isinstance(parsed_data, (dict, list)) else str(parsed_data)[:500],
                "metadata": data_source.get("metadata", {})
            }
        else:
            self.logger.warning("State surface not available - cannot retrieve parsed file content")
            return {
                "parsed_file_id": parsed_file_id,
                "data_preview": "Data retrieval unavailable",
                "metadata": data_source.get("metadata", {})
            }
    except Exception as e:
        self.logger.error(f"Failed to retrieve parsed file content: {e}", exc_info=True)
        return {
            "parsed_file_id": parsed_file_id,
            "data_preview": f"Error retrieving data: {str(e)}",
            "metadata": data_source.get("metadata", {})
        }
```

**Also Update:**
- `_extract_via_llm()` must be updated to call `_prepare_data_context()` as `async`
- All callers of `_prepare_data_context()` must await it

---

## Verification

After fix, verify:
1. ✅ `_prepare_data_context()` actually retrieves parsed file content
2. ✅ LLM receives actual policy data (not just file ID)
3. ✅ Extraction returns real policy rules (not empty/hallucinated)
4. ✅ Test with actual policy file

---

## Status

**Current:** 🔴 **BROKEN** - Extraction will NOT work  
**After Fix:** ✅ Should work correctly

---

## Related Issues

### Issue #2: `generate_config_from_target_model()` - Missing Target Model Content

**File:** `symphainy_platform/civic_systems/agentic/agents/structured_extraction_agent.py`

**Lines 567-577:**
```python
prompt = f"""
Analyze the target data model (file_id: {target_model_file_id}) and generate an extraction configuration.
The extraction config should extract data that matches the target model structure.
...
"""
```

**Problem:**
- ❌ LLM is asked to "analyze the target data model" but only receives a `file_id` string
- ❌ LLM never receives actual target model content (schema, structure, fields)
- ❌ LLM cannot analyze a file it doesn't have access to

**Result:**
- ❌ Config generation will FAIL or return generic/hallucinated configs
- ❌ Generated configs will NOT match actual target model structure

**Fix Required:**
- ✅ Retrieve actual target model content using `context.state_surface.retrieve_file(target_model_file_id)`
- ✅ Parse target model content (JSON Schema, SQL DDL, Excel structure, etc.)
- ✅ Pass actual model structure to LLM for analysis

### Issue #3: Pattern Discovery - May Have Similar Issue

**File:** `symphainy_platform/civic_systems/agentic/agents/structured_extraction_agent.py`

**Lines 463-470:**
```python
data_context = self._prepare_data_context(data_source)
...
prompt = f"""
Analyze the following data source and propose an extraction pattern.
...
Data Source:
{json.dumps(data_context, indent=2)}
```

**Status:** ⚠️ **AFFECTED** - Uses `_prepare_data_context()` which is broken (Issue #1)
