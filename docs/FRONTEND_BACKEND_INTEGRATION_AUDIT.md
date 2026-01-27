# Frontend/Backend Integration Audit

**Date:** January 22, 2026  
**Status:** 🔴 **CRITICAL ARCHITECTURAL MISMATCH**  
**Priority:** HIGH - Requires Strategic Remediation

---

## Executive Summary

**Critical Finding:** The frontend has **two competing session/state management systems** that are partially migrated, creating a fundamental architectural mismatch with the backend.

### The Problem

1. **Backend Architecture:** Uses Runtime session management via Experience Plane API
   - Sessions created via `/api/sessions` → Runtime → State Surface
   - Session state managed in backend (State Surface, Redis, ArangoDB)
   - Proper session lifecycle (create, get, update, clear)

2. **Frontend Architecture:** Has TWO systems running simultaneously:
   - **NEW:** `PlatformStateProvider` (intended replacement, aligns with backend)
   - **OLD:** `GlobalSessionProvider` (legacy, still used in 52 files)

3. **Current State:**
   - Root layout uses NEW system (`PlatformStateProvider`)
   - 52 components still use OLD system (`GlobalSessionProvider`)
   - Migration was started but **never completed**
   - This creates context errors, state mismatches, and integration failures

---

## Architecture Analysis

### Backend Session Management (✅ Correct)

**Location:** `symphainy_platform/runtime/runtime_api.py`

**Pattern:**
```python
# Backend creates sessions via Runtime
POST /api/sessions
{
  "tenant_id": "...",
  "user_id": "...",
  "metadata": {...}
}

# Response
{
  "session_id": "...",
  "tenant_id": "...",
  "user_id": "...",
  "created_at": "..."
}
```

**State Management:**
- Sessions stored in State Surface (Redis)
- Session state synced with ArangoDB
- Proper lifecycle management
- Experience Plane Client handles API communication

### Frontend Session Management (❌ Inconsistent)

#### System 1: PlatformStateProvider (NEW - Intended)

**Location:** `shared/state/PlatformStateProvider.tsx`

**Status:** ✅ **CORRECTLY ALIGNED WITH BACKEND**

**Features:**
- Uses `ExperiencePlaneClient` to communicate with backend
- Creates sessions via `/api/sessions` → Runtime
- Syncs with Runtime every 30 seconds
- Manages session, execution, realm, and UI state
- Proper session lifecycle (create, get, set, clear)

**Usage:** Only in `shared/state/AppProviders.tsx` (root layout)

#### System 2: GlobalSessionProvider (OLD - Legacy)

**Location:** `shared/agui/GlobalSessionProvider.tsx`

**Status:** ❌ **NOT ALIGNED WITH BACKEND**

**Features:**
- Uses `localStorage` for session storage (client-side only)
- Uses `guideSessionToken` (not backend session_id)
- No backend synchronization
- Pillar states stored locally
- TODO comments indicate "In future, persist to backend"

**Usage:** **52 files still using this**

---

## Impact Analysis

### Current Issues

1. **Context Errors:**
   - Components using `useGlobalSession()` but provider tree has `PlatformStateProvider`
   - Results in "must be used within provider" errors

2. **State Mismatches:**
   - `GlobalSessionProvider` uses `guideSessionToken` from `localStorage`
   - `PlatformStateProvider` uses `sessionId` from backend Runtime
   - These are **different concepts** and don't sync

3. **Session Lifecycle Mismatch:**
   - Backend: Session created via Runtime API
   - Frontend (OLD): Session stored in localStorage
   - Frontend (NEW): Session created via ExperiencePlaneClient → Runtime
   - **No synchronization between OLD and NEW systems**

4. **Authentication Integration:**
   - `AuthProvider` (new) uses `PlatformStateProvider` for sessions
   - But many components still expect `GlobalSessionProvider`
   - Creates authentication/session mismatches

### Files Still Using Old System (52 Total)

