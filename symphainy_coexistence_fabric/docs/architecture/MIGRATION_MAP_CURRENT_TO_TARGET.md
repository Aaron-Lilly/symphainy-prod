# Migration Map: Current → Target Layout

**Status:** Canonical  
**Date:** January 29, 2026  
**Purpose:** Single reference for "where does X go when we migrate?"

---

## Overview

This document maps every current `symphainy_platform` solution and realm to the target layout (capability + experience). **No migrations are performed in this document** — this is the recipe for a later migration phase.

---

## Migration Phases

| Phase | Description | Code Changes | Status |
|-------|-------------|--------------|--------|
| **Phase A** | Layout + READMEs | Create `capabilities/` and `experience/` directories with documentation. No code moves. | ✅ Complete |
| **Phase B** | Document references | READMEs reference existing `realms/` and `solutions/` implementations. | ✅ Complete |
| **Phase C** | Refactor registration | service_factory registers from `capabilities/` namespace. | ⏳ Future |
| **Phase D** | Move code | Actual code moves from `realms/` to `capabilities/` and from `solutions/` to `experience/`. | ⏳ Future |

---

## Realms → Capabilities Mapping

Current realm intent services become capabilities.

| Current Module | Target Capability | Intent Types |
|----------------|-------------------|--------------|
| `realms/content/intent_services/` | `capabilities/content/` | `ingest_file`, `parse_content`, `create_deterministic_embeddings`, `extract_embeddings`, `archive_file`, `delete_file`, etc. |
| `realms/coexistence/intent_services/` | `capabilities/coexistence/` | `initiate_guide_agent`, `navigate_to_solution`, `route_to_liaison_agent`, `show_solution_catalog`, etc. |
| `realms/insights/intent_services/` | `capabilities/insights/` | `analyze_structured_data`, `analyze_unstructured_data`, `assess_data_quality`, `map_relationships`, `visualize_lineage`, etc. |
| `realms/operations/intent_services/` | `capabilities/journey_engine/` | `create_workflow`, `generate_sop`, `optimize_process`, `analyze_coexistence`, etc. |
| `realms/outcomes/intent_services/` | `capabilities/solution_synthesis/` | `synthesize_outcome`, `generate_roadmap`, `create_poc`, `create_blueprint`, `export_artifact`, etc. |
| `realms/security/intent_services/` | `capabilities/security/` | `authenticate_user`, `create_session`, `terminate_session`, `validate_authorization`, etc. |
| `realms/control_tower/intent_services/` | `capabilities/control_tower/` | `get_platform_statistics`, `get_realm_health`, `get_solution_status`, `get_system_health`, etc. |

---

## Solutions → Experience + Capability Mapping

Current solutions split into capabilities (intent implementations) and experiences (SDK clients).

| Current Solution | Target Capability | Target Experience | Journeys |
|------------------|-------------------|-------------------|----------|
| `solutions/content_solution/` | `capabilities/content/` | `experience/content/` | file_upload, file_parsing, deterministic_embedding, file_management |
| `solutions/coexistence/` | `capabilities/coexistence/` | `experience/coexistence/` | guide_agent, introduction, navigation |
| `solutions/insights_solution/` | `capabilities/insights/` | `experience/insights/` | data_analysis, data_quality, lineage_visualization, relationship_mapping, etc. |
| `solutions/journey_solution/` | `capabilities/journey_engine/` | — | workflow_sop, coexistence_analysis |
| `solutions/operations_solution/` | `capabilities/journey_engine/` | `experience/operations/` | workflow_management, sop_management, process_optimization, coexistence_analysis |
| `solutions/outcomes_solution/` | `capabilities/solution_synthesis/` | `experience/outcomes/` | outcome_synthesis, roadmap_generation, poc_creation, blueprint_creation, artifact_export, solution_creation |
| `solutions/security_solution/` | `capabilities/security/` | `experience/security/` | authentication, registration, session_management |
| `solutions/control_tower/` | `capabilities/control_tower/` | `experience/control_tower/` | platform_monitoring, developer_docs, solution_composition, solution_management |

---

## MCP Servers Mapping

MCP servers are part of the Solutions Plane and must use Experience SDK only.

