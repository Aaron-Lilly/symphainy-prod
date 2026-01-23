# Architectural Audit - Remaining Instances

**Date:** January 2026  
**Status:** ⚠️ **REVIEW NEEDED**  
**Purpose:** Document remaining `state_surface.get_file()` instances for review

---

## Critical Fixes Completed ✅

All instances in **agentic/agents** and **insights/enabling_services** have been fixed:
- ✅ `StructuredExtractionAgent` (2 instances)
- ✅ `DataQualityService` (1 instance)
- ✅ `UnstructuredAnalysisService` (1 instance)
- ✅ `StructuredAnalysisService` (1 instance)

---

## Remaining Instances - Review Needed

### 1. Content Orchestrator (3 instances)

**File:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

**Instances:**
- Line 1491: `file_contents = await context.state_surface.get_file(file_reference)`
- Line 2225: `file_contents = await context.state_surface.get_file(file_reference)`
- Line 2766: `parsed_file_data = await context.state_surface.get_file(parsed_file_reference)`

**Status:** ⚠️ **NEEDS REVIEW**
- These are in Content Realm itself
- May be legitimate for internal Content Realm operations
- OR may need to use FileManagementAbstraction directly

**Action:** Review context - if these are Content Realm internal operations, they might be acceptable, but should still use FileManagementAbstraction for consistency.

---

### 2. Processing Abstractions (Multiple instances)

**Files:**
- `foundations/public_works/abstractions/*_processing_abstraction.py`
- `foundations/public_works/adapters/mainframe_parsing/*.py`

**Instances:** ~15 instances of `state_surface.get_file()`

**Status:** ⚠️ **NEEDS ARCHITECTURAL CLARIFICATION**
- These are in Public Works Foundation layer
- Processing abstractions may be a different architectural layer
- May be legitimate for abstraction layer to access state_surface

**Question:** Is Public Works Foundation layer allowed to access state_surface, or should it also go through Content Realm?

**Action:** Need architectural decision on whether Public Works abstractions can access state_surface directly.

---

### 3. Metadata Queries (Multiple instances)

**Instances:** ~15 instances of `state_surface.get_file_metadata()`

**Status:** ✅ **LIKELY ACCEPTABLE**
- User stated: "The state surface *can* answer things like: 'Is artifact X available?', 'Has artifact X expired?', 'Was artifact X accessed before?', 'What version was used?' That's metadata, lineage, and audit — not content."
- `get_file_metadata()` is metadata query, not content retrieval
- Should be acceptable

**Action:** Verify these are metadata-only queries, not content retrieval.

---

## Recommendation

1. ✅ **Fixed:** All agent and insights service instances (5 instances)
2. ⚠️ **Review:** Content Orchestrator instances (3 instances) - may need fixing
3. ⚠️ **Clarify:** Public Works abstractions (15 instances) - need architectural decision
4. ✅ **Acceptable:** Metadata queries (15 instances) - likely fine

---

## Next Steps

1. Review Content Orchestrator instances - fix if needed
2. Get architectural decision on Public Works abstractions
3. Verify metadata queries are metadata-only