**Critical Components:**
- `shared/components/MainLayout.tsx` - Uses `useGlobalSession()`
- `shared/components/chatbot/InteractiveChat.tsx` - Uses `useGlobalSession()`
- `shared/components/chatbot/InteractiveSecondaryChat.tsx` - Uses `useGlobalSession()`
- `shared/agui/GuideAgentProvider.tsx` - Uses `useGlobalSession()`
- All liaison agents (Content, Insights, Operations, Solution, Experience)
- All pillar components (content, insights, journey, outcomes)

**Impact:** These components cannot access session state correctly because the provider tree doesn't include `GlobalSessionProvider`.

---

## Root Cause

### Migration Started But Never Completed

**Evidence:**
1. Migration guide exists: `docs/archived_plans/SESSION_MIGRATION_GUIDE.md`
2. New system created: `PlatformStateProvider`
3. Root layout updated: Uses new `AppProviders`
4. **But:** 52 components still use old system
5. **Result:** Incomplete migration causing architectural mismatch

### Why This Happened

1. **Incremental Migration:** Migration was done incrementally (good approach)
2. **Incomplete:** Migration stopped partway through
3. **No Cleanup:** Old system never removed
4. **No Validation:** No check to ensure all components migrated

---

## Strategic Remediation Plan

### Phase 1: Assessment & Planning (1-2 hours)

**Tasks:**
1. ✅ **DONE:** Audit complete (this document)
2. ⏳ Create migration checklist with all 52 files
3. ⏳ Identify dependencies and migration order
4. ⏳ Create test plan for validation

**Deliverables:**
- Complete file list with migration priority
- Dependency graph
- Test cases for validation

### Phase 2: Core Infrastructure Migration (2-3 hours)

**Priority:** HIGH - Fixes fundamental architecture

**Tasks:**
1. **Update MainLayout** (blocks many components)
   - Replace `useGlobalSession()` with `usePlatformState()`
   - Update session token access pattern
   - Test layout rendering

2. **Update GuideAgentProvider**
   - Replace `useGlobalSession()` with `usePlatformState()`
   - Update session token usage
   - Test agent chat functionality

3. **Update Chat Components**
   - `InteractiveChat.tsx`
   - `InteractiveSecondaryChat.tsx`
   - Update session token access
   - Test chat functionality

**Success Criteria:**
- No context errors
- Chat components work
- MainLayout renders correctly

### Phase 3: Component Migration (4-6 hours)

**Priority:** MEDIUM - Fixes remaining components

**Tasks:**
1. **Liaison Agents** (5 files)
   - ContentLiaisonAgent
   - InsightsLiaisonAgent
   - OperationsLiaisonAgent
   - SolutionLiaisonAgent
   - ExperienceLiaisonAgent

2. **Pillar Components** (20+ files)
   - Content pillar components
   - Insights pillar components
   - Journey pillar components
   - Outcomes pillar components

3. **Other Components** (20+ files)
   - Various UI components
   - Dashboard components
   - Form components

**Migration Pattern:**
```typescript
// BEFORE
import { useGlobalSession } from '@/shared/agui/GlobalSessionProvider';
const { guideSessionToken } = useGlobalSession();

// AFTER
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
const { state } = usePlatformState();
const sessionToken = state.session.sessionId; // or use auth token
```

**Success Criteria:**
- All components migrated
- No references to `GlobalSessionProvider`
- All tests pass

### Phase 4: Cleanup & Validation (1-2 hours)

**Priority:** MEDIUM - Removes technical debt

**Tasks:**
1. **Remove Old System**
   - Delete `shared/agui/GlobalSessionProvider.tsx`
   - Delete `shared/agui/AppProviders.tsx` (old version)
   - Remove unused imports

2. **Update Documentation**
   - Update migration guide (mark as complete)
   - Update architecture docs
   - Update component docs

3. **Validation**
   - Run full test suite
   - Manual testing of all features
   - Verify no context errors
   - Verify session state syncs correctly

**Success Criteria:**
- Old system completely removed
- No broken imports
- All tests pass
- Documentation updated

---

## Migration Pattern Reference

### Pattern 1: Session Token Access

**Before:**
```typescript
import { useGlobalSession } from '@/shared/agui/GlobalSessionProvider';
const { guideSessionToken } = useGlobalSession();
```