| Current MCP Server | Target Location | SDK Pattern |
|--------------------|-----------------|-------------|
| `solutions/content_solution/mcp_server/` | `experience/content/mcp_server/` or `solutions/<domain>/mcp_server/` | Use `ExperienceSDK.invoke_intent()` |
| `solutions/coexistence/mcp_server/` | `experience/coexistence/mcp_server/` | Use `ExperienceSDK.invoke_intent()` |
| `solutions/insights_solution/mcp_server/` | `experience/insights/mcp_server/` | Use `ExperienceSDK.invoke_intent()` |
| `solutions/journey_solution/mcp_server/` | `experience/operations/mcp_server/` | Use `ExperienceSDK.invoke_intent()` |
| `solutions/operations_solution/mcp_server/` | `experience/operations/mcp_server/` | Use `ExperienceSDK.invoke_intent()` |
| `solutions/outcomes_solution/mcp_server/` | `experience/outcomes/mcp_server/` | Use `ExperienceSDK.invoke_intent()` |
| `solutions/security_solution/mcp_server/` | `experience/security/mcp_server/` | Use `ExperienceSDK.invoke_intent()` |
| `solutions/control_tower/mcp_server/` | `experience/control_tower/mcp_server/` | Use `ExperienceSDK.invoke_intent()` |

---

## Detailed Intent Service Migration

### Content Capability (`capabilities/content/`)

| Current File | Target File | Intent Type |
|--------------|-------------|-------------|
| `realms/content/intent_services/ingest_file_service.py` | `capabilities/content/ingest_file_service.py` | `ingest_file` |
| `realms/content/intent_services/parse_content_service.py` | `capabilities/content/parse_content_service.py` | `parse_content` |
| `realms/content/intent_services/create_deterministic_embeddings_service.py` | `capabilities/content/create_deterministic_embeddings_service.py` | `create_deterministic_embeddings` |
| `realms/content/intent_services/archive_file_service.py` | `capabilities/content/archive_file_service.py` | `archive_file` |
| `realms/content/intent_services/delete_file_service.py` | `capabilities/content/delete_file_service.py` | `delete_file` |
| `realms/content/intent_services/extract_embeddings_service.py` | `capabilities/content/extract_embeddings_service.py` | `extract_embeddings` |
| `realms/content/intent_services/get_parsed_file_service.py` | `capabilities/content/get_parsed_file_service.py` | `get_parsed_file` |
| `realms/content/intent_services/list_artifacts_service.py` | `capabilities/content/list_artifacts_service.py` | `list_artifacts` |
| `realms/content/intent_services/retrieve_artifact_metadata_service.py` | `capabilities/content/retrieve_artifact_metadata_service.py` | `retrieve_artifact_metadata` |
| `realms/content/intent_services/save_materialization_service.py` | `capabilities/content/save_materialization_service.py` | `save_materialization` |

### Coexistence Capability (`capabilities/coexistence/`)

| Current File | Target File | Intent Type |
|--------------|-------------|-------------|
| `realms/coexistence/intent_services/initiate_guide_agent_service.py` | `capabilities/coexistence/initiate_guide_agent_service.py` | `initiate_guide_agent` |
| `realms/coexistence/intent_services/navigate_to_solution_service.py` | `capabilities/coexistence/navigate_to_solution_service.py` | `navigate_to_solution` |
| `realms/coexistence/intent_services/route_to_liaison_agent_service.py` | `capabilities/coexistence/route_to_liaison_agent_service.py` | `route_to_liaison_agent` |
| `realms/coexistence/intent_services/show_solution_catalog_service.py` | `capabilities/coexistence/show_solution_catalog_service.py` | `show_solution_catalog` |
| `realms/coexistence/intent_services/process_guide_agent_message_service.py` | `capabilities/coexistence/process_guide_agent_message_service.py` | `process_guide_agent_message` |
| `realms/coexistence/intent_services/introduce_platform_service.py` | `capabilities/coexistence/introduce_platform_service.py` | `introduce_platform` |
| `realms/coexistence/intent_services/call_orchestrator_mcp_tool_service.py` | `capabilities/coexistence/call_orchestrator_mcp_tool_service.py` | `call_orchestrator_mcp_tool` |
| `realms/coexistence/intent_services/list_available_mcp_tools_service.py` | `capabilities/coexistence/list_available_mcp_tools_service.py` | `list_available_mcp_tools` |

### Journey Engine Capability (`capabilities/journey_engine/`)

