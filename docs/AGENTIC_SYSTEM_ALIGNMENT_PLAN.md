# Agentic System Alignment Plan

**Date:** January 2026  
**Status:** 📋 **PLAN READY FOR REVIEW**

---

## Executive Summary

**CRITICAL FINDINGS:**
1. **Agents Missing AgentDefinition (Layer 1)**: Newly created agents (CoexistenceAnalysisAgent, BlueprintCreationAgent, etc.) are NOT using the AgentDefinition pattern - they extend AgentBase directly without Layer 1 identity
2. **MCP Tool Access Pattern**: Agents should use MCP tools to access enabling services via Orchestrator SOA APIs, but current implementation may have direct service calls
3. **Architectural Reframing**: The MVP context document has some excellent insights but also some questionable suggestions that need careful evaluation

**REQUIRED PATTERN:**
```
Agent (with AgentDefinition) → MCP Tool → Orchestrator SOA API → Enabling Service
```

---

## Current State Analysis

### ✅ What's Working

1. **AgentDefinition Pattern Exists**: 
   - `AgentDefinition` model (Layer 1: Platform DNA)
   - `AgentDefinitionRegistry` for storage
   - Examples: `journey_liaison_agent_definition.py`, `stateless_agent_definition.py`

2. **MCP Server Pattern Exists**:
   - Realm MCP servers expose orchestrator SOA APIs as tools
   - Pattern: `_define_soa_api_handlers()` → MCP Server → Tools

3. **Orchestrator SOA APIs**:
   - Orchestrators define SOA APIs via `_define_soa_api_handlers()`
   - These are exposed as MCP tools automatically

4. **Some Services Correctly Use Agents**:
   - `StructuredExtractionService` - Uses `extraction_agent` for pattern discovery
   - `EmbeddingService` - Uses `semantic_meaning_agent` for semantic meaning inference
   - `UnstructuredAnalysisService` - Uses `InsightsLiaisonAgent` for deep dive

### ❌ What's Missing

1. **New Agents Lack AgentDefinition**:
   - `CoexistenceAnalysisAgent` - No AgentDefinition
   - `BlueprintCreationAgent` - No AgentDefinition
   - `OutcomesSynthesisAgent` - No AgentDefinition
   - `RoadmapGenerationAgent` - No AgentDefinition
   - `POCGenerationAgent` - No AgentDefinition
   - ❌ **`BusinessAnalysisAgent` - MISSING ENTIRELY** (CRITICAL GAP)

2. **Business Analysis Missing Agentic Pattern**:
   - **CRITICAL**: Business analysis (data interpretation) is currently done by `DataAnalyzerService.interpret_data()`
   - This is WRONG - business analysis requires agentic reasoning
   - Examples of what's needed:
     - "This looks like an aging report for collections data - many accounts are 90+ days past due"
     - "This looks like a claim report - the driver appears to be at fault"
     - "This looks like a book about the Statue of Liberty"
   - This requires LLM reasoning about data meaning, context, and business interpretation
   - **Solution**: Create `BusinessAnalysisAgent` that reasons about data and generates business interpretations

3. **Agent Implementation Pattern**:
   - New agents extend `AgentBase` directly
   - Should use AgentDefinition (Layer 1) + AgentPosture (Layer 2) + Runtime Context (Layer 3)

4. **MCP Tool Usage Verification**:
   - Need to verify agents use `use_tool()` for ALL service access
   - No direct service calls should exist

5. **Telemetry & Traceability**:
   - Need to ensure all agents use telemetry service
   - Need to ensure traceability is enabled

### ⚠️ Potential Gaps (Needs Review)

1. **Semantic Summary Generation**:
   - `SemanticSelfDiscoveryService._generate_semantic_summary()` - May need agent reasoning
   - **Review Needed**: Check if summary generation requires interpretation or is just aggregation
   - **If Agent Needed**: Create `SemanticDiscoveryAgent`

2. **Content Guidance**:
   - No ContentLiaisonAgent in new system
   - **Optional**: Would enhance UX but not critical path

---

## Architectural Principles (from MVP Context Document)

### ✅ Excellent Insights (Keep These)

1. **"Agents reason. Systems decide. Realms execute. Runtime records."**
   - This is the golden rule - must be enforced

2. **Orchestrators are thin coordinators**:
   - Not reasoning engines
   - Not god objects
   - Just compiled recipes

3. **MCP servers are realm-scoped agent execution surfaces**:
   - Not tool marketplaces
   - Not plugin systems
   - Just controlled execution interfaces

