# Agentic Forward Pattern - Holistic Platform Audit

**Date:** January 2026  
**Status:** 🔍 **AUDIT IN PROGRESS**

---

## Executive Summary

**CRITICAL FINDING:** The platform is missing agentic forward patterns for key capabilities. Services are being called directly by orchestrators, but according to the architecture guide and lessons learned, **agents must reason and construct outcomes using enabling services as tools**.

**Current State:** Services → Services (direct calls)  
**Required State:** Orchestrator → Agent → Tools (MCP) → Enabling Services → Outcomes

---

## Architecture Principle

From `Architecture_Guide_Final.md`:

> **Agents:**
> - Express intent
> - Reason
> - Select tools
> - Request realm actions
>
> **Agents do NOT:**
> - Fetch files
> - Read storage
> - Bypass policy
> - Manage lifecycle

**Pattern:** Agent → Intent → Runtime → Metadata → Policy → Authorization → Realm → Data

---

## Current State Audit

### ✅ Agents That Exist

1. **InsightsLiaisonAgent** (`realms/insights/agents/insights_liaison_agent.py`)
   - ✅ Extends `AgentBase`
   - ✅ Used by `UnstructuredAnalysisService` for deep dive
   - ✅ Uses `_call_llm()` for governed LLM access
   - ✅ Uses `SemanticDataAbstraction` and `StatelessEmbeddingAgent`

2. **JourneyLiaisonAgent** (`realms/journey/agents/journey_liaison_agent.py`)
   - ❌ **NOT extending AgentBase** (needs update)
   - ✅ Used for SOP generation via chat
   - ⚠️ May not follow agentic forward pattern

3. **WorkflowOptimizationSpecialist** (`civic_systems/agentic/agents/workflow_optimization_specialist.py`)
   - ✅ Extends `WorkflowOptimizationAgentBase`
   - ⚠️ **NOT being used by orchestrators** (exists but not integrated)

4. **ProposalAgentBase** (`civic_systems/agentic/agents/proposal_agent.py`)
   - ✅ Base class for roadmap/POC proposals
   - ⚠️ **NOT being used by orchestrators** (exists but not integrated)

5. **RoadmapProposalAgent** (`civic_systems/agentic/agents/roadmap_proposal_agent.py`)
   - ✅ Extends `ProposalAgentBase`
   - ⚠️ **NOT being used by orchestrators** (exists but not integrated)

### ❌ Missing Agents (Critical Gaps)

#### Content Realm
- ❌ **ContentLiaisonAgent** - Missing
  - Should handle: File analysis, embedding strategy, data mash flow reasoning
  - Current: Orchestrator calls services directly

#### Journey Realm
- ❌ **CoexistenceAnalysisAgent** - Missing
  - Should handle: Reasoning about friction points, human-positive optimization
  - Current: `CoexistenceAnalysisService` does rule-based analysis (no reasoning)
  
- ❌ **BlueprintCreationAgent** - Missing
  - Should handle: Reasoning about workflow transformation, responsibility matrix design
  - Current: `CoexistenceAnalysisService.create_blueprint()` does template-based generation

#### Outcomes Realm
- ❌ **OutcomesSynthesisAgent** - Missing
  - Should handle: Reasoning about pillar synthesis, summary visualization design
  - Current: `ReportGeneratorService` does data aggregation (no reasoning)

- ❌ **RoadmapGenerationAgent** - Missing
  - Should handle: Reasoning about strategic planning, phase design
  - Current: `RoadmapGenerationService` has placeholder comment "Use agents for reasoning"

- ❌ **POCGenerationAgent** - Missing
  - Should handle: Reasoning about POC scope, objectives, timeline
  - Current: `POCGenerationService` has placeholder comment "Use agents for reasoning"

#### Insights Realm
- ✅ **InsightsLiaisonAgent** - Exists and used
  - Used by `UnstructuredAnalysisService` for deep dive

---

## Current Anti-Patterns

### 1. Direct Service Calls (No Agent Reasoning)

