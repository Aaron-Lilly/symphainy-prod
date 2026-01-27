# Platform Build Guide

**Date:** January 24, 2026  
**Status:** ✅ **PRACTICAL REFERENCE**  
**Purpose:** How to fix, enhance, or add to the Symphainy platform correctly

---

## Executive Summary

This guide provides **practical, actionable instructions** for working with the Symphainy platform. It covers:

- How to fix common issues
- How to add new features
- What to do / what not to do
- Patterns to follow
- Common pitfalls
- Step-by-step guides

**Key Principle:** Follow the architectural principles. Use the patterns. Don't take shortcuts.

---

## Before You Start

### 1. Read the Architecture Documents

**Required Reading:**
1. `00_ARCHITECTURAL_PRINCIPLES_CTO_VALIDATED.md` - The 10 principles
2. `01_BACKEND_ARCHITECTURE_SUMMARY.md` - Backend structure
3. `02_FRONTEND_ARCHITECTURE_SUMMARY.md` - Frontend structure
4. `03_OVERALL_PLATFORM_ARCHITECTURE_NORTH_STAR.md` - Holistic vision

**Time Investment:** 30-60 minutes

**Why:** Understanding the architecture prevents mistakes and saves time.

### 2. Understand the 10 Principles

**Validation Questions to Ask Yourself:**

1. "If I make this change, does Runtime know about it?"
2. "Am I touching data? Should I be in a Realm?"
3. "Am I using Public Works abstractions?"
4. "Is this session-first or auth-first?"
5. "Am I expressing intent or causing execution?"
6. "Am I simulating success or failing truthfully?"
7. "Does this match the architecture guide?"
8. "Am I submitting an intent or calling a capability?"
9. "Is this policy-governed or ACID?"
10. "Is the frontend deciding outcomes?"

**If you can't answer these confidently, re-read the architecture documents.**

---

## How to Fix Common Issues

### Issue 1: State Management Placeholders

**Symptom:** `getPillarState()` or `setPillarState()` return null/empty

**Location:** Multiple frontend components

**Fix Pattern:**
```typescript
// ❌ WRONG: Placeholder
const getPillarState = (pillar: string) => null;
const setPillarState = async (pillar: string, state: any) => {};

// ✅ CORRECT: Use PlatformStateProvider
import { usePlatformState } from "@/shared/state/PlatformStateProvider";

const { getRealmState, setRealmState } = usePlatformState();
const contentState = getRealmState('content', 'files');
await setRealmState('content', 'files', updatedFiles);
```

**Steps:**
1. Import `usePlatformState` hook
2. Replace `getPillarState()` with `getRealmState(realm, key)`
3. Replace `setPillarState()` with `setRealmState(realm, key, value)`
4. Test state persistence across pillar navigation

**Files to Fix:**
- `components/content/FileUploader.tsx`
- `components/operations/CoexistenceBluprint.tsx`
- `components/insights/VARKInsightsPanel.tsx`

---

### Issue 2: Mock User ID

**Symptom:** Hardcoded `user_id: "mock-user"` in file metadata

**Location:** `components/content/FileUploader.tsx`

**Fix Pattern:**
```typescript
// ❌ WRONG: Mock user_id
user_id: "mock-user"

// ✅ CORRECT: Use session user_id
import { useSessionBoundary } from "@/shared/state/SessionBoundaryProvider";

const { state: sessionState } = useSessionBoundary();
user_id: sessionState.userId || sessionState.user_id
```

**Steps:**
1. Import `useSessionBoundary` hook
2. Get `userId` from session state
3. Replace all `"mock-user"` with actual user ID
4. Test with authenticated and anonymous sessions

---

### Issue 3: Business Outcomes TODOs

**Symptom:** `handleCreateBlueprint()`, `handleCreatePOC()`, etc. return errors

**Location:** `app/(protected)/pillars/business-outcomes/page.tsx`

