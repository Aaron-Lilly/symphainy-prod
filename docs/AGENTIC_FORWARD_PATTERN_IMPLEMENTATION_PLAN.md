# Agentic Forward Pattern - Implementation Plan

**Date:** January 2026  
**Status:** 📋 **IMPLEMENTATION PLAN READY**

---

## Executive Summary

**CRITICAL:** The platform is missing agentic forward patterns. Services are being called directly, but agents must reason and construct outcomes.

**Required Pattern:**
```
Orchestrator → Agent (reasons) → MCP Tools → Enabling Services → Outcomes
```

**Current Anti-Pattern:**
```
Orchestrator → Enabling Service (direct call, no reasoning)
```

---

## Missing Agents - Complete List

### Journey Realm
1. ❌ **CoexistenceAnalysisAgent** - CRITICAL
2. ✅ JourneyLiaisonAgent - EXISTS but needs update (extend AgentBase)

### Outcomes Realm
3. ❌ **BlueprintCreationAgent** - CRITICAL
4. ❌ **OutcomesSynthesisAgent** - HIGH
5. ❌ **RoadmapGenerationAgent** - HIGH
6. ❌ **POCGenerationAgent** - HIGH

### Content Realm
7. ❌ **ContentLiaisonAgent** - MEDIUM

---

## Implementation Priority

### Phase 1: Critical Path (Coexistence & Blueprint)
1. **CoexistenceAnalysisAgent** (Journey Realm)
2. **BlueprintCreationAgent** (Outcomes Realm)

**Why:** These are the core capabilities that require reasoning about friction removal and human-positive optimization.

### Phase 2: Outcomes Synthesis
3. **OutcomesSynthesisAgent** (Outcomes Realm)
4. **RoadmapGenerationAgent** (Outcomes Realm)
5. **POCGenerationAgent** (Outcomes Realm)

**Why:** These create the main outcome artifacts and require strategic reasoning.

### Phase 3: Content Enhancement
6. **ContentLiaisonAgent** (Content Realm)

**Why:** Enhances user experience but not critical path.

### Phase 4: Update Existing
7. **JourneyLiaisonAgent** - Update to extend AgentBase

---

## Agent Implementation Details

### 1. CoexistenceAnalysisAgent (Journey Realm)

**File:** `symphainy_platform/realms/journey/agents/coexistence_analysis_agent.py`

**Purpose:** Reason about workflow friction and human-positive optimization

**Capabilities:**
- Analyze workflows for friction points
- Identify human value in tasks
- Generate human-positive recommendations
- Use human-positive messaging (friction removal focus)

**Tools:**
- `journey_get_workflow` - Get workflow data
- `journey_analyze_coexistence` - Use CoexistenceAnalysisService as tool

**LLM Reasoning:**
- Analyze workflow structure and task characteristics
- Identify friction types (repetitive, manual, error-prone)
- Understand human value (decision-making, judgment, strategic)
- Generate recommendations with human-positive messaging

**Integration:**
- JourneyOrchestrator._handle_analyze_coexistence() → Agent
- Agent uses MCP tools to call services
- Agent constructs outcome with reasoning

### 2. BlueprintCreationAgent (Outcomes Realm)

**File:** `symphainy_platform/realms/outcomes/agents/blueprint_creation_agent.py`

**Purpose:** Reason about workflow transformation and blueprint design

**Capabilities:**
- Design coexistence workflows
- Create transition roadmaps
- Generate responsibility matrices
- Design workflow visualizations

**Tools:**
- `outcomes_create_blueprint` - Use CoexistenceAnalysisService as tool
- `journey_get_workflow` - Get workflow data
- `visual_generate_workflow_chart` - Generate charts

**LLM Reasoning:**
- Reason about current vs. optimized state
- Design phases based on complexity (not templates)
- Generate responsibility matrix with human-positive messaging
- Create educational content for blueprint sections

**Integration:**
- OutcomesOrchestrator._handle_create_blueprint() → Agent
- Agent uses MCP tools
- Agent constructs blueprint with reasoning

### 3. OutcomesSynthesisAgent (Outcomes Realm)

**File:** `symphainy_platform/realms/outcomes/agents/outcomes_synthesis_agent.py`

**Purpose:** Reason about pillar synthesis and visualization design

**Capabilities:**
- Synthesize pillar outputs
- Design tutorial content (Data Mash flow)
- Generate realm-specific visualizations
- Create educational explanations

