# Frontend Architecture Review & Holistic Refactoring Plan

**Date:** January 21, 2026  
**Status:** Comprehensive Review & Strategic Refactoring Plan

---

## Executive Summary

This document provides:
1. **Review** of the Frontend Architecture Guide (`01212026/frontend_architecture_guide.md`)
2. **Code Audit** identifying gaps between current implementation and architectural vision
3. **Holistic Refactoring Plan** to proactively prevent future issues

**Key Finding:** The architecture guide is **excellent** and aligns perfectly with the Session Boundary pattern we just implemented. However, there are **significant gaps** in the current codebase that need systematic refactoring.

---

## Part 1: Architecture Guide Review

### ✅ What's Excellent

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

7. **Red Flags Checklist**
   - Practical, actionable guardrails
   - Will prevent regression
   - Easy to enforce in code reviews

### 🔍 What Could Be Enhanced

1. **Add: Provider Hierarchy Diagram**
   ```typescript
   SessionBoundaryProvider (session authority)
     └─ AuthProvider (authentication - upgrades session)
         └─ PlatformStateProvider (execution, realm, UI state)
             └─ GuideAgentProvider (agent chat - follows session)
                 └─ Other providers...
   ```
   - Makes dependency relationships explicit
   - Prevents circular dependencies
   - Guides new engineer onboarding

2. **Add: Session State Machine Diagram**
   - Visual representation of state transitions
   - Shows when WebSocket connects/disconnects
   - Clarifies recovery flows

3. **Add: Error Signal Taxonomy**
   ```typescript
   // Session errors → boundary issue
   SessionInvalidError → SessionBoundaryProvider handles
   
   // Agent errors → reasoning surfaced
   AgentExecutionError → UI displays reasoning, doesn't retry
   
   // Tool errors → capability unavailable
   ToolUnavailableError → UI shows alternative, doesn't fail silently
   ```

4. **Add: Component Composition Patterns**
   - How to compose state-aware components
   - When to use hooks vs providers
   - How to handle SSR safely

5. **Add: Testing Strategy**
   - How to test state machines
   - How to test WebSocket following session
   - How to test error signal handling

### ✅ Overall Assessment

**Rating: 9/10**

The guide is **excellent** and provides a solid foundation. The suggested enhancements are minor and can be added incrementally. The core principles are sound and align perfectly with our Session Boundary implementation.

---

## Part 2: Code Audit

### 🔴 Critical Issues (Must Fix)

#### 1. **Multiple Provider Duplication**
**Location:** `shared/agui/`, `shared/session/`, `shared/components/`

**Problem:**
- `shared/agui/AuthProvider.tsx` vs `shared/auth/AuthProvider.tsx`
- `shared/agui/SessionProvider.tsx` vs `shared/components/SessionProvider.tsx` vs `shared/session/GlobalSessionProvider.tsx`
- `shared/agui/AppProvider.tsx` vs `shared/state/AppProviders.tsx`
- `shared/agui/AppProviders.tsx` (duplicate)

**Impact:**
- Confusion about which provider to use
- Potential circular dependencies
- Inconsistent state management
- Hard to maintain

**Recommendation:**
- Consolidate to single source of truth
- Archive/remove duplicates
- Update all imports

#### 2. **Direct API Calls in Components**
**Location:** Multiple components

**Problem:**
- Components calling `fetch()` directly
- Components using `axios` directly
- No consistent error handling
- No session boundary awareness

**Examples Found:**
- `shared/components/chatbot/InteractiveChat.tsx` - checks auth directly
- `shared/hooks/useAgentManager.ts` - creates WebSocket on mount
- Multiple components checking `isAuthenticated` directly

**Impact:**
- Violates "State Drives Actions" principle
- Bypasses SessionBoundaryProvider
- Creates race conditions
- Hard to test

**Recommendation:**
- All API calls through service layer
- Components subscribe to state, don't initiate actions
- Use hooks that wrap service layer

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
- Handle `Invalid` and `Recovering` states

#### 5. **Hidden Global State**
**Location:** `shared/atoms/chatbot-atoms.ts`, `shared/config/`

**Problem:**
- Jotai atoms used for global state
- No clear ownership
- No session boundary awareness
- State persists across sessions

**Impact:**
- State leaks between sessions
- Hard to debug
- Violates "Determinism Over Convenience"