**Journey Orchestrator:**
```python
# ❌ ANTI-PATTERN: Direct service call
analysis_result = await self.coexistence_analysis_service.analyze_coexistence(...)
```

**Should be:**
```python
# ✅ CORRECT: Agent reasons, uses service as tool
agent_result = await self.coexistence_agent.analyze_coexistence(
    workflow_id=workflow_id,
    context=context
)
# Agent internally uses CoexistenceAnalysisService via MCP tools
```

### 2. Template-Based Generation (No Reasoning)

**CoexistenceAnalysisService.create_blueprint():**
```python
# ❌ ANTI-PATTERN: Template-based, no reasoning
phases = [
    {"phase": 1, "name": "Foundation Setup", ...},  # Hardcoded
    {"phase": 2, "name": "Parallel Operation", ...},  # Hardcoded
]
```

**Should be:**
```python
# ✅ CORRECT: Agent reasons about transition
agent_result = await self.blueprint_agent.create_blueprint(
    workflow_id=workflow_id,
    coexistence_analysis=analysis,
    context=context
)
# Agent uses LLM to reason about phases, roadmap, responsibility matrix
```

### 3. Data Aggregation (No Reasoning)

**ReportGeneratorService.generate_realm_summary_visuals():**
```python
# ❌ ANTI-PATTERN: Data aggregation, no reasoning
content_visual = {
    "metrics": {...},  # Just aggregating numbers
    "tutorial": {...}  # Template-based
}
```

**Should be:**
```python
# ✅ CORRECT: Agent reasons about visualization design
agent_result = await self.outcomes_synthesis_agent.generate_summary_visuals(
    content_summary=content_summary,
    insights_summary=insights_summary,
    journey_summary=journey_summary,
    context=context
)
# Agent uses LLM to reason about what to show, how to explain it
```

---

## Required Agentic Forward Pattern

### Pattern Flow

```
User Intent
    ↓
Orchestrator.handle_intent()
    ↓
Agent.process_request()  ← AGENT REASONS HERE
    ↓
Agent uses Tools (MCP) → Enabling Services
    ↓
Agent constructs Outcome (using LLM reasoning)
    ↓
Orchestrator returns Result
```

### Example: Coexistence Analysis

**Current (Wrong):**
```
JourneyOrchestrator._handle_analyze_coexistence()
    → CoexistenceAnalysisService.analyze_coexistence()
        → Rule-based keyword matching
        → Return structured data
```

**Required (Correct):**
```
JourneyOrchestrator._handle_analyze_coexistence()
    → CoexistenceAnalysisAgent.process_request()
        → Agent reasons about workflow (LLM)
        → Agent uses MCP tool: "journey_analyze_coexistence"
            → CoexistenceAnalysisService.analyze_coexistence()
        → Agent reasons about friction points (LLM)
        → Agent constructs human-positive recommendations
        → Return structured outcome
```

---

## Missing Agents - Detailed Analysis

### 1. CoexistenceAnalysisAgent (Journey Realm)

**Purpose:** Reason about workflow friction and human-positive optimization

**Current Gap:**
- `CoexistenceAnalysisService.analyze_coexistence()` uses keyword matching
- No reasoning about task complexity, human value, friction types
- No LLM-based analysis of workflow structure

**Required Capabilities:**
- Reason about workflow tasks and their characteristics
- Identify friction points (not just keywords)
- Understand human value in each task
- Generate human-positive recommendations
- Use human-positive messaging (friction removal, not automation)

**Tools Needed:**
- `journey_analyze_coexistence` (MCP tool → CoexistenceAnalysisService)
- `journey_get_workflow` (MCP tool → get workflow data)
- LLM for reasoning

