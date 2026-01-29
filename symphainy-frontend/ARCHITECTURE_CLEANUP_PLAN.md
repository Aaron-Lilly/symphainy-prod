# Frontend Architecture Cleanup Plan

**Goal**: Transform the frontend into a production-ready, architecturally-aligned codebase that properly connects to the Runtime-based backend.

**Principles**:
- No backwards compatibility concerns - do it right
- No stubs - real connections only
- No `any` types - full type safety
- No overlapping providers - single source of truth
- Every component follows the same pattern

---

## Current State Analysis

| Metric | Count | Target |
|--------|-------|--------|
| Total TypeScript files | 515 | - |
| `any` type usages | 565 | 0 |
| Stub API imports | 28 | 0 |
| Provider files | 10+ | 2 |
| Tests passing | 113/259 (44%) | 90%+ |

---

## Target Architecture

### The One True Pattern

Every component that needs platform data follows this pattern:

```typescript
// Component.tsx
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { useSessionBoundary } from '@/shared/state/SessionBoundaryProvider';

export function Component() {
  // Session context
  const { sessionToken, isAuthenticated } = useSessionBoundary();
  
  // Platform state and actions
  const { state, submitIntent, getExecutionStatus } = usePlatformState();
  
  // Submit intent to Runtime
  const handleAction = async () => {
    const executionId = await submitIntent('intent_type', { params });
    // Poll or subscribe for result
    const result = await getExecutionStatus(executionId);
  };
  
  return <UI />;
}
```

### Provider Hierarchy (Final)

```
<SessionBoundaryProvider>      // Auth & session lifecycle
  <PlatformStateProvider>      // State & intent submission
    <App />
  </PlatformStateProvider>
</SessionBoundaryProvider>
```

**All other providers are DELETED.**

### Type Source of Truth

Types are generated from backend Pydantic models:

```
Backend (Pydantic)           Frontend (TypeScript)
─────────────────────────    ────────────────────────
SessionCreateRequest    →    SessionCreateRequest
SessionCreateResponse   →    SessionCreateResponse
IntentSubmitRequest     →    IntentSubmitRequest
IntentSubmitResponse    →    IntentSubmitResponse
ExecutionStatusResponse →    ExecutionStatusResponse
```

---

## Implementation Phases

### Phase 1: Foundation (Type System)

**Goal**: Establish type safety foundation

**Tasks**:

1. **Create canonical types from backend contracts**
   - File: `shared/types/runtime-contracts.ts`
   - Source: `symphainy_coexistence_fabric/symphainy_platform/runtime/runtime_api.py`
   - No `any` types allowed

2. **Create realm-specific types**
   - `shared/types/content-contracts.ts`
   - `shared/types/insights-contracts.ts`
   - `shared/types/journey-contracts.ts`
   - `shared/types/outcomes-contracts.ts`

3. **Update ExperiencePlaneClient to use canonical types**
   - Remove all `any` from `shared/services/ExperiencePlaneClient.ts`

**Deliverable**: Type-safe API layer with zero `any`

---

### Phase 2: Provider Consolidation

**Goal**: Single provider hierarchy

**Tasks**:

1. **Audit all provider usages**
   ```
   Files to DELETE:
   - shared/state/AGUIStateProvider.tsx
   - shared/state/AppProviders.tsx
   - shared/state/EnhancedStateProvider.tsx
   - shared/state/derived_atoms.ts (Jotai)
   - shared/agui/AGUIEventProvider.tsx
   - shared/agui/AppProvider.tsx
   - shared/agui/GuideAgentProvider.tsx
   - shared/agui/ProviderComposer.tsx
   
   Files to KEEP (and enhance):
   - shared/state/SessionBoundaryProvider.tsx
   - shared/state/PlatformStateProvider.tsx
   ```

2. **Migrate all usages to canonical providers**
   - Search for imports from deleted files
   - Replace with `usePlatformState` or `useSessionBoundary`

