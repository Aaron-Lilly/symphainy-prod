# Frontend Architecture Guide - Update Summary

**Date:** January 24, 2026  
**Status:** 📋 **RECOMMENDED CHANGES**  
**Reviewer:** Architecture Review vs Current Implementation

---

## Executive Summary

After reviewing yesterday's progress (Phase 7 authentication fixes, WebSocket fixes, routing foundation) and comparing the current codebase against `01212026/frontend_architecture_guide.md`, this document outlines recommended updates to reflect the **actual current state** of the frontend architecture.

**Key Findings:**
- ✅ **SessionBoundaryProvider** is fully implemented (not just planned)
- ✅ **Phase 5, 6, 7** are complete (State Management, Error Handling, Routing)
- ✅ **WebSocket authentication** is fixed and working
- ✅ **Routing utilities** are implemented with state-first navigation
- ⚠️ **AGUI State Layer** is not yet implemented (still planned)
- ⚠️ Some architecture guide sections need updates to reflect actual implementation

---

## Recommended Updates to `01212026/frontend_architecture_guide.md`

### 1. Session & Authentication Model (Section 3) - ✅ UPDATE NEEDED

**Current State in Guide:**
- Lists session states but doesn't show actual implementation
- Doesn't mention `SessionBoundaryProvider` as the canonical implementation

**What's Actually Implemented:**
- ✅ `SessionBoundaryProvider` is the single source of truth for session lifecycle
- ✅ `SessionStatus` enum: `Initializing`, `Anonymous`, `Authenticating`, `Active`, `Invalid`, `Recovering`
- ✅ Anonymous session creation on page load
- ✅ Session upgrade pattern (Anonymous → Active via authentication)
- ✅ Event-driven session recovery (not component-driven cleanup)

