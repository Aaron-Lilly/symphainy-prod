# Session Boundary Refactoring Plan

## Executive Summary

This plan refactors our frontend session management from a **distributed cleanup pattern** (whack-a-mole) to a **centralized Session Boundary pattern** used by mature platforms (Salesforce, Slack, Notion, etc.).

### Core Principle
> **Stale state is not a bug. Uncoordinated response to stale state is the bug.**

---

## Current Problems (What We're Reversing)

### ❌ Problem 1: Distributed Cleanup Logic
- Cleanup code scattered across components
- `PlatformStateProvider` tries to clean stale sessions
- `MainLayout` checks session validity
- `RuntimeClient` retries on 403
- Multiple components call `/api/session/*` directly

### ❌ Problem 2: Treating 404/401 as Errors
- 404 "Session not found" → treated as exception
- Components try/catch and "clean up" on 404
- Error logs everywhere
- Retry loops on invalid sessions

### ❌ Problem 3: WebSocket Leads Session State
- `RuntimeClient` connects with stale `session_token`
- Gets 403 → retries 5 times
- Doesn't check if session is valid first
- Creates cascade failures

### ❌ Problem 4: No Single Session Authority
- Multiple components can call session APIs
- No coordination between session state and WebSocket state
- Race conditions on session creation/cleanup

---

## Target Architecture (Session Boundary Pattern)

### ✅ Solution 1: Single Session Authority
**`SessionBoundaryProvider`** - The ONLY component that:
- Calls `/api/session/*` endpoints
- Stores `session_id` in `sessionStorage`
- Manages session lifecycle state machine
- Emits session status to all consumers

### ✅ Solution 2: State Machine, Not Error Handling
```typescript
enum SessionStatus {
  Initializing,    // Checking existing session
  Anonymous,       // Valid anonymous session
  Authenticating,  // Login in progress
  Active,          // Valid authenticated session
  Invalid,         // 404/401 received - session doesn't exist
  Recovering       // Creating new session after invalidation
}
```

**404/401 = State Transition, Not Error**

### ✅ Solution 3: WebSocket Follows Session
- `RuntimeClient` subscribes to `session.status`
- Only connects when `status === Active`
- No retries on 403/401 - escalates to SessionBoundary
- Disconnects immediately on `status === Invalid`

### ✅ Solution 4: Event-Driven, Not Component-Driven
- Backend emits "invalid" via HTTP status (404/401)
- `SessionBoundaryProvider` reacts once
- All consumers update automatically via context
- Zero proactive cleanup in components

---

## Refactoring Steps

### Phase 1: Create SessionBoundaryProvider

#### 1.1 Create Session State Machine
**File**: `shared/state/SessionBoundaryProvider.tsx`

```typescript
enum SessionStatus {
  Initializing,
  Anonymous,
  Authenticating,
  Active,
  Invalid,
  Recovering
}

interface SessionBoundaryState {
  status: SessionStatus;
  sessionId: string | null;
  tenantId: string | null;
  userId: string | null;
  error: string | null;
}
```

**Key Behaviors**:
- **ONLY** component that calls `/api/session/*`
- Treats 404 as transition to `Invalid` status
- Treats 401 as transition to `Invalid` status
- Emits status changes via React Context

#### 1.2 Session Lifecycle Transitions

```
Initializing → (check existing session)
  ├─ Session found → Active (if authenticated) or Anonymous
  └─ 404 → Invalid → Recovering → Anonymous

Anonymous → (user logs in)
  └─ Authenticating → Active

Active → (backend returns 404/401)
  └─ Invalid → Recovering → Anonymous (or re-auth)

Invalid → (recovery initiated)
  └─ Recovering → Anonymous
```

#### 1.3 Remove All Cleanup Logic
**Files to Clean**:
- `PlatformStateProvider.tsx` - Remove stale session cleanup
- `MainLayout.tsx` - Remove session validation checks
- `app/layout.tsx` - Remove pre-init cleanup script
- Any component with `sessionStorage.removeItem` for cleanup

---

### Phase 2: Make RuntimeClient a Follower

#### 2.1 Subscribe to Session Status
**File**: `shared/services/RuntimeClient.ts`

**Current (WRONG)**:
```typescript
// Connects immediately with session_token
connect(sessionToken) {
  this.ws = new WebSocket(url);
  // Retries on 403
}
```

**Target (CORRECT)**:
```typescript
// Only connects when session is Active
useEffect(() => {
  if (sessionStatus === SessionStatus.Active && sessionId) {
    connect(sessionId);
  } else {
    disconnect(); // No retries
  }
}, [sessionStatus, sessionId]);
```

#### 2.2 Remove Retry Logic
- Remove all retry loops on 403/401
- On 403/401: Disconnect immediately, escalate to SessionBoundary
- No "reconnecting in 1000ms" logic