**Recommendation:**
- Move state to `PlatformStateProvider`
- Clear state on session invalidation
- Make state session-scoped

### 🟡 Medium Issues (Should Fix)

#### 6. **Inconsistent Error Handling**
**Location:** Multiple files

**Problem:**
- Some components catch errors, some don't
- Error messages not structured
- No error signal taxonomy

**Recommendation:**
- Standardize error handling in service layer
- Use error signal taxonomy
- Components display errors, don't handle them

#### 7. **API Manager Pattern Inconsistency**
**Location:** `shared/managers/`, `shared/hooks/`

**Problem:**
- Some managers extend `BaseAPIManager`
- Some hooks use managers directly
- Some hooks create managers on mount
- Inconsistent session token handling

**Recommendation:**
- All API calls through service layer
- Hooks wrap service layer, don't create managers
- Session token from `SessionBoundaryProvider`

#### 8. **Routing Not Journey-Aware**
**Location:** `app/` directory structure

**Problem:**
- Routes are page-centric (`/pillars/content`, `/pillars/insights`)
- No journey state in routing
- No artifact context in URLs

**Recommendation:**
- Routes reflect current realm/artifact/journey step
- Workflows live in PlatformState, not routes
- URLs are views, not workflows

### 🟢 Minor Issues (Nice to Have)

#### 9. **Missing Observability**
**Location:** All components

**Problem:**
- No frontend telemetry
- No session transition logging (beyond console.log)
- No agent start/stop events

**Recommendation:**
- Add structured logging
- Emit events for session transitions
- Track agent execution lifecycle

#### 10. **SSR Safety Gaps**
**Location:** Multiple hooks and components

**Problem:**
- Some hooks not SSR-safe
- Some components access `window` without checks
- Some providers not SSR-safe

**Recommendation:**
- Audit all hooks for SSR safety
- Add SSR-safe defaults
- Test with Next.js SSR

---

## Part 3: Holistic Refactoring Plan

### Phase 1: Provider Consolidation (Week 1)

**Goal:** Single source of truth for all providers

**Tasks:**
1. **Audit all providers**
   - List all provider files
   - Identify duplicates
   - Map dependencies

2. **Consolidate providers**
   - Keep: `shared/state/AppProviders.tsx` (main composition)
   - Keep: `shared/state/SessionBoundaryProvider.tsx`
   - Keep: `shared/auth/AuthProvider.tsx`
   - Keep: `shared/state/PlatformStateProvider.tsx`
   - Keep: `shared/agui/GuideAgentProvider.tsx`
   - Archive: All duplicates in `shared/agui/`, `shared/session/`, `shared/components/`

3. **Update imports**
   - Find all imports of archived providers
   - Update to use consolidated providers
   - Test thoroughly

4. **Remove circular dependencies**
   - Map provider dependencies
   - Ensure correct hierarchy
   - Test for circular imports

**Success Criteria:**
- ✅ Single provider file per concern
- ✅ No duplicate providers
- ✅ All imports updated
- ✅ No circular dependencies
- ✅ Build passes

---

### Phase 2: Service Layer Standardization (Week 2)

**Goal:** All API calls go through service layer

**Tasks:**
1. **Audit all API calls**
   - Find all `fetch()` calls
   - Find all `axios` calls
   - Find all direct API manager usage

2. **Create unified service layer**
   - `shared/services/UnifiedServiceLayer.ts` (already exists, enhance)
   - All API calls through this layer
   - Session token from `SessionBoundaryProvider`
   - Consistent error handling

3. **Refactor components**
   - Remove direct API calls
   - Use hooks that wrap service layer
   - Subscribe to state, don't initiate actions

4. **Update hooks**
   - `useContentAPIManager` → wraps service layer
   - `useAgentManager` → uses service layer, doesn't create managers
   - All hooks get session from `SessionBoundaryProvider`

**Success Criteria:**
- ✅ No direct `fetch()` or `axios` calls in components
- ✅ All API calls through service layer
- ✅ Service layer uses `SessionBoundaryProvider` for tokens
- ✅ Consistent error handling

---

### Phase 3: WebSocket Consolidation (Week 2-3)

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
   - Consolidate: Multiple WebSocket managers into one

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

### Phase 4: Session-First Component Refactoring (Week 3)

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

### Phase 5: State Management Consolidation (Week 4)

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

3. **Remove hidden global state**
   - No atoms that persist across sessions
   - No localStorage for session state (already done)
   - All state in providers

