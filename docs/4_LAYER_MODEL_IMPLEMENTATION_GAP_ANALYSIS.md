# 4-Layer Model Implementation Gap Analysis

**Date:** January 2026  
**Status:** 🔍 **GAPS IDENTIFIED**

---

## Executive Summary

**The 4-layer model infrastructure exists, but runtime context hydration is incomplete.**

**Key Findings:**
- ✅ Layer 1 (AgentDefinition): Implemented via JSON configs
- ✅ Layer 2 (AgentPosture): Model exists, registry support needed
- ⚠️ Layer 3 (AgentRuntimeContext): Model exists, but `from_request()` doesn't extract from ExecutionContext/session state
- ⚠️ Layer 4 (Prompt Assembly): Implemented, but agents bypass it

---

## Gap Analysis

### Gap 1: AgentRuntimeContext.from_request() Doesn't Extract from ExecutionContext

**Current Implementation:**
```python
@classmethod
def from_request(
    cls,
    request: Dict[str, Any],
    context: Optional[Any] = None  # ⚠️ Parameter ignored!
) -> "AgentRuntimeContext":
    return cls(
        business_context=request.get("business_context", {}),  # Only from request
        journey_goal=request.get("journey_goal", request.get("goal", "")),
        available_artifacts=request.get("available_artifacts", []),
        human_preferences=request.get("human_preferences", {}),
        session_state=request.get("session_state")
    )
```

**Problem:**
- `context` parameter is ignored
- Doesn't extract from `ExecutionContext.metadata`
- Doesn't extract from session state (via `context.state_surface`)
- Doesn't extract from `Intent.parameters`

**Expected Behavior:**
Runtime context should be populated from:
1. Request dict (explicit parameters) - ✅ Currently works
2. ExecutionContext.metadata - ❌ Not extracted
3. Session state (from context.state_surface) - ❌ Not extracted
4. Intent.parameters (from context.intent) - ❌ Not extracted

---

### Gap 2: Agents Bypass 4-Layer Model's process_request()

**Current Pattern:**
```python
async def process_request(self, request: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
    # ⚠️ Bypasses AgentBase.process_request() which does 4-layer assembly
    request_type = request.get("type")
    if request_type == "interpret_data":
        return await self._handle_interpret_data(request, context)
```

**Problem:**
- Agents implement their own `process_request()` that bypasses `AgentBase.process_request()`
- `AgentBase.process_request()` does:
  - Layer 3: Assemble runtime context
  - Layer 4: Assemble prompts
  - Call `_process_with_assembled_prompt()`
- But agents bypass this and call handlers directly

**Expected Behavior:**
Agents should either:
1. Use `AgentBase.process_request()` and implement `_process_with_assembled_prompt()`, OR
2. Manually call `AgentRuntimeContext.from_request()` and use it in their handlers

---

### Gap 3: No Source for Runtime Context Data

**Missing Sources:**
1. **Landing Page Questions** → Should populate session state with:
   - `business_context` (industry, systems, constraints)
   - `journey_goal`
   - `human_preferences` (detail_level, wants_visuals)

2. **Session State** → Should store:
   - `business_context`
   - `journey_goal`
   - `human_preferences`
   - `available_artifacts`

3. **Intent Parameters** → Should include:
   - `business_context`
   - `journey_goal`
   - `human_preferences`

**Current State:**
- No mechanism to populate these from landing page
- No mechanism to store in session state
- No mechanism to pass via intent parameters

---

## Required Implementation

### Step 1: Fix AgentRuntimeContext.from_request()

**Enhance to extract from:**
1. Request dict (explicit)
2. ExecutionContext.metadata
3. Session state (via context.state_surface)
4. Intent.parameters (via context.intent)

### Step 2: Create Runtime Context Hydration Service

**Service to:**
1. Extract from session state
2. Extract from ExecutionContext
3. Merge with request parameters
4. Provide fallback defaults

### Step 3: Update Orchestrators to Assemble Runtime Context (Call Site Responsibility)

**ARCHITECTURAL PRINCIPLE:** Agents should NOT assemble their own runtime context.

**Why agents shouldn't assemble context:**
- ❌ Agents can accidentally skip sources
- ❌ Agents can override precedence
- ❌ Agents may add "just one more thing"
- ❌ Two agents may hydrate context slightly differently
- ❌ Replayability becomes probabilistic

**Correct Pattern (Call Site Responsibility):**
- ✅ Orchestrator (or agent runner) calls `RuntimeContextHydrationService`
- ✅ Orchestrator passes assembled `AgentRuntimeContext` into agent
- ✅ Agent treats runtime context as read-only