#### 2.3 WebSocket Connection Rules
```typescript
// ONLY connect if:
if (sessionStatus === SessionStatus.Active && sessionId) {
  // Connect
} else {
  // Do not connect
  // Do not retry
  // Wait for SessionBoundary to recover
}
```

---

### Phase 3: Refactor PlatformStateProvider

#### 3.1 Remove Session Management
**File**: `shared/state/PlatformStateProvider.tsx`

**Remove**:
- `createSession()`, `createAnonymousSession()`, `upgradeSession()`
- `getSession()` - move to SessionBoundaryProvider
- Session initialization `useEffect`
- Stale session cleanup logic
- All `sessionStorage` manipulation

**Keep**:
- Execution state management
- Realm state management
- UI state management
- Sync operations (but only when session is Active)

#### 3.2 Subscribe to SessionBoundary
```typescript
const { sessionStatus, sessionId } = useSessionBoundary();

// Only sync when session is Active
useEffect(() => {
  if (sessionStatus === SessionStatus.Active) {
    syncWithRuntime();
  }
}, [sessionStatus]);
```

---

### Phase 4: Update All Consumers

#### 4.1 Components Must Ask Permission
**Pattern for ALL components**:
```typescript
const { sessionStatus, sessionId } = useSessionBoundary();

if (sessionStatus !== SessionStatus.Active) {
  return <SessionRecoveryUI />; // or null
}

// Only fetch protected data when Active
```

#### 4.2 Remove Direct Session API Calls
**Files to Update**:
- Any component calling `client.getSession()` directly
- Any component calling `/api/session/*` directly
- All components must use `useSessionBoundary()` hook

#### 4.3 Update AuthProvider
**File**: `shared/auth/AuthProvider.tsx`

**Remove**:
- Direct calls to `createSession()` or `upgradeSession()`
- Session storage manipulation

**Use**:
- `useSessionBoundary()` to get session status
- Call `upgradeSession()` on SessionBoundaryProvider (not PlatformStateProvider)

---

### Phase 5: Error Handling Refactor

#### 5.1 Treat 404/401 as State Transitions
**File**: `shared/state/SessionBoundaryProvider.tsx`

```typescript
// WRONG (current):
catch (error) {
  if (error.status === 404) {
    console.error("Session not found");
    clearSession();
    createNewSession();
  }
}

// CORRECT (target):
catch (error) {
  if (error.status === 404 || error.status === 401) {
    // This is a state transition, not an error
    setStatus(SessionStatus.Invalid);
    // Recovery will happen automatically
  }
}
```

#### 5.2 Remove Error Logs for Expected Transitions
- No `console.error` for 404/401
- Use `console.info` for state transitions
- Only log actual errors (network failures, etc.)

#### 5.3 UI Responds, Not Panics
```typescript
// Show recovery UI, not error UI
if (sessionStatus === SessionStatus.Invalid) {
  return <SessionRecoveryMessage />;
}

if (sessionStatus === SessionStatus.Recovering) {
  return <SessionRecoveringSpinner />;
}
```

---

## Implementation Checklist

### Step 1: Create SessionBoundaryProvider
- [ ] Create `shared/state/SessionBoundaryProvider.tsx`
- [ ] Implement `SessionStatus` enum
- [ ] Implement state machine transitions
- [ ] Create `useSessionBoundary()` hook
- [ ] Make it the ONLY component calling `/api/session/*`

### Step 2: Remove Cleanup Code
- [ ] Remove stale session cleanup from `PlatformStateProvider.tsx`
- [ ] Remove cleanup script from `app/layout.tsx`
- [ ] Remove session validation from `MainLayout.tsx`
- [ ] Remove all `sessionStorage.removeItem` cleanup calls
- [ ] Remove all `localStorage.removeItem` cleanup calls

### Step 3: Refactor RuntimeClient
- [ ] Remove retry logic on 403/401
- [ ] Subscribe to `SessionBoundaryProvider`
- [ ] Only connect when `status === Active`
- [ ] Disconnect immediately on `status === Invalid`
- [ ] Remove all "reconnecting" logic

### Step 4: Refactor PlatformStateProvider
- [ ] Remove session management methods
- [ ] Remove session initialization logic
- [ ] Subscribe to `SessionBoundaryProvider` for session state
- [ ] Only sync when session is Active

### Step 5: Update AuthProvider
- [ ] Remove direct session creation/upgrade
- [ ] Use `SessionBoundaryProvider` for session operations
- [ ] Remove session storage manipulation

### Step 6: Update All Consumers
- [ ] Find all components calling session APIs directly
- [ ] Replace with `useSessionBoundary()` hook
- [ ] Add permission checks: `if (status !== Active) return null`
- [ ] Remove all try/catch blocks for 404/401

