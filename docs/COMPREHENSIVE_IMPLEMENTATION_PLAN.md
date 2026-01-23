# Comprehensive Implementation Plan - Production Readiness

**Date:** January 2026  
**Status:** 📋 **READY FOR EXECUTION**  
**Goal:** Achieve 100% production readiness for executive demo

---

## Executive Summary

This plan covers all identified gaps and improvements to achieve production readiness:

1. **Critical Missing Agents**: BusinessAnalysisAgent, SOPGenerationAgent
2. **Liaison Agents**: Complete coverage for all 4 pillars (Content, Insights, Journey, Outcomes)
3. **JSON Config Files + 4-Layer Model**: All agents must use JSON configs (Layer 1) with full 4-layer model
4. **MCP Tools & SOA APIs**: Complete and verify all required tools/APIs
5. **Architectural Compliance**: Fix violations, ensure agentic forward pattern
6. **Telemetry & Traceability**: Full observability

**Total Estimated Effort**: 78-115 hours (94-138 with buffer)  
**Critical Path**: BusinessAnalysisAgent → SOPGenerationAgent → Liaison Agents → JSON Configs + 4-Layer Model

---

## Key Pattern: JSON Config + 4-Layer Model

**All agents must follow this pattern**:

1. **JSON Config File** (Layer 1: Platform DNA):
   - Location: `agent_definitions/{agent_id}.json`
   - Contains: agent_id, agent_type, constitution, capabilities, permissions, collaboration_profile
   - Stable, platform-owned identity

2. **Python Implementation** (Agent Logic):
   - Location: `realms/{realm}/agents/{agent_id}.py`
   - Loads definition from JSON via AgentDefinitionRegistry
   - Implements agent reasoning and tool usage

3. **AgentPosture** (Layer 2: Tenant/Solution):
   - Loaded separately (tenant/solution-specific)
   - Behavioral tuning, custom instructions, tool budgets

4. **AgentRuntimeContext** (Layer 3: Journey/Session):
   - Provided at runtime (ephemeral)
   - Journey/session context, conversation history

5. **Prompt Assembly** (Layer 4: Derived):
   - Assembled at runtime from Layers 1-3
   - System and user messages derived from all layers

**AgentBase enforces this pattern** - all agents must load from JSON configs going forward.

---

## Phase 1: Critical Missing Agents (CRITICAL PATH)

### 1.1 BusinessAnalysisAgent (CRITICAL)

**Priority**: 🔴 **HIGHEST**  
**Estimated Effort**: 6-8 hours  
**Dependencies**: None

**Why Critical**:
- Core capability for Insights pillar
- Business analysis requires agentic reasoning
- Currently done by service (wrong pattern)

**Tasks**:
1. Create `business_analysis_agent.py` in `realms/insights/agents/`
2. Create `business_analysis_agent_definition.py` (AgentDefinition)
3. Implement agent with:
   - LLM reasoning about data meaning
   - Business interpretation generation
   - MCP tool usage for data access
   - Business context identification (aging report, claim report, etc.)
4. Update `InsightsOrchestrator._handle_interpret_data()` to use agent
5. Add MCP tool: `insights_interpret_data` (if not exists)
6. Add SOA API: `_handle_interpret_data_soa` (if not exists)

**Files to Create**:
- `symphainy_platform/realms/insights/agents/business_analysis_agent.py`
- `symphainy_platform/realms/insights/agents/business_analysis_agent_definition.py`

**Files to Update**:
- `symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py`
- `symphainy_platform/realms/insights/mcp_server/insights_mcp_server.py`

**Acceptance Criteria**:
- ✅ Agent reasons about data meaning (LLM)
- ✅ Generates business interpretations
- ✅ Uses MCP tools (no direct service calls)
- ✅ Identifies data types in business terms
- ✅ AgentDefinition created and registered

**Reference**: See `BUSINESS_ANALYSIS_AGENT_REQUIREMENT.md`

---

### 1.2 SOPGenerationAgent (ARCHITECTURAL FIX)

**Priority**: 🔴 **HIGH**  
**Estimated Effort**: 6-8 hours  
**Dependencies**: None