4. **Determinism rules**:
   - Same intent + same inputs → same execution graph
   - Same service version + same config + same inputs → same output

5. **Guardrail: "Orchestrators select paths. Enabling services do work. MCP servers expose verbs. Agents fill in blanks."**

### ⚠️ Questionable Suggestions (Need Review)

1. **"AI Agent Reasoning" in onboarding reframing**:
   - **Suggestion**: "Agent helps user express goals as platform intents"
   - **Concern**: This might be too restrictive. The current implementation where agent performs reasoning and generates solution structure seems valuable. The key is ensuring the agent's output is validated by Smart City and materialized by Solution System - which we're already doing.

2. **Content Pillar: "storing files by default"**:
   - **Suggestion**: Make "persist file" explicit choice, "ephemeral processing" default
   - **Evaluation**: This aligns with Data Mash boundary - GOOD suggestion

3. **Insights Pillar: "Interactive Analysis"**:
   - **Suggestion**: Query semantic artifacts, not re-invoke raw parsing
   - **Evaluation**: This is a good guardrail - prevents nondeterminism

4. **Journey Pillar: coexistence blueprints as purpose-bound outcomes**:
   - **Suggestion**: Treat as purpose-bound outcomes, not derived data
   - **Evaluation**: We're already doing this - GOOD

5. **Outcomes Pillar: "artifacts are inputs, solutions are registrations"**:
   - **Suggestion**: Clarify language - solutions are named compositions
   - **Evaluation**: This is just language clarification - GOOD

6. **Chat Interface: "Liaison agents may explain, guide, and request — but never execute directly"**:
   - **Evaluation**: This is already our pattern - GOOD

---

## Implementation Plan

### Phase 1: Create AgentDefinitions for All Agents

**Goal**: Ensure all agents have Layer 1 (Platform DNA) identity

**Tasks**:
1. Create `coexistence_analysis_agent_definition.py`
2. Create `blueprint_creation_agent_definition.py`
3. Create `outcomes_synthesis_agent_definition.py`
4. Create `roadmap_generation_agent_definition.py`
5. Create `poc_generation_agent_definition.py`
6. Create `content_liaison_agent_definition.py` (if we add it)
7. Update `insights_liaison_agent_definition.py` (if missing)
8. Register all definitions in `AgentDefinitionRegistry`

**Pattern**:
```python
COEXISTENCE_ANALYSIS_AGENT_DEFINITION = AgentDefinition(
    agent_id="coexistence_analysis_agent",
    agent_type="specialized",
    constitution={
        "role": "Coexistence Analysis Agent",
        "mission": "Analyze workflows to identify friction points and human-positive optimization opportunities",
        "non_goals": [
            "Do not execute actions directly",
            "Do not persist client data",
            "Do not bypass workflow governance"
        ],
        "guardrails": [
            "All actions must be expressed as intents",
            "Use human-positive messaging (friction removal, not automation)",
            "Validate workflow definitions before analysis"
        ],
        "authority": {
            "can_access": ["journey_realm"],
            "can_read": ["workflows", "coexistence_analyses"],
            "cannot_write": ["any_persistent_data"]
        }
    },
    capabilities=[
        "analyze_friction",
        "identify_human_value",
        "generate_recommendations"
    ],
    permissions={
        "allowed_tools": [
            "journey_analyze_coexistence",
            "journey_get_workflow"
        ],
        "allowed_mcp_servers": ["journey_mcp"],
        "required_roles": []
    },
    collaboration_profile={
        "can_delegate_to": [],
        "can_be_invoked_by": ["guide_agent", "journey_liaison_agent"],
        "collaboration_style": "specialized"
    },
    version="1.0.0",
    created_by="platform"
)
```

### Phase 2: Create BusinessAnalysisAgent (CRITICAL - MISSING)

**Goal**: Create agent for business analysis/data interpretation

**Why This is Critical**:
- Business analysis requires agentic reasoning (understanding context, making inferences)
- Current `DataAnalyzerService.interpret_data()` only does basic interpretation (data type, semantic mapping)
- Missing the reasoning layer that identifies "aging report", "claim report", "collections data", etc.

**Tasks**:
1. Create `business_analysis_agent.py` in `realms/insights/agents/`
2. Agent should:
   - Reason about data meaning using LLM
   - Identify data type in business terms (aging report, claim report, etc.)
   - Generate business interpretations with context
   - Use MCP tools to get parsed data and semantic embeddings
   - Construct business analysis outcomes

3. Update `InsightsOrchestrator._handle_interpret_data()` to use `BusinessAnalysisAgent`

