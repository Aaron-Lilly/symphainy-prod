# Phase 5: State Management Consolidation

**Date:** January 22, 2026  
**Status:** 🟡 **IN PROGRESS**

---

## Goal

Single source of truth for all state. All global state in `PlatformStateProvider`, session-scoped, cleared on session invalidation.

---

## Architecture Principles

1. **Single Source of Truth**: All global state in `PlatformStateProvider`
2. **Session-Scoped**: All state cleared on session invalidation
3. **No Hidden State**: No Jotai atoms for global concerns
4. **AGUI Integration**: AGUI state properly managed (already done, verify)
5. **State Lifecycle**: State follows session lifecycle

---

## Tasks

### 1. Audit All State Management

#### 1.1 Audit Jotai Atoms
- [ ] Find all `atom()` declarations
- [ ] Identify global vs local atoms
- [ ] Find duplicate atom definitions
- [ ] Document atom usage patterns

**Files to Check:**
- `shared/atoms/chatbot-atoms.ts`
- `shared/state/core.ts`
- Any other files with `atom(`

#### 1.2 Audit useState for Global Concerns
- [ ] Find `useState` that should be in providers
- [ ] Identify state that persists across sessions
- [ ] Find state that should be session-scoped

#### 1.3 Audit Context Providers
- [ ] List all context providers
- [ ] Identify provider responsibilities
- [ ] Find overlapping/duplicate providers
- [ ] Document provider hierarchy

**Providers to Check:**
- `SessionBoundaryProvider` ✅ (session state)
- `PlatformStateProvider` (platform state)
- `AGUIStateProvider` ✅ (AGUI state - already session-scoped)
- `AuthProvider` (auth state)
- Any other providers

### 2. Consolidate to PlatformStateProvider

#### 2.1 Move Jotai Atoms
- [ ] Move chatbot atoms to `PlatformStateProvider`
- [ ] Move analysis result atoms to `PlatformStateProvider`
- [ ] Remove standalone atom files (or mark as deprecated)
- [ ] Update all atom imports

#### 2.2 Integrate Global useState
- [ ] Move global `useState` to `PlatformStateProvider`
- [ ] Create provider methods for state access
- [ ] Update components to use provider methods

#### 2.3 Remove Duplicate Definitions
- [ ] Remove duplicate atom definitions
- [ ] Consolidate `chatbot-atoms.ts` and `core.ts`
- [ ] Single source of truth for each piece of state

### 3. Integrate AGUI State

#### 3.1 Verify AGUI Integration
- [ ] Verify `AGUIStateProvider` is session-scoped ✅
- [ ] Verify AGUI state clears on session invalidation ✅
- [ ] Verify AGUI state follows session lifecycle ✅

**Status:** Already done in Phase 2.5, verify integration

### 4. Remove Hidden Global State

#### 4.1 Remove Persisting Atoms
- [ ] Ensure no atoms persist across sessions
- [ ] Clear all state on session invalidation
- [ ] Remove localStorage for session state (already done)

#### 4.2 State Lifecycle Management
- [ ] Add state clearing on `SessionStatus.Invalid`
- [ ] Add state clearing on session recovery
- [ ] Ensure state resets on new session

### 5. Update Components

#### 5.1 Update Atom Usage
- [ ] Replace direct atom imports with provider methods
- [ ] Update `useAtom` → provider hooks
- [ ] Update `useSetAtom` → provider methods

#### 5.2 Update State Access
- [ ] Components use provider hooks, not direct atoms
- [ ] Remove direct atom imports
- [ ] Use provider methods for state updates

---

## Success Criteria

- ✅ All global state in `PlatformStateProvider`
- ✅ AGUI state properly managed (verify existing)
- ✅ No Jotai atoms for global concerns
- ✅ State cleared on session invalidation
- ✅ State is session-scoped
- ✅ No duplicate atom definitions
- ✅ Build passes
- ✅ Validation tests pass

---

## Implementation Strategy

### Step 1: Audit (No Changes)
1. Find all atoms
2. Find all global useState
3. Find all providers
4. Document current state

### Step 2: Consolidate (Incremental)
1. Move atoms to PlatformStateProvider
2. Update imports incrementally
3. Test after each group
4. Remove duplicates

### Step 3: Session Scoping
1. Add state clearing logic
2. Test session invalidation
3. Test session recovery
4. Verify state lifecycle

### Step 4: Validation
1. Create validation tests
2. Run smoke tests
3. Verify build passes
4. Document changes

---

## Risk Mitigation

### Risk 1: Breaking Changes
**Mitigation:**
- Incremental migration
- Test after each group
- Keep old atoms working during transition
- Rollback plan

### Risk 2: State Loss
**Mitigation:**
- Careful state migration
- Test state persistence
- Verify state clearing works
- Test session recovery

### Risk 3: Performance Impact
**Mitigation:**
- Monitor bundle size
- Test performance before/after
- Optimize provider updates
- Use memoization where needed

---

## Files to Modify

### Core State Files
- `shared/state/PlatformStateProvider.tsx` - Add atom state
- `shared/atoms/chatbot-atoms.ts` - Mark as deprecated or remove
- `shared/state/core.ts` - Remove duplicate atoms

### Component Files (Update Imports)
- All files using `useAtom`, `useSetAtom`, `useAtomValue`
- Files importing from `shared/atoms/*`

---

## Next Steps

1. **Audit Phase**: Document current state management
2. **Consolidation Phase**: Move atoms to PlatformStateProvider
3. **Session Scoping Phase**: Add state lifecycle management
4. **Validation Phase**: Test and verify

---

## Notes

- AGUI state already properly integrated (Phase 2.5)
- SessionBoundaryProvider handles session state
- Focus on consolidating Jotai atoms and global useState
- Maintain backward compatibility during migration
