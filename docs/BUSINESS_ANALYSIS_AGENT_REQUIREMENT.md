# Business Analysis Agent - Critical Missing Capability

**Date:** January 2026  
**Status:** 🔴 **CRITICAL GAP IDENTIFIED**

---

## Executive Summary

**CRITICAL FINDING:** Business analysis (data interpretation) is currently implemented as a service (`DataAnalyzerService.interpret_data()`), but it **REQUIRES agentic reasoning**.

**Current State**: Service does basic interpretation (data type, semantic mapping)  
**Required State**: Agent reasons about data meaning and generates business interpretations

---

## The Problem

### Current Implementation

**File**: `symphainy_platform/realms/insights/enabling_services/data_analyzer_service.py`

**Current `interpret_data()` method**:
- Gets semantic embeddings
- Identifies data type (structured/unstructured)
- Builds semantic mapping
- **Does NOT reason about business meaning**

**What's Missing**:
- No reasoning about what the data represents in business terms
- No identification of data types like "aging report", "claim report", "collections data"
- No business context interpretation
- No insights like "many accounts are 90+ days past due" or "driver appears to be at fault"

### Required Capability

**Examples of What Business Analysis Should Do**:

1. **Aging Report Analysis**:
   ```
   "This looks like an aging report for collections data. 
   Many accounts are more than 90 days past due, indicating 
   potential collection issues."
   ```

2. **Claim Report Analysis**:
   ```
   "This looks like a claim report. Based on the data, 
   the driver appears to be at fault. The claim amount 
   is significant and may require investigation."
   ```

3. **Document Classification**:
   ```
   "This looks like a book about the Statue of Liberty. 
   The content discusses historical context, construction 
   details, and cultural significance."
   ```

**This Requires**:
- LLM reasoning about data meaning
- Context understanding
- Business domain knowledge
- Pattern recognition
- Inference generation

**This is INHERENTLY agentic** - it cannot be done by a pure data processing service.

---

## Solution: BusinessAnalysisAgent

### Agent Responsibilities

1. **Reason about data meaning** (LLM):
   - What does this data represent?
   - What business context does it fit?
   - What patterns or insights are present?

2. **Generate business interpretations**:
   - Data type in business terms (not just "structured/unstructured")
   - Key insights and observations
   - Business implications
   - Confidence level

3. **Use MCP tools** to access data:
   - `insights_get_parsed_data` - Get parsed file data
   - `insights_get_embeddings` - Get semantic embeddings
   - `insights_get_quality` - Get quality metrics (optional)

4. **Construct business analysis outcome**:
   - Structured interpretation with business context
   - Key insights
   - Recommendations (if applicable)

### Agent Pattern

```
BusinessAnalysisAgent
    ↓ (reason about data)
    ↓ (use MCP tools to get data)
    ↓ (LLM reasoning about meaning)
    ↓ (construct business interpretation)
    → Business Analysis Outcome
```

### Integration Point

**File**: `symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py`

**Current**:
```python
async def _handle_interpret_data(self, intent, context):
    # ❌ WRONG: Direct service call
    interpretation_result = await self.data_analyzer_service.interpret_data(...)
```

**Required**:
```python
async def _handle_interpret_data(self, intent, context):
    # ✅ CORRECT: Use BusinessAnalysisAgent
    agent_result = await self.business_analysis_agent.process_request({
        "type": "interpret_data",
        "parsed_file_id": parsed_file_id
    }, context)
    
    # Extract business interpretation from agent result
    interpretation_result = agent_result.get("artifact", {})
```

---

## Implementation Details

### AgentDefinition

**File**: `symphainy_platform/civic_systems/agentic/agent_definitions/business_analysis_agent_definition.py`

```python
BUSINESS_ANALYSIS_AGENT_DEFINITION = AgentDefinition(
    agent_id="business_analysis_agent",
    agent_type="specialized",
    constitution={
        "role": "Business Analysis Agent",
        "mission": "Reason about data meaning and generate business interpretations",
        "non_goals": [
            "Do not execute actions directly",
            "Do not persist client data",
            "Do not bypass data governance"
        ],
        "guardrails": [
            "All interpretations must be based on actual data",
            "Provide confidence levels for interpretations",
            "Clearly distinguish between observations and inferences",
            "Respect data privacy and governance"
        ],
        "authority": {
            "can_access": ["insights_realm", "content_realm"],
            "can_read": ["parsed_files", "embeddings", "quality_metrics"],
            "cannot_write": ["any_persistent_data"]
        }
    },
    capabilities=[
        "interpret_data_meaning",
        "identify_business_context",
        "generate_insights",
        "classify_data_types"
    ],
    permissions={
        "allowed_tools": [
            "insights_get_parsed_data",
            "insights_get_embeddings",
            "insights_get_quality",
            "insights_interpret_data"
        ],
        "allowed_mcp_servers": ["insights_mcp", "content_mcp"],
        "required_roles": []
    },
    collaboration_profile={
        "can_delegate_to": [],
        "can_be_invoked_by": ["guide_agent", "insights_liaison_agent", "insights_orchestrator"],
        "collaboration_style": "specialized"
    },
    version="1.0.0",
    created_by="platform"
)
```

