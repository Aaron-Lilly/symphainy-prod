# Agent B Task: Test Suite Fixes

**Branch:** `cursor/parameter-assertion-tests-829c`
**Priority:** High
**Estimated Scope:** ~136 failing tests

## Context

The frontend build now passes (all TypeScript errors fixed), but 136/217 Jest tests are failing. Most failures are due to:

1. **Stale mocks** - Tests use old type signatures
2. **Missing provider mocks** - Components need PlatformStateProvider/SessionBoundaryProvider
3. **Async timeouts** - Tests need longer timeouts or better async handling

## Your Tasks

### Task 1: Update Jest Setup Mocks

File: `jest.setup.js`

The global mocks need to match the new `ExecutionStatusResponse` type:

```javascript
// Current mock returns wrong shape - needs:
// { execution_id, status, intent_id, error?, artifacts? }
```

### Task 2: Fix Phase 1 Cross-Pillar Tests

File: `__tests__/phase1-cross-pillar-navigation.test.tsx`

These tests are timing out. Issues:
- `setRealmState` is async but tests don't await
- Need to increase timeout or fix async handling

```typescript
// Example fix pattern:
await waitFor(() => {
  expect(screen.getByTestId('content-state')).toHaveTextContent('files');
}, { timeout: 10000 });
```

### Task 3: Fix Provider-Dependent Tests

Many component tests fail because they render without providers. Pattern to fix:

```typescript
// Bad - no providers
render(<ContentPillarUpload />);

// Good - wrap with providers
render(
  <SessionBoundaryProvider>
    <PlatformStateProvider>
      <ContentPillarUpload />
    </PlatformStateProvider>
  </SessionBoundaryProvider>
);
```

### Task 4: Update Type Assertions in Tests

Tests that check `status.artifacts?.something.property` need type assertions:

```typescript
// Bad
expect(status.artifacts?.file.id).toBe('123');

// Good
const fileArtifact = status.artifacts?.file as { id?: string } | undefined;
expect(fileArtifact?.id).toBe('123');
```

## Files to Focus On

Priority order:
1. `jest.setup.js` - Fix global mocks first
2. `__tests__/phase1-*.test.tsx` - Cross-pillar tests
3. `__tests__/unit/*.test.tsx` - Unit tests
4. `__tests__/integration/*.test.tsx` - Integration tests (may need backend)

## Success Criteria

- [ ] Jest runs without crashes
- [ ] At least 150/217 tests passing
- [ ] No TypeScript errors in test files
- [ ] All provider-dependent tests wrapped correctly

## Commands

```bash
# Run all tests
cd /workspace/symphainy-frontend && npm test

# Run specific test file
npm test -- __tests__/phase1-cross-pillar-navigation.test.tsx

# Run with verbose output
npm test -- --verbose

# Run and show coverage
npm test -- --coverage
```

## Coordination

- **Agent A (me)** is working on: Component migration to new hooks
- **You (Agent B)** are working on: Test fixes
- **Don't touch**: `shared/hooks/useFileOperations.ts`, `shared/hooks/useInsightsOperations.ts` (I'm using these)

## Git Workflow

```bash
# You're on the same branch
git pull origin cursor/parameter-assertion-tests-829c

# Commit frequently
git add -A && git commit -m "Fix: [describe what you fixed]"
git push
```
