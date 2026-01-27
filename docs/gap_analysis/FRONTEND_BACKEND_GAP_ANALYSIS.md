# Frontend-Backend Gap Analysis

**Date:** January 27, 2026  
**Status:** Active  
**Priority:** HIGH

---

## Executive Summary

This document identifies gaps between the frontend implementation and the newly rebuilt backend platform. The analysis is structured around the platform's architectural principles:

1. **Runtime is the execution authority** - Nothing executes without Runtime's knowledge
2. **Session-First Pattern** - SessionBoundaryProvider is the single source of truth
3. **Intent-Based Execution** - All operations via `submitIntent()` → Runtime flow
4. **Frontend Bends to Backend** - The architecture is rigid by design; fixes must strengthen patterns

### Classification

| Category | Count | Priority | Architectural Impact |
|----------|-------|----------|---------------------|
| **Frontend Architecture Violations** | 2 | P0 | Must fix to align with patterns |
| **Missing Backend Capability** | 1 | P1 | Required for landing page journey |
| **Legacy Anti-Patterns to Remove** | 1 | P1 | Architectural debt |
| **Naming Alignment** | 1 | P2 | Consistency |

---

## P0: Architecture Violations (Fix Required)

### 1. Business Outcomes Page - Session Pattern Violation

**Impact:** Page violates Session-First pattern and will crash at runtime.

**File:** `symphainy-frontend/app/(protected)/pillars/business-outcomes/page.tsx`

**Violations:**

1. **Missing Import**: Uses `useSessionBoundary()` but import is missing
2. **State Shadowing**: Creates local `sessionState` useState that shadows the SessionBoundary state
3. **Pattern Violation**: Page should NOT manage its own session state per Session-First pattern

**Current (WRONG):**
```typescript
// Line 62 - Uses hook but no import
const { state: sessionState } = useSessionBoundary();

// Line 87 - VIOLATES SESSION-FIRST PATTERN - creates local session state
const [sessionState, setSessionState] = useState<any | null>(null);
```

**Correct Pattern:**
Per Session-First architecture, pages should:
- Import and use `useSessionBoundary` for session status checks
- NEVER manage their own session state
- Use `usePlatformState` for realm state (cross-pillar data)

**Fix Required:**
```typescript
// Add import
import { useSessionBoundary, SessionStatus } from "@/shared/state/SessionBoundaryProvider";

// Remove the useState for sessionState entirely - use SessionBoundary
// Line 87 should NOT exist - local session state violates architecture

// For local UI state that's NOT session-related, rename appropriately:
const [localWorkflowState, setLocalWorkflowState] = useState<any | null>(null);
```

**Why This Matters:**
- SessionBoundaryProvider is the single source of truth for session lifecycle
- Duplicating session state leads to desync and bugs
- The architecture is "uncomfortably rigid by design" - strengthening this pattern is correct

---

### 2. Journey Page - Undefined Realm State Functions

**Impact:** Runtime error; also indicates incomplete realm state integration.

**File:** `symphainy-frontend/app/(protected)/pillars/journey/page.tsx`

**Bug:** Lines 189-190 call undefined functions:
```typescript
if (selected.SOP?.uuid) setSelectedSopId(selected.SOP.uuid);
if (selected.workflow?.uuid) setSelectedWorkflowId(selected.workflow.uuid);
```

**Architectural Issue:**
These should use `setRealmState` from PlatformStateProvider, not local state functions.
Per the architecture, realm state is the canonical location for pillar-specific data.

**Correct Pattern:**
```typescript
const { setRealmState } = usePlatformState();

// Instead of local state, use realm state:
if (selected.SOP?.uuid) {
  setRealmState('journey', 'selectedSopId', selected.SOP.uuid);
}
if (selected.workflow?.uuid) {
  setRealmState('journey', 'selectedWorkflowId', selected.workflow.uuid);
}
```

**Why This Matters:**
- Realm state persists across navigation and is synced with Runtime
- Local useState is lost on navigation
- PlatformStateProvider is the correct abstraction

---

## P1: Required Backend Capability

### 3. MVP Solution Journey Endpoints (Backend Required)

**Impact:** Landing page goal-driven journey feature non-functional.

