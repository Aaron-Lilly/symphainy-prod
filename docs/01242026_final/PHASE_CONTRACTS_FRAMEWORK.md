# Phase Contracts Framework

**Date:** January 25, 2026  
**Status:** 🔴 **CRITICAL - REQUIRED FOR ALL PHASES**  
**Priority:** 🔴 **HIGHEST** - Prevents false confidence

---

## Executive Summary

**Problem:** Phases were treated as implementation milestones instead of behavioral contracts, leading to false "complete" declarations.

**Solution:** Each phase must exit with **executable contracts** that make violations impossible, not just detectable.

**Key Principle:** Make wrong behavior impossible, not just detectable.

---

## Phase Contract Structure

Each phase contract must have **exactly three sections**:

1. **Invariants** (Positive + Negative)
2. **Enforcement Mechanism** (Make violations impossible)
3. **Proof** (Tests that verify enforcement)

---

## Phase 0 Contract: Foundation & Infrastructure

### 1. Invariants

**Negative:**
- No `sessionStorage` mutations outside SessionBoundaryProvider
- No direct `get_X()` method calls on Public Works abstractions
- No agent instantiation without 4-layer model compliance

**Positive:**
- All session state changes flow through SessionBoundaryProvider
- All Public Works abstractions accessed as attributes
- All agents implement `_process_with_assembled_prompt()`
- Runtime authoritative overwrite works (frontend submits to backend)

---

### 2. Enforcement Mechanism

**Implementation:**
- ESLint rule: Ban `sessionStorage.setItem` outside SessionBoundaryProvider
- TypeScript: Make Public Works abstractions attribute-only (no methods)
- Runtime: Reject agent instantiation without 4-layer compliance
- Test: Intentional violation must fail at compile/runtime

**Example:**
```typescript
// ESLint rule
"no-restricted-syntax": [
  "error",
  {
    "selector": "CallExpression[callee.property.name='setItem'][callee.object.name='sessionStorage']",
    "message": "Session mutations must go through SessionBoundaryProvider"
  }
]
```

---

### 3. Proof

**Tests:**
1. **Intentional Violation Test:** Try to mutate sessionStorage directly → Must fail
2. **Public Works Test:** Try to call `get_X()` method → Must fail at compile time
3. **Agent Compliance Test:** Try to instantiate agent without 4-layer model → Must fail
4. **Runtime Overwrite Test:** Create state divergence → Runtime must win

**CI/CD:**
- Phase 0 gate: All tests must pass
- Phase 0 gate: ESLint must pass
- Phase 0 gate: TypeScript must compile

---

## Phase 1 Contract: Frontend State Management

### 1. Invariants

**Negative:**
- No `GlobalSessionProvider` imports in production code
- No `getPillarState()` / `setPillarState()` calls
- No mock user IDs (`mock-user`)

**Positive:**
- All state access uses `getRealmState()` / `setRealmState()`
- All session identity from `useSessionBoundary()`
- All realm state from `usePlatformState()`
- State persists across pillar navigation

---

### 2. Enforcement Mechanism

**Implementation:**
- ESLint rule: Ban `GlobalSessionProvider` / `useGlobalSession` imports
- ESLint rule: Ban `getPillarState` / `setPillarState` calls
- ESLint rule: Ban `mock-user` string literals
- TypeScript: Remove GlobalSessionProvider from exports (or mark deprecated)
- Test: Intentional violation must fail

**Example:**
```typescript
// ESLint rule
"no-restricted-imports": [
  "error",
  {
    "paths": [
      {
        "name": "@/shared/state/GlobalSessionProvider",
        "message": "Use PlatformStateProvider instead"
      }
    ]
  }
]
```

---

### 3. Proof

**Tests:**
1. **Intentional Violation Test:** Try to import GlobalSessionProvider → Must fail
2. **Migration Test:** All production files use PlatformStateProvider
3. **State Persistence Test:** State survives pillar navigation
4. **Mock Data Test:** No mock-user IDs in production code

