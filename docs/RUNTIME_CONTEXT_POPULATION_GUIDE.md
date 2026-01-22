# Runtime Context Population Guide

**Date:** January 2026  
**Purpose:** Document how to populate AgentRuntimeContext from landing page and session state

---

## Executive Summary

**The infrastructure exists, but we need to ensure the landing page populates session state correctly.**

**Status:**
- ✅ Session state storage/retrieval exists (`StateSurface.store_session_state()`)
- ✅ Runtime context extraction from session state exists (just implemented)
- ⚠️ Landing page needs to populate session state with runtime context fields
- ⚠️ Need to document the pattern for developers

---

## What Already Exists

### 1. Session State Storage ✅

**Location:** `symphainy_platform/runtime/state_surface.py`

**Methods:**
- `store_session_state(session_id, tenant_id, state_dict)` - Store session state
- `get_session_state(session_id, tenant_id)` - Retrieve session state

**Usage Example:**
```python
# Store session state
await context.state_surface.store_session_state(
    session_id=context.session_id,
    tenant_id=context.tenant_id,
    state_dict={
        "business_context": {
            "industry": "insurance",
            "systems": ["legacy_policy_system", "claims_system"],
            "constraints": ["compliance_required", "data_retention_5_years"]
        },
        "journey_goal": "Migrate 350k policies from 8 legacy systems to 1 target",
        "human_preferences": {
            "detail_level": "detailed",
            "wants_visuals": True
        },
        "available_artifacts": ["parsed_file_123", "workflow_456"]
    }
)
```

### 2. Runtime Context Extraction ✅

**Location:** `symphainy_platform/civic_systems/agentic/models/agent_runtime_context.py`

**Method:** `AgentRuntimeContext.from_request(request, context)`

**Extraction Priority:**
1. Request dict (explicit parameters) - **highest priority**
2. ExecutionContext.metadata
3. Session state (via context.state_surface)
4. Intent.parameters (from context.intent)

**Usage:**
```python
# Agents automatically extract runtime context
runtime_context = await AgentRuntimeContext.from_request(request, context)

# Runtime context now includes:
# - business_context (from session state)
# - journey_goal (from session state)
# - human_preferences (from session state)
# - available_artifacts (from session state)
```

---

## What Needs to Be Implemented/Documented

### Gap: Landing Page → Session State Population

**Current State:**
- MVP showcase description mentions "Welcome Journey (Solution Landing Page)" that collects:
  - Goal Analysis (business goals, challenges)
  - AI Agent Reasoning
  - Customized Solution Structure
- But we need to ensure this data is stored in session state with the correct structure

**Required Implementation:**

#### Option A: Landing Page Stores Directly (Recommended)

**Pattern:**
```python
# In landing page handler (orchestrator/service)
async def handle_landing_page_submission(
    self,
    user_goals: str,
    industry: str,
    systems: List[str],
    constraints: List[str],
    preferences: Dict[str, Any],
    context: ExecutionContext
):
    """Handle landing page submission and store in session state."""
    
    # Store in session state
    session_state = {
        "business_context": {
            "industry": industry,
            "systems": systems,
            "constraints": constraints
        },
        "journey_goal": user_goals,
        "human_preferences": preferences,
        "available_artifacts": []  # Will be populated as user progresses
    }
    
    await context.state_surface.store_session_state(
        context.session_id,
        context.tenant_id,
        session_state
    )
```

#### Option B: Intent Parameters → Session State

**Pattern:**
```python
# In orchestrator intent handler
async def _handle_welcome_journey(
    self,
    intent: Intent,
    context: ExecutionContext
):
    """Handle welcome journey intent."""
    
    # Extract from intent parameters
    business_context = intent.parameters.get("business_context", {})
    journey_goal = intent.parameters.get("journey_goal", "")
    human_preferences = intent.parameters.get("human_preferences", {})
    
    # Store in session state for future use
    session_state = {
        "business_context": business_context,
        "journey_goal": journey_goal,
        "human_preferences": human_preferences,
        "available_artifacts": []
    }
    
    await context.state_surface.store_session_state(
        context.session_id,
        context.tenant_id,
        session_state
    )
```

---

## Session State Structure

### Required Fields for Runtime Context:

```json
{
  "business_context": {
    "industry": "insurance",
    "systems": ["legacy_system_1", "legacy_system_2"],
    "constraints": ["compliance_required", "data_retention_5_years"]
  },
  "journey_goal": "Migrate 350k policies from 8 legacy systems to 1 target",
  "human_preferences": {
    "detail_level": "detailed",
    "wants_visuals": true,
    "explanation_style": "technical"
  },
  "available_artifacts": ["parsed_file_123", "workflow_456", "sop_789"]
}
```

