# Frontend Architecture Review & Holistic Refactoring Plan (V2)

**Date:** January 22, 2026  
**Status:** Comprehensive Review & Integrated Strategic Refactoring Plan  
**Version:** 2.0 - Updated with Breaking Changes & AGUI Architecture

---

## Executive Summary

This document provides:
1. **Review** of the Frontend Architecture Guide (`01212026/frontend_architecture_guide.md`)
2. **Review** of AGUI Architecture (`01212026/AGUIinthefrontend.md`)
3. **Code Audit** identifying gaps between current implementation and architectural vision
4. **Holistic Refactoring Plan** integrating breaking changes and AGUI architecture

**Key Findings:**
- The architecture guide is **excellent** and aligns with Session Boundary pattern
- AGUI architecture proposal is **strategically sound** and should be integrated **natively** as we refactor
- Breaking changes are **necessary** to enforce proper architecture
- Current codebase has **significant gaps** requiring systematic refactoring
- **Backend assessment confirms:** No backend changes needed for MVP (frontend compiles AGUI → Intent, backend validates Intent only)

---

## Part 1: Architecture Review

### 1.1 Frontend Architecture Guide Review

#### ✅ What's Excellent

1. **"Frontend is a Platform Runtime" Reframe**
   - Perfectly captures the architectural shift needed
   - Aligns with Session Boundary pattern
   - Sets correct mental model for engineers

2. **Session-First, Auth-Second Principle**
   - Matches our SessionBoundaryProvider implementation
   - Correctly identifies the coupling problem
   - Provides clear prevention strategy

3. **State Drives Actions, Not Components**
   - Critical principle we've been implementing
   - Prevents UI-triggered backend reality anti-pattern
   - Aligns with agentic forward pattern

4. **Layering Model**
   - Clear separation of concerns
   - Correct hierarchy (UI → View Models → Providers → Services → Transport)
   - Prevents direct component-to-transport coupling

5. **WebSocket Follows Session**
   - Matches our RuntimeClient refactoring
   - Correctly identifies retry anti-patterns
   - Treats disconnects as state transitions

6. **Error Handling Philosophy**
   - "Errors are signals, not exceptions" is spot-on
   - Aligns with Session Boundary pattern (404/401 = state transitions)
   - Prevents error masking

### 1.2 AGUI Architecture Review

#### ✅ Core Proposal Assessment

The AGUI architecture proposal (`AGUIinthefrontend.md`) is **strategically sound** and aligns with our existing patterns:

1. **Frontend as Reference Implementation** ✅
   - Frontend defines the interaction contract
   - Experience SDK follows the frontend, not leads it
   - Stronger position than dogfooding

2. **AGUI as First-Class Primitive** ✅
   - New "Experience State Layer" for AGUI state
   - Hooks: `useAGUIState()`, `useJourneyStep()`, `useAGUIValidator()`
   - AGUI state persists in session