3. **Update root layout**
   - `app/layout.tsx` uses only SessionBoundary + PlatformState

**Deliverable**: Two providers, zero overlap

---

### Phase 3: Stub Elimination

**Goal**: All API calls go through ExperiencePlaneClient

**Files to DELETE** (stub APIs):
```
lib/api/admin.ts
lib/api/content.ts
lib/api/experience-dimension.ts
lib/api/experience.ts
lib/api/file-processing.ts
lib/api/fms-insights.ts
lib/api/fms.ts
lib/api/global.ts
lib/api/insights.ts
lib/api/operations.ts
```

**Migration for each component**:

| Current (Stub) | Target (Real) |
|----------------|---------------|
| `import { listFiles } from '@/lib/api/fms'` | `usePlatformState().submitIntent('list_files', {})` |
| `import { analyzeContent } from '@/lib/api/insights'` | `usePlatformState().submitIntent('analyze_content', {})` |
| `import { startGlobalSession } from '@/lib/api/global'` | `useSessionBoundary().startSession()` |

**Components to migrate** (28 files):
1. `shared/session/core.ts` - startGlobalSession
2. `shared/components/chatbot/SecondaryChatbot.tsx` - listFiles, insights APIs
3. `shared/hooks/useSessionElements.ts` - session elements
4. `shared/hooks/useSession.ts` - session elements
5. `app/(protected)/pillars/content/components/DataMash.tsx` - content types
6. `app/(protected)/pillars/content/components/EnhancedFileProcessor/hooks.ts` - content APIs
7. `app/(protected)/pillars/insights/components/*.tsx` - insights APIs
8. `components/admin/*.tsx` - admin types
9. All test files - mocks

**Deliverable**: Zero stub imports, all real connections

---

### Phase 4: Component Standardization

**Goal**: Every component follows the pattern

**Tasks**:

1. **Create component template**
   ```typescript
   // Template for all platform-connected components
   'use client';
   
   import { usePlatformState } from '@/shared/state/PlatformStateProvider';
   import { useSessionBoundary } from '@/shared/state/SessionBoundaryProvider';
   import type { /* types */ } from '@/shared/types/runtime-contracts';
   
   interface Props { /* typed props */ }
   
   export function ComponentName({ ...props }: Props) {
     const { isAuthenticated, sessionToken } = useSessionBoundary();
     const { state, submitIntent } = usePlatformState();
     
     // Implementation
   }
   ```

2. **Audit and fix all 515 TypeScript files**
   - Remove `any` types
   - Use canonical types
   - Follow standard pattern

3. **Create custom hooks for common operations**
   - `useFileOperations()` - wraps file intents
   - `useInsightsOperations()` - wraps insights intents
   - `useJourneyOperations()` - wraps journey intents
   - `useOutcomesOperations()` - wraps outcomes intents

**Deliverable**: Consistent codebase, zero `any`

---

### Phase 5: Hook Consolidation

**Goal**: Clean hook layer between components and platform

**Current hooks** (to audit):
```
shared/hooks/
├── useAgentManager.ts
├── useArtifactLifecycle.ts
├── useContentAPI.ts          → DELETE (use useFileOperations)
├── useErrorHandler.ts        → KEEP
├── useFileAPI.ts             → DELETE (use useFileOperations)
├── useInsightsAPI.ts         → DELETE (use useInsightsOperations)
├── useOperationsAPI.ts       → DELETE (use useJourneyOperations)
├── usePillarOrchestrator.ts  → REVIEW
├── useSession.ts             → DELETE (use useSessionBoundary)
├── useSessionElements.ts     → DELETE (use usePlatformState)
├── useUnifiedAgentChat.ts    → REVIEW
```