**Why Critical**:
- Fixes architectural violation (liaison executing)
- Separates conversation from reasoning
- Enables proper agentic forward pattern

**Tasks**:
1. Create `sop_generation_agent.py` in `realms/journey/agents/`
2. Create `sop_generation_agent_definition.py` (AgentDefinition)
3. Implement agent with:
   - LLM reasoning about requirements
   - SOP structure design
   - MCP tool usage for SOP generation
4. Refactor `JourneyLiaisonAgent`:
   - Remove execution logic (pattern matching, direct SOP generation)
   - Add LLM reasoning for conversation understanding
   - Delegate to SOPGenerationAgent when ready
5. Add MCP tool: `journey_generate_sop_from_structure` (if not exists)
6. Add SOA API: `_handle_generate_sop_from_structure_soa` (if not exists)
7. Update `WorkflowConversionService` to support `generate_sop_from_structure()`

**Files to Create**:
- `symphainy_platform/realms/journey/agents/sop_generation_agent.py`
- `symphainy_platform/realms/journey/agents/sop_generation_agent_definition.py`

**Files to Update**:
- `symphainy_platform/realms/journey/agents/journey_liaison_agent.py` (refactor)
- `symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py`
- `symphainy_platform/realms/journey/mcp_server/journey_mcp_server.py`
- `symphainy_platform/realms/journey/enabling_services/workflow_conversion_service.py`

**Acceptance Criteria**:
- ✅ JourneyLiaisonAgent handles conversation only (no execution)
- ✅ SOPGenerationAgent reasons about requirements (LLM)
- ✅ SOPGenerationAgent uses MCP tools
- ✅ No architectural violations
- ✅ AgentDefinition created and registered

**Reference**: See `SOP_GENERATION_AGENTIC_PATTERN.md`

---

## Phase 2: Complete Liaison Agent Coverage

### 2.1 ContentLiaisonAgent (NEW)

**Priority**: 🟡 **MEDIUM**  
**Estimated Effort**: 4-6 hours  
**Dependencies**: None

**Why Needed**:
- Complete coverage for all 4 pillars
- Chat-based guidance for Content pillar
- Explains Data Mash flow
- Helps with embedding strategies

**Tasks**:
1. Create `content_liaison_agent.py` in `realms/content/agents/`
2. Create `content_liaison_agent_definition.py` (AgentDefinition)
3. Implement agent with:
   - Chat-based guidance for file processing
   - Data Mash flow explanation
   - Embedding strategy guidance
   - File upload assistance
4. Add MCP tools for Content realm (if needed)
5. Update `ContentOrchestrator` to use agent (if chat interface exists)

**Files to Create**:
- `symphainy_platform/realms/content/agents/content_liaison_agent.py`
- `symphainy_platform/realms/content/agents/content_liaison_agent_definition.py`

**Files to Update**:
- `symphainy_platform/realms/content/orchestrators/content_orchestrator.py` (if chat exists)
- `symphainy_platform/realms/content/mcp_server/content_mcp_server.py` (if exists)

**Acceptance Criteria**:
- ✅ Agent handles conversation for Content pillar
- ✅ Explains Data Mash flow
- ✅ Provides guidance on embeddings
- ✅ AgentDefinition created and registered
- ✅ No execution (conversation only)

---

### 2.2 OutcomesLiaisonAgent (NEW)

**Priority**: 🟡 **MEDIUM**  
**Estimated Effort**: 4-6 hours  
**Dependencies**: None

**Why Needed**:
- Complete coverage for all 4 pillars
- Chat-based guidance for Outcomes/Solution pillar
- Explains artifact generation options
- Helps with blueprint/POC/roadmap selection

**Tasks**:
1. Create `outcomes_liaison_agent.py` in `realms/outcomes/agents/`
2. Create `outcomes_liaison_agent_definition.py` (AgentDefinition)
3. Implement agent with:
   - Chat-based guidance for Outcomes pillar
   - Artifact generation explanation (Blueprint, POC, Roadmap)
   - Solution synthesis guidance
   - Export assistance
4. Add MCP tools for Outcomes realm (if needed)
5. Update `OutcomesOrchestrator` to use agent (if chat interface exists)