**CI/CD:**
- Phase 1 gate: ESLint must pass
- Phase 1 gate: All production files verified
- Phase 1 gate: State persistence tests pass

---

## Phase 2/3 Contract: Semantic Pattern Migration

### 1. Invariants

**Negative:**
- No `parsed_file_id` in embedding queries
- No direct embedding queries without chunk_id
- No legacy `extract_embeddings` intent usage

**Positive:**
- All embedding queries use `chunk_id` (not `parsed_file_id`)
- All services use chunk-based pattern
- All semantic computation is trigger-based
- Anti-corruption layer fails fast on violations

---

### 2. Enforcement Mechanism

**Implementation:**
- Python: Fail-fast assertion in `SemanticDataAbstraction.get_semantic_embeddings()` - Rejects `parsed_file_id`
- Python: Fail-fast assertion in `SemanticDataAbstraction.store_semantic_embeddings()` - Requires `chunk_id`
- Python: Fail-fast assertion in `SemanticTriggerBoundary` - Rejects invalid triggers
- Test: Intentional violation must fail at runtime

**Example:**
```python
# Anti-corruption layer
def get_semantic_embeddings(self, filter_conditions: Dict[str, Any]) -> List[Embedding]:
    # Fail fast if parsed_file_id is used
    if "parsed_file_id" in filter_conditions:
        raise ValueError(
            "parsed_file_id is not allowed. Use chunk_id instead. "
            "This is enforced by the semantic anti-corruption layer."
        )
    # ... rest of implementation
```

---

### 3. Proof

**Tests:**
1. **Intentional Violation Test:** Try to query by `parsed_file_id` → Must fail fast
2. **Chunk-Based Test:** All services use chunk-based pattern
3. **Trigger Test:** Semantic computation only on valid triggers
4. **Anti-Corruption Test:** Legacy paths fail fast with clear error

**CI/CD:**
- Phase 2/3 gate: All fail-fast assertions work
- Phase 2/3 gate: No parsed_file_id queries
- Phase 2/3 gate: All services use chunk-based pattern

---

## Phase 4 Contract: Frontend Feature Completion

### 1. Invariants

**Negative:**
- No direct calls to `/api/v1/*`
- No direct calls to `/api/operations/*`
- No `fetch()` calls outside API managers (except documented exceptions)

**Positive:**
- Every user action results in exactly one intent submission
- Every intent submission flows through ExecutionLifecycleManager
- Every intent has a traceable execution_id
- All operations go through Runtime

---

### 2. Enforcement Mechanism

**Implementation:**
- ESLint rule: Ban `fetch('/api/v1')` and `fetch('/api/operations')`
- Runtime: Reject any request without intent envelope
- Proxy: Deny legacy routes in non-dev environments
- TypeScript: Remove legacy endpoint types (or mark deprecated)
- Test: Intentional violation must fail

**Example:**
```typescript
// ESLint rule
"no-restricted-syntax": [
  "error",
  {
    "selector": "CallExpression[callee.name='fetch'][arguments.0.value=/^\\/api\\/v1\\//]",
    "message": "Use intent-based API via submitIntent() instead"
  }
]
```

**Runtime Enforcement:**
```python
# Backend: Reject legacy endpoints
@app.route("/api/v1/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def legacy_endpoint(path):
    raise HTTPException(
        status_code=410,  # Gone
        detail="Legacy endpoint removed. Use intent-based API: /api/intent/submit"
    )
```

---

### 3. Proof

**Tests:**
1. **Intentional Violation Test:** Try to call `/api/v1/*` → Must fail
2. **Intent Flow Test:** Every user action creates intent submission
3. **Execution Trace Test:** Every intent has execution_id
4. **Runtime Authority Test:** All operations go through Runtime

**CI/CD:**
- Phase 4 gate: ESLint must pass
- Phase 4 gate: Runtime rejects legacy endpoints
- Phase 4 gate: All operations use intent-based API