**Fix Pattern:**
```typescript
// ❌ WRONG: TODO placeholder
const handleCreatePOC = async () => {
  return { success: false, error: "Not implemented" };
};

// ✅ CORRECT: Implement API call
import { useOutcomesAPI } from "@/shared/hooks/useOutcomesAPI";

const { createPOC } = useOutcomesAPI();

const handleCreatePOC = async () => {
  const { data, error } = await createPOC({
    description: "...",
    synthesis: businessOutcomesOutputs?.synthesis
  });
  
  if (error) {
    setError(error.message);
    return;
  }
  
  setArtifacts(prev => ({ ...prev, poc: data }));
};
```

**Steps:**
1. Check if `useOutcomesAPI` hook exists
2. If not, create it following `useFileAPI` pattern
3. Implement API calls to Outcomes realm endpoints
4. Connect to `OutcomesOrchestrator` endpoints
5. Test end-to-end flow

**Backend Endpoints Needed:**
- `POST /api/v1/outcomes/create-blueprint`
- `POST /api/v1/outcomes/create-poc`
- `POST /api/v1/outcomes/generate-roadmap`
- `POST /api/v1/outcomes/export-artifact`

---

### Issue 4: SemanticMeaningAgent Placeholder

**Symptom:** Returns empty artifact with 0.0 confidence

**Location:** `realms/content/enabling_services/embedding_service.py`

**Fix Pattern:**
```python
# ❌ WRONG: Placeholder
async def _process_with_assembled_prompt(...):
    return {
        "artifact_type": "semantic_meaning",
        "artifact": {},
        "confidence": 0.0
    }

# ✅ CORRECT: Implement semantic meaning inference
async def _process_with_assembled_prompt(
    self,
    system_message: str,
    user_message: str,
    runtime_context: AgentRuntimeContext,
    context: ExecutionContext
) -> Dict[str, Any]:
    # Extract text from user_message or runtime_context
    text = self._extract_text(user_message, runtime_context)
    
    # Call LLM for semantic interpretation
    interpretation = await self._call_llm(
        prompt=f"Interpret the semantic meaning of: {text}",
        system_message=system_message,
        model="gpt-4o-mini",
        max_tokens=500,
        temperature=0.3,
        context=context
    )
    
    return {
        "artifact_type": "semantic_meaning",
        "artifact": {
            "interpretation": interpretation,
            "text": text
        },
        "confidence": 0.8
    }
```

**Steps:**
1. Implement text extraction from user_message/runtime_context
2. Call LLM for semantic interpretation
3. Return meaningful semantic analysis
4. Test with real data

---

### Issue 5: File Upload Mock Fallback

**Symptom:** Creates mock file when sessionId === null

**Location:** `components/content/FileUploader.tsx`

**Fix Pattern:**
```typescript
// ❌ WRONG: Mock fallback
if (sessionId === null) {
  const mockFile = { ... }; // Don't do this
}

// ✅ CORRECT: Fail gracefully
if (!sessionId) {
  throw new Error("Session not available. Please ensure you're logged in.");
  // Or show user-friendly error message
  setError("Please log in to upload files.");
  return;
}
```

**Steps:**
1. Remove mock file creation code
2. Add proper error handling
3. Show user-friendly error message
4. Test with invalid session

---

## How to Add New Features

### Pattern 1: Add New Realm Intent

**Scenario:** Add new intent to Content Realm (e.g., `validate_schema`)

**Steps:**

1. **Define Intent in Realm Orchestrator**
   ```python
   # realms/content/orchestrators/content_orchestrator.py
   async def handle_intent(self, intent: Intent, context: ExecutionContext):
       intent_type = intent.intent_type
       
       if intent_type == "validate_schema":
           return await self._handle_validate_schema(intent, context)
       # ... existing handlers
   ```

2. **Implement Handler**
   ```python
   async def _handle_validate_schema(
       self,
       intent: Intent,
       context: ExecutionContext
   ) -> Dict[str, Any]:
       # Use enabling services
       # Use Public Works abstractions
       # Return artifact
       return {
           "artifact_type": "validation_result",
           "artifact": {...},
           "confidence": 0.9
       }
   ```

3. **Register Intent in Realm**
   ```python
   # realms/content/content_realm.py
   def get_supported_intents(self) -> List[str]:
       return [
           "upload_file",
           "parse_file",
           "validate_schema",  # New intent
           # ... existing intents
       ]
   ```

