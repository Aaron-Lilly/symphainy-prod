# Runtime Context E2E Implementation Plan

**Date:** January 2026  
**Status:** 📋 **PLAN CREATED**

---

## Executive Summary

**Validate if landing page stores runtime context, and if not, implement complete E2E pattern.**

**Current State:**
- ✅ Landing page collects `userGoals` (via WelcomeJourney component)
- ⚠️ Landing page does NOT collect: industry, systems, constraints, preferences
- ⚠️ Landing page does NOT store in session state with runtime context structure
- ✅ Runtime context extraction exists (from session state)
- ✅ Orchestrator pattern exists (call site responsibility)

---

## Validation Steps

### Step 1: Check Current Landing Page Implementation

**Check:**
1. Does `WelcomeJourney` component collect:
   - Industry/domain?
   - Legacy systems?
   - Business constraints?
   - User preferences (detail level, wants visuals)?

2. Does `mvpSolutionService.createSession()` store:
   - `business_context` in session state?
   - `journey_goal` in session state?
   - `human_preferences` in session state?

**Expected Finding:**
- Currently only collects `userGoals`
- Does NOT collect full runtime context structure
- Does NOT store in session state with correct structure

---

## E2E Implementation (If Not Available)

### Frontend: Enhanced Landing Page UI

**Location:** `symphainy-frontend/components/landing/WelcomeJourney.tsx`

**Add UI Elements:**
1. **Industry Selection** (Dropdown/Select)
   - Options: Insurance, Healthcare, Finance, Manufacturing, etc.
   - Or free-form text input

2. **Legacy Systems** (Multi-select or Text Input)
   - Allow multiple systems
   - Examples: "legacy_policy_system", "claims_system", "billing_system"

3. **Business Constraints** (Multi-select or Text Input)
   - Examples: "compliance_required", "data_retention_5_years", "real-time_processing"

4. **User Preferences** (Checkboxes/Selects)
   - Detail level: "summary", "detailed", "technical"
   - Wants visuals: true/false
   - Explanation style: "simple", "technical", "business"

5. **Journey Goal** (Already exists - Textarea)
   - Keep existing `userGoals` field

**UI Structure:**
```tsx
<Card>
  <CardHeader>
    <CardTitle>Business Context</CardTitle>
  </CardHeader>
  <CardContent>
    <Select label="Industry" value={industry} onChange={setIndustry}>
      <option>Insurance</option>
      <option>Healthcare</option>
      ...
    </Select>
    
    <MultiSelect 
      label="Legacy Systems" 
      value={systems} 
      onChange={setSystems}
      options={[...]}
    />
    
    <MultiSelect 
      label="Business Constraints" 
      value={constraints} 
      onChange={setConstraints}
      options={[...]}
    />
  </CardContent>
</Card>

<Card>
  <CardHeader>
    <CardTitle>User Preferences</CardTitle>
  </CardHeader>
  <CardContent>
    <Select label="Detail Level" value={detailLevel} onChange={setDetailLevel}>
      <option>Summary</option>
      <option>Detailed</option>
      <option>Technical</option>
    </Select>
    
    <Checkbox 
      label="Include Visualizations" 
      checked={wantsVisuals} 
      onChange={setWantsVisuals}
    />
  </CardContent>
</Card>
```

---

### Backend: Session State Storage

**Location:** Backend API handler (orchestrator/service)

**Implementation:**
```python
async def handle_welcome_journey_submission(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """Handle welcome journey submission and store runtime context in session state."""
    
    # Extract from intent parameters
    industry = intent.parameters.get("industry")
    systems = intent.parameters.get("systems", [])
    constraints = intent.parameters.get("constraints", [])
    goals = intent.parameters.get("goals", "")
    preferences = intent.parameters.get("preferences", {})
    
    # Structure runtime context fields
    session_state = {
        "business_context": {
            "industry": industry,
            "systems": systems,
            "constraints": constraints
        },
        "journey_goal": goals,
        "human_preferences": {
            "detail_level": preferences.get("detail_level", "detailed"),
            "wants_visuals": preferences.get("wants_visuals", True),
            "explanation_style": preferences.get("explanation_style", "technical")
        },
        "available_artifacts": []  # Will be populated as user progresses
    }
    
    # Store in session state
    await context.state_surface.store_session_state(
        context.session_id,
        context.tenant_id,
        session_state
    )
    
    return {
        "artifacts": {
            "session_created": True,
            "session_id": context.session_id
        },
        "events": [
            {
                "type": "session_created",
                "session_id": context.session_id
            }
        ]
    }
```

