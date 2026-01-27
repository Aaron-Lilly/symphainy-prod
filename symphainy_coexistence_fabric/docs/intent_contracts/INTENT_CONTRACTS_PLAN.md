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

**📊 Content Realm Analysis**
- ✅ `CONTENT_REALM_ANALYSIS.md` - Documents all gaps and recommendations

---

### ✅ Completed - Journey Realm (Reorganized into 5 Journeys)

**Journey: Coexistence Analysis**
- `journey_coexistence_analysis/`
  - ✅ `intent_analyze_coexistence.md` (comprehensive - includes identify_opportunities)
  - ✅ `intent_optimize_process.md` (comprehensive)

**Journey: SOP Management**
- `journey_sop_management/`
  - ✅ `intent_generate_sop.md` (comprehensive - supports workflow_id or chat_mode)
  - ✅ `intent_generate_sop_from_chat.md` (comprehensive)
  - ✅ `intent_sop_chat_message.md` (comprehensive)

**Journey: Workflow Management**
- `journey_workflow_management/`
  - ✅ `intent_create_workflow.md` (comprehensive - supports SOP or BPMN file)
  - ✅ `intent_get_workflow.md` (comprehensive)

**📊 Journey Realm Analysis**
- ✅ `JOURNEY_REALM_ANALYSIS.md` - Documents all gaps and recommendations

**Note:** Original journey contracts reorganized based on implementation:
- `journey_journey_coexistence_analysis` → `journey_coexistence_analysis`
- `journey_journey_sop_creation_chat` → `journey_sop_management`
- `journey_journey_workflow_sop_conversion` → `journey_workflow_management`
- `journey_journey_workflow_sop_visualization` → Intents integrated into above
- `journey_journey_create_coexistence_blueprint` → Moved to Outcomes Realm

---

### ⏳ Pending - To Be Implemented

**Journey Realm - Guide Agent Operations (Frontend expects, not yet in orchestrator)**
- `journey_agent_operations/`
  - ⏳ `intent_analyze_user_intent.md`
  - ⏳ `intent_get_journey_guidance.md`
  - ⏳ `intent_get_conversation_history.md`

**Journey Realm - Cross-Pillar Operations (Frontend expects, not yet in orchestrator)**
- `journey_cross_pillar_operations/`
  - ⏳ `intent_send_message_to_pillar_agent.md`
  - ⏳ `intent_get_pillar_conversation_history.md`

---

### ✅ Completed - Insights Realm (Reorganized into 5 Journeys)

**Key Finding:** Backend is comprehensive (16 intents implemented), not shells. Journey contracts were placeholder templates.

**Journey: Data Quality**
- `insights_data_quality/`
  - ✅ `intent_assess_data_quality.md` (comprehensive - combines parsing + embedding quality)

**Journey: Data Interpretation**
- `insights_data_interpretation/`
  - ✅ `intent_interpret_data_self_discovery.md` (comprehensive - unguided discovery)
  - ✅ `intent_interpret_data_guided.md` (comprehensive - guided with guide_id)

**Journey: Data Analysis**
- `insights_data_analysis/`
  - ✅ `intent_analyze_structured_data.md` (comprehensive - statistics, patterns, anomalies)
  - ✅ `intent_analyze_unstructured_data.md` (comprehensive - NLP, deep dive with agent)

**Journey: Lineage & Relationships**
- `insights_lineage/`
  - ✅ `intent_visualize_lineage.md` (comprehensive - "Your Data Mash")
  - ✅ `intent_map_relationships.md` (comprehensive - entity relationships)

**Journey: Extraction & Matching**
- `insights_extraction/`
  - ✅ `intent_extract_structured_data.md` (MCP tool - patterns: VLP, AAR, PSO)
  - ✅ `intent_match_source_to_target.md` (three-phase matching)

**📊 Insights Realm Analysis**
- ✅ `INSIGHTS_REALM_ANALYSIS.md` - Documents backend implementation (16 intents, 12 services)