4. **Add Frontend Hook (if needed)**
   ```typescript
   // shared/hooks/useContentAPI.ts
   export function useContentAPI() {
     const validateSchema = async (fileId: string) => {
       return await submitIntent({
         intent_type: "validate_schema",
         file_id: fileId,
         session_id: sessionId
       });
     };
     
     return { validateSchema };
   }
   ```

5. **Test End-to-End**
   - Test intent submission
   - Test handler execution
   - Test artifact return
   - Test frontend integration

---

### Pattern 2: Add New Agent

**Scenario:** Add new agent (e.g., `DataQualityAgent`)

**Steps:**

1. **Create Agent Class**
   ```python
   # realms/insights/agents/data_quality_agent.py
   from symphainy_platform.civic_systems.agentic.agent_base import AgentBase
   from symphainy_platform.civic_systems.agentic.models.agent_runtime_context import AgentRuntimeContext
   
   class DataQualityAgent(AgentBase):
       def __init__(self, public_works: Optional[Any] = None, **kwargs):
           super().__init__(
               agent_id="data_quality_agent",
               agent_type="specialized",
               capabilities=["assess_quality", "identify_issues"],
               public_works=public_works,
               **kwargs
           )
       
       async def _process_with_assembled_prompt(
           self,
           system_message: str,
           user_message: str,
           runtime_context: AgentRuntimeContext,
           context: ExecutionContext
       ) -> Dict[str, Any]:
           # Extract request
           # Route to handler
           # Return artifact
           pass
       
       async def get_agent_description(self) -> str:
           return "Data Quality Agent - Assesses data quality and identifies issues"
   ```

2. **Register Agent in Realm**
   ```python
   # realms/insights/insights_realm.py
   def __init__(self, realm_id: str, public_works: Optional[Any] = None):
       # ... existing initialization
       self.data_quality_agent = DataQualityAgent(public_works=public_works)
   ```

3. **Add MCP Tool (if needed)**
   ```python
   # realms/insights/mcp_server/insights_mcp_server.py
   @tool
   async def insights_assess_quality(
       parsed_file_id: str,
       context: ExecutionContext
   ) -> Dict[str, Any]:
       # Call DataQualityService
       # Return result
       pass
   ```

4. **Test Agent**
   - Test agent instantiation
   - Test `_process_with_assembled_prompt()`
   - Test MCP tool integration
   - Test end-to-end flow

---

### Pattern 3: Add New Frontend Component

**Scenario:** Add new component for data quality visualization

**Steps:**

1. **Create Component**
   ```typescript
   // components/insights/DataQualityVisualization.tsx
   import { usePlatformState } from "@/shared/state/PlatformStateProvider";
   import { useInsightsAPI } from "@/shared/hooks/useInsightsAPI";
   
   export function DataQualityVisualization({ fileId }: { fileId: string }) {
     const { getRealmState } = usePlatformState();
     const { assessQuality } = useInsightsAPI();
     
     // Subscribe to state
     const qualityData = getRealmState('insights', `quality_${fileId}`);
     
     // Express intent (don't execute)
     const handleAssess = async () => {
       await assessQuality(fileId);
     };
     
     // Render based on state
     return <div>{/* Render quality data */}</div>;
   }
   ```

2. **Add to Pillar Page**
   ```typescript
   // app/(protected)/pillars/insights/page.tsx
   import { DataQualityVisualization } from "@/components/insights/DataQualityVisualization";
   
   // Use component
   <DataQualityVisualization fileId={selectedFileId} />
   ```

3. **Test Component**
   - Test state subscription
   - Test intent expression
   - Test rendering
   - Test integration

---

## What to Do / What Not to Do

### ✅ DO

#### Backend

- Use Public Works abstractions for all infrastructure
- Return artifacts from realm orchestrators
- Use Runtime for all execution
- Implement `_process_with_assembled_prompt()` in agents
- Use MCP tools for agent-service communication
- Classify data correctly (Working Material vs Record of Fact)
- Use dependency injection for Public Works
- Return structured artifacts with `artifact_type`, `artifact`, `confidence`

#### Frontend

