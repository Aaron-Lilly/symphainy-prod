# Artifact Plane Realm Migration Plan

**Date:** January 20, 2026  
**Status:** 📋 **Planning Phase**  
**Goal:** Migrate all realms to use Artifact Plane for derived artifacts while preserving FMS for source data

---

## Executive Summary

**Key Principle:** Files (source data) ≠ Artifacts (derived representations)

- **Files (FMS):** Source data ingested from external sources → Preserve FMS for lineage/traceability
- **Artifacts (Artifact Plane):** Derived representations created by platform → Migrate to Artifact Plane

**Migration Strategy:** 
1. ✅ Outcomes Realm - **COMPLETE** (roadmaps, POCs)
2. 🟡 Journey Realm - **IN PROGRESS** (blueprints, SOPs, workflows)
3. ⏳ Content Realm - **REVIEW** (analysis results, visualizations - NOT files)
4. ⏳ Insights Realm - **PENDING** (interpretations, quality reports)

---

## Architecture Principles

### 1. File vs Artifact Distinction

| Type | Storage | Purpose | Lineage | Example |
|------|---------|--------|---------|---------|
| **File (FMS)** | `FileManagementProtocol` | Source data from external | Critical (data provenance) | Uploaded PDF, EDI file, API payload |
| **Artifact (Artifact Plane)** | `ArtifactPlane` | Derived representation | Important (creation lineage) | Roadmap, POC, Blueprint, Analysis result |

### 2. FMS Preservation (Content Realm)

**FMS Construct Must Preserve:**
- File metadata (file_id, file_reference, storage_location)
- Ingestion lineage (how data came into platform)
- Boundary contract tracking (materialization scope)
- File hash/checksum (data integrity)
- Source tracking (external vs internal)

**FMS Does NOT Store:**
- Derived analysis results (these are artifacts)
- Visualizations (these are artifacts)
- Parsed content summaries (these are artifacts)

### 3. Artifact Plane Usage

**Artifact Plane Stores:**
- Derived representations (roadmaps, POCs, blueprints, SOPs, workflows)
- Analysis results (data quality reports, semantic interpretations)
- Visualizations (charts, diagrams, graphs)
- Generated documents (SOPs, proposals, reports)

**Artifact Plane Does NOT Store:**
- Source files (these are in FMS)
- Raw data (this is in Data Steward)
- Execution state (this is in Runtime)

---

## Realm-by-Realm Migration Plan

### ✅ Outcomes Realm - COMPLETE

**Status:** ✅ **5/6 tests passing (83%)**

**What Was Migrated:**
- ✅ Roadmaps → Artifact Plane
- ✅ POCs → Artifact Plane
- ✅ Solution creation retrieves from Artifact Plane

**What Remains:**
- ⏳ Blueprint → Solution (depends on Journey Realm)

**Files Modified:**
- `outcomes_orchestrator.py` - Uses Artifact Plane for roadmap/POC creation and retrieval

---

### 🟡 Journey Realm - IN PROGRESS

**Status:** 🟡 **Needs Artifact Plane integration**

**Artifacts to Migrate:**
1. **Blueprints** (`create_blueprint`)
   - Currently: Stored via `ArtifactStorageProtocol` directly
   - Target: Store via Artifact Plane
   - Critical: Blueprint → Solution flow depends on this

2. **SOPs** (`generate_sop`, `generate_sop_from_chat`)
   - Currently: Stored in execution state
   - Target: Store via Artifact Plane
   - Note: SOPs are derived documents

3. **Workflows** (`create_workflow`)
   - Currently: Stored in execution state
   - Target: Store via Artifact Plane
   - Note: Workflows are derived representations

**Implementation Steps:**

1. **Initialize Artifact Plane in JourneyOrchestrator**
   ```python
   # Similar to OutcomesOrchestrator
   self.artifact_plane = ArtifactPlane(
       artifact_storage=public_works.artifact_storage_abstraction,
       state_management=public_works.state_abstraction
   )
   ```

2. **Update `_handle_create_blueprint`**
   - Store blueprint in Artifact Plane (not execution state)
   - Return `blueprint_id` reference
   - Preserve blueprint structure (coexistence analysis, visualizations)

3. **Update `_handle_generate_sop`**
   - Store SOP in Artifact Plane
   - Return `sop_id` reference
   - Preserve SOP structure (document, metadata)

4. **Update `_handle_create_workflow`**
   - Store workflow in Artifact Plane
   - Return `workflow_id` reference
   - Preserve workflow structure (BPMN, visualizations)

5. **Test Blueprint → Solution Flow**
   - Verify blueprint retrieval from Artifact Plane
   - Test solution creation from blueprint