| Current File | Target File | Intent Type |
|--------------|-------------|-------------|
| `realms/operations/intent_services/create_workflow_service.py` | `capabilities/journey_engine/create_workflow_service.py` | `create_workflow` |
| `realms/operations/intent_services/generate_sop_service.py` | `capabilities/journey_engine/generate_sop_service.py` | `generate_sop` |
| `realms/operations/intent_services/generate_sop_from_chat_service.py` | `capabilities/journey_engine/generate_sop_from_chat_service.py` | `generate_sop_from_chat` |
| `realms/operations/intent_services/optimize_process_service.py` | `capabilities/journey_engine/optimize_process_service.py` | `optimize_process` |
| `realms/operations/intent_services/analyze_coexistence_service.py` | `capabilities/journey_engine/analyze_coexistence_service.py` | `analyze_coexistence` |
| `realms/operations/intent_services/sop_chat_message_service.py` | `capabilities/journey_engine/sop_chat_message_service.py` | `sop_chat_message` |

### Solution Synthesis Capability (`capabilities/solution_synthesis/`)

| Current File | Target File | Intent Type |
|--------------|-------------|-------------|
| `realms/outcomes/intent_services/synthesize_outcome_service.py` | `capabilities/solution_synthesis/synthesize_outcome_service.py` | `synthesize_outcome` |
| `realms/outcomes/intent_services/generate_roadmap_service.py` | `capabilities/solution_synthesis/generate_roadmap_service.py` | `generate_roadmap` |
| `realms/outcomes/intent_services/create_poc_service.py` | `capabilities/solution_synthesis/create_poc_service.py` | `create_poc` |
| `realms/outcomes/intent_services/create_blueprint_service.py` | `capabilities/solution_synthesis/create_blueprint_service.py` | `create_blueprint` |
| `realms/outcomes/intent_services/export_artifact_service.py` | `capabilities/solution_synthesis/export_artifact_service.py` | `export_artifact` |
| `realms/outcomes/intent_services/create_solution_service.py` | `capabilities/solution_synthesis/create_solution_service.py` | `create_solution` |
| `realms/outcomes/intent_services/generate_report_service.py` | `capabilities/solution_synthesis/generate_report_service.py` | `generate_report` |
| `realms/outcomes/intent_services/generate_visual_service.py` | `capabilities/solution_synthesis/generate_visual_service.py` | `generate_visual` |

### Insights Capability (`capabilities/insights/`)

| Current File | Target File | Intent Type |
|--------------|-------------|-------------|
| `realms/insights/intent_services/analyze_structured_data_service.py` | `capabilities/insights/analyze_structured_data_service.py` | `analyze_structured_data` |
| `realms/insights/intent_services/analyze_unstructured_data_service.py` | `capabilities/insights/analyze_unstructured_data_service.py` | `analyze_unstructured_data` |
| `realms/insights/intent_services/assess_data_quality_service.py` | `capabilities/insights/assess_data_quality_service.py` | `assess_data_quality` |
| `realms/insights/intent_services/extract_structured_data_service.py` | `capabilities/insights/extract_structured_data_service.py` | `extract_structured_data` |
| `realms/insights/intent_services/interpret_data_guided_service.py` | `capabilities/insights/interpret_data_guided_service.py` | `interpret_data_guided` |
| `realms/insights/intent_services/interpret_data_self_discovery_service.py` | `capabilities/insights/interpret_data_self_discovery_service.py` | `interpret_data_self_discovery` |
| `realms/insights/intent_services/map_relationships_service.py` | `capabilities/insights/map_relationships_service.py` | `map_relationships` |
| `realms/insights/intent_services/visualize_lineage_service.py` | `capabilities/insights/visualize_lineage_service.py` | `visualize_lineage` |

### Security Capability (`capabilities/security/`)

| Current File | Target File | Intent Type |
|--------------|-------------|-------------|
| `realms/security/intent_services/authenticate_user_service.py` | `capabilities/security/authenticate_user_service.py` | `authenticate_user` |
| `realms/security/intent_services/create_session_service.py` | `capabilities/security/create_session_service.py` | `create_session` |
| `realms/security/intent_services/terminate_session_service.py` | `capabilities/security/terminate_session_service.py` | `terminate_session` |
| `realms/security/intent_services/validate_authorization_service.py` | `capabilities/security/validate_authorization_service.py` | `validate_authorization` |
| `realms/security/intent_services/validate_token_service.py` | `capabilities/security/validate_token_service.py` | `validate_token` |
| `realms/security/intent_services/create_user_account_service.py` | `capabilities/security/create_user_account_service.py` | `create_user_account` |
| `realms/security/intent_services/check_email_availability_service.py` | `capabilities/security/check_email_availability_service.py` | `check_email_availability` |