### Agent Implementation

**File**: `symphainy_platform/realms/insights/agents/business_analysis_agent.py`

**Key Features**:
- Uses LLM to reason about data meaning
- Generates business interpretations
- Uses MCP tools for data access
- Constructs structured outcomes

**Example LLM Prompt**:
```
System: You are a business analyst expert at interpreting data 
and identifying what it represents in business terms.

User: Analyze this data:
- Columns: account_id, account_name, days_past_due, balance
- Sample values: Account A, 120 days, $5,000
- Data type: structured, 1000 rows

What does this data represent? What business insights can you provide?
```

**Expected Output**:
```json
{
  "data_type": "aging_report",
  "business_interpretation": "This appears to be an aging report for collections data. The data shows accounts with days past due and outstanding balances.",
  "key_insights": [
    "Many accounts are 90+ days past due",
    "Total outstanding balance is significant",
    "Collection efforts may be needed"
  ],
  "confidence": 0.92
}
```

---

## Required SOA APIs

### Insights Orchestrator

**Add to `_define_soa_api_handlers()`**:

1. **`get_parsed_data`**:
   ```python
   "get_parsed_data": {
       "handler": self._handle_get_parsed_data_soa,
       "input_schema": {
           "type": "object",
           "properties": {
               "parsed_file_id": {
                   "type": "string",
                   "description": "Parsed file identifier"
               }
           },
           "required": ["parsed_file_id"]
       },
       "description": "Get parsed file data"
   }
   ```

2. **`get_embeddings`**:
   ```python
   "get_embeddings": {
       "handler": self._handle_get_embeddings_soa,
       "input_schema": {
           "type": "object",
           "properties": {
               "parsed_file_id": {
                   "type": "string",
                   "description": "Parsed file identifier"
               }
           },
           "required": ["parsed_file_id"]
       },
       "description": "Get semantic embeddings for parsed file"
   }
   ```

3. **`interpret_data`** (update to use agent):
   - Keep existing SOA API
   - Update handler to use BusinessAnalysisAgent instead of direct service call

---

## Integration with Existing Services

### DataAnalyzerService Role

**After BusinessAnalysisAgent is created**:
- `DataAnalyzerService.interpret_data()` should become a **data retrieval service**
- It should get parsed data and semantic embeddings
- It should NOT do business interpretation (that's the agent's job)

**OR**:
- Keep `DataAnalyzerService.interpret_data()` for basic interpretation
- `BusinessAnalysisAgent` uses it as a tool via MCP for data retrieval
- Agent adds the reasoning layer on top

### InsightsLiaisonAgent Role

**Current**: Handles deep dive analysis, answers questions  
**With BusinessAnalysisAgent**: 
- `BusinessAnalysisAgent` does initial business interpretation
- `InsightsLiaisonAgent` handles follow-up questions and deep dives
- They collaborate: BusinessAnalysisAgent provides context, InsightsLiaisonAgent explores

---

## Testing Strategy

### Unit Tests
- Agent reasoning logic
- Business interpretation generation
- MCP tool usage

### Integration Tests
- Agent → MCP Tool → Orchestrator SOA API → Service flow
- Verify business interpretations are generated
- Verify confidence levels are reasonable

### End-to-End Tests
- Upload file → Parse → Business Analysis → Verify interpretation
- Test with different data types (aging report, claim report, etc.)
- Verify interpretations are accurate and useful

---

## Acceptance Criteria

- ✅ BusinessAnalysisAgent exists with AgentDefinition
- ✅ Agent uses LLM to reason about data meaning
- ✅ Agent generates business interpretations (data type, insights, context)
- ✅ Agent uses MCP tools for data access (no direct calls)
- ✅ InsightsOrchestrator uses agent (not direct service call)
- ✅ Agent can identify common data types (aging reports, claim reports, etc.)
- ✅ Agent provides confidence levels
- ✅ Agent distinguishes observations from inferences

---

## Priority

**CRITICAL** - This is a missing capability that's essential for the Insights pillar to demonstrate value.

Without this agent, the platform cannot show that it can "interpret and reason about data" - which is a core value proposition.

---

**Status:** Critical gap identified, implementation plan ready