**Implementation:**
```python
class CoexistenceAnalysisAgent(AgentBase):
    async def process_request(self, request, context):
        # 1. Get workflow via MCP tool
        workflow = await self.use_tool("journey_get_workflow", {...}, context)
        
        # 2. Reason about workflow (LLM)
        reasoning = await self._call_llm(
            system_message="You analyze workflows to identify friction points...",
            user_message=f"Analyze this workflow: {workflow}",
            context=context
        )
        
        # 3. Use service as tool for structured analysis
        analysis = await self.use_tool("journey_analyze_coexistence", {
            "workflow_id": workflow_id
        }, context)
        
        # 4. Reason about friction removal opportunities (LLM)
        friction_analysis = await self._call_llm(
            system_message="You identify friction points and human value...",
            user_message=f"Analyze friction: {analysis}",
            context=context
        )
        
        # 5. Construct outcome
        return {
            "friction_points": friction_analysis.friction_points,
            "human_focus_areas": friction_analysis.human_focus,
            "recommendations": friction_analysis.recommendations
        }
```

### 2. BlueprintCreationAgent (Outcomes Realm)

**Purpose:** Reason about workflow transformation and blueprint design

**Current Gap:**
- `CoexistenceAnalysisService.create_blueprint()` uses templates
- Hardcoded phases, responsibility matrix structure
- No reasoning about transition complexity, dependencies

**Required Capabilities:**
- Reason about current vs. optimized state
- Design transition roadmap based on complexity
- Generate responsibility matrix with human-positive messaging
- Create workflow charts with proper visualization
- Use LLM to reason about integration requirements

**Tools Needed:**
- `outcomes_create_blueprint` (MCP tool → CoexistenceAnalysisService)
- `journey_get_workflow` (MCP tool)
- `visual_generate_workflow_chart` (MCP tool)
- LLM for reasoning

### 3. OutcomesSynthesisAgent (Outcomes Realm)

**Purpose:** Reason about pillar synthesis and visualization design

**Current Gap:**
- `ReportGeneratorService.generate_realm_summary_visuals()` aggregates data
- Template-based tutorial content
- No reasoning about what to show, how to explain

**Required Capabilities:**
- Reason about pillar outputs and their relationships
- Design tutorial content (explain Data Mash flow)
- Generate realm-specific visualizations
- Use LLM to create educational content

**Tools Needed:**
- `outcomes_synthesize` (MCP tool → ReportGeneratorService)
- `content_get_files` (MCP tool)
- `insights_get_quality` (MCP tool)
- `journey_get_workflows` (MCP tool)
- LLM for reasoning

### 4. RoadmapGenerationAgent (Outcomes Realm)

**Purpose:** Reason about strategic planning and phase design

**Current Gap:**
- `RoadmapGenerationService.generate_roadmap()` has placeholder
- Comment says "Use agents for reasoning" but not implemented

**Required Capabilities:**
- Reason about goals and constraints
- Design strategic phases
- Generate timeline and milestones
- Use LLM for strategic planning

**Tools Needed:**
- `outcomes_generate_roadmap` (MCP tool → RoadmapGenerationService)
- LLM for reasoning

### 5. POCGenerationAgent (Outcomes Realm)

**Purpose:** Reason about POC scope, objectives, timeline

**Current Gap:**
- `POCGenerationService.create_poc()` has placeholder
- Comment says "Use agents for reasoning" but not implemented

**Required Capabilities:**
- Reason about POC requirements
- Design objectives and scope
- Generate timeline and resources
- Use LLM for proposal generation

**Tools Needed:**
- `outcomes_create_poc` (MCP tool → POCGenerationService)
- LLM for reasoning

### 6. ContentLiaisonAgent (Content Realm)

**Purpose:** Reason about file analysis and embedding strategy

**Current Gap:**
- Orchestrator calls services directly
- No reasoning about file types, parsing strategy, embedding approach

**Required Capabilities:**
- Reason about file characteristics
- Recommend parsing strategy
- Design embedding approach
- Explain Data Mash flow

**Tools Needed:**
- `content_ingest_file` (MCP tool)
- `content_parse_file` (MCP tool)
- `content_create_embeddings` (MCP tool)
- LLM for reasoning

---

## Implementation Plan

### Phase 1: Create Missing Agents (Priority Order)

1. **CoexistenceAnalysisAgent** (Journey Realm) - CRITICAL
   - **Why:** Coexistence analysis requires reasoning about friction and human value
   - **Impact:** Blueprint creation depends on this
   - **Time:** 4-6 hours