**Tools:**
- `outcomes_synthesize` - Use ReportGeneratorService as tool
- `content_get_files` - Get file data
- `insights_get_quality` - Get quality data
- `journey_get_workflows` - Get workflow data

**LLM Reasoning:**
- Understand relationships between pillars
- Design tutorial content (explain Data Mash stages)
- Generate educational "What happens?", "Why it matters?" content
- Create visual data structures

**Integration:**
- OutcomesOrchestrator._handle_synthesize_outcome() → Agent
- Agent constructs synthesis with tutorial content

### 4. RoadmapGenerationAgent (Outcomes Realm)

**File:** `symphainy_platform/realms/outcomes/agents/roadmap_generation_agent.py`

**Purpose:** Reason about strategic planning and phase design

**Capabilities:**
- Analyze goals and constraints
- Design strategic phases
- Generate timeline and milestones
- Create strategic recommendations

**Tools:**
- `outcomes_generate_roadmap` - Use RoadmapGenerationService as tool

**LLM Reasoning:**
- Understand goals and business context
- Design phases based on dependencies and complexity
- Generate realistic timelines
- Create strategic recommendations

**Integration:**
- OutcomesOrchestrator._handle_generate_roadmap() → Agent

### 5. POCGenerationAgent (Outcomes Realm)

**File:** `symphainy_platform/realms/outcomes/agents/poc_generation_agent.py`

**Purpose:** Reason about POC scope, objectives, timeline

**Capabilities:**
- Analyze POC requirements
- Design objectives and scope
- Generate timeline and resources
- Create proposal content

**Tools:**
- `outcomes_create_poc` - Use POCGenerationService as tool

**LLM Reasoning:**
- Understand synthesis context
- Design POC scope based on analysis
- Generate realistic objectives and timeline
- Create compelling proposal content

**Integration:**
- OutcomesOrchestrator._handle_create_poc() → Agent

### 6. ContentLiaisonAgent (Content Realm)

**File:** `symphainy_platform/realms/content/agents/content_liaison_agent.py`

**Purpose:** Reason about file analysis and embedding strategy

**Capabilities:**
- Analyze file characteristics
- Recommend parsing strategy
- Design embedding approach
- Explain Data Mash flow

**Tools:**
- `content_get_files` - Get file data
- `content_parse_file` - Parse files
- `content_create_embeddings` - Create embeddings

**LLM Reasoning:**
- Understand file types and structure
- Recommend optimal parsing approach
- Design embedding strategy
- Create educational content

**Integration:**
- ContentOrchestrator → Agent (optional enhancement)

---

## Implementation Steps

### Step 1: Create CoexistenceAnalysisAgent

**File:** `symphainy_platform/realms/journey/agents/coexistence_analysis_agent.py`

**Key Features:**
- Extends `AgentBase`
- Uses `_call_llm()` for reasoning
- Uses `use_tool()` for MCP tool calls
- Human-positive messaging in all outputs
- Friction removal focus (not automation)

**System Message:**
```
You are the Coexistence Analysis Agent. Your role is to analyze workflows 
and identify friction points that can be removed with AI assistance, enabling 
humans to focus on high-value work.

Key principles:
- AI removes friction, humans focus on high-value work
- Never suggest replacing humans - suggest removing friction
- Emphasize human value: decision-making, judgment, strategic analysis
- Identify repetitive tasks that create friction
- Recommend AI assistance for friction removal, not automation for replacement

Always use human-positive messaging:
- "Remove friction from X" not "Automate X"
- "Enable human focus on Y" not "Replace human with AI"
- "AI assistance" not "AI automation"
```

### Step 2: Create BlueprintCreationAgent

**File:** `symphainy_platform/realms/outcomes/agents/blueprint_creation_agent.py`

**Key Features:**
- Extends `AgentBase`
- Reasons about workflow transformation
- Designs phases based on complexity (not templates)
- Generates human-positive responsibility matrix
- Creates educational blueprint sections

**System Message:**
```
You are the Blueprint Creation Agent. Your role is to design coexistence 
blueprints that show how AI removes friction, enabling humans to focus on 
high-value work.

Key principles:
- Design transition roadmaps based on actual complexity
- Create phases that make sense for the specific workflow
- Generate responsibility matrices emphasizing human value
- Use human-positive messaging throughout
- Explain how AI assistance enables human focus areas
```

### Step 3: Create OutcomesSynthesisAgent