**Pattern**:
```python
class BusinessAnalysisAgent(AgentBase):
    async def process_request(self, request, context):
        # 1. Get parsed data via MCP tool
        parsed_data = await self.use_tool("insights_get_parsed_data", {...}, context)
        
        # 2. Get semantic embeddings via MCP tool
        embeddings = await self.use_tool("insights_get_embeddings", {...}, context)
        
        # 3. Reason about data meaning (LLM)
        interpretation = await self._call_llm(
            system_message="You are a business analyst...",
            user_message=f"Analyze this data: {parsed_data}. What does it represent?",
            context=context
        )
        
        # 4. Construct business analysis outcome
        return {
            "artifact_type": "business_analysis",
            "artifact": {
                "data_type": interpretation.data_type,  # e.g., "aging_report", "claim_report"
                "business_interpretation": interpretation.interpretation,
                "key_insights": interpretation.insights,
                "confidence": interpretation.confidence
            }
        }
```

### Phase 3: Refactor Agents to Use AgentDefinition Pattern

**Goal**: Ensure all agents load and use AgentDefinition (4-layer model)

**Tasks**:
1. Update `CoexistenceAnalysisAgent` to:
   - Accept `agent_definition_id` or `agent_definition` in constructor
   - Load from registry if `agent_definition_id` provided
   - Use `AgentBase` initialization with 4-layer model support

2. Update all other new agents similarly (including `BusinessAnalysisAgent`)

3. Ensure agents use `_call_llm()` for reasoning (already doing this)

4. Ensure agents use `use_tool()` for ALL service access (verify this)

**Pattern**:
```python
class CoexistenceAnalysisAgent(AgentBase):
    def __init__(
        self,
        agent_definition_id: Optional[str] = None,
        agent_definition: Optional[AgentDefinition] = None,
        agent_posture_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        public_works: Optional[Any] = None,
        agent_definition_registry: Optional[Any] = None,
        agent_posture_registry: Optional[Any] = None,
        telemetry_service: Optional[Any] = None,
        mcp_client_manager: Optional[Any] = None
    ):
        super().__init__(
            agent_id="coexistence_analysis_agent",
            agent_type="specialized",
            agent_definition_id=agent_definition_id,
            agent_definition=agent_definition,
            agent_posture_id=agent_posture_id,
            tenant_id=tenant_id,
            public_works=public_works,
            agent_definition_registry=agent_definition_registry,
            agent_posture_registry=agent_posture_registry,
            telemetry_service=telemetry_service,
            mcp_client_manager=mcp_client_manager
        )
```

### Phase 4: Verify MCP Tool Access Pattern

**Goal**: Ensure agents ONLY use MCP tools, never direct service calls

**Tasks**:
1. Audit all agent implementations:
   - `CoexistenceAnalysisAgent` - Verify uses `use_tool("journey_analyze_coexistence")`
   - `BlueprintCreationAgent` - Verify uses `use_tool("outcomes_create_blueprint")`
   - `OutcomesSynthesisAgent` - Verify uses `use_tool("outcomes_synthesize")`
   - `RoadmapGenerationAgent` - Verify uses `use_tool("outcomes_generate_roadmap")`
   - `POCGenerationAgent` - Verify uses `use_tool("outcomes_create_poc")`

2. Verify orchestrators expose all needed SOA APIs:
   - Journey Orchestrator: `analyze_coexistence` SOA API
   - Outcomes Orchestrator: `create_blueprint`, `synthesize_outcome`, `generate_roadmap`, `create_poc` SOA APIs

3. Remove any direct service calls from agents

**Pattern Verification**:
```python
# ✅ CORRECT: Agent uses MCP tool
result = await self.use_tool(
    "journey_analyze_coexistence",
    {"workflow_id": workflow_id},
    context
)

# ❌ WRONG: Direct service call
result = await self.coexistence_analysis_service.analyze_coexistence(...)
```

### Phase 4: Ensure Telemetry & Traceability

**Goal**: All agents have full telemetry and traceability

**Tasks**:
1. Verify all agents use `telemetry_service`:
   - Tool usage tracking (via `_track_tool_usage()`)
   - LLM call tracking (via `_call_llm()`)
   - Operation tracking

2. Ensure traceability:
   - Agent ID in all logs
   - Execution context in all operations
   - Tool call tracking with parameters and results

3. Verify health monitoring:
   - Agent health metrics
   - Error tracking
   - Performance metrics

### Phase 6: Orchestrator SOA API Completeness

**Goal**: Ensure all orchestrators expose needed SOA APIs

**Current State Audit**:

1. **Journey Orchestrator**:
   - ✅ `optimize_process` - EXISTS
   - ✅ `generate_sop` - EXISTS
   - ✅ `create_workflow` - EXISTS
   - ❌ `analyze_coexistence` - **MISSING** (handler exists but not in SOA API definitions)
   - ❌ `get_workflow` - **MISSING** (needed for agents to get workflow data)

2. **Outcomes Orchestrator**:
   - ✅ `synthesize_outcome` - EXISTS
   - ✅ `generate_roadmap` - EXISTS
   - ✅ `create_poc` - EXISTS
   - ✅ `export_to_migration_engine` - EXISTS
   - ❌ `create_blueprint` - **MISSING** (handler exists but not in SOA API definitions)
   - ❌ `export_artifact` - **MISSING** (handler exists but not in SOA API definitions)

3. **Content Orchestrator**:
   - ✅ `ingest_file` - EXISTS
   - ✅ `parse_content` - EXISTS
   - ✅ `extract_embeddings` - EXISTS
   - ❌ `get_files` - **MISSING** (needed for agents to get file data)
   - ❌ `get_parsed_files` - **MISSING** (needed for agents to get parsed file data)

4. **Insights Orchestrator**:
   - ✅ `extract_structured_data` - EXISTS
   - ❌ `get_quality` - **MISSING** (needed for agents to get quality data)
   - ❌ `get_analysis` - **MISSING** (needed for agents to get analysis data)

**Tasks**:
1. Add missing SOA APIs to `_define_soa_api_handlers()` in each orchestrator
2. Create SOA API handler methods (following dual call pattern)
3. Verify MCP servers automatically expose them as tools

### Phase 7: Architectural Reframing Evaluation

**Goal**: Carefully evaluate and implement good suggestions, reject questionable ones

**Detailed Evaluation**:

#### ✅ Implement (Excellent Suggestions - Align with Architecture)

1. **Content Pillar: Ephemeral Processing Default**
   - **Suggestion**: Make "persist file" explicit choice, default to "ephemeral processing"
   - **Rationale**: Reinforces Data Mash boundary, aligns with "Only Realms touch data" principle
   - **Action**: Update UI language, make persistence opt-in, update documentation
   - **Priority**: HIGH

2. **Insights Pillar: Query Semantic Artifacts**
   - **Suggestion**: Interactive analysis should query semantic artifacts, not re-invoke raw parsing
   - **Rationale**: Prevents nondeterminism, respects artifact lifecycle
   - **Action**: Verify InsightsLiaisonAgent queries artifacts, not re-parsing
   - **Priority**: HIGH

3. **Language Clarification: Solutions as Registrations**
   - **Suggestion**: Clarify that artifacts are inputs, solutions are named compositions (registrations)
   - **Rationale**: Aligns with Artifact Lifecycle model (Purpose-Bound Outcomes)
   - **Action**: Update documentation, clarify in code comments
   - **Priority**: MEDIUM

4. **Journey Pillar: Blueprints as Purpose-Bound Outcomes**
   - **Suggestion**: Treat coexistence blueprints as purpose-bound outcomes, not derived data
   - **Rationale**: We're already doing this - just needs explicit documentation
   - **Action**: Document this clearly, verify Artifact Plane usage
   - **Priority**: MEDIUM

5. **Chat Interface: Liaison Agents Never Execute**
   - **Suggestion**: Liaison agents may explain, guide, and request — but never execute directly
   - **Rationale**: This is already our pattern - just needs explicit enforcement
   - **Action**: Verify all liaison agents use MCP tools, never direct execution
   - **Priority**: HIGH

#### ⚠️ Review Carefully (Questionable Suggestions - Need Discussion)

1. **Onboarding: "Agent helps express goals as intents"**
   - **Current Implementation**: 
     - Agent performs reasoning about goals
     - Agent generates solution structure with pillar prioritization
     - Agent creates customized solution context
     - Solution System materializes the structure
   - **Suggested Reframing**: 
     - "Agent helps user express goals as platform intents"
     - Smart City validates
     - Solution System materializes
   - **Concern**: The current approach is MORE valuable:
     - Agent reasoning provides strategic focus
     - Agent generates insights and recommendations
     - Agent creates personalized solution structure
     - This is valuable reasoning, not just intent translation
   - **Recommendation**: **KEEP CURRENT APPROACH** but ensure:
     - Agent output is validated by Smart City (already happening)
     - Solution System materializes the structure (already happening)
     - Agent reasoning is preserved and displayed (already happening)
     - Document that agent reasoning is validated, not just accepted
   - **Action**: Document the current pattern clearly, emphasize validation step
   - **Priority**: LOW (just documentation)