**Journey Contracts Updated:**
- ✅ `journey_insights_data_quality.md` - Updated to reflect assess_data_quality
- ✅ `journey_insights_data_interpretation.md` - Updated with self-discovery + guided
- ✅ `journey_insights_business_analysis.md` - Updated with structured + unstructured
- ✅ `journey_insights_relationship_mapping.md` - Updated with lineage + relationships
- ✅ `journey_insights_semantic_embedding.md` - Renamed to Extraction & Matching

---

### 📋 Remaining Realms

**Outcomes Realm (includes create_blueprint from Journey):**
- `journey_outcomes_synthesis/`
- `journey_outcomes_blueprint/` (moved from Journey Realm)
- `journey_outcomes_roadmap/`
- `journey_outcomes_poc/`

**Security Solution (2 journeys):**
- `journey_security_registration/`
- `journey_security_authentication/`

**Coexistence Solution (3 journeys):**
- `journey_coexistence_introduction/`
- `journey_coexistence_navigation/`
- `journey_coexistence_guide_agent/`

---

### ✅ Completed - Control Tower / Admin Dashboard (3 Views, 16 Intents)

**Key Finding:** Control Tower is implemented as **Admin Dashboard** in `civic_systems/experience/admin_dashboard/`.

**View: Control Room (Platform Observability)**
- `control_tower_monitoring/`
  - ✅ `intent_admin_get_platform_statistics.md` (comprehensive)
  - ✅ `intent_admin_get_execution_metrics.md` (MVP - aggregation TODO)
  - ✅ `intent_admin_get_realm_health.md` (comprehensive)
  - ✅ `intent_admin_get_solution_registry_status.md` (comprehensive)
  - ✅ `intent_admin_get_system_health.md` (comprehensive)

**View: Developer View (SDK Documentation & Tools)**
- `control_tower_developer/`
  - ✅ `intent_admin_get_documentation.md` (comprehensive)
  - ✅ `intent_admin_get_code_examples.md` (comprehensive)
  - ✅ `intent_admin_get_patterns.md` (comprehensive)
  - ✅ `intent_admin_validate_solution.md` (comprehensive - Solution Builder Playground)
  - ✅ `intent_admin_preview_solution.md` (comprehensive)
  - ✅ `intent_admin_submit_feature_request.md` (Coming Soon - gated)

**View: Business User View (Solution Composition)**
- `control_tower_business/`
  - ✅ `intent_admin_get_composition_guide.md` (comprehensive)
  - ✅ `intent_admin_get_solution_templates.md` (comprehensive)
  - ✅ `intent_admin_compose_solution.md` (comprehensive - gated)
  - ✅ `intent_admin_register_solution.md` (comprehensive)
  - ✅ `intent_admin_submit_business_feature_request.md` (comprehensive)

**📊 Control Tower Analysis**
- ✅ `CONTROL_TOWER_ANALYSIS.md` - Documents backend implementation (3 views, 16 intents)

**Architecture Notes:**
- Frontend (AdminAPIManager.ts) uses intent-based API
- Backend has REST endpoints + services
- All intents use `admin_` prefix for access control filtering

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
11. Cross-Reference Analysis (contract vs implementation vs frontend)

---

## Summary

| Realm/Solution | Journeys/Views | Intents | Status |
|----------------|----------------|---------|--------|
| Content | 4 | 9 | ✅ Complete |
| Journey | 3 (reorganized) | 7 | ✅ Complete |
| Journey (Guide Agent) | 1 | 3 | ⏳ Pending |
| Journey (Cross-Pillar) | 1 | 2 | ⏳ Pending |
| Insights | 5 (reorganized) | 9 | ✅ Complete |
| Control Tower | 3 views | 16 | ✅ Complete |
| Outcomes | 4 | TBD | 📋 Remaining |
| Security | 2 | TBD | 📋 Remaining |
| Coexistence | 3 | TBD | 📋 Remaining |

**Notes:**
- Insights Realm backend has 16 intents implemented, 9 documented in contracts (those used by frontend + key extraction intents).
- Control Tower = Admin Dashboard in `civic_systems/experience/admin_dashboard/`

---

**Last Updated:** January 27, 2026