**Files to Create**:
- `symphainy_platform/realms/outcomes/agents/outcomes_liaison_agent.py`
- `symphainy_platform/realms/outcomes/agents/outcomes_liaison_agent_definition.py`

**Files to Update**:
- `symphainy_platform/realms/outcomes/orchestrators/outcomes_orchestrator.py` (if chat exists)
- `symphainy_platform/realms/outcomes/mcp_server/outcomes_mcp_server.py` (if exists)

**Acceptance Criteria**:
- ✅ Agent handles conversation for Outcomes pillar
- ✅ Explains artifact generation options
- ✅ Provides guidance on Blueprint/POC/Roadmap
- ✅ AgentDefinition created and registered
- ✅ No execution (conversation only)

---

### 2.3 JourneyLiaisonAgent Refactoring (ARCHITECTURAL FIX)

**Priority**: 🔴 **HIGH**  
**Estimated Effort**: 4-6 hours  
**Dependencies**: SOPGenerationAgent (Phase 1.2)

**Why Critical**:
- Fixes architectural violation
- Separates conversation from execution
- Aligns with "liaison agents don't execute" principle

**Tasks**:
1. Remove pattern matching logic from `process_chat_message()`
2. Remove direct SOP generation from `generate_sop_from_chat()`
3. Add LLM reasoning for conversation understanding
4. Add intent recognition (LLM-based)
5. Delegate to SOPGenerationAgent when requirements complete
6. Update to use AgentDefinition pattern (if not already)

**Files to Update**:
- `symphainy_platform/realms/journey/agents/journey_liaison_agent.py`
- `symphainy_platform/realms/journey/agents/journey_liaison_agent_definition.py` (if not exists)

**Acceptance Criteria**:
- ✅ No execution logic in liaison agent
- ✅ LLM reasoning for conversation
- ✅ Delegates to SOPGenerationAgent
- ✅ No architectural violations

---

### 2.4 InsightsLiaisonAgent Verification

**Priority**: 🟢 **LOW**  
**Estimated Effort**: 2-3 hours  
**Dependencies**: None

**Why Needed**:
- Verify existing agent follows correct pattern
- Ensure no execution logic
- Verify AgentDefinition exists

**Tasks**:
1. Review `insights_liaison_agent.py`
2. Verify no execution logic
3. Verify AgentDefinition exists
4. Update if needed to match pattern

**Files to Review/Update**:
- `symphainy_platform/realms/insights/agents/insights_liaison_agent.py`
- `symphainy_platform/realms/insights/agents/insights_liaison_agent_definition.py` (if not exists)

**Acceptance Criteria**:
- ✅ No execution logic
- ✅ AgentDefinition exists
- ✅ Follows liaison agent pattern

---

## Phase 3: JSON Config Files + 4-Layer Model Implementation

**Priority**: 🔴 **HIGH**  
**Estimated Effort**: 16-24 hours  
**Dependencies**: Phases 1 & 2 (agents must exist first)

**Why Critical**:
- All agents must use JSON config files (Layer 1: Platform DNA)
- 4-layer model must be fully implemented
- AgentBase must enforce the pattern going forward
- Required for architectural compliance

### 3.1 Implement 4-Layer Model Infrastructure & JSON Loading

**Priority**: 🔴 **CRITICAL**  
**Estimated Effort**: 4-6 hours

**Current State**:
- ✅ AgentBase already has 4-layer model support (imports AgentPosture, AgentRuntimeContext)
- ✅ AgentBase has prompt assembly methods (`_assemble_system_message`, `_assemble_user_message`)
- ✅ AgentBase has initialization logic for 4-layer model
- ✅ AgentPosture model exists (`models/agent_posture.py`)
- ✅ AgentRuntimeContext model exists (`models/agent_runtime_context.py`)
- ❌ Need to add JSON file loading to AgentDefinitionRegistry
- ❌ Need to verify models are complete and match requirements

**Tasks**:
1. **Verify AgentPosture Model** (Layer 2):
   - Verify `agent_posture.py` has all required fields
   - Ensure it supports: behavioral_tuning, custom_instructions, tool_budgets, cost_limits, safety_rails
   - Update if needed