**Files to Modify:**
- `journey_orchestrator.py` - Add Artifact Plane initialization and usage
- `journey_orchestrator.py` - Update blueprint/SOP/workflow creation handlers

**Test Files:**
- `test_create_solution_from_blueprint.py` - Should pass after migration
- `test_generate_sop.py` - May need updates
- `test_create_workflow.py` - May need updates

---

### ⏳ Content Realm - REVIEW REQUIRED

**Status:** ⏳ **Needs careful review - FMS preservation critical**

**Key Concern:** Content Realm has dual identity:
1. **FMS Operations** (ingest, retrieve, list files) → **PRESERVE AS-IS**
2. **Artifact Operations** (analysis results, visualizations) → **MIGRATE TO ARTIFACT PLANE**

**FMS Operations (DO NOT CHANGE):**
- ✅ `ingest_file` - Uses `FileManagementProtocol` → **KEEP**
- ✅ `register_file` - Uses `FileManagementProtocol` → **KEEP**
- ✅ `retrieve_file` - Uses `FileManagementProtocol` → **KEEP**
- ✅ `store_file_reference` - Uses `StateSurface` → **KEEP**
- ✅ File metadata tracking → **KEEP**
- ✅ Ingestion lineage → **KEEP**

**Artifact Operations (MIGRATE TO ARTIFACT PLANE):**
- ⏳ `parse_content` - Creates parsed content artifacts → **MIGRATE**
- ⏳ `extract_embeddings` - Creates embedding artifacts → **MIGRATE**
- ⏳ Analysis results (if any) → **MIGRATE**
- ⏳ Visualizations (if any) → **MIGRATE**

**Implementation Strategy:**

1. **Review Current Implementation**
   - Verify FMS operations use `FileManagementProtocol` (not execution state)
   - Identify which operations create derived artifacts
   - Document file → artifact relationships

2. **Preserve FMS Vocabulary**
   - Keep `file_id`, `file_reference`, `storage_location` in FMS
   - Keep `store_file_reference` for lineage tracking
   - Do NOT store files in Artifact Plane

3. **Migrate Derived Artifacts**
   - Parsed content summaries → Artifact Plane
   - Embedding metadata → Artifact Plane
   - Analysis visualizations → Artifact Plane
   - Link artifacts to source files via `file_id` in artifact metadata

4. **Lineage Preservation**
   - Artifact metadata includes `source_file_id`
   - Artifact metadata includes `source_file_reference`
   - FMS tracks file → artifact relationships (if needed)

**Files to Review:**
- `content_orchestrator.py` - Review all handlers
- `file_parser_service.py` - Review artifact creation
- Verify FMS operations are using correct protocols

**Test Strategy:**
- Verify file ingestion still works (FMS)
- Verify file retrieval still works (FMS)
- Test parsed content artifact retrieval (Artifact Plane)
- Test embedding artifact retrieval (Artifact Plane)

---

### ⏳ Insights Realm - PENDING

**Status:** ⏳ **Needs Artifact Plane integration**

**Artifacts to Migrate:**
1. **Semantic Interpretations** (`interpret_data`, `interpret_data_self_discovery`, `interpret_data_guided`)
   - Currently: Stored in execution state
   - Target: Store via Artifact Plane
   - Note: These are derived analysis results

2. **Data Quality Reports** (`assess_data_quality`)
   - Currently: Stored in execution state
   - Target: Store via Artifact Plane
   - Note: These are derived analysis results

3. **Business Analysis Results** (`analyze_structured_data`, `analyze_unstructured_data`)
   - Currently: Stored in execution state
   - Target: Store via Artifact Plane
   - Note: These are derived analysis results

4. **Lineage Visualizations** (`visualize_lineage`)
   - Currently: Stored in execution state
   - Target: Store via Artifact Plane
   - Note: These are derived visualizations

**Implementation Steps:**

1. **Initialize Artifact Plane in InsightsOrchestrator**
   ```python
   self.artifact_plane = ArtifactPlane(
       artifact_storage=public_works.artifact_storage_abstraction,
       state_management=public_works.state_abstraction
   )
   ```

2. **Update Interpretation Handlers**
   - Store interpretation results in Artifact Plane
   - Return `interpretation_id` reference
   - Preserve interpretation structure (semantic model, metadata)

3. **Update Quality Assessment Handlers**
   - Store quality reports in Artifact Plane
   - Return `quality_report_id` reference
   - Preserve quality report structure (metrics, recommendations)

4. **Update Analysis Handlers**
   - Store analysis results in Artifact Plane
   - Return `analysis_id` reference
   - Preserve analysis structure (insights, visualizations)

5. **Update Lineage Visualization Handler**
   - Store lineage visualizations in Artifact Plane
   - Return `lineage_visualization_id` reference
   - Preserve visualization structure (graph, metadata)

