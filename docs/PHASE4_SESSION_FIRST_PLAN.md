# Phase 4: Session-First Component Refactoring - Implementation Plan

**Date:** January 22, 2026  
**Status:** 📋 **IN PROGRESS**

---

## Goal

Components subscribe to session state, not auth. All components handle all session states gracefully.

---

## Implementation Strategy

### Step 1: Audit All Auth Checks
- Find all `isAuthenticated` checks
- Find all `useAuth()` usage
- Find all auth-gated components
- Document current patterns

### Step 2: Create Migration Pattern
- Define how to replace `isAuthenticated` with `SessionStatus`
- Define how to replace `useAuth()` with `useSessionBoundary()`
- Create helper utilities if needed

### Step 3: Refactor Components Systematically
- Start with core layout components (MainLayout)
- Update protected routes
- Update interactive components (InteractiveChat)
- Update remaining components

### Step 4: Remove Auth Assumptions
- Ensure no component assumes auth exists
- All components handle anonymous sessions
- All components handle session invalidation

---

## Session States to Handle

- `Initializing` - Session is being created
- `Anonymous` - Session exists but user not authenticated
- `Authenticating` - User is logging in
- `Active` - User authenticated, session active
- `Invalid` - Session invalidated (404/401)
- `Recovering` - Attempting to recover session

---

## Success Criteria

- ✅ No `isAuthenticated` checks in components
- ✅ All components use `SessionStatus`
- ✅ Components handle all session states
- ✅ No auth assumptions
- ✅ Build passes
- ✅ Validation test passes

---

## Files to Update

1. `components/layout/MainLayout.tsx` (or similar)
2. `components/chat/InteractiveChat.tsx` (or similar)
3. Protected route components
4. Any components using `useAuth()` or `isAuthenticated`

---

## Next Steps

1. Audit auth checks
2. Create migration utilities
3. Refactor components
4. Run validation test
