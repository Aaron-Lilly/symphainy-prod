# Platform Type Alignment Plan

**Purpose:** Holistic execution plan that aligns frontend TypeScript types with the backend platform fix (PLATFORM_FIX_EXECUTION_PLAN.md). Ensures end-to-end type safety from Runtime → Solutions → Journeys → Frontend.

**Context:** 
- Backend: [PLATFORM_FIX_EXECUTION_PLAN.md](../../symphainy_coexistence_fabric/docs/architecture/PLATFORM_FIX_EXECUTION_PLAN.md)
- Frontend: Phase 4 type cleanup (removing `any` types)
- Goal: Single source of truth for contracts flowing through the platform

---

## Executive Summary

The backend platform fix standardizes on:
- **BaseSolution** with `build_journey_result()` 
- **Standard journey result shape**: `{success, artifacts, events, journey_id, journey_execution_id, error?}`
- **No RealmBase** - realms = solution + orchestrators + intent services

The frontend must align:
- **runtime-contracts.ts** - canonical TypeScript types matching backend Pydantic models
- **API Managers** - expect standardized journey/execution responses
- **State Management** - `PlatformStateProvider` works with standardized shapes
- **All `any` types removed** - replaced with proper types aligned to contracts

---

## Part 1: Backend-First (PLATFORM_FIX_EXECUTION_PLAN)

Execute the backend platform fix **first** to establish the contract:

### 1.1 Remove RealmBase (Part A)
- Simplify RealmRegistry to realm-name registry
- Update control_room_service, developer_view_service
- Remove/slim realm_sdk.py
- Update docs

### 1.2 Standardize Solutions (Part B)
- All solutions inherit from BaseSolution
- All journeys return standard shape via `build_journey_result()`
- Fix tests to use canonical action names and standard asserts

### 1.3 Verify Backend Contracts
After Part A and B, the backend exports these canonical shapes:

```python
# Journey Result (from BaseSolution.build_journey_result)
JourneyResult = {
    "success": bool,
    "journey_id": str,
    "journey_execution_id": str,
    "artifacts": Dict[str, Any],  # Keyed by artifact type
    "events": List[Dict],         # Execution events
    "error": Optional[str]
}

# Execution Status Response (from Runtime API)
ExecutionStatusResponse = {
    "execution_id": str,
    "status": Literal["pending", "running", "completed", "failed", "cancelled"],
    "intent_id": str,
    "artifacts": Optional[Dict],
    "events": Optional[List],
    "error": Optional[str]
}

# Intent Submit Response
IntentSubmitResponse = {
    "execution_id": str,
    "intent_id": str,
    "status": Literal["accepted", "rejected", "pending", "processing"],
    "created_at": str
}
```

---

## Part 2: Frontend Alignment (Phase 4 Completion + Contract Alignment)

Once backend contracts are stable, align frontend:

### 2.1 Update runtime-contracts.ts (Canonical Types)

Ensure these match backend exactly:

```typescript
// symphainy-frontend/shared/types/runtime-contracts.ts

/**
 * Standard journey result shape
 * Maps to: BaseSolution.build_journey_result() in Python
 */
export interface JourneyResult {
  success: boolean;
  journey_id: string;
  journey_execution_id: string;
  artifacts: Record<string, unknown>;
  events: ExecutionEvent[];
  error?: string | null;
}

/**
 * Execution status response
 * Maps to: ExecutionStatusResponse in runtime_api.py
 */
export interface ExecutionStatusResponse {
  execution_id: string;
  status: ExecutionStatus;
  intent_id: string;
  artifacts?: Record<string, unknown>;
  events?: ExecutionEvent[];
  error?: string | null;
}

/**
 * Execution event structure
 */
export interface ExecutionEvent {
  event_type: string;
  timestamp: string;
  data?: Record<string, unknown>;
}

/**
 * Execution status values
 */
export type ExecutionStatus = 
  | 'pending' 
  | 'running' 
  | 'completed' 
  | 'failed' 
  | 'cancelled';

/**
 * Intent status values
 */
export type IntentStatus = 'accepted' | 'rejected' | 'pending' | 'processing';
```

### 2.2 Update API Managers

Ensure managers expect standardized responses:

```typescript
// ContentAPIManager, OperationsAPIManager, etc.

// When waiting for execution completion:
const status = await platformState.getExecutionStatus(executionId);

if (status?.status === "completed") {
  // Standard shape: artifacts, events, success implied by status
  const artifacts = status.artifacts || {};
  const events = status.events || [];
  
  // Access specific artifact types
  const fileArtifact = artifacts.file as FileArtifact | undefined;
}
```

### 2.3 Update PlatformStateProvider

Ensure state types align:

```typescript
// PlatformStateProvider types should use:
// - ExecutionStatusResponse for getExecutionStatus()
// - IntentSubmitResponse for submitIntent()
// - JourneyResult when journeys complete
```

