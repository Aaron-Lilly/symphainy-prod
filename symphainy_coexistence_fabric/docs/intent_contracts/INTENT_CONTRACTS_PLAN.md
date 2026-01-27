# Intent Contracts Creation Plan

**Date:** January 27, 2026  
**Status:** ⏳ **IN PROGRESS**

---

## Overview

Creating intent contracts for all 28 journeys, organized by journey folder. Each intent contract follows the same pattern and is informed by:
1. Journey contracts (what intents are in each journey)
2. Actual implementations in `symphainy_platform`
3. Frontend expectations in `symphainy-frontend`

---

## Progress

### ✅ Completed - Content Realm (All 4 Journeys)

**Journey: File Upload & Materialization**
- `journey_content_file_upload_materialization/`
  - ✅ `intent_ingest_file.md`
  - ✅ `intent_save_materialization.md`

**Journey: File Parsing**
- `journey_content_file_parsing/`
  - ✅ `intent_parse_content.md` (comprehensive)
  - ✅ `intent_get_parsed_file.md` (added - used by frontend)
  - ❌ `intent_save_parsed_content.md` (removed - not implemented, parsing auto-saves)

**Journey: Deterministic Embedding**
- `journey_content_deterministic_embedding/`
  - ✅ `intent_create_deterministic_embeddings.md` (comprehensive)
  - ✅ `intent_extract_embeddings.md` (renamed from save_embeddings - matches implementation)

**Journey: File Management**
- `journey_content_file_management/`
  - ✅ `intent_list_artifacts.md` (artifact-centric vocabulary - backend to be updated)
  - ✅ `intent_retrieve_artifact_metadata.md` (renamed from get_artifact_metadata)
  - ✅ `intent_archive_file.md` (comprehensive)

### 📊 Cross-Reference Analysis
- ✅ `CONTENT_REALM_ANALYSIS.md` - Documents all gaps and recommendations

### ⏳ In Progress
- None currently

### 📋 Pending (26 journeys remaining)

**Content Realm (2 remaining journeys):**
- `journey_content_deterministic_embedding/`
- `journey_content_file_management/`

**Insights Realm (5 journeys):**
- `journey_insights_data_quality/`
- `journey_insights_semantic_embedding/`
- `journey_insights_data_interpretation/`
- `journey_insights_relationship_mapping/`
- `journey_insights_business_analysis/`

**Journey Realm (5 journeys):**
- `journey_journey_workflow_sop_visualization/`
- `journey_journey_workflow_sop_conversion/`
- `journey_journey_sop_creation_chat/`
- `journey_journey_coexistence_analysis/`
- `journey_journey_create_coexistence_blueprint/`

**Solution Realm (4 journeys):**
- `journey_solution_synthesis/`
- `journey_solution_roadmap_generation/`
- `journey_solution_poc_proposal/`
- `journey_solution_cross_pillar_integration/`

**Security Solution (2 journeys):**
- `journey_security_registration/`
- `journey_security_authentication/`

**Coexistence Solution (3 journeys):**
- `journey_coexistence_introduction/`
- `journey_coexistence_navigation/`
- `journey_coexistence_guide_agent/`

**Control Tower Solution (4 journeys):**
- `journey_control_tower_monitoring/`
- `journey_control_tower_solution_management/`
- `journey_control_tower_developer_docs/`
- `journey_control_tower_solution_composition/`

---

## Intent Contract Template

Each intent contract includes:
1. Intent Overview (purpose, flow, observable artifacts)
2. Intent Parameters (required, optional, context metadata)
3. Intent Returns (success, error responses)
4. Artifact Registration (State Surface, Artifact Index)
5. Idempotency (key, scope, behavior)
6. Implementation Details (handler location, steps, dependencies)
7. Frontend Integration (usage, expected behavior)
8. Error Handling (validation, runtime errors)
9. Testing & Validation (happy path, boundary violations, failures)
10. Contract Compliance (required artifacts, events, lifecycle)

---

## Next Steps

1. **Continue with File Parsing Journey** (2 intents)
2. **Create script to extract intents from journey contracts** (automation)
3. **Create intent contracts for remaining journeys** (systematic approach)
4. **Validate against implementations** (ensure alignment)

---

**Last Updated:** January 27, 2026