**New hook structure**:
```
shared/hooks/
├── useFileOperations.ts      # File upload, parse, embed intents
├── useInsightsOperations.ts  # Analysis, visualization intents
├── useJourneyOperations.ts   # Workflow, SOP intents
├── useOutcomesOperations.ts  # Roadmap, POC, solution intents
├── useAgentChat.ts           # Unified agent chat
├── useErrorHandler.ts        # Error handling
```

**Deliverable**: Clean, minimal hook layer

---

### Phase 6: Test Alignment

**Goal**: Tests verify real architecture

**Tasks**:

1. **Update jest.setup.js**
   - Remove global provider mocks
   - Tests should use real providers with mocked fetch

2. **Create test utilities**
   ```typescript
   // testUtils.tsx
   export function renderWithProviders(ui: React.ReactElement) {
     return render(
       <SessionBoundaryProvider>
         <PlatformStateProvider>
           {ui}
         </PlatformStateProvider>
       </SessionBoundaryProvider>
     );
   }
   ```

3. **Update all tests**
   - Use `renderWithProviders`
   - Mock `fetch` not providers
   - Verify intent submissions

**Deliverable**: Tests that verify real behavior

---

## File Deletion List

### Definitely Delete (Stubs)
```
lib/api/admin.ts
lib/api/content.ts
lib/api/experience-dimension.ts
lib/api/experience.ts
lib/api/file-processing.ts
lib/api/fms-insights.ts
lib/api/fms.ts
lib/api/global.ts
lib/api/insights.ts
lib/api/operations.ts
lib/contexts/ExperienceDimensionContext.tsx
lib/contexts/ExperienceLayerProvider.tsx
lib/contexts/UserContextProvider.tsx
lib/hooks/useExperienceDimensionAPI.ts
lib/utils/tokenRefresh.ts
```

### Definitely Delete (Old Providers)
```
shared/state/AGUIStateProvider.tsx
shared/state/AppProviders.tsx
shared/state/EnhancedStateProvider.tsx
shared/state/derived_atoms.ts
shared/agui/AGUIEventProvider.tsx
shared/agui/AppProvider.tsx
shared/agui/GuideAgentProvider.tsx
shared/agui/ProviderComposer.tsx
```

### Definitely Delete (Old Hooks)
```
shared/hooks/useContentAPI.ts
shared/hooks/useFileAPI.ts
shared/hooks/useInsightsAPI.ts
shared/hooks/useOperationsAPI.ts
shared/hooks/useSession.ts
shared/hooks/useSessionElements.ts
```

### Review and Consolidate
```
shared/session/* (much of this duplicates SessionBoundaryProvider)
shared/services/* (many overlap with ExperiencePlaneClient)
```

---

## Success Criteria

1. **Zero `any` types** - `grep -r ": any" --include="*.ts*" | wc -l` = 0
2. **Zero stub imports** - `grep -r "lib/api/" --include="*.ts*" | wc -l` = 0
3. **Two providers only** - SessionBoundaryProvider, PlatformStateProvider
4. **Build passes** - `npm run build` exits 0
5. **90%+ tests pass** - Unit tests verify real behavior
6. **Type-safe contracts** - All API types match backend Pydantic models

---

## Testing Handoff Document

Once cleanup is complete, create `TESTING_HANDOFF.md` with:

1. **Docker Compose setup instructions**
2. **Environment variables required**
3. **Integration test commands**
4. **E2E test commands (Playwright)**
5. **Expected test coverage targets**
6. **CI/CD pipeline configuration**

---

## Execution Order

```
Phase 1: Foundation (Type System)     ████░░░░░░  ~2 hours
Phase 2: Provider Consolidation       ████░░░░░░  ~2 hours
Phase 3: Stub Elimination             ████████░░  ~4 hours
Phase 4: Component Standardization    ████████░░  ~4 hours
Phase 5: Hook Consolidation           ████░░░░░░  ~2 hours
Phase 6: Test Alignment               ████░░░░░░  ~2 hours
                                      ──────────
                                      ~16 hours total
```

---

## Let's Begin

Ready to execute Phase 1?
