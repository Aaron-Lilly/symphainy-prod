# Intent Contracts: Vision Alignment Summary

**Purpose:** Map current intent contract folders (journey/realm) to the target architecture in solution_realm_refactoring_vision.md. Capabilities = what the platform CAN DO; Experience = how users TOUCH it.

**References:** [solution_realm_refactoring_vision.md](../solution_realm_refactoring_vision.md), [RUNTIME_OBLIGATIONS_INDEX.md](RUNTIME_OBLIGATIONS_INDEX.md).

---

## Mapping: Current folder to Capability and Experience

- **journey_content_*** (file_upload_materialization, file_parsing, deterministic_embedding, file_management) → capabilities/content → experience/content
- **insights_*** (data_analysis, data_interpretation, data_quality, extraction, lineage) → capabilities/insights → experience/insights
- **journey_insights_*** (business_analysis, data_interpretation, data_quality, relationship_mapping, semantic_embedding) → capabilities/insights → experience/insights
- **journey_coexistence_*** (analysis, chat_session, context_sharing, guide_agent, introduction, liaison_agent, navigation, orchestrator_interaction) → capabilities/coexistence → experience/coexistence
- **journey_journey_***, **journey_sop_management**, **journey_workflow_management** → capabilities/journey_engine → experience/operations
- **journey_outcomes_*** (artifact_export, blueprint_creation, creation, poc_proposal, roadmap_generation, synthesis) → capabilities/solution_synthesis → experience/outcomes
- **journey_security_authentication**, **journey_security_registration** → capabilities/security → experience/security
- **control_tower_***, **journey_control_tower_*** → capabilities/control_tower → experience/control_tower

---

## Quick reference

- Content: journey_content_* → capabilities/content → experience/content
- Insights: insights_*, journey_insights_* → capabilities/insights → experience/insights
- Coexistence: journey_coexistence_* → capabilities/coexistence → experience/coexistence
- Journey engine (Operations): journey_journey_*, journey_sop_*, journey_workflow_* → capabilities/journey_engine → experience/operations
- Solution synthesis (Outcomes): journey_outcomes_* → capabilities/solution_synthesis → experience/outcomes
- Security: journey_security_* → capabilities/security → experience/security
- Control tower: control_tower_*, journey_control_tower_* → capabilities/control_tower → experience/control_tower

---

## Gaps and renames (no code change yet)

1. **Naming:** Current folders use journey_<domain>_* and control_tower_*, insights_*. Target layout uses capabilities/<name> and experience/<name>. Intent contracts can stay in docs/intent_contracts/ with current folder names; this mapping is the source of truth.
2. **Operations vs journey_engine:** Operations is the experience (UI); journey_engine is the capability. All journey_journey_*, journey_sop_*, journey_workflow_* intents implement the journey_engine capability and are exposed via experience/operations.

Runtime obligations per journey are in RUNTIME_OBLIGATIONS_INDEX.md.
