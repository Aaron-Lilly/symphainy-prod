# Content Realm Structured Artifacts Refactoring - Implementation Plan

**Date:** January 19, 2026  
**Status:** 📋 **READY FOR IMPLEMENTATION**  
**Priority:** 🔴 **HIGH** - Solves root cause, aligns architecture

---

## Executive Summary

**Goal:** Refactor Content Realm to use structured artifacts pattern (like other realms) to:
1. ✅ Solve JSON serialization issue (bytes in execution state)
2. ✅ Align with platform architecture
3. ✅ Properly leverage materialization policy
4. ✅ Maintain lineage through semantic_payload

**Approach:** Update all Content Realm handlers to return structured artifacts with result_type, semantic_payload, and renderings.

---

## Recommended Answers to Questions

### Q1: File Listing - How to structure multiple files?

**Recommendation:** Use structured artifact with result_type: "file_list" and files array in semantic_payload.

**Rationale:**
- Maintains consistency with single-file pattern
- All file metadata (lineage) in semantic_payload (JSON-serializable)
- Can include file count, pagination info in semantic_payload
- Materialization policy can evaluate file_list type

**Structure:**


### Q2: MVP Policy - Add file to materialization policy?

**Recommendation:** ✅ **YES** - Add file: persist to MVP policy.

**Rationale:**
- Consistency with other artifacts (workflow, sop, solution, etc.)
- MVP demonstrates persistence for demo purposes
- semantic_payload always stored regardless of policy
- renderings (file_contents) handled by policy

**Update:**


### Q3: Test Updates - How should tests access structured artifacts?

**Recommendation:** Update tests to directly access structured artifacts (NO backward compatibility).

**Rationale:**
- Breaking change ensures architecture is clean
- Forces proper adoption of structured pattern
- Tests access: artifacts["file"]["semantic_payload"]["file_id"]
- No legacy format support - clean break

**Helper Methods:**


---

## Implementation Plan

### Phase 1: Update MVP Materialization Policy

**File:** config/mvp_materialization_policy.yaml

**Change:**


**Validation:**
- Policy loads correctly
- Runtime recognizes file type

---

### Phase 2: Refactor Content Realm Handlers

#### 2.1: _handle_ingest_file

**Current Pattern:**


**After (Structured):**


**Lineage Maintained:**
- ✅ file_id - Unique identifier
- ✅ file_reference - State Surface reference
- ✅ storage_location - GCS path
- ✅ All metadata in semantic_payload

---

#### 2.2: _handle_retrieve_file

**Current Pattern:**


**After (Structured):**


**Benefits:**
- ✅ semantic_payload (JSON-serializable) → stored in execution state
- ✅ renderings (bytes) → handled by materialization policy
- ✅ No JSON serialization failures

---

#### 2.3: _handle_retrieve_file_metadata

**After (Structured):**


---

#### 2.4: _handle_list_files

**After (Structured):**


---

#### 2.5: _handle_register_file

**After (Structured):**


---

### Phase 3: Update Test Helpers

**File:** tests/integration/capabilities/base_capability_test.py

**Update find_artifact_by_type() to handle structured artifacts:**
- Check for structured format: artifacts["file"]["result_type"] == "file"
- Remove legacy format support (clean break)
- Ensure tests use structured pattern only

---

### Phase 4: Update Tests

**Breaking Change:** Tests must access structured artifacts directly.

**Update test_register_file.py:**
```python
# Before: artifacts.get("file_id")
# After: artifacts["file"]["semantic_payload"]["file_id"]
```

**Update test_retrieve_file.py:**
```python
# Before: artifacts.get("file_id")
# After: artifacts["file"]["semantic_payload"]["file_id"]
```

**Update test_list_files.py (if exists):**
```python
# Before: artifacts.get("files")
# After: artifacts["file_list"]["semantic_payload"]["files"]
```

---

### Phase 5: Remove Sanitization Code

**File:** symphainy_platform/runtime/execution_lifecycle_manager.py

**Remove:**
- _sanitize_artifacts_for_storage() method
- Sanitization calls before storing execution state
- Aggressive sanitization fallbacks

---

## Implementation Checklist

### Phase 1: MVP Policy
- [ ] Add file: persist to mvp_materialization_policy.yaml
- [ ] Verify policy loads correctly

### Phase 2: Content Realm Handlers
- [ ] Refactor _handle_ingest_file
- [ ] Refactor _handle_retrieve_file
- [ ] Refactor _handle_retrieve_file_metadata
- [ ] Refactor _handle_list_files
- [ ] Refactor _handle_register_file

### Phase 3: Test Helpers
- [ ] Update find_artifact_by_type() to handle structured artifacts (remove legacy support)

### Phase 4: Test Updates
- [ ] Update test_register_file.py
- [ ] Update test_retrieve_file.py
- [ ] Update test_list_files.py (if exists)

### Phase 5: Cleanup
- [ ] Remove _sanitize_artifacts_for_storage() method
- [ ] Remove sanitization calls from execution lifecycle manager
- [ ] Remove aggressive sanitization fallbacks

### Phase 6: Validation
- [ ] Run test_register_file.py - should pass
- [ ] Run test_retrieve_file.py - should pass (no more JSON serialization errors)
- [ ] Verify execution state stores successfully
- [ ] Verify materialization policy evaluates correctly
- [ ] Verify lineage maintained in semantic_payload

---

## Expected Outcomes

### ✅ Solves Root Cause
- No more JSON serialization failures
- semantic_payload (JSON-serializable) stored in execution state
- renderings (bytes) handled by materialization policy

### ✅ Architectural Alignment
- Content Realm matches other realms
- Consistent structured artifact pattern
- Materialization policy works correctly

### ✅ Maintains Lineage
- All lineage info in semantic_payload
- Always stored in execution state
- Independent of materialization policy

---

## Timeline Estimate

| Phase | Tasks | Estimate |
|-------|-------|----------|
| Phase 1: MVP Policy | 1 task | 5 min |
| Phase 2: Handlers | 5 handlers | 2-3 hours |
| Phase 3: Test Helpers | 3 methods | 30 min |
| Phase 4: Test Updates | 2-3 tests | 30 min |
| Phase 5: Cleanup | Remove sanitization | 15 min |
| Phase 6: Validation | Run tests | 30 min |
| **Total** | | **4-5 hours** |

---

**Last Updated:** January 19, 2026  
**Status:** ✅ **READY FOR IMPLEMENTATION**  
**Priority:** 🔴 **HIGH** - Solves root cause, architectural alignment