**Context:**
The landing page (`WelcomeJourney.tsx`) offers AI-powered solution structure creation.
This feature calls `/api/v1/mvp-solution/*` endpoints that don't exist.

**Frontend Code:**
```typescript
// symphainy-frontend/shared/services/mvp/core.ts
await mvpSolutionService.getSolutionGuidance(userGoals, userContext);
await mvpSolutionService.customizeSolution(solutionStructure, customizations, userContext);
await mvpSolutionService.createSession(userId, sessionType, userContext);
await mvpSolutionService.navigateToPillar(sessionId, pillar, userContext);
```

**Required Backend Implementation:**
Create `symphainy_platform/civic_systems/experience/api/mvp_solution.py`:

```python
# Architecture-Aligned Implementation:
# 1. /guidance - Uses Guide Agent for reasoning (Agentic Civic System)
# 2. /customize - Returns customized structure (no execution)  
# 3. /session - Uses Runtime to create session (via Traffic Cop SDK)
# 4. /navigate - Updates session context (via State Surface)

@router.post("/guidance")
async def get_solution_guidance(request: GuidanceRequest):
    """
    Guide Agent performs critical reasoning FIRST.
    Returns solution structure with agent reasoning.
    Does NOT execute anything - just provides guidance.
    """
    # Use Guide Agent SDK for reasoning
    result = await guide_agent_sdk.analyze_goals(
        goals=request.user_goals,
        context=request.user_context
    )
    return result

@router.post("/session")
async def create_mvp_session(request: SessionRequest):
    """
    Create session via Runtime (Traffic Cop SDK → Runtime).
    Session-First pattern: session exists before any execution.
    """
    # Use Traffic Cop SDK to prepare session intent
    session_intent = await traffic_cop_sdk.create_session_intent(...)
    # Submit to Runtime
    result = await runtime_client.submit_intent(session_intent)
    return result
```

**Why This Matters:**
- Guide Agent reasoning is part of Agentic Civic System
- Session creation must go through Runtime
- This is a legitimate missing capability, not an architectural workaround

---

## P1: Legacy Anti-Pattern to Remove

### 4. OperationsAPIManager - Direct REST Anti-Pattern

**Impact:** Architectural violation; endpoints don't exist because pattern is wrong.

**File:** `symphainy-frontend/shared/managers/OperationsAPIManager.ts`

**Problem:**
This manager uses direct REST calls to `/api/v1/operations-pillar/*` endpoints.
This violates the Intent-Based Execution principle.

**Current (WRONG):**
```typescript
// OperationsAPIManager.ts - Direct REST calls (ANTI-PATTERN)
async analyzeCoexistence(request) {
  return this.post('/api/v1/operations-pillar/coexistence/analyze', request);
}
```

**Correct Pattern (Already Exists):**
```typescript
// JourneyAPIManager.ts - Intent-based (CORRECT)
async analyzeCoexistence(sopId, workflowId) {
  const execution = await platformState.submitIntent(
    "analyze_coexistence",
    { sop_id: sopId, workflow_id: workflowId }
  );
  return await this._waitForExecution(execution, platformState);
}
```