2. **Verify AgentRuntimeContext Model** (Layer 3):
   - Verify `agent_runtime_context.py` has all required fields
   - Ensure it supports: journey_id, session_id, user_context, conversation_history, temporary_state
   - Verify `from_request()` method exists
   - Update if needed

3. **Add JSON File Loading to AgentDefinitionRegistry**:
   - Add `load_from_json_file()` method
   - Load from `agent_definitions/*.json` files
   - Cache loaded definitions in memory
   - Support both JSON files and Supabase (for migration)
   - Add `get_definition_from_file()` method

4. **Update AgentBase** (if needed):
   - Verify JSON config loading path works
   - Ensure registry can load from JSON files
   - Verify 4-layer model initialization is complete
   - Test prompt assembly uses all layers correctly

**Files to Verify/Update**:
- `symphainy_platform/civic_systems/agentic/models/agent_posture.py` (verify/update)
- `symphainy_platform/civic_systems/agentic/models/agent_runtime_context.py` (verify/update)

**Files to Update**:
- `symphainy_platform/civic_systems/agentic/agent_definition_registry.py` (add JSON loading)
- `symphainy_platform/civic_systems/agentic/models/agent_base.py` (verify JSON loading works)
- All agent implementations to use JSON configs

**Acceptance Criteria**:
- ✅ AgentPosture model verified/updated (has all required fields)
- ✅ AgentRuntimeContext model verified/updated (has all required fields)
- ✅ AgentDefinitionRegistry loads from JSON files
- ✅ AgentBase can load definitions from JSON via registry
- ✅ 4-layer model fully functional

### 3.2 Create JSON Config Files for All Agents

**Priority**: 🔴 **HIGH**  
**Estimated Effort**: 8-12 hours

**Agents Needing JSON Configs**:

1. ✅ **CoexistenceAnalysisAgent** - Create JSON config
2. ✅ **BlueprintCreationAgent** - Create JSON config
3. ✅ **OutcomesSynthesisAgent** - Create JSON config
4. ✅ **RoadmapGenerationAgent** - Create JSON config
5. ✅ **POCGenerationAgent** - Create JSON config
6. ✅ **BusinessAnalysisAgent** - Create JSON config (Phase 1.1)
7. ✅ **SOPGenerationAgent** - Create JSON config (Phase 1.2)
8. ✅ **ContentLiaisonAgent** - Create JSON config (Phase 2.1)
9. ✅ **OutcomesLiaisonAgent** - Create JSON config (Phase 2.2)
10. ✅ **JourneyLiaisonAgent** - Migrate to JSON config (Phase 2.3)
11. ✅ **InsightsLiaisonAgent** - Migrate to JSON config (Phase 2.4)
12. ✅ **StructuredExtractionAgent** - Migrate to JSON config (existing)
13. ✅ **GuideAgent** - Migrate to JSON config (existing)

**Tasks**:
1. **Migrate Existing Python Definitions to JSON**:
   - Use existing Python definitions as inspiration
   - Convert to JSON format
   - Place in `symphainy_platform/civic_systems/agentic/agent_definitions/`
   - Keep Python files for backward compatibility (deprecated)

2. **Create JSON Configs for New Agents**:
   - Create JSON file for each new agent
   - Follow structure from existing definitions
   - Include all required fields (constitution, capabilities, permissions, etc.)

3. **Update AgentDefinitionRegistry**:
   - Support loading from JSON files
   - Cache loaded definitions
   - Support both JSON and Python (for migration)

**File Structure**:
```
symphainy_platform/civic_systems/agentic/agent_definitions/
  ├── journey_liaison_agent.json
  ├── journey_liaison_agent_definition.py (deprecated, keep for reference)
  ├── business_analysis_agent.json
  ├── sop_generation_agent.json
  ├── coexistence_analysis_agent.json
  ├── blueprint_creation_agent.json
  ├── outcomes_synthesis_agent.json
  ├── roadmap_generation_agent.json
  ├── poc_generation_agent.json
  ├── content_liaison_agent.json
  ├── outcomes_liaison_agent.json
  ├── insights_liaison_agent.json
  ├── structured_extraction_agent.json
  └── guide_agent.json
```