**File:** `symphainy_platform/realms/outcomes/agents/outcomes_synthesis_agent.py`

**Key Features:**
- Extends `AgentBase`
- Reasons about pillar relationships
- Creates tutorial content (Data Mash stages)
- Generates educational explanations
- Designs visual data structures

**System Message:**
```
You are the Outcomes Synthesis Agent. Your role is to synthesize outputs 
from all pillars and create educational visualizations.

Key principles:
- Explain Data Mash flow in plain language
- Create tutorial content: "What happens?", "Why it matters?", "Think of it like..."
- Design visualizations that help users understand
- Use real data examples when possible
```

### Step 4: Create RoadmapGenerationAgent

**File:** `symphainy_platform/realms/outcomes/agents/roadmap_generation_agent.py`

**Key Features:**
- Extends `AgentBase`
- Reasons about strategic planning
- Designs phases based on dependencies
- Generates realistic timelines
- Creates strategic recommendations

### Step 5: Create POCGenerationAgent

**File:** `symphainy_platform/realms/outcomes/agents/poc_generation_agent.py`

**Key Features:**
- Extends `AgentBase`
- Reasons about POC requirements
- Designs scope based on analysis
- Generates realistic objectives and timeline
- Creates compelling proposal content

### Step 6: Update Orchestrators

**Pattern:**
```python
# ❌ OLD
result = await self.service.method(...)

# ✅ NEW
result = await self.agent.process_request({
    "type": "analyze_coexistence",
    "workflow_id": workflow_id,
    ...
}, context)
```

**Files:**
- `journey_orchestrator.py` - Use CoexistenceAnalysisAgent
- `outcomes_orchestrator.py` - Use BlueprintCreationAgent, OutcomesSynthesisAgent, RoadmapGenerationAgent, POCGenerationAgent

### Step 7: Update JourneyLiaisonAgent

**File:** `symphainy_platform/realms/journey/agents/journey_liaison_agent.py`

**Changes:**
- Extend `AgentBase` instead of standalone class
- Use MCP tools for service access
- Use `_call_llm()` for reasoning

---

## Agent Implementation Template

See `AGENTIC_FORWARD_PATTERN_AUDIT.md` for full template.

---

## Testing Strategy

### Unit Tests
- Agent reasoning logic
- Tool usage patterns
- Human-positive messaging validation

### Integration Tests
- Agent → MCP Tool → Service flow
- Verify agents use tools (not direct calls)
- Verify LLM reasoning is used

### End-to-End Tests
- Orchestrator → Agent → Outcome
- Verify outcomes have reasoning
- Verify human-positive messaging

---

## Estimated Effort

**Phase 1 (Critical):** 8-12 hours
- CoexistenceAnalysisAgent: 4-6 hours
- BlueprintCreationAgent: 4-6 hours

**Phase 2 (Outcomes):** 9-12 hours
- OutcomesSynthesisAgent: 3-4 hours
- RoadmapGenerationAgent: 3-4 hours
- POCGenerationAgent: 3-4 hours

**Phase 3 (Content):** 2-3 hours
- ContentLiaisonAgent: 2-3 hours

**Phase 4 (Updates):** 4-6 hours
- Update orchestrators: 2-3 hours
- Update JourneyLiaisonAgent: 2-3 hours

**Phase 5 (Testing):** 8-10 hours
- Unit tests: 3-4 hours
- Integration tests: 3-4 hours
- End-to-end tests: 2-3 hours

**Total:** 31-43 hours

---

## Acceptance Criteria

### For Each Agent
- ✅ Extends `AgentBase`
- ✅ Uses `_call_llm()` for reasoning
- ✅ Uses `use_tool()` for MCP tool calls (no direct service calls)
- ✅ Constructs outcomes (not just passes through)
- ✅ Uses human-positive messaging
- ✅ No placeholders, mocks, or hardcoded cheats

### For Orchestrators
- ✅ Call agents (not services directly)
- ✅ Agents handle reasoning
- ✅ Services are tools only

### For Services
- ✅ Remain pure data processing
- ✅ Exposed as MCP tools
- ✅ No LLM calls in services

---

## Next Steps

1. **Review Plan** - Confirm approach
2. **Start with CoexistenceAnalysisAgent** - Critical path
3. **Implement agents one by one** - Follow template
4. **Update orchestrators** - Replace direct calls
5. **Test thoroughly** - Verify pattern works

---

**Status:** Implementation plan ready, awaiting approval to proceed