2. **Orchestrator Responsibilities: "Select paths, not do work"**
   - **Suggestion**: Orchestrators select paths, enabling services do work
   - **Current State**: 
     - Orchestrators call agents (good - agents reason)
     - Agents use MCP tools to call orchestrator SOA APIs (good - controlled access)
     - Orchestrator SOA APIs call enabling services (good - services do work)
   - **Evaluation**: This is ALREADY our pattern - just needs verification
   - **Action**: Audit orchestrators to ensure they're thin coordinators:
     - ✅ Select which agent to call
     - ✅ Select which SOA API to expose
     - ❌ NOT doing the actual work (services do that)
     - ❌ NOT encoding business logic (agents/services do that)
   - **Priority**: MEDIUM (verification)

#### ❌ Reject (Misaligned Suggestions)

1. **"AI Agent Reasoning" reframing as "intent translation"**
   - **Why Reject**: The current agent reasoning is valuable and aligns with "Agents reason" principle
   - **Current Value**: 
     - Strategic focus identification
     - Pillar prioritization
     - Customization recommendations
     - This is reasoning, not just translation
   - **Action**: Keep current approach, document validation step

---

## Reframing Implementation Plan

### Step 1: Content Pillar - Ephemeral Processing Default

**Files to Update**:
- `symphainy-frontend/app/(protected)/pillars/content/components/FileUploader.tsx`
- `symphainy-frontend/app/(protected)/pillars/content/page.tsx`
- Content realm documentation

**Changes**:
- Default to ephemeral processing
- Make "persist file" explicit checkbox/option
- Update UI language: "Process file" not "Upload file"
- Update help text to explain ephemeral vs. persistent

### Step 2: Insights Pillar - Query Semantic Artifacts

**Files to Verify**:
- `symphainy_platform/realms/insights/agents/insights_liaison_agent.py`

**Verification**:
- Ensure `answer_question()` queries semantic artifacts
- Ensure `explore_relationships()` uses semantic data abstraction
- Ensure no re-parsing unless explicitly requested

### Step 3: Language Clarification

**Files to Update**:
- All documentation
- Code comments in solution synthesis service
- Frontend labels and descriptions

**Changes**:
- "Artifacts are inputs to solutions"
- "Solutions are named compositions (registrations)"
- "Solutions are not documents - they are platform registrations"

### Step 4: Orchestrator Audit

**Files to Audit**:
- All orchestrator implementations

**Checklist**:
- ✅ Orchestrators select paths (which agent, which SOA API)
- ✅ Orchestrators don't do work (services do)
- ✅ Orchestrators don't encode business logic
- ✅ Orchestrators are thin coordinators

---

## Detailed Implementation Steps

### Step 1: Create AgentDefinitions

**File**: `symphainy_platform/civic_systems/agentic/agent_definitions/coexistence_analysis_agent_definition.py`

```python
"""
Coexistence Analysis Agent Definition (Layer 1: Platform DNA)
"""

from symphainy_platform.civic_systems.agentic.models.agent_definition import AgentDefinition

COEXISTENCE_ANALYSIS_AGENT_DEFINITION = AgentDefinition(
    agent_id="coexistence_analysis_agent",
    agent_type="specialized",
    constitution={
        "role": "Coexistence Analysis Agent",
        "mission": "Analyze workflows to identify friction points and human-positive optimization opportunities using AI reasoning",
        "non_goals": [
            "Do not execute actions directly",
            "Do not persist client data",
            "Do not bypass workflow governance",
            "Do not replace human decision-making"
        ],
        "guardrails": [
            "All actions must be expressed as intents",
            "Use human-positive messaging (friction removal, not automation)",
            "Validate workflow definitions before analysis",
            "Emphasize human value in all recommendations",
            "Never suggest replacing humans - suggest removing friction"
        ],
        "authority": {
            "can_access": ["journey_realm"],
            "can_read": ["workflows", "coexistence_analyses"],
            "cannot_write": ["any_persistent_data"]
        }
    },
    capabilities=[
        "analyze_friction",
        "identify_human_value",
        "generate_recommendations",
        "reason_about_workflows"
    ],
    permissions={
        "allowed_tools": [
            "journey_analyze_coexistence",
            "journey_get_workflow"
        ],
        "allowed_mcp_servers": ["journey_mcp"],
        "required_roles": []
    },
    collaboration_profile={
        "can_delegate_to": [],
        "can_be_invoked_by": ["guide_agent", "journey_liaison_agent", "outcomes_orchestrator"],
        "collaboration_style": "specialized"
    },
    version="1.0.0",
    created_by="platform"
)
```

