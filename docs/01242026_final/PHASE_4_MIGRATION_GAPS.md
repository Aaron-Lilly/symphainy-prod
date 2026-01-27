# Phase 4 Migration Gaps - Operations Needing New Intents

**Date:** January 25, 2026  
**Status:** ⚠️ **DOCUMENTED FOR RESOLUTION**  
**Purpose:** Document operations that don't have direct intent mappings yet

---

## Operations Without Clear Intent Mappings

### 1. Data Mapping (File-to-File)
**Component:** `DataMappingSection.tsx`  
**Legacy Endpoint:** `/api/v1/insights-solution/mapping`  
**Current Intent:** `map_relationships` (but this is for relationships within a file, not file-to-file mapping)

**Gap:** File-to-file data mapping doesn't have a direct intent equivalent.

**Options:**
1. Create new intent: `map_data` or `execute_data_mapping`
2. Use artifact retrieval if mapping results are stored as artifacts
3. Extend `map_relationships` to support file-to-file mapping

**Recommendation:** Create new intent `map_data` for file-to-file mapping operations.

---

### 2. PSO (Permit Semantic Object) Retrieval
**Component:** `PSOViewer.tsx`  
**Legacy Endpoint:** `/api/v1/insights-solution/pso/{psoId}`  
**Current Intent:** None

**Gap:** PSO retrieval doesn't have an intent equivalent.

**Options:**
1. Create new intent: `get_pso` or `retrieve_pso`
2. Use artifact retrieval (if PSOs are stored as artifacts)
3. Use `query_data` intent with PSO-specific query

**Recommendation:** Use artifact retrieval if PSOs are stored as artifacts, otherwise create `get_pso` intent.

---

### 3. Permit Processing
**Component:** `PermitProcessingSection.tsx`  
**Legacy Endpoint:** `/api/v1/insights-solution/permit-processing`  
**Current Intent:** None

**Gap:** Permit processing workflow doesn't have an intent equivalent.

**Options:**
1. Create new intent: `process_permit` or `execute_permit_processing`
2. Use combination of existing intents (PSO extraction + mapping)
3. Use workflow intent if permit processing is a workflow

**Recommendation:** Create new intent `process_permit` for permit processing workflow.

---

### 4. Mapping Results Export
**Component:** `DataMappingSection.tsx`  
**Legacy Endpoint:** `/api/v1/insights-solution/mapping/{mappingId}/export`  
**Current Intent:** None

**Gap:** Artifact export doesn't have an intent equivalent.

**Options:**
1. Use artifact export API (if available)
2. Create new intent: `export_artifact`
3. Use file retrieval + client-side export

**Recommendation:** Use artifact export API if available, otherwise create `export_artifact` intent.

---

## Migration Strategy for Gaps

### Option 1: Document and Defer
- Document operations that need new intents
- Leave clear TODOs in code
- Migrate when intents are available

### Option 2: Use Artifact Retrieval
- For read operations, use artifact retrieval API
- For operations that produce artifacts, retrieve via artifact API

### Option 3: Create Placeholder Pattern
- Create intent submission pattern that will work when intent is available
- Document what intent is needed
- Code will work once backend implements intent

---

## Recommended Approach

**For Phase 4 (100% Coverage):**
1. Migrate all operations that have clear intent mappings ✅
2. For operations without mappings:
   - Use artifact retrieval where applicable
   - Document clearly what intent is needed
   - Create placeholder pattern that will work when intent is available
   - Remove legacy endpoint calls completely

**This ensures:**
- ✅ No legacy endpoints remain in components
- ✅ Clear path forward for operations needing new intents
- ✅ Code is ready when backend implements intents
- ✅ 100% coverage achieved (even if some operations need backend work)

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** ⚠️ **DOCUMENTED - READY FOR RESOLUTION**
