# Runtime Obligations Index (Intent Contracts)

**Purpose:** Document runtime obligations (registration, execution, state, artifacts) per journey/capability so intent implementations plug into the platform correctly. See [RUNTIME_CONTRACTS.md](../architecture/RUNTIME_CONTRACTS.md) for the full contract definitions.

**References:** [RUNTIME_CONTRACTS.md](../architecture/RUNTIME_CONTRACTS.md), [VISION_ALIGNMENT_SUMMARY.md](VISION_ALIGNMENT_SUMMARY.md).

---

## Obligation categories

For each journey (or capability), intent implementations must:

| Obligation | What the runtime provides | What the intent does |
|------------|---------------------------|------------------------|
| **Registration** | IntentRegistry; intent_type; handler_name; optional handler_function | Register with IntentRegistry at boot (via solution/capability initializer) |
| **Execution** | ExecutionContext (execution_id, intent, tenant_id, session_id, solution_id, state_surface, wal?, metadata) | Accept context; return result (artifacts, events); do not create execution records |
| **State** | StateSurface: get_session_state(session_id, tenant_id), set_session_state(...); execution-scoped state as needed | Read/write only via state surface; no direct DB/cache |
| **Artifacts** | ArtifactRegistry (via State Surface): register_artifact(artifact_id, type, produced_by, lifecycle_state, semantic_descriptor, ...); resolve, list | Register artifacts via registry; do not write directly to storage for platform authority |

---

## By capability / journey group

### Security (journey_security_authentication, journey_security_registration)

| Obligation | Details |
|------------|---------|
| **Registration** | intent_type: create_session, authenticate_user, refresh_session, terminate_session, validate_authorization; create_user_account, check_email_availability, send_verification_email, validate_registration_data, verify_email. Handler name = security solution / auth journey. |
| **Execution** | ExecutionContext with tenant_id, session_id, solution_id; auth intents may have user_id, access_token in parameters. |
| **State** | Session state: store session_id, user_id, tenant_id, lifecycle_state; get/set via state_surface. |
| **Artifacts** | Session artifact: register with artifact_type "session", produced_by intent create_session/terminate_session, lifecycle_state ACTIVE/TERMINATED. |

### Content (journey_content_*)

| Obligation | Details |
|------------|---------|
| **Registration** | intent_type: ingest_file, save_materialization, parse_content, get_parsed_file, create_deterministic_embeddings, extract_embeddings, save_embeddings, list_artifacts, retrieve_artifact_metadata, archive_file. Handler name = content solution / file/journey service. |
| **Execution** | ExecutionContext; parameters include file refs, artifact_ids, options. |
| **State** | Session state for upload/session context; execution state for pipeline step. |
| **Artifacts** | Register file, parsed_content, embeddings artifacts; produced_by intent; lifecycle_state PENDING/READY; materializations for GCS/Arango. |

### Insights (insights_*, journey_insights_*)

| Obligation | Details |
|------------|---------|
| **Registration** | intent_type: analyze_structured_data, analyze_unstructured_data, interpret_data_guided, interpret_data_self_discovery, assess_data_quality, extract_structured_data, visualize_lineage; explore_relationships, identify_patterns, initiate_guided_discovery; assess_data_quality, generate_quality_report, validate_schema; create_relationship_graph, visualize_relationships; semantic embedding intents. Handler name = insights realm / journey service. |
| **Execution** | ExecutionContext; parameters include artifact_ids, analysis options. |
| **State** | Session state for analysis context; execution state for intermediate results. |
| **Artifacts** | Register analysis results, reports, lineage visuals; produced_by intent; lifecycle_state READY. |

### Coexistence (journey_coexistence_*)

| Obligation | Details |
|------------|---------|
| **Registration** | intent_type: analyze_coexistence, optimize_process; chat session intents; get_shared_context, merge_agent_contexts, share_context_to_agent; initiate_guide_agent, process_guide_agent_message, route_to_liaison_agent; explain_coexistence, introduce_platform, show_solution_catalog; execute_pillar_action, get_pillar_context, initiate_liaison_agent, process_liaison_agent_message; establish_solution_context, get_solution_context, navigate_to_solution; call_orchestrator_mcp_tool, list_available_mcp_tools, validate_mcp_tool_call. Handler name = coexistence solution / guide/liaison/navigation service. |
| **Execution** | ExecutionContext; session_id and tenant_id for agent context; parameters for message content, pillar, solution_id. |
| **State** | Session state for conversation context, shared context, agent state. |
| **Artifacts** | Register conversation artifacts, shared context artifacts as needed; produced_by intent. |

### Journey engine / Operations (journey_journey_*, journey_sop_*, journey_workflow_*)

| Obligation | Details |
|------------|---------|
| **Registration** | intent_type: compose_journey; analyze_coexistence, identify_opportunities; create_blueprint, save_blueprint; chat_with_journey_agent, initiate_sop_wizard, save_sop_from_chat; create_workflow_from_sop, generate_sop_from_workflow; generate_visualization, select_sop, select_workflow; generate_sop, generate_sop_from_chat, sop_chat_message; create_workflow, get_workflow. Handler name = operations/journey solution. |
| **Execution** | ExecutionContext; parameters include journey_id, workflow_id, sop_id, options. |
| **State** | Session state for workflow/SOP context; execution state for saga steps. |
| **Artifacts** | Register workflow, SOP, blueprint artifacts; produced_by intent; lifecycle_state READY. |

### Solution synthesis / Outcomes (journey_outcomes_*)

| Obligation | Details |
|------------|---------|
| **Registration** | intent_type: export_artifact; create_blueprint; create_solution; synthesize_outcome; create_poc; generate_roadmap; etc. Handler name = outcomes/solution_synthesis service. |
| **Execution** | ExecutionContext; parameters include solution_id, artifact refs, synthesis options. |
| **State** | Session state for outcome context; execution state for synthesis steps. |
| **Artifacts** | Register outcome artifacts, blueprints, reports; produced_by intent; lifecycle_state READY. |

### Control tower (control_tower_*, journey_control_tower_*)

| Obligation | Details |
|------------|---------|
| **Registration** | intent_type: admin/get_platform_statistics, get_execution_metrics, get_realm_health, get_solution_registry_status, get_system_health; get_code_examples, get_patterns, get_sdk_documentation, validate_solution; get_execution_metrics, get_platform_statistics, get_realm_health, get_solution_registry_status; compose_solution, create_solution_from_template, get_composition_guide, get_solution_templates; solution_management intents. Handler name = control_tower service. |
| **Execution** | ExecutionContext; tenant_id for isolation; parameters for admin queries. |
| **State** | Session state for admin context; read-only for platform stats. |
| **Artifacts** | Control tower typically reads artifacts and platform state; may register audit or report artifacts. |

---

## Summary

- Every intent **registers** with IntentRegistry (intent_type, handler_name).
- Every intent **receives** ExecutionContext and **returns** a result (artifacts, events).
- Every intent **reads/writes state** only via StateSurface.
- Every intent **registers artifacts** via ArtifactRegistry (State Surface); no direct storage writes for platform authority.

For per-intent details, see the individual intent contract files in each journey folder. This index is the runtime-obligations reference for the handoff.