---

## Phase 5 Contract: Data Architecture & Polish

### 1. Invariants

**Negative:**
- No direct API calls in API managers
- No missing parameter validation
- No missing session validation

**Positive:**
- All API managers use intent-based API
- All intents have parameter validation
- All operations have session validation
- All data follows four-class architecture

---

### 2. Enforcement Mechanism

**Implementation:**
- TypeScript: API managers must use `submitIntent()` (no direct fetch)
- ESLint rule: Ban `fetch()` in API manager classes
- Runtime: Reject intents without required parameters
- Runtime: Reject operations without valid session
- Test: Intentional violation must fail

---

### 3. Proof

**Tests:**
1. **Intentional Violation Test:** Try to use direct fetch in API manager → Must fail
2. **Parameter Validation Test:** Missing parameters → Must fail
3. **Session Validation Test:** Invalid session → Must fail
4. **Data Architecture Test:** Data follows four-class pattern

**CI/CD:**
- Phase 5 gate: All API managers use intent-based API
- Phase 5 gate: All intents have validation
- Phase 5 gate: All operations have session validation

---

## Unknown Detection Mechanisms

### 1. Boundary Matrix Testing

**Concept:** Test every boundary (realm, intent, data class) systematically

**Implementation:**
- Create matrix of all boundaries
- Test each boundary combination
- Verify correct behavior at boundaries
- Catch unexpected interactions

---

### 2. Chaos Testing

**Concept:** Intentionally break things to find weaknesses

**Implementation:**
- Randomly fail services
- Randomly delay responses
- Randomly corrupt state
- Verify system handles gracefully

---

### 3. Execution Flow Tracing

**Concept:** Trace every execution from intent to completion

**Implementation:**
- Log every step in execution flow
- Verify all steps execute correctly
- Catch missing steps or unexpected paths
- Verify state transitions

---

### 4. State Authority Verification

**Concept:** Verify Runtime always wins on state divergence

**Implementation:**
- Create state divergence scenarios
- Verify Runtime overwrites frontend
- Verify frontend reconciles correctly
- Catch split-brain scenarios

---

## Integration with 3D Testing

### Functional Dimension

**Phase Contracts:**
- Verify correct behavior (positive invariants)
- Verify no incorrect behavior (negative invariants)

**Unknown Detection:**
- Boundary matrix testing
- Execution flow tracing

---

### Architectural Dimension

**Phase Contracts:**
- Verify enforcement mechanisms work
- Verify architectural patterns followed

**Unknown Detection:**
- State authority verification
- Intent flow verification

---

### SRE/Distributed Systems Dimension

**Phase Contracts:**
- Verify system handles failures
- Verify system recovers correctly

**Unknown Detection:**
- Chaos testing
- Failure scenario testing

---

## Success Criteria

### Phase Exit Criteria

Each phase can only exit when:

1. ✅ **All invariants defined** (positive + negative)
2. ✅ **Enforcement mechanism implemented** (makes violations impossible)
3. ✅ **Proof tests pass** (intentional violations fail)
4. ✅ **CI/CD gates pass** (automated verification)
5. ✅ **Independent verification** (CTO/CIO review)

---

### Platform Readiness Criteria

Platform is ready when:

1. ✅ **All phase contracts defined**
2. ✅ **All enforcement mechanisms active**
3. ✅ **All proof tests passing**
4. ✅ **3D testing comprehensive**
5. ✅ **Unknown detection mechanisms active**

---

## Next Steps

1. ✅ **Create phase contracts** for all phases
2. ⏭️ **Implement enforcement mechanisms** for all phases
3. ⏭️ **Add proof tests** for all phases
4. ⏭️ **Enhance E2E 3D test plan** with enforcement verification
5. ⏭️ **Add unknown detection mechanisms** to 3D testing

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** 🔴 **CRITICAL - REQUIRED FOR ALL PHASES**