3. **Agent Role Change** ✅
   - Guide Agent → **proposes AGUI changes** (doesn't execute)
   - Chat → **AGUI mutation + explanation UI**
   - Removes non-determinism at UI layer

4. **Capability Calls → Intent Submission** ✅
   - ❌ `parseFile()` → ✅ `updateAGUI()` + `submitIntent()`
   - ❌ `analyzeData()` → ✅ `updateAGUI()` + `submitIntent()`
   - Frontend stops calling capabilities directly

5. **Pillar Pages → AGUI Views** ✅
   - Pages render AGUI steps
   - Same UI, different contract

#### ⚠️ Implementation Strategy

**Recommendation: Hybrid Incremental Approach**

- ✅ Add AGUI foundation (hooks, state layer) - **Phase 2.5** (Native Integration)
- ✅ Assess backend AGUI support needs - **Phase 2.6** (Backend Assessment)
- ✅ Keep existing patterns working initially
- ✅ Implement one journey (Agentic SDLC) as proof of concept
- ✅ Learn and iterate before expanding

**Why This Works:**
- Lays foundation without breaking everything
- Validates pattern before full commitment
- Doesn't derail Phase 2 (service layer)
- Takes advantage of "breaking change" window
- Can always expand later

---

## Part 2: Code Audit

### 🔴 Critical Issues (Must Fix)

#### 1. **Multiple Provider Duplication** ✅ (Phase 1 Complete)
**Status:** Resolved in Phase 1
- Consolidated to single source of truth
- Archived duplicates
- All imports updated

#### 2. **Direct API Calls in Components** ⏳ (Phase 2 In Progress)
**Location:** Multiple components

**Problem:**
- Components calling `fetch()` directly
- Components using `axios` directly
- Components importing `lib/api/*` directly
- No consistent error handling
- No session boundary awareness

**Examples Found:**
- `shared/auth/AuthProvider.tsx` - ✅ Fixed (uses ServiceLayerAPI)
- `shared/agui/AGUIEventProvider.tsx` - ✅ Fixed (uses ServiceLayerAPI)
- `components/content/FileDashboard.tsx` - ✅ Fixed (uses useFileAPI)
- `components/content/FileUploader.tsx` - ⏳ Needs update
- Multiple other components - ⏳ Need update

**Impact:**
- Violates "State Drives Actions" principle
- Bypasses SessionBoundaryProvider
- Creates race conditions
- Hard to test

**Recommendation:**
- ✅ **BREAKING CHANGE:** All API calls through service layer hooks
- ✅ Mark `lib/api/*` as internal
- ✅ Remove direct imports (build will fail)
- ✅ Components use hooks only

#### 3. **WebSocket Created on Component Mount**
**Location:** `shared/hooks/useAgentManager.ts`, `shared/components/chatbot/`

**Problem:**
```typescript
// ❌ BAD: WebSocket created on mount
useEffect(() => {
  if (sessionToken) {
    wsManager.connect(sessionToken); // Wrong!
  }
}, [sessionToken]);
```

**Impact:**
- Violates "WebSocket Follows Session" principle
- Creates connections before session is Active
- Retries on 403/401 (we fixed this in RuntimeClient, but not everywhere)

**Recommendation:**
- WebSocket only connects when `SessionStatus === Active`
- Use `GuideAgentProvider` pattern (already implemented correctly)
- Remove all other WebSocket creation logic

#### 4. **Auth Checks Inside Components**
**Location:** `shared/components/MainLayout.tsx`, `shared/components/chatbot/`

**Problem:**
```typescript
// ❌ BAD: Component checks auth directly
const { isAuthenticated } = useAuth();
if (!isAuthenticated) {
  return <LoginScreen />;
}
```

**Impact:**
- Violates "Session-First, Auth-Second" principle
- Components assume auth exists
- Doesn't handle session invalidation gracefully

**Recommendation:**
- Components subscribe to `SessionBoundaryProvider` state
- Use `SessionStatus` enum, not `isAuthenticated` boolean
- Handle all session states: `Initializing`, `Anonymous`, `Authenticating`, `Active`, `Invalid`, `Recovering`

#### 5. **Missing AGUI State Layer**
**Location:** N/A (doesn't exist yet)

**Problem:**
- No AGUI state management
- No `useAGUIState()` hook
- No AGUI schema validation
- No journey step enforcement
- Guide Agent executes instead of proposing

**Impact:**
- Non-deterministic UI behavior
- Agents execute directly (should propose AGUI changes)
- No clear separation between planning and execution

**Recommendation:**
- Create AGUI State Layer (Phase 2.5 - Native Integration)
- Add `useAGUIState()` hook (first-class primitive)
- Assess backend AGUI support needs (Phase 2.6 - Backend Assessment)
- Refactor Guide Agent to propose AGUI changes
- Implement one journey (Agentic SDLC) as proof of concept

---

## Part 3: Integrated Refactoring Plan

### Phase 1: Provider Consolidation ✅ **COMPLETE**

**Goal:** Single source of truth for all providers

**Status:** ✅ Completed
- Consolidated all providers
- Archived duplicates
- Updated all imports
- No circular dependencies

**Success Criteria:** ✅ All met

---

### Phase 2: Service Layer Standardization (BREAKING CHANGES) ⏳ **IN PROGRESS**

**Goal:** All API calls go through service layer (breaking changes)

**Status:** ⏳ In Progress
- ✅ ServiceLayerAPI created
- ✅ useServiceLayerAPI hook created
- ✅ useFileAPI hook created
- ✅ AuthProvider updated
- ✅ AGUIEventProvider updated
- ✅ FileDashboard updated
- ⏳ Marking `lib/api/*` as internal
- ⏳ Updating remaining components

**Breaking Change Strategy:**
1. **Mark `lib/api/*` as Internal**
   - Add `@internal` JSDoc tags
   - Add deprecation warnings
   - Keep functions working but warn developers

2. **Update Components by Feature Area**
   - Group 1: File Management ✅ (FileDashboard done)
   - Group 2: Content Operations ⏳
   - Group 3: Insights ⏳
   - Group 4: Operations ⏳
   - Group 5: Auth Forms ⏳
   - Group 6: Admin/Other ⏳

3. **Remove Direct Access**
   - After all components updated
   - Remove exports from `lib/api/*` (or make truly internal)
   - Build will fail if anyone imports directly

**Migration Pattern:**

**Before (Breaking):**
```typescript
import { listFiles } from "@/lib/api/fms"; // ❌ No longer allowed
const token = sessionStorage.getItem("access_token");
const files = await listFiles(token);
```

**After (Required):**
```typescript
import { useFileAPI } from "@/shared/hooks/useFileAPI"; // ✅ Required
const { listFiles } = useFileAPI();
const files = await listFiles(); // Token automatic
```

**Success Criteria:**
- ✅ No direct `lib/api/*` imports in components
- ✅ All components use hooks
- ✅ All API calls go through service layer
- ✅ Service layer uses SessionBoundaryProvider for tokens
- ✅ Build fails if someone tries to import `lib/api/*` directly
- ✅ Consistent error handling

---

### Phase 2.5: AGUI Foundation (Incremental) 📋 **PLANNED**

**Goal:** Lay foundation for AGUI architecture without breaking everything

**Strategy:** Hybrid incremental approach

**Tasks:**

1. **Create AGUI State Layer (Minimal)**
   - Create `useAGUIState()` hook
   - Store AGUI state in session (via SessionBoundaryProvider)
   - Define AGUI schema structure
   - Keep it simple - just state management for now

2. **Create AGUI Hooks**
   - `useAGUIState()` - main AGUI state hook
   - `useJourneyStep()` - current journey step
   - `useAGUIValidator()` - schema validation
   - Integrate with SessionBoundaryProvider

3. **Refactor Guide Agent (Incremental)**
   - Keep current functionality working
   - Add AGUI proposal pattern alongside existing pattern
   - Guide Agent proposes AGUI changes (doesn't execute)
   - Gradually shift from execution → proposal

4. **Implement One Journey (Proof of Concept)**
   - Agentic SDLC as suggested in AGUI doc
   - Use as learning/validation
   - Full AGUI → Intent → Execution flow
   - Learn from it before expanding

5. **Update Service Layer for AGUI**
   - Add `updateAGUI()` function
   - Add `submitIntentFromAGUI()` function
   - Service layer supports both patterns initially
   - Gradually shift to AGUI + Intent pattern

**What We Keep:**
- ✅ Existing patterns working
- ✅ Current Guide Agent functionality
- ✅ Current capability calls (for now)
- ✅ MVP demos working

**What We Add:**
- ✅ AGUI state management
- ✅ AGUI hooks
- ✅ One journey using AGUI pattern
- ✅ Foundation for future expansion

**Success Criteria:**
- ✅ `useAGUIState()` hook exists and works
- ✅ AGUI state persists in session
- ✅ Guide Agent can propose AGUI changes
- ✅ One journey (Agentic SDLC) uses AGUI end-to-end
- ✅ Existing functionality still works
- ✅ Pattern validated before expanding

**Timing:** 
- **Foundation (Hooks, State Layer):** Now (Phase 2.5)
- **Integration into Refactoring:** Phases 3-8 (as we refactor components)
- **Full Migration:** After validation (Phase 8+)

---

### Phase 3: WebSocket Consolidation

**Goal:** WebSocket only connects when session is Active

**Tasks:**
1. **Audit all WebSocket creation**
   - Find all `new WebSocket()` calls
   - Find all WebSocket manager creation
   - Find all WebSocket connection logic

2. **Consolidate to GuideAgentProvider pattern**
   - All WebSocket connections through `GuideAgentProvider`
   - Only connects when `SessionStatus === Active`
   - Disconnects immediately when session becomes Invalid
   - No retries on 403/401

3. **Remove duplicate WebSocket clients**
   - Keep: `shared/services/RuntimeClient.ts` (for Guide Agent)
   - Keep: `shared/agui/GuideAgentProvider.tsx` (wrapper)
   - Archive: Other WebSocket clients if not needed

4. **Update components**
   - Remove WebSocket creation from components
   - Use `GuideAgentProvider` for all agent chat
   - Subscribe to connection state, don't create connections

**Success Criteria:**
- ✅ WebSocket only connects when `SessionStatus === Active`
- ✅ WebSocket disconnects on session invalidation
- ✅ No retries on 403/401
- ✅ All WebSocket logic in `GuideAgentProvider`

---

### Phase 4: Session-First Component Refactoring

**Goal:** Components subscribe to session state, not auth

**Tasks:**
1. **Audit all auth checks**
   - Find all `isAuthenticated` checks
   - Find all `useAuth()` usage
   - Find all auth-gated components

2. **Refactor to session-first**
   - Replace `isAuthenticated` with `SessionStatus`
   - Use `useSessionBoundary()` instead of `useAuth()` for session state
   - Handle all session states: `Initializing`, `Anonymous`, `Authenticating`, `Active`, `Invalid`, `Recovering`

3. **Update components**
   - `MainLayout.tsx` - use `SessionStatus` instead of `isAuthenticated`
   - `InteractiveChat.tsx` - only connect when `Active`
   - All protected routes - check `SessionStatus`, not `isAuthenticated`

4. **Remove auth assumptions**
   - No component assumes auth exists
   - All components handle anonymous sessions
   - All components handle session invalidation

**Success Criteria:**
- ✅ No `isAuthenticated` checks in components
- ✅ All components use `SessionStatus`
- ✅ Components handle all session states
- ✅ No auth assumptions

---

### Phase 5: State Management Consolidation

**Goal:** Single source of truth for all state

**Tasks:**
1. **Audit all state management**
   - Find all Jotai atoms
   - Find all `useState` for global concerns
   - Find all context providers

2. **Consolidate to PlatformStateProvider**
   - Move Jotai atoms to `PlatformStateProvider`
   - Clear state on session invalidation
   - Make state session-scoped

3. **Integrate AGUI State**
   - AGUI state in PlatformStateProvider (or separate AGUI provider)
   - AGUI state cleared on session invalidation
   - AGUI state session-scoped

4. **Remove hidden global state**
   - No atoms that persist across sessions
   - No localStorage for session state (already done)
   - All state in providers

**Success Criteria:**
- ✅ All global state in `PlatformStateProvider`
- ✅ AGUI state properly managed
- ✅ No Jotai atoms for global concerns
- ✅ State cleared on session invalidation
- ✅ State is session-scoped

---

### Phase 6: Error Handling Standardization

**Goal:** Consistent error signal handling

**Tasks:**
1. **Create error signal taxonomy**
   - `SessionError` → handled by `SessionBoundaryProvider`
   - `AgentError` → displayed to user with reasoning
   - `AGUIError` → AGUI validation/state errors
   - `ToolError` → shown as capability unavailable
   - `NetworkError` → retry with backoff

2. **Standardize error handling in service layer**
   - All errors structured
   - Error signals, not exceptions
   - Consistent error format

3. **Update components**
   - Components display errors, don't handle them
   - Error boundaries for unexpected errors
   - User-friendly error messages

**Success Criteria:**
- ✅ Error signal taxonomy defined
- ✅ Service layer handles errors consistently
- ✅ Components display errors, don't handle them
- ✅ User-friendly error messages

---

### Phase 7: Routing Refactoring

**Goal:** Routes reflect journey state, not workflows

**Scope:** MVP routes only (capability by design, implementation by policy)

**Tasks:**
1. **Audit current routing**
   - Review `app/` directory structure
   - Identify page-centric routes
   - Map journey state to routes
   - **Include `/admin` (Platform Showcase) as MVP route**

2. **Refactor routes**
   - Routes reflect current realm/artifact/journey step
   - Workflows live in `PlatformStateProvider` (or AGUI state)
   - URLs are views, not workflows
   - **Apply to all MVP routes:**
     - `/` (protected) - Main dashboard
     - `/pillars/content` - Content pillar
     - `/pillars/insights` - Insights pillar
     - `/pillars/journey` - Journey pillar
     - `/pillars/business-outcomes` - Business outcomes pillar
     - `/admin` - Platform Showcase (formerly Admin Dashboard)
     - `/login` - Authentication

3. **Update navigation**
   - Navigation updates state, not just routes
   - State drives route changes
   - Journey state in URL params

**Success Criteria:**
- ✅ Routes reflect journey state
- ✅ Workflows in state, not routes
- ✅ Navigation updates state first
- ✅ All MVP routes refactored

---

### Phase 7.5: Platform Showcase Integration & Navigation

**Goal:** Ensure Platform Showcase (`/admin`) is in sync with backend vision and accessible to users

**Prerequisites:**
- Phase 7 complete (routing refactored)
- Backend vision for Platform Showcase assessed

**Tasks:**
1. **Sync with backend vision**
   - Review backend Platform Showcase requirements
   - Ensure frontend aligns with backend architecture
   - Update Platform Showcase components as needed

2. **Add navigation access**
   - Add Platform Showcase link to main layout titlebar
   - Make it visually distinct and "lower key" than pillars
   - Use hyperlink or subtle visual treatment
   - Ensure it's accessible but doesn't compete with primary navigation

3. **Update Platform Showcase route**
   - Ensure route follows Phase 7 patterns
   - Journey state integration if applicable
   - Consistent with other MVP routes

**Success Criteria:**
- ✅ Platform Showcase in sync with backend vision
- ✅ Navigation link added to titlebar
- ✅ Visually distinct but lower key than pillars
- ✅ Accessible to users
- ✅ Follows Phase 7 routing patterns

---

### Phase 8: AGUI Expansion (After Validation)

**Goal:** Expand AGUI pattern to all journeys

**Prerequisites:**
- Phase 2.5 foundation complete (AGUI foundation native, Agentic SDLC journey deferred to post-MVP)
- Phase 2.6 complete (backend AGUI support assessed - no changes needed for MVP)
- AGUI ready for MVP use cases (can use when complexity warrants it)
- Pattern proven and documented
- Backend validates Intent (already implemented, no changes needed)

**Tasks:**
1. **Refactor remaining journeys**
   - Content pillar → AGUI views
   - Insights → AGUI views
   - Operations → AGUI views

2. **Refactor Guide Agent fully**
   - Guide Agent only proposes AGUI changes
   - Never executes directly
   - All execution through Intent submission

3. **Remove direct capability calls**
   - Replace `parseFile()` → `updateAGUI()` + `submitIntent()`
   - Replace `analyzeData()` → `updateAGUI()` + `submitIntent()`
   - All capabilities through Intent submission

4. **Update service layer**
   - Service layer fully supports AGUI pattern
   - Remove legacy capability call patterns
   - All calls go through AGUI → Intent flow

**Success Criteria:**
- ✅ All journeys use AGUI pattern
- ✅ Guide Agent only proposes, never executes
- ✅ No direct capability calls
- ✅ All execution through Intent submission
- ✅ Frontend is deterministic

---

## Implementation Priority

### 🔴 Critical (Do First)
1. **Phase 2: Service Layer Standardization** ✅ **COMPLETE** - Prevents direct API calls, enforces architecture
2. **Phase 2.5: AGUI Native Integration** - Makes AGUI native platform language, integrates into refactoring
3. **Phase 2.6: Backend AGUI Assessment** - Assesses backend needs, ensures Experience Service supports AGUI
4. **Phase 3: WebSocket Consolidation** - Prevents connection issues
5. **Phase 4: Session-First Component Refactoring** - Prevents auth coupling

### 🟡 Important (Do Next)
5. **Phase 5: State Management Consolidation** - Prevents state leaks, integrates AGUI state
6. **Phase 6: Error Handling Standardization** - Improves UX

### 🟢 Nice to Have (Do Later)
7. **Phase 7: Routing Refactoring** - Improves architecture
7.5. **Phase 7.5: Platform Showcase Integration & Navigation** - Sync with backend, add navigation access
8. **Phase 8: AGUI Expansion** - Full AGUI pattern (after validation)

---

## Success Metrics

### Code Quality
- ✅ No duplicate providers
- ✅ No direct API calls in components
- ✅ No direct `lib/api/*` imports
- ✅ WebSocket only connects when session Active
- ✅ All components use `SessionStatus`
- ✅ All state in providers
- ✅ AGUI state properly managed

### Architecture Alignment
- ✅ Follows architecture guide principles
- ✅ Matches Session Boundary pattern
- ✅ State drives actions, not components
- ✅ WebSocket follows session
- ✅ AGUI pattern implemented (incrementally)
- ✅ Frontend is reference implementation

### Developer Experience
- ✅ Clear provider hierarchy
- ✅ Consistent patterns
- ✅ Easy to add new features
- ✅ Easy to debug
- ✅ AGUI hooks available

---

## Risk Mitigation

### Risk 1: Breaking Changes
**Mitigation:**
- Phased rollout
- Incremental updates by feature area
- Comprehensive testing after each group
- Rollback plan

### Risk 2: AGUI Complexity
**Mitigation:**
- Start minimal (just foundation)
- Validate with one journey first
- Keep existing patterns working
- Learn before expanding

### Risk 3: Scope Creep
**Mitigation:**
- Clear phase boundaries
- Don't rebuild everything at once
- Focus on foundation first
- Expand only after validation

### Risk 4: Performance Impact
**Mitigation:**
- Performance testing before/after
- Monitor bundle size
- Optimize service layer
- Lazy load providers

---

## Next Steps

1. **Complete Phase 2 Testing**
   - Test updated components (AuthProvider, AGUIEventProvider, FileDashboard)
   - Verify no regressions
   - Document any issues

2. **Continue Phase 2**
   - Mark remaining `lib/api/*` files as internal
   - Update remaining components by feature area
   - Remove direct access

3. **Plan Phase 2.5**
   - Design AGUI state structure
   - Design `useAGUIState()` hook
   - Plan Agentic SDLC journey implementation

4. **Iterate Based on Learnings**
   - Adjust plan based on Phase 2 results
   - Validate AGUI pattern before expanding
   - Document patterns and best practices

---

## Conclusion

This integrated plan combines:
- ✅ **Breaking changes** to enforce proper architecture
- ✅ **AGUI foundation** to enable future deterministic UI
- ✅ **Incremental approach** to minimize risk
- ✅ **Holistic vision** that doesn't lose sight of the big picture

**Key Takeaways:**
1. Breaking changes are necessary and now is the time
2. AGUI architecture is strategically sound and should be integrated **natively** as we refactor
3. AGUI becomes the **native platform language** for complex interactions, not an add-on
4. Foundation first (Phase 2.5), backend assessment (Phase 2.6), expansion after validation
5. Don't rebuild everything - integrate AGUI patterns where they make sense as we refactor
6. Frontend becomes the reference implementation that defines the Experience SDK contract
7. Backend changes (if any) should be contained in Experience Civic System

The Session Boundary pattern we implemented is the foundation. Now we systematically refactor to align with the architectural vision while adding AGUI as a first-class primitive.