**After:**
```typescript
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { useAuth } from '@/shared/auth/AuthProvider';

// Option 1: Use session ID from PlatformState
const { state } = usePlatformState();
const sessionId = state.session.sessionId;

// Option 2: Use auth token (for backward compatibility)
const { sessionToken } = useAuth();
```

### Pattern 2: Session State Access

**Before:**
```typescript
const { getPillarState, setPillarState } = useGlobalSession();
const pillarState = getPillarState('content');
```

**After:**
```typescript
const { getRealmState, setRealmState } = usePlatformState();
const realmState = getRealmState('content', 'key');
```

### Pattern 3: Session Creation

**Before:**
```typescript
// GlobalSessionProvider doesn't create backend sessions
// Just stores token in localStorage
const { setGuideSessionToken } = useGlobalSession();
await setGuideSessionToken(token);
```

**After:**
```typescript
// PlatformStateProvider creates backend sessions
const { createSession } = usePlatformState();
const sessionId = await createSession(tenantId, userId, metadata);
```

### Pattern 4: Session Synchronization

**Before:**
```typescript
// No backend sync - localStorage only
const { guideSessionToken } = useGlobalSession();
```

**After:**
```typescript
// Automatic sync with Runtime every 30 seconds
const { state, syncWithRuntime } = usePlatformState();
// Manual sync if needed
await syncWithRuntime();
```

---

## Risk Assessment

### High Risk Areas

1. **Chat Components**
   - Critical user-facing feature
   - Complex WebSocket integration
   - Requires careful testing

2. **Authentication Flow**
   - Security-critical
   - Session creation timing
   - Token management

3. **Pillar Components**
   - Core functionality
   - Many components
   - State dependencies

### Mitigation Strategies

1. **Incremental Migration:**
   - Migrate one component at a time
   - Test after each migration
   - Rollback if issues found

2. **Feature Flags:**
   - Use feature flags for gradual rollout
   - A/B test if needed
   - Monitor error rates

3. **Comprehensive Testing:**
   - Unit tests for each component
   - Integration tests for flows
   - E2E tests for critical paths

---

## Success Metrics

### Technical Metrics

- ✅ Zero context errors
- ✅ Zero references to `GlobalSessionProvider`
- ✅ All tests passing
- ✅ Session state syncing correctly
- ✅ No localStorage session storage (backend only)

### Functional Metrics

- ✅ Login flow works
- ✅ Chat components work
- ✅ Pillar components work
- ✅ Session persistence works
- ✅ Session restoration works

---

## Recommendations

### Immediate Actions (Today)

1. **Stop using GlobalSessionProvider in new code**
2. **Use PlatformStateProvider for all new components**
3. **Document the migration plan** (this document)

### Short-term (This Week)

1. **Migrate core infrastructure** (MainLayout, GuideAgentProvider, Chat)
2. **Test thoroughly** after each migration
3. **Fix any issues** as they arise

### Medium-term (Next Week)

1. **Complete component migration** (all 52 files)
2. **Remove old system** (GlobalSessionProvider)
3. **Update documentation**

### Long-term (Ongoing)

1. **Monitor session state sync**
2. **Optimize sync frequency** if needed
3. **Add session analytics** for debugging

---

## Conclusion

**The frontend has a fundamental architectural mismatch with the backend due to an incomplete migration from GlobalSessionProvider to PlatformStateProvider.**

**This is causing:**
- Context errors
- State mismatches
- Session lifecycle issues
- Integration failures

**The solution is a strategic, phased migration to complete the transition to PlatformStateProvider, which correctly aligns with the backend's Runtime session management.**

**Estimated Time:** 8-12 hours total
**Priority:** HIGH
**Risk:** MEDIUM (with proper testing and incremental migration)

---

**Next Steps:**
1. Review this audit
2. **See updated plan:** `docs/01242026_final/05_HOLISTIC_PLATFORM_READINESS_PLAN.md`
3. **See migration checklist:** `docs/01242026_final/MIGRATION_CHECKLIST.md`
4. Begin Phase 1 (Frontend State Management Migration)
5. Execute phases incrementally following the holistic plan