**JSON Config Template**:
```json
{
  "agent_id": "agent_name",
  "agent_type": "specialized",
  "constitution": {
    "role": "Agent Role",
    "mission": "Agent mission statement",
    "non_goals": [
      "Things agent should NOT do"
    ],
    "guardrails": [
      "Governance constraints"
    ],
    "authority": {
      "can_access": ["realms"],
      "can_read": ["artifacts"],
      "can_write": ["artifacts"]
    }
  },
  "capabilities": [
    "capability1",
    "capability2"
  ],
  "permissions": {
    "allowed_tools": [
      "tool1",
      "tool2"
    ],
    "allowed_mcp_servers": ["mcp_server"],
    "required_roles": []
  },
  "collaboration_profile": {
    "can_delegate_to": ["other_agents"],
    "can_be_invoked_by": ["invokers"],
    "collaboration_style": "specialized"
  },
  "version": "1.0.0",
  "created_by": "platform"
}
```

**Files to Create** (JSON configs):
- One JSON file per agent in `agent_definitions/` directory

**Files to Update**:
- `symphainy_platform/civic_systems/agentic/agent_definition_registry.py` (JSON loading)
- All agent implementations to load from JSON

**Acceptance Criteria**:
- ✅ JSON config files created for all agents
- ✅ Existing Python definitions migrated to JSON
- ✅ AgentDefinitionRegistry loads from JSON
- ✅ All agents load from JSON configs
- ✅ Backward compatibility maintained during migration

### 3.3 Update All Agents to Use 4-Layer Model

**Priority**: 🔴 **HIGH**  
**Estimated Effort**: 4-6 hours

**Tasks**:
1. **Update Agent Initialization**:
   - All agents must load AgentDefinition from JSON
   - Support AgentPosture loading (Layer 2)
   - Accept AgentRuntimeContext at runtime (Layer 3)
   - Use PromptAssembler for prompts (Layer 4)

2. **Update AgentBase**:
   - Enforce JSON config loading
   - Require AgentDefinition (Layer 1)
   - Support optional AgentPosture (Layer 2)
   - Accept AgentRuntimeContext (Layer 3)
   - Use PromptAssembler (Layer 4)

3. **Update All Agent Implementations**:
   - Use new initialization pattern
   - Load from JSON configs
   - Support 4-layer model

**Pattern**:
```python
class MyAgent(AgentBase):
    def __init__(
        self,
        agent_definition_id: str,
        agent_definition_path: Optional[str] = None,
        agent_posture_id: Optional[str] = None,
        agent_posture: Optional[AgentPosture] = None,
        public_works: Optional[Any] = None,
        agent_definition_registry: Optional[Any] = None,
        agent_posture_registry: Optional[Any] = None,
        ...
    ):
        # Load AgentDefinition from JSON (Layer 1)
        if agent_definition_path:
            agent_definition = self._load_definition_from_json(agent_definition_path)
        else:
            agent_definition = agent_definition_registry.get(agent_definition_id)
        
        # Load AgentPosture (Layer 2) - if provided
        if agent_posture_id:
            agent_posture = agent_posture_registry.get(agent_posture_id)
        elif agent_posture:
            pass  # Use provided posture
        
        # Initialize with 4-layer model
        super().__init__(
            agent_id=agent_definition_id,
            agent_definition=agent_definition,
            agent_posture=agent_posture,
            ...
        )
    
    async def process_request(self, request, context: ExecutionContext):
        # Create AgentRuntimeContext (Layer 3)
        runtime_context = AgentRuntimeContext(
            journey_id=context.journey_id,
            session_id=context.session_id,
            user_context=request.get("user_context"),
            conversation_history=request.get("conversation_history", [])
        )
        
        # Use PromptAssembler (Layer 4)
        prompts = self.prompt_assembler.assemble_prompt(
            agent_definition=self.agent_definition,
            agent_posture=self.agent_posture,
            runtime_context=runtime_context,
            user_message=request.get("message", "")
        )
        
        # Use prompts for LLM call
        response = await self._call_llm(
            system_message=prompts["system_message"],
            user_message=prompts["user_message"],
            context=context
        )
        
        return response
```

**Files to Update**:
- All agent implementation files
- `symphainy_platform/civic_systems/agentic/models/agent_base.py`