### Optional Fields (Platform-Specific):

```json
{
  "content_pillar_summary": {...},
  "insights_pillar_summary": {...},
  "journey_pillar_summary": {...},
  "ingested_files": [...],
  "parsed_files": [...],
  "sop_chat_session": {...}
}
```

---

## Implementation Checklist

### For Landing Page Implementation:

- [ ] **Collect User Input:**
  - Industry/domain
  - Legacy systems
  - Business constraints
  - Journey goals
  - User preferences (detail level, visuals, etc.)

- [ ] **Store in Session State:**
  - Use `context.state_surface.store_session_state()`
  - Store with keys: `business_context`, `journey_goal`, `human_preferences`

- [ ] **Verify Extraction:**
  - Agents will automatically extract via `AgentRuntimeContext.from_request()`
  - Runtime context will be included in prompt assembly (Layer 4)

### For Agent Usage:

- [ ] **Agents Automatically Get Runtime Context:**
  - If using `AgentBase.process_request()` → automatic
  - If implementing custom `process_request()` → call `AgentRuntimeContext.from_request()` manually

- [ ] **Use Runtime Context in Prompts:**
  - System message includes business context and journey goal
  - User message includes human preferences
  - Available artifacts are listed

---

## Example: Complete Flow

### 1. Landing Page Submission

```python
# User submits landing page form
POST /api/welcome-journey
{
  "industry": "insurance",
  "systems": ["legacy_policy_system", "claims_system"],
  "constraints": ["compliance_required"],
  "goals": "Migrate 350k policies from 8 legacy systems",
  "preferences": {
    "detail_level": "detailed",
    "wants_visuals": true
  }
}

# Handler stores in session state
await context.state_surface.store_session_state(
    session_id=context.session_id,
    tenant_id=context.tenant_id,
    state_dict={
        "business_context": {
            "industry": "insurance",
            "systems": ["legacy_policy_system", "claims_system"],
            "constraints": ["compliance_required"]
        },
        "journey_goal": "Migrate 350k policies from 8 legacy systems",
        "human_preferences": {
            "detail_level": "detailed",
            "wants_visuals": true
        }
    }
)
```

### 2. Agent Request (Later in Journey)

```python
# Agent receives request
request = {
    "type": "interpret_data",
    "parsed_file_id": "file_123"
}

# Agent automatically extracts runtime context
runtime_context = await AgentRuntimeContext.from_request(request, context)

# Runtime context now includes:
# - business_context: {"industry": "insurance", ...}
# - journey_goal: "Migrate 350k policies..."
# - human_preferences: {"detail_level": "detailed", ...}
```

### 3. Prompt Assembly (Layer 4)

```python
# System message includes:
"""
You are the Business Analysis Agent.
Mission: Reason about data meaning and generate business interpretations...

Business Context:
  - Industry: insurance
  - Systems: legacy_policy_system, claims_system
  - Constraints: compliance_required

Current Goal: Migrate 350k policies from 8 legacy systems
"""

# User message includes:
"""
Interpret this data file.

Preferences: Detail level: detailed, Include visualizations
"""
```

---

## Documentation Requirements

### What to Document:

1. **Session State Structure** - What fields to store
2. **Landing Page Pattern** - How to collect and store user input
3. **Agent Usage** - How agents automatically get runtime context
4. **Prompt Assembly** - How runtime context appears in prompts

### Where to Document:

1. **Developer Guide** - For frontend/backend developers implementing landing page
2. **Agent Development Guide** - For developers creating new agents
3. **Architecture Guide** - For understanding the 4-layer model

---

## Recommendation

**Status:** Infrastructure exists, pattern needs to be documented and verified.

**Action Items:**
1. ✅ **Document the pattern** (this document)
2. ⚠️ **Verify landing page implementation** - Check if landing page actually stores these fields
3. ⚠️ **Add examples** - Show concrete examples of storing/retrieving
4. ⚠️ **Test end-to-end** - Verify runtime context flows from landing page → session state → agent prompts

**If landing page doesn't exist yet:**
- Document the required structure
- Provide implementation pattern
- Add to backlog for landing page implementation

**If landing page exists but doesn't store these fields:**
- Update landing page to store in session state
- Verify extraction works
- Test with agents

---

**Status:** Pattern documented, ready for implementation verification