- Use `useSessionBoundary()` for session management
- Use `usePlatformState()` for platform state
- Use service layer hooks for all API calls
- Subscribe to state changes in components
- Express intent, don't execute
- Handle errors as signals
- Connect WebSocket when `SessionStatus === Active`
- Use `getRealmState()` / `setRealmState()` for realm state

### ❌ DON'T

#### Backend

- Call infrastructure directly (Redis, ArangoDB, GCS, Supabase)
- Put data logic in Runtime
- Execute outside Runtime
- Call services directly from agents
- Mix data classes in same storage
- Bypass Runtime for state, retries, or orchestration
- Use `get_X()` methods on Public Works (use attributes)
- Return side effects instead of artifacts

#### Frontend

- Call APIs directly from components
- Use `localStorage` for session storage
- Create WebSocket on component mount
- Check `isAuthenticated` instead of `SessionStatus`
- Put business logic in frontend
- Access database directly from frontend
- Bypass service layer hooks
- Use placeholder `getPillarState()` / `setPillarState()`
- Create mock files when session fails
- Use hardcoded `user_id: "mock-user"`

---

## Common Patterns

### Pattern 1: Adding New Intent Handler

```python
# 1. Add handler method in orchestrator
async def _handle_new_intent(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    # Extract parameters
    param1 = intent.parameters.get("param1")
    
    # Use enabling services
    result = await self.enabling_service.do_something(param1)
    
    # Return artifact
    return {
        "artifact_type": "result",
        "artifact": result,
        "confidence": 0.9
    }

# 2. Route in handle_intent
async def handle_intent(self, intent: Intent, context: ExecutionContext):
    if intent.intent_type == "new_intent":
        return await self._handle_new_intent(intent, context)
    # ... existing routes
```

### Pattern 2: Adding New Service Layer Hook

```typescript
// 1. Create hook
export function useNewAPI() {
  const { state: sessionState } = useSessionBoundary();
  const { submitIntent } = useServiceLayerAPI();
  
  const doSomething = async (param: string) => {
    return await submitIntent({
      intent_type: "new_intent",
      parameters: { param },
      session_id: sessionState.sessionId
    });
  };
  
  return { doSomething };
}

// 2. Use in component
const { doSomething } = useNewAPI();
await doSomething("value");
```

### Pattern 3: Adding New Public Works Abstraction

```python
# 1. Create abstraction interface
class NewAbstraction(Protocol):
    async def do_something(self, param: str) -> Dict[str, Any]:
        ...

# 2. Create abstraction implementation
class NewAbstractionImpl:
    def __init__(self, adapter: NewAdapter):
        self.adapter = adapter
    
    async def do_something(self, param: str) -> Dict[str, Any]:
        return await self.adapter.call(param)

# 3. Add to Public Works
class PublicWorksFoundationService:
    def __init__(self, ...):
        self.new_abstraction: Optional[NewAbstraction] = None
    
    async def initialize(self):
        # Initialize adapter
        adapter = NewAdapter(...)
        # Initialize abstraction
        self.new_abstraction = NewAbstractionImpl(adapter)
    
    def get_new_abstraction(self) -> Optional[NewAbstraction]:
        return self.new_abstraction
```

---

## Testing Guidelines

### Unit Tests

**Pattern:**
```python
async def test_new_feature(mock_abstraction):
    service = NewService(abstraction=mock_abstraction)
    result = await service.do_something("param")
    assert result["success"] == True
```

**Key Principle:** Tests must fail if code has cheats.

### Integration Tests

**Pattern:**
```python
async def test_new_feature_integration(real_abstraction):
    service = NewService(abstraction=real_abstraction)
    result = await service.do_something("param")
    assert result["success"] == True
    # Verify side effects
```

**Key Principle:** Test with real abstractions (but mocked adapters if needed).

### E2E Tests

**Pattern:**
```typescript
test('file upload flow', async ({ page }) => {
  await page.goto('/pillars/content');
  await page.uploadFile('input[type="file"]', 'test.csv');
  await expect(page.locator('.file-list')).toContainText('test.csv');
});
```

**Key Principle:** Test full user journeys with real backend.

---

## Debugging Guide

### Issue: "Agent can't instantiate - missing _process_with_assembled_prompt"