**Acceptance Criteria**:
- ✅ All agents use JSON config loading
- ✅ All agents support 4-layer model
- ✅ AgentBase enforces pattern
- ✅ PromptAssembler used for all LLM calls
- ✅ No hardcoded definitions in Python

**Reference**: See `AGENT_CONFIGURATION_PATTERN_ANALYSIS.md`

---

## Phase 4: MCP Tools & SOA APIs Completeness

**Priority**: 🟡 **MEDIUM**  
**Estimated Effort**: 6-10 hours  
**Dependencies**: Phases 1 & 2 (agents need tools)

**Why Critical**:
- Agents must use MCP tools (not direct service calls)
- All required tools must exist
- SOA APIs must be complete

**Required MCP Tools** (verify/create):

### Journey Realm:
- ✅ `journey_analyze_coexistence` - Verify exists
- ✅ `journey_get_workflow` - Verify/create
- ✅ `journey_generate_sop` - Verify exists
- ✅ `journey_generate_sop_from_structure` - **CREATE** (for SOPGenerationAgent)
- ✅ `journey_create_workflow` - Verify exists

### Outcomes Realm:
- ✅ `outcomes_synthesize` - Verify exists
- ✅ `outcomes_create_blueprint` - Verify/create
- ✅ `outcomes_generate_roadmap` - Verify exists
- ✅ `outcomes_create_poc` - Verify exists
- ✅ `outcomes_export_artifact` - Verify/create

### Insights Realm:
- ✅ `insights_get_parsed_data` - **CREATE** (for BusinessAnalysisAgent)
- ✅ `insights_get_embeddings` - **CREATE** (for BusinessAnalysisAgent)
- ✅ `insights_get_quality` - Verify/create
- ✅ `insights_interpret_data` - **CREATE** (for BusinessAnalysisAgent)
- ✅ `insights_get_analysis` - Verify/create

### Content Realm:
- ✅ `content_get_files` - Verify/create
- ✅ `content_get_parsed_files` - Verify/create
- ✅ `content_get_embeddings` - Verify/create

**Required SOA APIs** (verify/create):

### Journey Orchestrator:
- ✅ `_handle_analyze_coexistence_soa` - Verify exists
- ✅ `_handle_get_workflow_soa` - **CREATE**
- ✅ `_handle_generate_sop_soa` - Verify exists
- ✅ `_handle_generate_sop_from_structure_soa` - **CREATE**
- ✅ `_handle_create_workflow_soa` - Verify exists

### Outcomes Orchestrator:
- ✅ `_handle_synthesize_outcome_soa` - Verify exists
- ✅ `_handle_create_blueprint_soa` - **CREATE**
- ✅ `_handle_generate_roadmap_soa` - Verify exists
- ✅ `_handle_create_poc_soa` - Verify exists
- ✅ `_handle_export_artifact_soa` - **CREATE**

### Insights Orchestrator:
- ✅ `_handle_get_parsed_data_soa` - **CREATE**
- ✅ `_handle_get_embeddings_soa` - **CREATE**
- ✅ `_handle_get_quality_soa` - **CREATE**
- ✅ `_handle_interpret_data_soa` - **CREATE**
- ✅ `_handle_get_analysis_soa` - **CREATE**

### Content Orchestrator:
- ✅ `_handle_get_files_soa` - **CREATE**
- ✅ `_handle_get_parsed_files_soa` - **CREATE**
- ✅ `_handle_get_embeddings_soa` - **CREATE**

**Tasks**:
1. Audit existing MCP tools
2. Create missing MCP tools
3. Audit existing SOA APIs
4. Create missing SOA APIs
5. Verify tool → API → Service flow
6. Test all tools end-to-end

**Files to Update**:
- All realm MCP servers (`*_mcp_server.py`)
- All realm orchestrators (`*_orchestrator.py`)

**Acceptance Criteria**:
- ✅ All required MCP tools exist
- ✅ All required SOA APIs exist
- ✅ Tools call APIs correctly
- ✅ APIs call services correctly
- ✅ No direct service calls from agents

**Reference**: See `AGENTIC_SYSTEM_ALIGNMENT_PLAN.md` Phase 6

---

## Phase 5: Agent Implementation Pattern Compliance