**Resolution:**
1. **Audit all OperationsAPIManager usages** 
2. **Migrate to JourneyAPIManager** (uses correct intent-based pattern)
3. **Delete OperationsAPIManager** (don't create backend endpoints for it)

**Why This Matters:**
- Backend endpoints should NOT be created for legacy patterns
- JourneyAPIManager already implements correct pattern
- Creating REST endpoints would perpetuate architectural violation
- "Frontend bends to backend" - the intent pattern is correct

---

## P2: Naming Alignment

### 5. Operations vs Journey Naming

**Issue:** The frontend names the pillar "Operations" but uses `/pillars/journey` route.

| Location | Name Used | Route/Path |
|----------|-----------|------------|
| Frontend Pillar Data | "Operations" | `/pillars/journey` |
| Backend Realm | "Operations Realm" | N/A |
| Frontend Page | `journey/page.tsx` | `/pillars/journey` |
| API Manager | `JourneyAPIManager` | N/A |
| Realm State Key | `realm.journey` | N/A |

**Context:** 
The backend was renamed from "Journey Realm" to "Operations Realm" to avoid confusion with the platform concept of "journeys" (user journeys through pillars).

**Decision Required:**
Frontend team to decide: rename route/directory to `/pillars/operations` OR keep current structure and document the mapping.

**Architectural Note:**
This is a naming/consistency issue, NOT an architectural violation. The intent-based API still works correctly.

---

## Clarification: Blueprint Ownership

### Coexistence Blueprint Intent Location

**Question raised:** Is `create_blueprint` an Outcomes or Operations intent?

**Current Backend:**
- `OutcomesSolution` handles `create_blueprint` → `CreateBlueprintService`
- `OperationsSolution` does NOT handle `create_blueprint`

**Frontend:**
- `CoexistenceBlueprint` component uses `JourneyAPIManager.createBlueprint()`
- `OutcomesAPIManager` also has `createBlueprint()`

**Resolution:**
Per the architecture, blueprints are **Purpose-Bound Outcomes** (intentional deliverables).
The `create_blueprint` intent correctly belongs to **Outcomes Realm**.

**Frontend Fix:**
`CoexistenceBlueprint` should use `OutcomesAPIManager.createBlueprint()` to align with backend.

---

## Action Plan (Architecture-Aligned)

### Backend Team Tasks

| Priority | Task | Architectural Alignment |
|----------|------|------------------------|
| P1 | Create MVP Solution API | Agentic (Guide Agent) + Runtime (session) |
| P2 | Verify Operations Realm intents | Runtime Participation Contract |

**MVP Solution API Implementation Notes:**
- `/guidance` - Pure reasoning via Guide Agent (no execution)
- `/session` - Via Runtime (Traffic Cop SDK → Runtime)
- `/navigate` - State Surface update (no execution)
- Must NOT bypass Runtime for session/state

### Frontend Team Tasks

| Priority | Task | Architectural Alignment |
|----------|------|------------------------|
| P0 | Fix Business Outcomes page | Session-First Pattern |
| P0 | Fix Journey page | Realm State (PlatformStateProvider) |
| P1 | Remove OperationsAPIManager | Intent-Based Execution |
| P1 | Update CoexistenceBlueprint | Correct intent routing (Outcomes) |

**Business Outcomes Fix Requirements:**
1. Add missing `useSessionBoundary` import
2. Remove local `sessionState` useState entirely
3. Use SessionBoundary for session checks, PlatformState for realm state
4. This STRENGTHENS Session-First pattern

**Journey Page Fix Requirements:**
1. Replace undefined `setSelectedSopId/setSelectedWorkflowId` with:
   ```typescript
   setRealmState('journey', 'selectedSopId', value)
   setRealmState('journey', 'selectedWorkflowId', value)
   ```
2. This STRENGTHENS Realm State pattern

**OperationsAPIManager Removal:**
1. Audit usages - migrate to `JourneyAPIManager`
2. Delete the file - do NOT create backend endpoints for legacy pattern
3. This REMOVES architectural debt

### Verification Tasks

| Priority | Task | What to Verify |
|----------|------|----------------|
| P0 | Test pillar pages | Pages load without runtime errors |
| P1 | Test intent flow | Content → Insights → Journey → Outcomes journey |
| P1 | Test realm state | State persists across navigation |
| P2 | Test landing page | Graceful handling of missing MVP endpoints |

---

## Appendix: Architectural Reference

### Session-First Pattern Summary
```
SessionBoundaryProvider (ONLY source of session lifecycle)
    ↓ reads from
PlatformStateProvider (syncs session state for realm access)
    ↓ uses
API Managers (submit intents with session context)
    ↓ via
ExperiencePlaneClient → Runtime
```

Pages should:
- ✅ Use `useSessionBoundary()` for session status checks
- ✅ Use `usePlatformState()` for realm state and UI state
- ❌ NEVER manage their own session state
- ❌ NEVER call session APIs directly

### Intent-Based Execution Pattern Summary
```
User Action
    ↓
API Manager (ContentAPIManager, InsightsAPIManager, etc.)
    ↓ calls
platformState.submitIntent(intentType, params)
    ↓ goes to
ExperiencePlaneClient.submitIntent()
    ↓ POST to
/api/intent/submit → Runtime
    ↓
Runtime validates, executes, returns artifacts
    ↓
API Manager waits for completion, updates realm state
```

### File Reference

**Frontend API Managers:**
- `ContentAPIManager.ts` ✅ Intent-based
- `InsightsAPIManager.ts` ✅ Intent-based  
- `JourneyAPIManager.ts` ✅ Intent-based
- `OutcomesAPIManager.ts` ✅ Intent-based
- `OperationsAPIManager.ts` ❌ **LEGACY - TO BE REMOVED**

**Backend API Endpoints:**
- `/api/auth/login` ✅
- `/api/auth/register` ✅
- `/api/session/create` ✅
- `/api/session/create-anonymous` ✅
- `/api/session/upgrade` ✅
- `/api/intent/submit` ✅
- `/api/guide-agent/*` ✅
- `/api/v1/mvp-solution/*` ❌ **TO BE IMPLEMENTED**

**Pillar Pages Status:**
- `content/page.tsx` ✅ Correct patterns
- `insights/page.tsx` ✅ Correct patterns
- `journey/page.tsx` ⚠️ Undefined functions (use setRealmState)
- `business-outcomes/page.tsx` ❌ Session pattern violation

---

## Update: January 27, 2026 - Frontend Fixes Completed

### Changes Made

1. **Renamed JourneyAPIManager → OperationsAPIManager**
   - Aligns frontend API manager name with backend Operations Realm naming
   - Internal state key remains "journey" for backwards compatibility (documented)
   - Updated pillar type from `'journey'` to `'operations'` in API methods
   - Added backwards compatibility aliases for migration period

2. **Fixed Business Outcomes Page (P0)**
   - Added missing `useSessionBoundary` import
   - Removed shadowing local `sessionState` useState
   - Page now correctly uses SessionBoundaryProvider for session state

3. **Fixed Journey Page (P0)**
   - Replaced undefined `setSelectedSopId`/`setSelectedWorkflowId` calls
   - Now uses `setRealmState('journey', 'selectedSopId/selectedWorkflowId', value)`
   - Added `setRealmState` to usePlatformState destructuring
   - Fixed malformed code block structure (bad merge artifact)

4. **Fixed WizardActive Hook Bug**
   - The hook imported `useJourneyAPIManager` but never called it
   - Added missing `const operationsAPIManager = useOperationsAPIManager();` call

5. **Updated Consumer Files**
   - `CoexistenceBlueprint/hooks.ts` → uses `useOperationsAPIManager`
   - `WizardActive/hooks.ts` → uses `useOperationsAPIManager`
   - `LiaisonAgentsAPIManager.ts` → delegates to `OperationsAPIManager`
   - `GuideAgentAPIManager.ts` → delegates to `OperationsAPIManager`
   - `useAgentManager.ts` → dynamically imports `OperationsAPIManager`
   - `page-updated.tsx` → uses `useOperationsAPIManager` (backup file)

6. **Deleted Old Files**
   - `shared/managers/JourneyAPIManager.ts` (replaced by OperationsAPIManager)
   - `shared/hooks/useJourneyAPIManager.ts` (replaced by useOperationsAPIManager)

### Backend Naming Duplication (Identified, Not Fixed)

**Issue:** The backend has BOTH `journey/` and `operations/` directories:
- `symphainy_platform/realms/journey/` - old naming (journey_realm.py, etc.)
- `symphainy_platform/realms/operations/` - new naming (operations_realm.py, etc.)
- `symphainy_platform/solutions/journey_solution/` - old naming
- `symphainy_platform/solutions/operations_solution/` - new naming

**Status:** This requires a separate cleanup effort to:
1. Migrate functionality from `journey/` to `operations/`
2. Update agent definitions that reference "journey realm"
3. Update service factory and MCP client manager references
4. Remove old `journey/` directories

**Recommendation:** Track this as a separate task. The frontend is now correctly aligned to "Operations" naming; backend cleanup can proceed independently.

### Remaining Tasks

| Task | Status | Priority |
|------|--------|----------|
| Frontend manager rename | ✅ Completed | P0 |
| Business Outcomes fix | ✅ Completed | P0 |
| Journey page fix | ✅ Completed | P0 |
| MVP Solution API | ⏳ Pending | P1 |
| Backend journey→operations cleanup | ⏳ Identified | P2 |