### Control Tower Capability (`capabilities/control_tower/`)

| Current File | Target File | Intent Type |
|--------------|-------------|-------------|
| `realms/control_tower/intent_services/get_platform_statistics_service.py` | `capabilities/control_tower/get_platform_statistics_service.py` | `get_platform_statistics` |
| `realms/control_tower/intent_services/get_realm_health_service.py` | `capabilities/control_tower/get_realm_health_service.py` | `get_realm_health` |
| `realms/control_tower/intent_services/get_solution_status_service.py` | `capabilities/control_tower/get_solution_status_service.py` | `get_solution_status` |
| `realms/control_tower/intent_services/get_system_health_service.py` | `capabilities/control_tower/get_system_health_service.py` | `get_system_health` |
| `realms/control_tower/intent_services/list_solutions_service.py` | `capabilities/control_tower/list_solutions_service.py` | `list_solutions` |
| `realms/control_tower/intent_services/validate_solution_service.py` | `capabilities/control_tower/validate_solution_service.py` | `validate_solution` |
| `realms/control_tower/intent_services/get_code_examples_service.py` | `capabilities/control_tower/get_code_examples_service.py` | `get_code_examples` |
| `realms/control_tower/intent_services/get_documentation_service.py` | `capabilities/control_tower/get_documentation_service.py` | `get_documentation` |
| `realms/control_tower/intent_services/get_patterns_service.py` | `capabilities/control_tower/get_patterns_service.py` | `get_patterns` |

---

## Journeys Migration

Journeys from solutions become part of experience surfaces (SDK clients that compose intents).

| Current Journey | Target Experience | Journey Pattern |
|-----------------|-------------------|-----------------|
| `solutions/content_solution/journeys/file_upload_materialization_journey.py` | `experience/content/journeys/` | SDK: invoke_intent → trigger_journey |
| `solutions/content_solution/journeys/file_parsing_journey.py` | `experience/content/journeys/` | SDK: invoke_intent → trigger_journey |
| `solutions/coexistence/journeys/guide_agent_journey.py` | `experience/coexistence/journeys/` | SDK: invoke_intent → trigger_journey |
| `solutions/operations_solution/journeys/workflow_management_journey.py` | `experience/operations/journeys/` | SDK: invoke_intent → trigger_journey |
| `solutions/outcomes_solution/journeys/roadmap_generation_journey.py` | `experience/outcomes/journeys/` | SDK: invoke_intent → trigger_journey |

---

## Files That Do Not Move

| File | Reason | Stays At |
|------|--------|----------|
| `runtime/*` | Runtime Plane (Takeoff owns) | `runtime/` |
| `civic_systems/*` | Civic Systems (Takeoff owns) | `civic_systems/` |
| `foundations/*` | Foundations (Takeoff owns) | `foundations/` |
| `bases/*` | Base classes (shared) | `bases/` |
| `bootstrap/*` | Boot infrastructure (Takeoff owns) | `bootstrap/` |
| `config/*` | Configuration (shared) | `config/` |

---

## Migration Checklist

### Phase C: Refactor Registration

- [ ] Update service_factory to import from `capabilities/` namespace
- [ ] Update IntentRegistry registration to use new import paths
- [ ] Verify all intent handlers resolve correctly
- [ ] Run full test suite

### Phase D: Move Code

- [ ] Move each realm intent service to corresponding capability
- [ ] Update all imports (internal and external)
- [ ] Move solution journeys to experience surfaces
- [ ] Update MCP servers to use Experience SDK
- [ ] Deprecate old `realms/` and `solutions/` paths
- [ ] Final test pass and cleanup

---

## References

- [CANONICAL_PLATFORM_ARCHITECTURE.md](CANONICAL_PLATFORM_ARCHITECTURE.md)
- [ADR_JOURNEY_OPERATIONS_OUTCOMES_NAMING.md](ADR_JOURNEY_OPERATIONS_OUTCOMES_NAMING.md)
- [BOOT_PHASES.md](BOOT_PHASES.md)
- [EXPERIENCE_SDK_CONTRACT.md](EXPERIENCE_SDK_CONTRACT.md)