2. **BlueprintCreationAgent** (Outcomes Realm) - CRITICAL
   - **Why:** Blueprint creation requires reasoning about transformation
   - **Impact:** Core outcome artifact
   - **Time:** 4-6 hours

3. **OutcomesSynthesisAgent** (Outcomes Realm) - HIGH
   - **Why:** Summary visualization requires reasoning about what to show
   - **Impact:** User experience
   - **Time:** 3-4 hours

4. **RoadmapGenerationAgent** (Outcomes Realm) - HIGH
   - **Why:** Strategic planning requires reasoning
   - **Impact:** Core outcome artifact
   - **Time:** 3-4 hours

5. **POCGenerationAgent** (Outcomes Realm) - HIGH
   - **Why:** POC proposals require reasoning
   - **Impact:** Core outcome artifact
   - **Time:** 3-4 hours

6. **ContentLiaisonAgent** (Content Realm) - MEDIUM
   - **Why:** File analysis could benefit from reasoning
   - **Impact:** Enhanced user experience
   - **Time:** 2-3 hours

### Phase 2: Update Orchestrators to Use Agents

**Pattern:**
```python
# ❌ OLD: Direct service call
result = await self.service.method(...)

# ✅ NEW: Agent forward pattern
result = await self.agent.process_request({
    "type": "analyze_coexistence",
    "workflow_id": workflow_id,
    ...
}, context)
```

**Files to Update:**
1. `journey_orchestrator.py` - Use `CoexistenceAnalysisAgent`
2. `outcomes_orchestrator.py` - Use `BlueprintCreationAgent`, `OutcomesSynthesisAgent`, `RoadmapGenerationAgent`, `POCGenerationAgent`
3. `content_orchestrator.py` - Use `ContentLiaisonAgent` (optional)

### Phase 3: Update Services to be Tool-Only

**Pattern:**
- Services become pure data processing (current state is good)
- Services exposed as MCP tools
- Agents call services via MCP tools (not direct calls)

**Files to Update:**
- All enabling services should be accessible via MCP tools
- Verify MCP servers expose all needed tools

### Phase 4: Update JourneyLiaisonAgent

**Current:** Doesn't extend `AgentBase`  
**Required:** Extend `AgentBase`, use MCP tools

---

## Agent Implementation Template

```python
"""
[Agent Name] - [Purpose]

Agent for [capability] using agentic forward pattern.

WHAT (Agent Role): I [agent purpose]
HOW (Agent Implementation): I reason about [domain], use tools to [actions]
"""

from symphainy_platform.civic_systems.agentic.agent_base import AgentBase
from symphainy_platform.runtime.execution_context import ExecutionContext

class [AgentName](AgentBase):
    """
    [Agent Name] - [Purpose description].
    
    Uses agentic forward pattern:
    1. Reason about request (LLM)
    2. Use MCP tools to call enabling services
    3. Reason about results (LLM)
    4. Construct outcome
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        super().__init__(
            agent_id="[agent_id]",
            agent_type="[agent_type]",
            capabilities=["[capability1]", "[capability2]"],
            public_works=public_works
        )
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process request using agentic forward pattern.
        
        Args:
            request: Request dictionary with type and parameters
            context: Execution context
            
        Returns:
            Dict with outcome artifacts
        """
        request_type = request.get("type")
        
        if request_type == "[operation]":
            return await self._handle_[operation](request, context)
        else:
            raise ValueError(f"Unknown request type: {request_type}")
    
    async def _handle_[operation](
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle [operation] using agentic forward pattern.
        
        Pattern:
        1. Get data via MCP tools
        2. Reason about data (LLM)
        3. Use services as tools via MCP
        4. Reason about results (LLM)
        5. Construct outcome
        """
        # 1. Get input data via MCP tool
        input_data = await self.use_tool(
            "[realm]_[get_data]",
            {"[param]": request.get("[param]")},
            context
        )
        
        # 2. Reason about input (LLM)
        reasoning = await self._call_llm(
            system_message=self._get_system_message(),
            user_message=f"Analyze: {input_data}",
            context=context
        )
        
        # 3. Use enabling service as tool via MCP
        service_result = await self.use_tool(
            "[realm]_[service_operation]",
            {
                "[param]": request.get("[param]"),
                "reasoning_context": reasoning
            },
            context
        )
        
        # 4. Reason about service result (LLM)
        outcome_reasoning = await self._call_llm(
            system_message=self._get_outcome_system_message(),
            user_message=f"Based on analysis: {service_result}, create outcome...",
            context=context
        )
        
        # 5. Construct and return outcome
        return {
            "artifact_type": "[artifact_type]",
            "artifact": outcome_reasoning.artifact,
            "reasoning": outcome_reasoning.reasoning,
            "confidence": outcome_reasoning.confidence
        }
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return "[Agent description]"
    
    def _get_system_message(self) -> str:
        """Get system message for reasoning."""
        return """
        You are the [Agent Name]. Your role is to [purpose].
        
        Key principles:
        - [Principle 1]
        - [Principle 2]
        
        Always use human-positive messaging: [messaging guidance]
        """
```