4. **Update components**
   - Use `usePlatformState()` instead of atoms
   - Subscribe to state, don't manage it
   - Clear state on session invalidation

**Success Criteria:**
- ✅ All global state in `PlatformStateProvider`
- ✅ No Jotai atoms for global concerns
- ✅ State cleared on session invalidation
- ✅ State is session-scoped

---

### Phase 6: Error Handling Standardization (Week 4-5)

**Goal:** Consistent error signal handling

**Tasks:**
1. **Create error signal taxonomy**
   - `SessionError` → handled by `SessionBoundaryProvider`
   - `AgentError` → displayed to user with reasoning
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

### Phase 7: Routing Refactoring (Week 5)

**Goal:** Routes reflect journey state, not workflows

**Tasks:**
1. **Audit current routing**
   - Review `app/` directory structure
   - Identify page-centric routes
   - Map journey state to routes

2. **Refactor routes**
   - Routes reflect current realm/artifact/journey step
   - Workflows live in `PlatformStateProvider`
   - URLs are views, not workflows

3. **Update navigation**
   - Navigation updates state, not just routes
   - State drives route changes
   - Journey state in URL params

**Success Criteria:**
- ✅ Routes reflect journey state
- ✅ Workflows in state, not routes
- ✅ Navigation updates state first

---

### Phase 8: Observability & Testing (Week 6)

**Goal:** Frontend observability and comprehensive testing

**Tasks:**
1. **Add structured logging**
   - Session transitions
   - Agent start/stop events
   - Realm switches
   - Artifact creation

2. **Add frontend telemetry**
   - Track session lifecycle
   - Track agent execution
   - Track user interactions (privacy-respecting)

3. **Add comprehensive tests**
   - Test state machines
   - Test WebSocket following session
   - Test error signal handling
   - Test SSR safety

**Success Criteria:**
- ✅ Structured logging for key events
- ✅ Frontend telemetry integrated
- ✅ Comprehensive test coverage
- ✅ SSR tests passing

---

## Implementation Priority

### 🔴 Critical (Do First)
1. **Phase 1: Provider Consolidation** - Prevents confusion and bugs
2. **Phase 2: Service Layer Standardization** - Prevents direct API calls
3. **Phase 3: WebSocket Consolidation** - Prevents connection issues
4. **Phase 4: Session-First Component Refactoring** - Prevents auth coupling

### 🟡 Important (Do Next)
5. **Phase 5: State Management Consolidation** - Prevents state leaks
6. **Phase 6: Error Handling Standardization** - Improves UX

### 🟢 Nice to Have (Do Later)
7. **Phase 7: Routing Refactoring** - Improves architecture
8. **Phase 8: Observability & Testing** - Improves maintainability

---

## Success Metrics

### Code Quality
- ✅ No duplicate providers
- ✅ No direct API calls in components
- ✅ WebSocket only connects when session Active
- ✅ All components use `SessionStatus`
- ✅ All state in providers

### Architecture Alignment
- ✅ Follows architecture guide principles
- ✅ Matches Session Boundary pattern
- ✅ State drives actions, not components
- ✅ WebSocket follows session

### Developer Experience
- ✅ Clear provider hierarchy
- ✅ Consistent patterns
- ✅ Easy to add new features
- ✅ Easy to debug

---

## Risk Mitigation

### Risk 1: Breaking Changes
**Mitigation:**
- Phased rollout
- Feature flags for new patterns
- Comprehensive testing
- Rollback plan

### Risk 2: Performance Impact
**Mitigation:**
- Performance testing before/after
- Monitor bundle size
- Optimize service layer
- Lazy load providers

### Risk 3: Developer Confusion
**Mitigation:**
- Clear documentation
- Code examples
- Architecture guide updates
- Team training

---

## Next Steps

1. **Review this plan with team**
2. **Prioritize phases based on current pain points**
3. **Create detailed tickets for Phase 1**
4. **Start with provider consolidation**
5. **Iterate based on learnings**

---

## Conclusion

The architecture guide is **excellent** and provides a solid foundation. The codebase has **significant gaps** that need systematic refactoring. This plan provides a **holistic approach** to align the codebase with the architectural vision and prevent future issues.

**Key Takeaway:** The Session Boundary pattern we just implemented is the foundation. Now we need to systematically refactor the rest of the codebase to follow the same principles.