**Repeat for all other agents** (BlueprintCreationAgent, OutcomesSynthesisAgent, RoadmapGenerationAgent, POCGenerationAgent, **BusinessAnalysisAgent**)

### Step 2: Update Agent Implementations

**File**: `symphainy_platform/realms/journey/agents/coexistence_analysis_agent.py`

**Changes**:
1. Import AgentDefinition
2. Update `__init__` to accept `agent_definition_id` or `agent_definition`
3. Use `AgentBase` 4-layer model initialization
4. Ensure all service access goes through `use_tool()`

### Step 3: Add Missing SOA APIs

**File**: `symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py`

**Add to `_define_soa_api_handlers()`**:
```python
"analyze_coexistence": {
    "handler": self._handle_analyze_coexistence_soa,
    "input_schema": {
        "type": "object",
        "properties": {
            "workflow_id": {
                "type": "string",
                "description": "Workflow identifier to analyze"
            },
            "reasoning_context": {
                "type": "object",
                "description": "Optional reasoning context from agent"
            },
            "user_context": {
                "type": "object",
                "description": "Optional user context"
            }
        },
        "required": ["workflow_id"]
    },
    "description": "Analyze workflow for coexistence opportunities (friction removal focus)"
},
"get_workflow": {
    "handler": self._handle_get_workflow_soa,
    "input_schema": {
        "type": "object",
        "properties": {
            "workflow_id": {
                "type": "string",
                "description": "Workflow identifier"
            },
            "user_context": {
                "type": "object",
                "description": "Optional user context"
            }
        },
        "required": ["workflow_id"]
    },
    "description": "Get workflow data"
}
```

**Create SOA API handler methods** (following dual call pattern):
```python
async def _handle_analyze_coexistence_soa(
    self,
    intent: Optional[Intent] = None,
    context: Optional[ExecutionContext] = None,
    **kwargs
) -> Dict[str, Any]:
    """Handle analyze_coexistence SOA API (dual call pattern)."""
    if intent and context:
        return await self._handle_analyze_coexistence(intent, context)
    else:
        workflow_id = kwargs.get("workflow_id")
        reasoning_context = kwargs.get("reasoning_context", {})
        user_context = kwargs.get("user_context", {})
        tenant_id = user_context.get("tenant_id", "default")
        session_id = user_context.get("session_id", "default")
        
        from symphainy_platform.runtime.intent_model import IntentFactory
        intent_obj = IntentFactory.create_intent(
            intent_type="analyze_coexistence",
            tenant_id=tenant_id,
            session_id=session_id,
            parameters={
                "workflow_id": workflow_id,
                "reasoning_context": reasoning_context
            }
        )
        
        exec_context = ExecutionContext(
            execution_id="analyze_coexistence",
            intent=intent_obj,
            tenant_id=tenant_id,
            session_id=session_id
        )
        
        return await self._handle_analyze_coexistence(intent_obj, exec_context)

async def _handle_get_workflow_soa(
    self,
    intent: Optional[Intent] = None,
    context: Optional[ExecutionContext] = None,
    **kwargs
) -> Dict[str, Any]:
    """Handle get_workflow SOA API (dual call pattern)."""
    workflow_id = kwargs.get("workflow_id")
    user_context = kwargs.get("user_context", {})
    tenant_id = user_context.get("tenant_id", "default")
    
    # Get workflow from state or storage
    # This should use Public Works abstractions
    # For now, return workflow data structure
    return {
        "success": True,
        "workflow": {
            "workflow_id": workflow_id,
            # ... workflow data
        }
    }
```

**File**: `symphainy_platform/realms/outcomes/orchestrators/outcomes_orchestrator.py`

**Add to `_define_soa_api_handlers()`**:
```python
"create_blueprint": {
    "handler": self._handle_create_blueprint_soa,
    "input_schema": {
        "type": "object",
        "properties": {
            "workflow_id": {
                "type": "string",
                "description": "Workflow identifier"
            },
            "current_state_workflow_id": {
                "type": "string",
                "description": "Current state workflow identifier (optional)"
            },
            "reasoning_context": {
                "type": "object",
                "description": "Optional reasoning context from agent"
            },
            "user_context": {
                "type": "object",
                "description": "Optional user context"
            }
        },
        "required": ["workflow_id"]
    },
    "description": "Create coexistence blueprint (human-positive friction removal focus)"
},
"export_artifact": {
    "handler": self._handle_export_artifact_soa,
    "input_schema": {
        "type": "object",
        "properties": {
            "artifact_type": {
                "type": "string",
                "enum": ["blueprint", "poc", "roadmap"],
                "description": "Type of artifact to export"
            },
            "artifact_id": {
                "type": "string",
                "description": "Artifact identifier"
            },
            "format": {
                "type": "string",
                "enum": ["json", "yaml", "docx"],
                "description": "Export format",
                "default": "docx"
            },
            "user_context": {
                "type": "object",
                "description": "Optional user context"
            }
        },
        "required": ["artifact_type", "artifact_id"]
    },
    "description": "Export artifact in specified format"
}
```