### Step 7: Error Handling
- [ ] Replace error logs with state transition logs
- [ ] Remove error UI for 404/401
- [ ] Add recovery UI for Invalid/Recovering states
- [ ] Only log actual errors (network, etc.)

### Step 8: Testing
- [ ] Test session invalidation flow (404 → Invalid → Recovering → Anonymous)
- [ ] Test WebSocket connection only when Active
- [ ] Test no retries on 403/401
- [ ] Test recovery UI displays correctly
- [ ] Test all components respect session status

---

## Migration Strategy

### Phase A: Add SessionBoundaryProvider (Non-Breaking)
1. Create `SessionBoundaryProvider` alongside `PlatformStateProvider`
2. Wrap app with both providers
3. `SessionBoundaryProvider` manages session, `PlatformStateProvider` subscribes
4. No breaking changes yet

### Phase B: Migrate Consumers (Gradual)
1. Update `RuntimeClient` to subscribe to `SessionBoundaryProvider`
2. Update `AuthProvider` to use `SessionBoundaryProvider`
3. Update components one by one
4. Keep old code working during migration

### Phase C: Remove Old Code (Cleanup)
1. Remove session management from `PlatformStateProvider`
2. Remove all cleanup logic
3. Remove retry logic from `RuntimeClient`
4. Remove direct session API calls

---

## Key Files to Modify

### New Files
- `shared/state/SessionBoundaryProvider.tsx` - **NEW** - Single session authority

### Files to Refactor
- `shared/state/PlatformStateProvider.tsx` - Remove session management
- `shared/services/RuntimeClient.ts` - Make it a follower
- `shared/auth/AuthProvider.tsx` - Use SessionBoundaryProvider
- `shared/components/MainLayout.tsx` - Remove session validation
- `app/layout.tsx` - Remove cleanup script

### Files to Update (Consumers)
- All components using `usePlatformState()` for session
- All components calling session APIs directly
- All WebSocket clients

---

## Success Criteria

### ✅ Session Authority
- Only `SessionBoundaryProvider` calls `/api/session/*`
- All other components subscribe via `useSessionBoundary()`

### ✅ State Machine
- 404/401 trigger state transitions, not errors
- No error logs for expected transitions
- Recovery happens automatically

### ✅ WebSocket Behavior
- Only connects when `status === Active`
- No retries on 403/401
- Disconnects immediately on `status === Invalid`

### ✅ No Cleanup Code
- Zero `sessionStorage.removeItem` for cleanup
- Zero `localStorage.removeItem` for cleanup
- Zero try/catch blocks for 404/401

### ✅ UI Behavior
- Shows recovery UI for Invalid/Recovering states
- No error messages for expected transitions
- Graceful degradation

---

## Expected Outcomes

### Before (Current)
```
GET /api/session/... 404
↓
console.error("Session not found")
↓
Multiple components try to clean up
↓
RuntimeClient still connects
↓
WebSocket 403
↓
Retry loop (x5)
↓
Cascade failure
```

### After (Target)
```
GET /api/session/... 404
↓
SessionBoundaryProvider: status = Invalid
↓
All consumers update automatically
↓
RuntimeClient disconnects (no retry)
↓
SessionBoundaryProvider: status = Recovering
↓
New anonymous session created
↓
SessionBoundaryProvider: status = Anonymous
↓
UI shows normal state
```

---

## Notes

- This is a **fundamental architectural shift**, not a small fix
- The pattern matches what mature platforms do (Salesforce, Slack, Notion)
- It will eliminate the "whack-a-mole" feeling
- It will make session management predictable and testable
- It will solve both the stale state issue AND the SSR issues (SessionBoundaryProvider can be SSR-safe)

---

## Questions to Resolve

1. **Should SessionBoundaryProvider replace PlatformStateProvider entirely?**
   - Option A: Keep both (SessionBoundaryProvider for session, PlatformStateProvider for other state)
   - Option B: Merge into single provider
   - **Recommendation**: Option A (separation of concerns)

2. **How should we handle session recovery UI?**
   - Option A: Silent recovery (no UI)
   - Option B: Show spinner during recovery
   - Option C: Show message "Session expired, restarting..."
   - **Recommendation**: Option C (transparency)

3. **Should we keep anonymous sessions?**
   - Yes (already implemented, aligns with session-first architecture)
   - SessionBoundaryProvider should support Anonymous status

---

## Next Steps

1. Review this plan
2. Create `SessionBoundaryProvider.tsx` with state machine
3. Start Phase A (non-breaking addition)
4. Gradually migrate consumers
5. Remove old cleanup code
6. Test thoroughly