**Files to Modify:**
- `insights_orchestrator.py` - Add Artifact Plane initialization and usage
- `insights_orchestrator.py` - Update all artifact creation handlers

**Test Files:**
- All Insights Realm test files may need updates
- Verify artifact retrieval works correctly

---

## Implementation Checklist

### Phase 1: Journey Realm (Priority 1 - Blocks Solution Creation)

- [ ] Initialize Artifact Plane in JourneyOrchestrator
- [ ] Update `_handle_create_blueprint` to use Artifact Plane
- [ ] Update `_handle_generate_sop` to use Artifact Plane
- [ ] Update `_handle_create_workflow` to use Artifact Plane
- [ ] Test blueprint creation and retrieval
- [ ] Test blueprint → solution creation flow
- [ ] Update test files
- [ ] Verify all Journey Realm tests pass

### Phase 2: Content Realm Review (Priority 2 - FMS Preservation)

- [ ] Review Content Realm FMS operations (verify they're correct)
- [ ] Identify derived artifacts in Content Realm
- [ ] Document file → artifact relationships
- [ ] Migrate parsed content artifacts to Artifact Plane
- [ ] Migrate embedding artifacts to Artifact Plane
- [ ] Preserve FMS lineage tracking
- [ ] Test file ingestion (FMS) still works
- [ ] Test artifact retrieval (Artifact Plane) works
- [ ] Update test files

### Phase 3: Insights Realm (Priority 3 - Complete Migration)

- [ ] Initialize Artifact Plane in InsightsOrchestrator
- [ ] Update interpretation handlers to use Artifact Plane
- [ ] Update quality assessment handlers to use Artifact Plane
- [ ] Update analysis handlers to use Artifact Plane
- [ ] Update lineage visualization handler to use Artifact Plane
- [ ] Test all Insights Realm capabilities
- [ ] Update test files
- [ ] Verify all Insights Realm tests pass

### Phase 4: Cleanup (Priority 4 - Remove Execution State Artifacts)

- [ ] Remove artifact storage from execution state
- [ ] Update Runtime to only store artifact_id references
- [ ] Update frontend to retrieve artifacts separately
- [ ] Remove backward compatibility fallbacks
- [ ] Update documentation

---

## Risk Mitigation

### Risk 1: FMS Lineage Loss

**Mitigation:**
- Keep FMS operations unchanged
- Preserve `file_id`, `file_reference` in FMS
- Link artifacts to files via metadata (not storage)
- Test file → artifact traceability

### Risk 2: Breaking Changes

**Mitigation:**
- Implement backward compatibility fallbacks
- Test all existing flows
- Gradual migration (realm by realm)
- Keep execution state fallback during transition

### Risk 3: Artifact Retrieval Failures

**Mitigation:**
- Comprehensive logging in Artifact Plane
- Fallback to execution state during migration
- Test artifact retrieval for all artifact types
- Monitor error rates

### Risk 4: Content Realm Confusion

**Mitigation:**
- Clear documentation of file vs artifact distinction
- Code comments explaining FMS vs Artifact Plane usage
- Review Content Realm implementation carefully
- Test file operations separately from artifact operations

---

## Success Criteria

### Journey Realm
- ✅ Blueprints stored in Artifact Plane
- ✅ Blueprint → Solution flow works
- ✅ SOPs stored in Artifact Plane
- ✅ Workflows stored in Artifact Plane
- ✅ All Journey Realm tests pass

### Content Realm
- ✅ FMS operations unchanged (file ingestion/retrieval works)
- ✅ Derived artifacts stored in Artifact Plane
- ✅ File → artifact lineage preserved
- ✅ All Content Realm tests pass

### Insights Realm
- ✅ All analysis results stored in Artifact Plane
- ✅ All visualizations stored in Artifact Plane
- ✅ All Insights Realm tests pass

### Overall
- ✅ No artifacts in execution state (only references)
- ✅ All artifact retrieval works via Artifact Plane
- ✅ All tests pass
- ✅ FMS lineage preserved

---

## Timeline Estimate

- **Phase 1 (Journey Realm):** 2-3 hours
- **Phase 2 (Content Realm Review):** 1-2 hours
- **Phase 3 (Insights Realm):** 2-3 hours
- **Phase 4 (Cleanup):** 1-2 hours

**Total:** 6-10 hours

---

## Next Steps

1. **Start with Journey Realm** (highest priority - blocks solution creation)
2. **Review Content Realm** (verify FMS preservation)
3. **Migrate Insights Realm** (complete the migration)
4. **Cleanup** (remove execution state artifacts)

---

**Status:** Ready to begin Phase 1 (Journey Realm)