**Debug Steps:**
1. Check if agent extends `AgentBase`
2. Check if `_process_with_assembled_prompt()` is implemented
3. Check method signature matches abstract method
4. Check imports (`AgentRuntimeContext`)

**Fix:** Implement `_process_with_assembled_prompt()` following pattern in `docs/AGENT_4_LAYER_MODEL_IMPLEMENTATION_PATTERN.md`

### Issue: "AttributeError: 'PublicWorksFoundationService' object has no attribute 'get_X'"

**Debug Steps:**
1. Check if abstraction exists in Public Works
2. Check if it's an attribute or method
3. Check Public Works initialization

**Fix:** Use attribute access, not method calls:
```python
# ✅ CORRECT
abstraction = public_works.semantic_data_abstraction

# ❌ WRONG
abstraction = public_works.get_semantic_data_abstraction()
```

### Issue: "State not persisting across pillar navigation"

**Debug Steps:**
1. Check if using `usePlatformState()`
2. Check if using `getRealmState()` / `setRealmState()`
3. Check if state is being set correctly
4. Check if PlatformStateProvider is syncing with Runtime

**Fix:** Replace placeholder `getPillarState()` / `setPillarState()` with `usePlatformState()`

### Issue: "WebSocket not connecting"

**Debug Steps:**
1. Check `SessionStatus` (must be `Active`)
2. Check if WebSocket connects when status changes
3. Check authentication token
4. Check WebSocket endpoint URL

**Fix:** WebSocket should connect when `SessionStatus === Active`, not on component mount

---

## Code Review Checklist

### Before Submitting Code

- [ ] Code works (no stubs/cheats)
- [ ] Tests pass (and would fail if code had cheats)
- [ ] Uses Public Works abstractions (no direct infrastructure)
- [ ] Matches architecture guide
- [ ] Has type hints (Python) / types (TypeScript)
- [ ] Has docstrings / comments
- [ ] Handles errors properly
- [ ] No backwards compatibility code
- [ ] No mock data in production code
- [ ] No hardcoded values that should be configurable

### Architecture Compliance

- [ ] Runtime knows about all execution
- [ ] Only Realms touch data (through abstractions)
- [ ] All infrastructure via Public Works
- [ ] Session-first, not auth-first
- [ ] State drives actions, not components
- [ ] Intent-based, not capability calls
- [ ] Policy-governed, not ACID

---

## Common Pitfalls

### Pitfall 1: "Just This Once" Direct Calls

**Temptation:** "I'll just call Supabase directly this one time, it's faster."

**Reality:** This violates Public Works principle and creates technical debt.

**Fix:** Always use Public Works abstractions, even if slower.

### Pitfall 2: Mock Data in Production

**Temptation:** "I'll use mock data for now, fix it later."

**Reality:** Mock data becomes permanent and masks real issues.

**Fix:** Fail loudly and truthfully. Use feature flags if needed.

### Pitfall 3: Bypassing Runtime

**Temptation:** "I'll just call the service directly, Runtime is slow."

**Reality:** This breaks auditability and governance.

**Fix:** All execution must go through Runtime.

### Pitfall 4: Frontend Business Logic

**Temptation:** "I'll just add this logic in the frontend, it's easier."

**Reality:** This breaks the "frontend as platform runtime" principle.

**Fix:** Business logic belongs in Realms. Frontend renders state.

---

## Step-by-Step: Adding Complete Feature

### Example: Add "Data Quality Dashboard" Feature

**Step 1: Backend - Add Intent Handler**
```python
# realms/insights/orchestrators/insights_orchestrator.py
async def _handle_get_quality_dashboard(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    file_id = intent.parameters.get("file_id")
    quality_data = await self.data_quality_service.get_quality_metrics(file_id)
    return {
        "artifact_type": "quality_dashboard",
        "artifact": quality_data,
        "confidence": 0.9
    }
```

**Step 2: Backend - Register Intent**
```python
# realms/insights/insights_realm.py
def get_supported_intents(self) -> List[str]:
    return [
        # ... existing intents
        "get_quality_dashboard",
    ]
```