**Priority**: 🟡 **MEDIUM**  
**Estimated Effort**: 6-8 hours  
**Dependencies**: Phase 3 (AgentDefinitions must exist)

**Why Critical**:
- All agents must use correct pattern
- Must use `use_tool()` for ALL service access
- Must use `_call_llm()` for reasoning
- Must have telemetry and traceability

**Tasks**:
1. Audit all agents for direct service calls
2. Replace direct calls with MCP tool usage
3. Verify all agents use `_call_llm()` for reasoning
4. Ensure telemetry is enabled
5. Ensure traceability is enabled
6. Verify no execution logic in liaison agents

**Agents to Audit**:
- CoexistenceAnalysisAgent
- BlueprintCreationAgent
- OutcomesSynthesisAgent
- RoadmapGenerationAgent
- POCGenerationAgent
- BusinessAnalysisAgent
- SOPGenerationAgent
- All liaison agents

**Pattern to Enforce**:
```python
# ✅ CORRECT: Use MCP tool
result = await self.use_tool(
    tool_name="realm_action",
    parameters={...},
    context=context
)

# ❌ WRONG: Direct service call
result = await self.service.do_something(...)
```

**Acceptance Criteria**:
- ✅ No direct service calls in agents
- ✅ All service access via MCP tools
- ✅ All reasoning via `_call_llm()`
- ✅ Telemetry enabled
- ✅ Traceability enabled

**Reference**: See `AGENTIC_SYSTEM_ALIGNMENT_PLAN.md` Phase 4

---

## Phase 6: Telemetry & Traceability

**Priority**: 🟢 **LOW**  
**Estimated Effort**: 4-6 hours  
**Dependencies**: Phase 5 (agents must be correct)

**Why Important**:
- Full observability
- Debugging and monitoring
- Compliance and audit

**Tasks**:
1. Verify all agents use telemetry service
2. Verify all agents log operations
3. Verify traceability is enabled
4. Add missing telemetry calls
5. Test telemetry end-to-end

**Acceptance Criteria**:
- ✅ All agents log operations
- ✅ Telemetry service used
- ✅ Traceability enabled
- ✅ Can trace agent → tool → API → service

---

## Phase 7: Testing & Validation

**Priority**: 🔴 **HIGH**  
**Estimated Effort**: 12-16 hours  
**Dependencies**: All previous phases

**Why Critical**:
- Ensure everything works
- Verify architectural compliance
- Ready for executive demo

**Test Categories**:

### 7.1 Unit Tests
- Agent reasoning logic
- MCP tool usage
- Service calls
- Error handling

### 7.2 Integration Tests
- Agent → MCP Tool → Orchestrator → Service flow
- Liaison → Specialist delegation
- End-to-end chat flows

### 7.3 End-to-End Tests
- Complete user journeys
- SOP generation from chat
- Business analysis
- Artifact generation

### 7.4 Architectural Compliance Tests
- No direct service calls
- No execution in liaison agents
- All agents use AgentDefinitions
- All tools/APIs exist

**Test Files to Create/Update**:
- Unit tests for each agent
- Integration tests for agent flows
- E2E tests for user journeys
- Compliance tests

**Acceptance Criteria**:
- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ All E2E tests pass
- ✅ All compliance tests pass
- ✅ Ready for executive demo

---

## Implementation Order & Dependencies

### Critical Path (Must Complete First):
1. **Phase 1.1**: BusinessAnalysisAgent (CRITICAL)
2. **Phase 1.2**: SOPGenerationAgent (CRITICAL)
3. **Phase 2.3**: JourneyLiaisonAgent Refactoring (depends on 1.2)
4. **Phase 4**: MCP Tools & SOA APIs (agents need tools)
5. **Phase 3**: AgentDefinitions (agents must exist)
6. **Phase 5**: Pattern Compliance (definitions must exist)
7. **Phase 7**: Testing (everything must be done)

### Can Be Done in Parallel:
- **Phase 2.1**: ContentLiaisonAgent (independent)
- **Phase 2.2**: OutcomesLiaisonAgent (independent)
- **Phase 2.4**: InsightsLiaisonAgent Verification (independent)
- **Phase 6**: Telemetry & Traceability (can be done alongside)