**Implementation:**
```python
# In Orchestrator (call site)
async def _handle_interpret_data(self, intent, context):
    # Orchestrator assembles runtime context
    runtime_context = await self.runtime_context_service.create_runtime_context(
        request={"type": "interpret_data", "parsed_file_id": ...},
        context=context
    )
    
    # Pass to agent (read-only)
    agent_result = await self.business_analysis_agent.process_request(
        request={"type": "interpret_data", "parsed_file_id": ...},
        context=context,
        runtime_context=runtime_context  # Passed in, not assembled by agent
    )
```

**Agent Pattern:**
```python
# In Agent
async def process_request(
    self,
    request: Dict[str, Any],
    context: ExecutionContext,
    runtime_context: Optional[AgentRuntimeContext] = None  # Provided by orchestrator
) -> Dict[str, Any]:
    # Use provided runtime context (read-only)
    if runtime_context:
        # Use runtime_context.business_context, journey_goal, etc.
        pass
    # ... agent logic
```

### Step 4: Validate and Implement E2E Pattern for Runtime Context Population

**ARCHITECTURAL PRINCIPLE:** Runtime context should be collected from users, not agents (to avoid circular reference).

**Validation:**
1. ✅ Check if landing page already collects and stores runtime context fields
2. ✅ Verify session state structure matches expected format
3. ✅ Test end-to-end: Landing page → Session state → Orchestrator → Agent

**If Not Implemented - E2E Pattern Required:**

**Frontend (Landing Page):**
- Collect user input via UI elements:
  - Industry/domain selection
  - Legacy systems (multi-select or text input)
  - Business constraints (multi-select or text input)
  - Journey goals (text area)
  - User preferences (detail level, wants visuals, etc.)
- Submit to backend API endpoint

**Backend (Orchestrator/Service):**
- Receive landing page submission
- Store in session state via `StateSurface.store_session_state()`
- Structure:
  ```python
  session_state = {
      "business_context": {
          "industry": user_input["industry"],
          "systems": user_input["systems"],
          "constraints": user_input["constraints"]
      },
      "journey_goal": user_input["goals"],
      "human_preferences": user_input["preferences"]
  }
  ```

**Why UI Elements (Not Agent Collection):**
- ✅ Avoids circular reference (agent needs context to collect context)
- ✅ Ensures consistency (same structure for all users)
- ✅ Better UX (explicit collection vs. inferred)
- ✅ Deterministic (same input → same context)

**State Flow (How State Works):**
```
1. User Input (Landing Page UI)
   - User enters: industry, systems, constraints, goals, preferences
   - Frontend collects via form/UI elements
   
2. Frontend → Backend API
   - POST /api/welcome-journey or similar
   - Sends: {industry, systems, constraints, goals, preferences}
   
3. Backend API → Session State Storage
   - Orchestrator/Service receives request
   - Calls: context.state_surface.store_session_state(
       session_id=context.session_id,
       tenant_id=context.tenant_id,
       state_dict={
           "business_context": {...},
           "journey_goal": "...",
           "human_preferences": {...}
       }
   )
   - Session state is stored in StateSurface (Supabase/Redis)
   
4. Later: Agent Request
   - User performs action (e.g., interpret data)
   - Orchestrator receives intent
   
5. Orchestrator → Runtime Context Hydration
   - Orchestrator calls: runtime_context_service.create_runtime_context(request, context)
   - Service extracts from:
     a. Request dict (explicit)
     b. ExecutionContext.metadata
     c. Session state (via context.state_surface.get_session_state)
     d. Intent.parameters
   
6. Orchestrator → Agent (Read-only)
   - Orchestrator passes assembled runtime_context to agent
   - Agent uses it (read-only) in prompts
   
7. Agent → LLM Prompt
   - System message includes: business_context, journey_goal
   - User message includes: human_preferences
```

**Key Points:**
- **Session State** = Persistent storage (Supabase/Redis) keyed by `session_id` + `tenant_id`
- **Runtime Context** = Ephemeral, assembled at call time, never stored
- **State Surface** = Abstraction layer for session state storage/retrieval
- **No Circular Reference** = UI collects → Backend stores → Orchestrator extracts → Agent uses

---

## Implementation Plan

### Phase 6.5: Fix 4-Layer Model Runtime Context Hydration

**Tasks:**
1. ✅ Enhance `AgentRuntimeContext.from_request()` to extract from ExecutionContext and session state
2. ✅ Create `RuntimeContextHydrationService` (optional helper)
3. ✅ Update agents to use runtime context (or ensure they call `from_request()` properly)
4. ✅ Document how to populate runtime context from landing page/session state

**Estimated Effort:** 4-6 hours

---

## Next Steps (After Fix)

1. Health monitoring integration
2. Orchestrator telemetry integration
3. Metrics dashboard (for admin dashboard)
4. Test and validate everything

---

**Status:** Gaps identified, ready to implement fixes