**Step 3: Frontend - Add Hook**
```typescript
// shared/hooks/useInsightsAPI.ts
export function useInsightsAPI() {
  const getQualityDashboard = async (fileId: string) => {
    return await submitIntent({
      intent_type: "get_quality_dashboard",
      parameters: { file_id: fileId },
      session_id: sessionId
    });
  };
  
  return { getQualityDashboard };
}
```

**Step 4: Frontend - Create Component**
```typescript
// components/insights/QualityDashboard.tsx
export function QualityDashboard({ fileId }: { fileId: string }) {
  const { getQualityDashboard } = useInsightsAPI();
  const { getRealmState } = usePlatformState();
  
  const dashboardData = getRealmState('insights', `quality_dashboard_${fileId}`);
  
  useEffect(() => {
    getQualityDashboard(fileId);
  }, [fileId]);
  
  return <div>{/* Render dashboard */}</div>;
}
```

**Step 5: Test End-to-End**
- Test intent submission
- Test handler execution
- Test artifact return
- Test component rendering
- Test state persistence

---

## Validation Questions

Before implementing any change, ask:

1. **"Does Runtime know about this execution?"**
   - If no, fix it. All execution must go through Runtime.

2. **"Am I touching data? Should I be in a Realm?"**
   - If yes and not in Realm, move it to Realm.

3. **"Am I using Public Works abstractions?"**
   - If no, fix it. All infrastructure via Public Works.

4. **"Is this session-first or auth-first?"**
   - Should be session-first. Fix if auth-first.

5. **"Am I expressing intent or causing execution?"**
   - Should express intent. Fix if causing execution.

6. **"Am I simulating success or failing truthfully?"**
   - Should fail truthfully. Fix if simulating success.

7. **"Does this match the architecture guide?"**
   - If no, fix code to match guide.

8. **"Am I submitting an intent or calling a capability?"**
   - Should submit intent. Fix if calling capability.

9. **"Is this policy-governed or ACID?"**
   - Should be policy-governed. Fix if ACID.

10. **"Is the frontend deciding outcomes?"**
    - Should not. Frontend renders state, doesn't decide outcomes.

---

## Quick Reference

### Backend Patterns

**Add Intent Handler:**
```python
async def _handle_new_intent(intent, context):
    # Use services
    # Use Public Works
    # Return artifact
```

**Add Agent:**
```python
class NewAgent(AgentBase):
    async def _process_with_assembled_prompt(...):
        # Implement
        pass
```

**Use Public Works:**
```python
file_storage = public_works.get_file_storage_abstraction()
await file_storage.store_file(file_id, data)
```

### Frontend Patterns

**Use State:**
```typescript
const { getRealmState, setRealmState } = usePlatformState();
const state = getRealmState('content', 'files');
await setRealmState('content', 'files', newState);
```

**Submit Intent:**
```typescript
const { submitIntent } = useServiceLayerAPI();
await submitIntent({
  intent_type: "parse_file",
  file_id: fileId,
  session_id: sessionId
});
```

**Use Service Hook:**
```typescript
const { uploadAndProcessFile } = useFileAPI();
const result = await uploadAndProcessFile(file, sessionId, fileType);
```

---

## Emergency Fixes

### If Runtime Container Won't Start

1. Check agent abstract methods (all must implement `_process_with_assembled_prompt`)
2. Check Public Works attribute access (use attributes, not methods)
3. Check imports (all imports must be correct)
4. Check syntax errors (Python syntax must be valid)

### If Frontend Won't Build

1. Check TypeScript errors
2. Check import paths
3. Check hook usage (must be within providers)
4. Check API calls (must use service layer hooks)

### If State Not Persisting

1. Check `usePlatformState()` usage
2. Check `getRealmState()` / `setRealmState()` calls
3. Check PlatformStateProvider sync with Runtime
4. Check session state (must be Active)

---

## Next Steps

1. Review this guide
2. Understand the patterns
3. Follow the principles
4. Use the checklists
5. Ask validation questions
6. Test thoroughly

---

**Remember:** We're building a platform that works. No shortcuts. No cheats. No backwards compatibility baggage. Working code only.

---

**Last Updated:** January 24, 2026  
**Status:** ✅ **PRACTICAL REFERENCE**