### Recommended Sequence:
```
Week 1 (Critical Path):
Day 1-2: Phase 1.1 (BusinessAnalysisAgent)
Day 3-4: Phase 1.2 (SOPGenerationAgent)
Day 5: Phase 2.3 (JourneyLiaisonAgent Refactoring)

Week 2 (Completeness):
Day 1-2: Phase 2.1 & 2.2 (Liaison Agents)
Day 3: Phase 2.4 (InsightsLiaisonAgent Verification)
Day 4-5: Phase 3.1 (4-Layer Model Infrastructure)

Week 3 (Config & Compliance):
Day 1-2: Phase 3.2 (JSON Config Files)
Day 3: Phase 3.3 (Update Agents to Use 4-Layer)
Day 4-5: Phase 4 (MCP Tools & SOA APIs)

Week 4 (Compliance & Polish):
Day 1-2: Phase 5 (Pattern Compliance)
Day 3: Phase 6 (Telemetry)
Day 4-5: Phase 7 (Testing)
```

---

## Effort Summary

| Phase | Task | Effort (Hours) | Priority |
|-------|------|----------------|----------|
| 1.1 | BusinessAnalysisAgent | 6-8 | 🔴 CRITICAL |
| 1.2 | SOPGenerationAgent | 6-8 | 🔴 CRITICAL |
| 2.1 | ContentLiaisonAgent | 4-6 | 🟡 MEDIUM |
| 2.2 | OutcomesLiaisonAgent | 4-6 | 🟡 MEDIUM |
| 2.3 | JourneyLiaisonAgent Refactor | 4-6 | 🔴 HIGH |
| 2.4 | InsightsLiaisonAgent Verify | 2-3 | 🟢 LOW |
| 3.1 | 4-Layer Model Infrastructure | 6-8 | 🔴 HIGH |
| 3.2 | JSON Config Files (All Agents) | 8-12 | 🔴 HIGH |
| 3.3 | Update Agents to Use 4-Layer | 4-6 | 🔴 HIGH |
| 4 | MCP Tools & SOA APIs | 6-10 | 🟡 MEDIUM |
| 5 | Pattern Compliance | 6-8 | 🟡 MEDIUM |
| 6 | Telemetry & Traceability | 4-6 | 🟢 LOW |
| 7 | Testing & Validation | 12-16 | 🔴 HIGH |

**Total**: 78-115 hours (estimated)  
**With Buffer (20%)**: 94-138 hours

**Note**: Phase 3 effort increased due to JSON config + 4-layer model implementation

---

## Risk Assessment

### High Risk:
1. **BusinessAnalysisAgent Complexity** - May need more time for LLM reasoning
2. **SOPGenerationAgent Integration** - Complex refactoring of existing code
3. **MCP Tools Completeness** - May discover missing dependencies

### Medium Risk:
1. **AgentDefinition Pattern** - Need to ensure 4-layer model compliance
2. **Testing Coverage** - May need more tests than estimated

### Low Risk:
1. **Liaison Agents** - Straightforward implementation
2. **Telemetry** - Mostly verification

---

## Success Criteria

### Must Have (Blocking):
- ✅ BusinessAnalysisAgent working
- ✅ SOPGenerationAgent working
- ✅ All liaison agents exist
- ✅ All agents use AgentDefinitions
- ✅ All required MCP tools exist
- ✅ All required SOA APIs exist
- ✅ No architectural violations
- ✅ All tests pass

### Should Have (Important):
- ✅ Full telemetry
- ✅ Complete test coverage
- ✅ Documentation updated

### Nice to Have (Optional):
- ✅ Performance optimizations
- ✅ Additional error handling
- ✅ Enhanced logging

---

## Next Steps

1. **Review Plan** - Confirm approach aligns with architecture
2. **Prioritize Phases** - Start with Phase 1 (Critical Path)
3. **Begin Implementation** - Start with BusinessAnalysisAgent
4. **Daily Checkpoints** - Review progress daily
5. **Final Audit** - Complete readiness audit before executive demo

---

**Status:** Plan ready, awaiting approval to begin implementation

**Estimated Completion**: 2-3 weeks (with focused effort)

**Ready for Executive Demo**: After Phase 7 completion + final audit