**Create corresponding SOA API handler methods** (following dual call pattern)

### Step 4: Register AgentDefinitions

**File**: `symphainy_platform/civic_systems/agentic/agent_registry_bootstrap.py` (or create new bootstrap)

**Add registration**:
```python
from symphainy_platform.civic_systems.agentic.agent_definitions.coexistence_analysis_agent_definition import COEXISTENCE_ANALYSIS_AGENT_DEFINITION

async def bootstrap_agent_definitions(registry: AgentDefinitionRegistry):
    """Bootstrap all platform agent definitions."""
    definitions = [
        COEXISTENCE_ANALYSIS_AGENT_DEFINITION,
        BLUEPRINT_CREATION_AGENT_DEFINITION,
        # ... all others
    ]
    
    for definition in definitions:
        await registry.register_definition(definition)
```

### Step 5: Update Orchestrators to Initialize Agents with Definitions

**File**: `symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py`

**Update agent initialization**:
```python
# Get agent definition registry from context or public_works
agent_definition_registry = context.agent_definition_registry if hasattr(context, 'agent_definition_registry') else None

self.coexistence_analysis_agent = CoexistenceAnalysisAgent(
    agent_definition_id="coexistence_analysis_agent",
    agent_definition_registry=agent_definition_registry,
    public_works=public_works,
    mcp_client_manager=mcp_client_manager,  # From context
    telemetry_service=telemetry_service  # From context
)
```

---

## Testing Strategy

### Unit Tests
1. AgentDefinition validation
2. Agent initialization with definitions
3. MCP tool usage (mock)
4. Telemetry tracking

### Integration Tests
1. Agent → MCP Tool → Orchestrator SOA API → Service flow
2. Verify no direct service calls
3. Verify telemetry is recorded
4. Verify traceability

### End-to-End Tests
1. Full agent flow with AgentDefinition
2. Verify 4-layer model works
3. Verify determinism (same inputs → same outputs)

---

## Acceptance Criteria

### For Each Agent
- ✅ Has AgentDefinition (Layer 1)
- ✅ Loads definition from registry
- ✅ Uses AgentBase 4-layer model
- ✅ Uses `use_tool()` for ALL service access
- ✅ Uses `_call_llm()` for reasoning
- ✅ Has telemetry tracking
- ✅ Has traceability
- ✅ No direct service calls

### For Orchestrators
- ✅ Expose all needed SOA APIs
- ✅ SOA APIs are exposed as MCP tools
- ✅ Thin coordinators (not god objects)
- ✅ Select paths, don't do work

### For MCP Servers
- ✅ One MCP server per realm
- ✅ Expose orchestrator SOA APIs as tools
- ✅ No business logic in MCP servers
- ✅ Replaceable adapters

---

## Estimated Effort

**Phase 1 (AgentDefinitions)**: 5-7 hours
- Create 6-7 agent definitions (including BusinessAnalysisAgent)
- Register in registry

**Phase 2 (Create BusinessAnalysisAgent)**: 6-8 hours
- Create agent implementation
- Create agent definition
- Update InsightsOrchestrator to use agent
- **CRITICAL**: This is a missing capability

**Phase 3 (Refactor Agents)**: 6-8 hours
- Update all agent implementations
- Ensure 4-layer model usage

**Phase 4 (Verify MCP Tools)**: 4-6 hours
- Audit all agents
- Verify tool usage
- Remove direct calls

**Phase 5 (Telemetry)**: 2-3 hours
- Verify telemetry setup
- Add missing tracking

**Phase 6 (SOA APIs)**: 6-8 hours
- Add missing SOA APIs (including Insights: get_parsed_data, get_embeddings)
- Update orchestrators

**Phase 7 (Reframing)**: 2-4 hours
- Evaluate suggestions
- Implement good ones
- Document decisions

**Total**: 31-44 hours

---

## Risk Assessment