---

## MCP Tool Requirements

### Journey Realm MCP Server
- ✅ `journey_analyze_coexistence` - Expose CoexistenceAnalysisService
- ✅ `journey_create_blueprint` - Expose blueprint creation
- ✅ `journey_get_workflow` - Get workflow data

### Outcomes Realm MCP Server
- ✅ `outcomes_synthesize` - Expose synthesis
- ✅ `outcomes_generate_roadmap` - Expose roadmap generation
- ✅ `outcomes_create_poc` - Expose POC creation
- ✅ `outcomes_create_blueprint` - Expose blueprint creation
- ✅ `outcomes_export_artifact` - Expose export

### Content Realm MCP Server
- ✅ `content_get_files` - Get file data
- ✅ `content_get_parsed_files` - Get parsed file data
- ✅ `content_get_embeddings` - Get embedding data

### Insights Realm MCP Server
- ✅ `insights_get_quality` - Get quality data
- ✅ `insights_get_analysis` - Get analysis data

---

## Testing Strategy

### Agent Testing
1. **Unit Tests:** Agent reasoning logic
2. **Integration Tests:** Agent → MCP Tool → Service flow
3. **End-to-End Tests:** Orchestrator → Agent → Outcome

### Pattern Validation
1. Verify agents use MCP tools (not direct service calls)
2. Verify agents use LLM for reasoning
3. Verify agents construct outcomes (not just pass through)
4. Verify human-positive messaging in agent outputs

---

## Estimated Effort

### Phase 1: Create Agents (20-26 hours)
- CoexistenceAnalysisAgent: 4-6 hours
- BlueprintCreationAgent: 4-6 hours
- OutcomesSynthesisAgent: 3-4 hours
- RoadmapGenerationAgent: 3-4 hours
- POCGenerationAgent: 3-4 hours
- ContentLiaisonAgent: 2-3 hours

### Phase 2: Update Orchestrators (6-8 hours)
- JourneyOrchestrator: 2-3 hours
- OutcomesOrchestrator: 3-4 hours
- ContentOrchestrator: 1-2 hours

### Phase 3: Verify MCP Tools (2-3 hours)
- Verify all tools exposed
- Test tool access from agents

### Phase 4: Update JourneyLiaisonAgent (2-3 hours)
- Extend AgentBase
- Use MCP tools

### Phase 5: Testing (8-10 hours)
- Unit tests
- Integration tests
- End-to-end tests

**Total:** 38-50 hours

---

## Next Steps

1. **Review and Approve Plan** - Confirm approach aligns with architecture
2. **Prioritize Agents** - Start with CoexistenceAnalysisAgent (critical path)
3. **Implement Agents** - Follow template, ensure human-positive messaging
4. **Update Orchestrators** - Replace direct service calls with agent calls
5. **Test Thoroughly** - Verify agentic forward pattern works end-to-end

---

**Status:** Audit complete, implementation plan ready