---

### API Endpoint

**Location:** Runtime API or Realm Orchestrator

**New Endpoint:**
```python
@app.post("/api/welcome-journey/submit")
async def submit_welcome_journey(request: WelcomeJourneyRequest):
    """Submit welcome journey data and store in session state."""
    
    # Create intent
    intent = IntentFactory.create_intent(
        intent_type="welcome_journey_submit",
        tenant_id=request.tenant_id,
        session_id=request.session_id,
        solution_id=request.solution_id,
        parameters={
            "industry": request.industry,
            "systems": request.systems,
            "constraints": request.constraints,
            "goals": request.goals,
            "preferences": request.preferences
        }
    )
    
    # Create execution context
    context = ExecutionContextFactory.create_context(
        intent=intent,
        state_surface=state_surface,
        wal=wal
    )
    
    # Handle via orchestrator
    result = await orchestrator.handle_intent(intent, context)
    
    return result
```

---

## State Flow Explanation

### How State Works (Step-by-Step):

1. **User Fills Landing Page Form**
   - User enters: industry="insurance", systems=["legacy_policy"], goals="Migrate 350k policies"
   - Frontend collects this data

2. **Frontend Calls Backend API**
   ```typescript
   await fetch('/api/welcome-journey/submit', {
     method: 'POST',
     body: JSON.stringify({
       industry: "insurance",
       systems: ["legacy_policy"],
       constraints: ["compliance_required"],
       goals: "Migrate 350k policies",
       preferences: { detail_level: "detailed" }
     })
   })
   ```

3. **Backend Stores in Session State**
   ```python
   # In orchestrator/service
   await context.state_surface.store_session_state(
       session_id="session_123",
       tenant_id="tenant_456",
       state_dict={
           "business_context": {...},
           "journey_goal": "Migrate 350k policies",
           "human_preferences": {...}
       }
   )
   ```
   - This stores in Supabase/Redis with key: `session_123:tenant_456`
   - Persists across requests

4. **Later: User Performs Action (e.g., Interpret Data)**
   - User clicks "Interpret Data" button
   - Frontend calls: `POST /api/insights/interpret_data`

5. **Orchestrator Extracts Runtime Context**
   ```python
   # In InsightsOrchestrator._handle_interpret_data()
   runtime_context = await self.runtime_context_service.create_runtime_context(
       request={"type": "interpret_data", "parsed_file_id": "file_123"},
       context=context
   )
   # Service automatically extracts from session state
   ```

6. **Orchestrator Passes to Agent**
   ```python
   agent_result = await self.business_analysis_agent.process_request(
       request={...},
       context=context,
       runtime_context=runtime_context  # Read-only
   )
   ```

7. **Agent Uses in Prompts**
   ```python
   # In agent (read-only)
   system_message = f"""
   You are the Business Analysis Agent.
   Business Context:
     - Industry: {runtime_context.business_context['industry']}
     - Systems: {', '.join(runtime_context.business_context['systems'])}
   Current Goal: {runtime_context.journey_goal}
   """
   ```

**Key Points:**
- **Session State** = Database/Redis storage (persistent, keyed by session_id)
- **Runtime Context** = In-memory object (ephemeral, assembled at call time)
- **No Circular Reference** = UI collects → Backend stores → Orchestrator extracts → Agent uses

---

## Implementation Checklist

### Frontend:
- [ ] Add industry selection UI element
- [ ] Add legacy systems multi-select UI element
- [ ] Add business constraints multi-select UI element
- [ ] Add user preferences UI elements (detail level, wants visuals)
- [ ] Update form submission to include all fields
- [ ] Update API call to send all fields

### Backend:
- [ ] Create/update welcome journey handler
- [ ] Store runtime context fields in session state
- [ ] Verify session state structure matches expected format
- [ ] Test session state retrieval

### Validation:
- [ ] Test E2E: Landing page → Session state → Orchestrator → Agent
- [ ] Verify runtime context appears in agent prompts
- [ ] Verify no circular reference (agents don't collect their own context)

---

## Next Steps

1. **Validate** current landing page implementation
2. **Implement** E2E pattern if not available
3. **Test** end-to-end flow
4. **Document** for developers

---

**Status:** Plan created, ready for validation and implementation