### High Risk
- **Breaking existing functionality**: Agents currently work but don't use AgentDefinition pattern
  - **Mitigation**: Implement incrementally, test thoroughly

### Medium Risk
- **MCP tool access pattern**: Need to verify all agents use tools correctly
  - **Mitigation**: Comprehensive audit, automated tests

### Low Risk
- **Architectural reframing**: Most suggestions are language/clarification
  - **Mitigation**: Careful evaluation, document decisions

---

## Next Steps

1. **Review Plan** - Confirm approach aligns with architecture
2. **Prioritize Phases** - Start with Phase 1 (AgentDefinitions)
3. **Implement Incrementally** - One agent at a time
4. **Test Thoroughly** - Verify pattern works end-to-end
5. **Document Decisions** - Especially for reframing evaluation

---

## Key Decisions Summary

### ✅ Decisions Made

1. **AgentDefinition Pattern**: ALL agents must use AgentDefinition (Layer 1: Platform DNA)
   - This is non-negotiable - it's the platform's agent identity system
   - Enables telemetry, traceability, governance

2. **MCP Tool Access Pattern**: Agents MUST use MCP tools, never direct service calls
   - Pattern: Agent → `use_tool()` → MCP Server → Orchestrator SOA API → Enabling Service
   - This is the only legal way agents can touch realm data

3. **Onboarding Agent Reasoning**: KEEP CURRENT APPROACH
   - Agent reasoning is valuable (strategic focus, pillar prioritization)
   - Just ensure validation by Smart City (already happening)
   - Document the validation step clearly

4. **Content Pillar Ephemeral Default**: IMPLEMENT
   - Aligns with Data Mash boundary
   - Make persistence explicit choice

5. **Orchestrator Thin Coordinator Pattern**: VERIFY
   - Already our pattern, just needs verification
   - Orchestrators select paths, services do work

### ⚠️ Decisions Pending Review

1. **Missing SOA APIs**: Need to add:
   - Journey: `analyze_coexistence`, `get_workflow`
   - Outcomes: `create_blueprint`, `export_artifact`
   - Content: `get_files`, `get_parsed_files`
   - Insights: `get_quality`, `get_analysis`

2. **Agent Initialization**: How to pass AgentDefinitionRegistry to agents?
   - Via ExecutionContext?
   - Via Public Works?
   - Via orchestrator initialization?

3. **Telemetry Service**: How to ensure all agents have telemetry?
   - Via ExecutionContext?
   - Via Public Works?
   - Via orchestrator initialization?

---

## Critical Path

**Must Complete First** (Blocking):
1. **Create BusinessAnalysisAgent** (CRITICAL - Missing capability)
2. Create AgentDefinitions for all new agents (including BusinessAnalysisAgent)
3. Add missing SOA APIs to orchestrators (especially Insights: get_parsed_data, get_embeddings)
4. Verify agents use MCP tools (not direct calls)

**Can Do in Parallel**:
4. Refactor agents to use AgentDefinition pattern
5. Implement good reframing suggestions
6. Orchestrator audit

**Can Do Later**:
7. Content pillar ephemeral default (UI change)
8. Language clarifications (documentation)

---

## Success Criteria

### Phase 1 Success (AgentDefinitions)
- ✅ All agents have AgentDefinition
- ✅ All definitions registered in registry
- ✅ Agents can load definitions

### Phase 2 Success (MCP Tools)
- ✅ All agents use `use_tool()` for service access
- ✅ No direct service calls in agents
- ✅ All needed SOA APIs exist

### Phase 3 Success (Architecture Alignment)
- ✅ Orchestrators are thin coordinators (verified)
- ✅ Agents reason, services execute (verified)
- ✅ MCP servers are controlled execution surfaces (verified)

### Phase 4 Success (Reframing)
- ✅ Content pillar defaults to ephemeral
- ✅ Insights queries semantic artifacts
- ✅ Language clarified (solutions as registrations)

---

## Risk Mitigation

### Risk: Breaking Existing Functionality
- **Mitigation**: Implement incrementally, test each agent separately
- **Rollback Plan**: Keep old agent implementations until new ones verified

### Risk: Missing SOA APIs Break Agent Calls
- **Mitigation**: Add SOA APIs first, then update agents
- **Verification**: Test MCP tool calls before agent refactoring

### Risk: AgentDefinition Pattern Not Fully Understood
- **Mitigation**: Review existing examples (journey_liaison_agent_definition.py)
- **Documentation**: Create agent definition template with examples

---

**Status:** Plan ready, awaiting approval to proceed

**Next Step**: Review plan, prioritize phases, begin implementation