### 2.4 Complete Phase 4 (Remove remaining `any` types)

Continue fixing the ~407 remaining `any` types:

**Priority files:**
- `shared/services/operations/index.ts` (19)
- `shared/orchestrators/PillarOrchestrator.ts` (18)
- `shared/services/insights/smart-city-integration.ts` (14)
- `shared/services/insights/vark-analysis.ts` (13)
- `shared/services/operations/coexistence.ts` (12)
- `shared/state/PlatformStateProvider.tsx` (8)

**Pattern:** Replace `any` with types from `runtime-contracts.ts` or create specific interfaces that extend the canonical types.

---

## Part 3: Verification and Testing

### 3.1 Backend Tests (from PLATFORM_FIX_EXECUTION_PLAN Part C)
```bash
pytest tests/3d/solution/ tests/3d/journey/ tests/e2e/demo_paths/ -v --tb=short
```

### 3.2 Frontend Type Checking
```bash
cd symphainy-frontend
npm run type-check  # or tsc --noEmit
```

### 3.3 Frontend Tests
```bash
cd symphainy-frontend
npm test
```

### 3.4 E2E Tests (Full Stack)
```bash
docker-compose -f docker-compose.fullstack.yml up -d
npm run e2e
```

---

## Part 4: Documentation Sync

### 4.1 Backend Docs
- Update SOLUTION_PATTERN.md with final result shape
- Mark RealmBase as removed in PLATFORM_BASES_REVIEW.md
- Add execution log to PLATFORM_FIX_EXECUTION_PLAN.md

### 4.2 Frontend Docs
- Update runtime-contracts.ts header comments with backend references
- Document type mapping in shared/types/README.md (if exists)
- Update TESTING_HANDOFF.md with type requirements

---

## Execution Order (Recommended)

### Phase 1: Backend Stabilization (1-2 days)
1. Execute PLATFORM_FIX_EXECUTION_PLAN Part A (Remove RealmBase)
2. Execute PLATFORM_FIX_EXECUTION_PLAN Part B (Standardize solutions)
3. Run backend tests, fix any regressions
4. Document final contract shapes

### Phase 2: Frontend Alignment (1-2 days)
5. Update runtime-contracts.ts to match verified backend shapes
6. Update ExperiencePlaneClient types
7. Update API managers to use standardized types
8. Update PlatformStateProvider types

### Phase 3: Complete Type Cleanup (1-2 days)
9. Fix remaining ~407 `any` types using proper contract types
10. Run TypeScript type checking
11. Fix any type errors

### Phase 4: Integration Verification (0.5-1 day)
12. Run frontend unit tests
13. Run E2E tests against full stack
14. Document completion

---

## Success Criteria

1. **Zero `RealmBase`** references in backend
2. **All solutions** inherit from `BaseSolution`
3. **All journeys** return standard `{success, artifacts, events, journey_id, journey_execution_id}` shape
4. **Frontend types** in `runtime-contracts.ts` match backend Pydantic models exactly
5. **Zero `any`** types in `shared/` directory (or <50 with documented exceptions)
6. **All tests pass** (backend 3d/e2e, frontend unit/e2e)

---

## Risk Mitigation

### Contract Drift
- **Risk:** Backend changes contract after frontend aligned
- **Mitigation:** Run alignment as single coordinated effort; freeze backend contracts during frontend work

### Breaking Changes
- **Risk:** Type changes break existing components
- **Mitigation:** Phase 4 work already uses `unknown` for generics; specific types only narrow, not widen

### Test Failures
- **Risk:** Stricter types expose existing bugs
- **Mitigation:** This is actually a benefit - type errors reveal contract mismatches that should be fixed

---

## References

- [PLATFORM_FIX_EXECUTION_PLAN.md](../../symphainy_coexistence_fabric/docs/architecture/PLATFORM_FIX_EXECUTION_PLAN.md) - Backend platform fix
- [SOLUTION_CONTRACT_RESOLUTION.md](../../symphainy_coexistence_fabric/docs/architecture/SOLUTION_CONTRACT_RESOLUTION.md) - Solution contract analysis
- [SOLUTION_PATTERN.md](../../symphainy_platform_old/solutions/SOLUTION_PATTERN.md) - How to add solutions
- [runtime-contracts.ts](../../symphainy-frontend/shared/types/runtime-contracts.ts) - Frontend canonical types
- [PlatformStateProvider.tsx](../../symphainy-frontend/shared/state/PlatformStateProvider.tsx) - Frontend state management

---

## Execution Log

*(To be filled as work progresses)*

| Date | Phase | Action | Status |
|------|-------|--------|--------|
| 2026-01-28 | Frontend Phase 4 | Reduced `any` from 585 to 407 (~30%) | In Progress |
| | | | |