**Recommended Update:**
```markdown
### 3.1 Session States

**Implementation:** `SessionBoundaryProvider` (`shared/state/SessionBoundaryProvider.tsx`)

```ts
export enum SessionStatus {
  Initializing = "Initializing",     // Checking existing session
  Anonymous = "Anonymous",           // Valid anonymous session
  Authenticating = "Authenticating", // Login in progress
  Active = "Active",                 // Valid authenticated session
  Invalid = "Invalid",               // 404/401 received - session doesn't exist
  Recovering = "Recovering",        // Creating new session after invalidation
}
```

**Key Implementation Details:**
- ✅ Single source of truth: Only `SessionBoundaryProvider` calls `/api/session/*`
- ✅ Anonymous sessions created on page load (no auth required)
- ✅ Authentication upgrades session (adds `user_id`, `tenant_id`)
- ✅ 404/401 = state transition to `Invalid`, not error
- ✅ Event-driven recovery (no component cleanup logic)
- ✅ WebSocket follows session state (only connects when `Active`)

**Usage Pattern:**
```ts
const { state, upgradeSession } = useSessionBoundary();

// Check session status
if (state.status === SessionStatus.Active) {
  // Session is authenticated and active
}

// Upgrade anonymous session after login
await upgradeSession({
  user_id: userId,
  tenant_id: tenantId,
  access_token: accessToken
});
```
```

---

### 2. WebSocket & Realtime Architecture (Section 5) - ✅ UPDATE NEEDED

**Current State in Guide:**
- States "WebSocket Follows Session" principle
- Doesn't show actual implementation details
- Doesn't mention authentication parameter requirements

**What's Actually Implemented:**
- ✅ `RuntimeClient` only connects when `SessionStatus === Active`
- ✅ WebSocket authentication uses `access_token` (JWT) for authentication
- ✅ WebSocket uses `session_id` for session state (not authentication)
- ✅ No retries on 403/401 - escalates to SessionBoundary
- ✅ Parameter naming: `access_token` + `session_id` (not `session_token`)

**Recommended Update:**
```markdown
### 5.1 WebSocket Follows Session (Law) - ✅ IMPLEMENTED

**Implementation:** `RuntimeClient` (`shared/services/RuntimeClient.ts`)

**Connection Rules:**
```ts
// ✅ CORRECT: Only connect when session is Active
useEffect(() => {
  if (sessionState.status === SessionStatus.Active && sessionToken) {
    const client = new RuntimeClient({
      baseUrl,
      accessToken: accessToken,  // JWT for authentication
      sessionId: sessionId,      // Session ID for state
      autoReconnect: true,
    });
    setRuntimeClient(client);
  }
}, [sessionState.status, sessionToken]);
```

**WebSocket Authentication:**
- Endpoint: `/api/runtime/agent` (Experience Plane)
- Parameters:
  - `access_token`: JWT from Supabase (required for authentication)
  - `session_id`: Session identifier (required for session state)
- Backend validates `access_token` as JWT (not `session_id`)
- Backend uses `session_id` for session operations

**State Transitions:**
- `SessionStatus.Active` → WebSocket connects ✅
- `SessionStatus.Invalid` → WebSocket disconnects immediately (no retry)
- `SessionStatus.Anonymous` → No WebSocket connection (correct behavior)

**No Retry Logic:**
- ❌ No retries on 403/401
- ❌ No "reconnecting in 1000ms" loops
- ✅ Disconnect immediately, escalate to SessionBoundary
```

---

### 3. Routing & Navigation (Section 6) - ✅ UPDATE NEEDED

**Current State in Guide:**
- States "Routes Are Views, Not Workflows"
- Doesn't show actual routing utilities implementation
- Doesn't mention state-first navigation pattern

**What's Actually Implemented:**
- ✅ `routing.ts` utilities (`shared/utils/routing.ts`)
- ✅ `buildPillarRoute()` - Build routes with journey state params
- ✅ `parseRouteParams()` - Parse URL params to journey state
- ✅ `syncRouteToState()` - Sync route → PlatformStateProvider
- ✅ `syncStateToRoute()` - Sync PlatformStateProvider → route
- ✅ State-first navigation: Update state first, then push route
- ✅ Route format: `/pillars/{realm}?artifact=id&step=step&view=view`

**Recommended Update:**
```markdown
### 6.1 Routes Are Views, Not Workflows - ✅ IMPLEMENTED

**Implementation:** `shared/utils/routing.ts`

**Route Structure:**
```
/pillars/{realm}?artifact={id}&step={step}&view={view}
```

**Examples:**
- `/pillars/content?artifact=file-123&step=parse`
- `/pillars/journey?artifact=sop-456&step=analyze&view=detail`
- `/pillars/insights?artifact=analysis-789`

**Routing Utilities:**
```ts
// Build route with journey state
const route = buildPillarRoute("content", {
  artifact: "file-123",
  step: "parse"
});
// Returns: "/pillars/content?artifact=file-123&step=parse"

// Parse route params
const params = parseRouteParams(pathname, searchParams);
// Returns: { artifact: "file-123", step: "parse" }

// Sync route to state (URL → PlatformStateProvider)
syncRouteToState(pathname, searchParams, setRealmState);

// Sync state to route (PlatformStateProvider → URL)
syncStateToRoute(realmState, router);
```

**State-First Navigation Pattern:**
```ts
// ✅ CORRECT: Update state first, then push route
const handleNavigation = (realm: Realm, params?: JourneyStateParams) => {
  // 1. Update PlatformStateProvider state
  setRealmState(realm, params);
  
  // 2. Build route from state
  const route = buildPillarRoute(realm, params);
  
  // 3. Push route (state already updated)
  router.push(route);
};
```

**Route-to-State Synchronization:**
- ✅ Routes reflect current journey state
- ✅ State changes update routes
- ✅ Browser back/forward works correctly
- ✅ Deep linking works (URL → state → UI)
```

---

### 4. Frontend Layering Model (Section 2) - ✅ UPDATE NEEDED

**Current State in Guide:**
- Shows layer overview but doesn't list actual implementations
- Doesn't mention `PlatformStateProvider` vs `SessionBoundaryProvider` separation

**What's Actually Implemented:**
- ✅ `SessionBoundaryProvider` - Session lifecycle (single source of truth)
- ✅ `PlatformStateProvider` - Execution, realm, UI state (not session)
- ✅ `ServiceLayerAPI` - Unified API client layer
- ✅ `RuntimeClient` - WebSocket client (follows session state)
- ✅ `ExperiencePlaneClient` - HTTP client for Experience Plane APIs

**Recommended Update:**
```markdown
### 2.1 Layer Overview - ✅ IMPLEMENTED

```
┌──────────────────────────────┐
│ UI Components (Dumb)         │
├──────────────────────────────┤
│ View Models / Hooks           │
│  - useServiceLayerAPI         │
│  - useFileAPI                 │
│  - useContentAPI              │
├──────────────────────────────┤
│ Frontend State Providers      │
│  - SessionBoundaryProvider    │ ← Session lifecycle (single source)
│  - PlatformStateProvider      │ ← Execution, realm, UI state
│  - AuthProvider               │ ← Authentication (upgrades session)
├──────────────────────────────┤
│ Client Services               │
│  - RuntimeClient              │ ← WebSocket (follows session)
│  - ExperiencePlaneClient     │ ← HTTP (session-aware)
│  - ServiceLayerAPI            │ ← Unified API layer
├──────────────────────────────┤
│ Transport (HTTP / WS)         │
└──────────────────────────────┘
```

**Key Implementations:**
- ✅ `SessionBoundaryProvider`: Session lifecycle, anonymous → authenticated
- ✅ `PlatformStateProvider`: Execution state, realm state, UI state
- ✅ `ServiceLayerAPI`: Unified API client (uses SessionBoundary for tokens)
- ✅ `RuntimeClient`: WebSocket client (only connects when `SessionStatus.Active`)
- ✅ `ExperiencePlaneClient`: HTTP client for Experience Plane APIs

**Separation of Concerns:**
- Session lifecycle ≠ Platform state
- SessionBoundaryProvider owns session
- PlatformStateProvider owns execution/realm/UI
- Services use SessionBoundary for authentication
```

---

### 5. Error Handling Philosophy (Section 8) - ✅ UPDATE NEEDED

**Current State in Guide:**
- States "Errors Are Signals, Not Exceptions"
- Doesn't show actual error handling implementation

**What's Actually Implemented:**
- ✅ `ServiceResult<T>` pattern (`shared/types/errors.ts`)
- ✅ `wrapServiceCall()` utility for consistent error handling
- ✅ `ErrorBoundary` components for React error boundaries
- ✅ Session errors → state transitions (404/401 = `Invalid` status)
- ✅ Agent errors → surfaced to UI (not masked)

**Recommended Update:**
```markdown
### 8.1 Errors Are Signals, Not Exceptions - ✅ IMPLEMENTED

**Implementation:** `ServiceResult<T>` pattern (`shared/types/errors.ts`)

**Error Handling Pattern:**
```ts
type ServiceResult<T> = 
  | { success: true; data: T }
  | { success: false; error: ServiceError };

// Wrap service calls
const result = await wrapServiceCall(async () => {
  return await api.call();
});

if (result.success) {
  // Use result.data
} else {
  // Handle result.error
}
```

**Session Errors:**
- 404/401 → `SessionStatus.Invalid` (state transition, not exception)
- No retry logic in components
- SessionBoundary handles recovery

**Agent Errors:**
- Agent execution errors → surfaced to UI
- Not masked or hidden
- User sees reasoning/explanation

**Component Errors:**
- React ErrorBoundary catches component errors
- Graceful degradation
- Error state shown to user
```

---

### 6. AGUI State Layer - ⚠️ NOT YET IMPLEMENTED

**Current State in Guide:**
- Mentions AGUI as future architecture
- Not yet implemented in codebase

**What's Actually Implemented:**
- ❌ No `useAGUIState()` hook yet
- ❌ No AGUI state management
- ❌ Guide Agent still executes directly (doesn't propose AGUI changes)

**Recommended Update:**
```markdown
### 4.4 AGUI State Layer - 📋 PLANNED (Phase 2.5)

**Status:** Not yet implemented (planned for Phase 2.5)

**Planned Implementation:**
- `useAGUIState()` hook for AGUI state management
- AGUI state persists in session
- Guide Agent proposes AGUI changes (doesn't execute)
- Frontend compiles AGUI → Intent
- Backend validates Intent only

**Current State:**
- Guide Agent executes directly (will be refactored)
- No AGUI state layer yet
- Capability calls still direct (will move to Intent pattern)

**See:** `FRONTEND_ARCHITECTURE_REVIEW_AND_REFACTORING_PLAN_V2.md` for details
```

---

## Summary of Changes

### ✅ Updates Needed (Reflect Actual Implementation)

1. **Section 3 (Session & Authentication):**
   - Add `SessionBoundaryProvider` implementation details
   - Show actual `SessionStatus` enum
   - Document anonymous session creation pattern
   - Document session upgrade pattern

2. **Section 5 (WebSocket & Realtime):**
   - Add `RuntimeClient` implementation details
   - Document authentication parameter requirements (`access_token` + `session_id`)
   - Show connection rules based on `SessionStatus`
   - Document no-retry pattern

3. **Section 6 (Routing & Navigation):**
   - Add `routing.ts` utilities documentation
   - Show state-first navigation pattern
   - Document route-to-state synchronization
   - Show actual route format examples

4. **Section 2 (Layering Model):**
   - List actual provider implementations
   - Show separation: SessionBoundaryProvider vs PlatformStateProvider
   - Document ServiceLayerAPI pattern

5. **Section 8 (Error Handling):**
   - Add `ServiceResult<T>` pattern documentation
   - Show `wrapServiceCall()` usage
   - Document session error → state transition pattern

### ⚠️ Additions Needed (Document Current State)

6. **New Section: Phase 5, 6, 7 Completion Status**
   - Document that Phase 5 (State Management) is complete
   - Document that Phase 6 (Error Handling) is complete
   - Document that Phase 7 (Routing) foundation is complete
   - Reference `FRONTEND_ARCHITECTURE_REVIEW_AND_REFACTORING_PLAN_V2.md` for details

7. **New Section: WebSocket Authentication Fix (January 24, 2026)**
   - Document parameter naming fix (`session_token` → `session_id`)
   - Document authentication validation fix (JWT validation)
   - Reference `PHASE7_AUTH_ISSUE_FIXED.md` for details

### 📋 Keep As-Is (Still Planned)

8. **Section 4.4 (AGUI State Layer):**
   - Mark as "Planned" not "Implemented"
   - Reference Phase 2.5 planning document

---

## Priority

**High Priority (Update Immediately):**
- Section 3 (Session & Authentication) - Core architecture
- Section 5 (WebSocket) - Critical for understanding current implementation
- Section 6 (Routing) - Recently completed, needs documentation

**Medium Priority (Update Soon):**
- Section 2 (Layering Model) - Important for understanding structure
- Section 8 (Error Handling) - Important pattern

**Low Priority (Can Wait):**
- AGUI State Layer section (not yet implemented)
- Add completion status section (nice to have)

---

## Next Steps

1. ✅ Review this summary
2. ⏳ Update `01212026/frontend_architecture_guide.md` with recommended changes
3. ⏳ Add "Implementation Status" section at top of guide
4. ⏳ Cross-reference with `FRONTEND_ARCHITECTURE_REVIEW_AND_REFACTORING_PLAN_V2.md`

---

**Last Updated:** January 24, 2026
