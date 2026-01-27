# E2E 3D Testing: Issues to Fix

**Date:** January 25, 2026  
**Status:** ⚠️ **ISSUES IDENTIFIED - REQUIRES FIXES**  
**Priority:** 🔴 **HIGH** - These are anti-patterns that Phase 4 refactoring was designed to eliminate

---

## Executive Summary

The E2E 3D testing suite identified 4 warnings that are actually **architectural anti-patterns** that need to be fixed. These are not acceptable warnings - they violate the Phase 4 refactoring goals and must be addressed.

---

## Issue 1: Legacy API Calls (23 found) 🔴 **CRITICAL**

### Problem

**Location:** `shared/services/operations/`

**Anti-Pattern:** Direct API calls (`/api/v1/`, `fetch()`) instead of intent-based API

**Impact:**
- Bypasses Runtime authority
- Violates intent-based architecture
- Creates architectural inconsistency
- Prevents proper execution tracking
- **Breaks Phase 4 refactoring goals**

### Root Cause

OperationsService uses direct API calls:
- `core.ts`: Direct `fetch()` calls to `/api/operations/optimize-coexistence-with-content`
- `solution-service.ts`: Direct `fetch()` calls to `/api/v1/operations-solution/...`
- `coexistence.ts`: Direct `fetch()` calls
- Not using `submitIntent()` pattern

**Current Usage:**
- `CoexistenceBlueprint/hooks.ts` calls `OperationsService.optimizeCoexistenceWithContent()`
- This bypasses Runtime and intent-based architecture

### Required Fix

**Action:** Migrate OperationsService operations to intent-based API via JourneyAPIManager

**Steps:**
1. **Add method to JourneyAPIManager** for `optimize_coexistence_with_content` intent
2. **Update CoexistenceBlueprint** to use JourneyAPIManager instead of OperationsService
3. **Verify all operations** use intent-based API
4. **Deprecate OperationsService** direct API calls (or migrate all to intents)

**Files to Modify:**
- `shared/managers/JourneyAPIManager.ts` - Add `optimizeCoexistenceWithContent()` method using intent
- `app/(protected)/pillars/journey/components/CoexistenceBlueprint/hooks.ts` - Replace OperationsService call
- `shared/services/operations/core.ts` - Mark as deprecated or migrate
- `shared/services/operations/solution-service.ts` - Mark as deprecated or migrate

**Example Fix:**
```typescript
// JourneyAPIManager.ts
async optimizeCoexistenceWithContent(
  sopContent: string,
  workflowContent: string
): Promise<{ success: boolean; optimized_sop?: any; optimized_workflow?: any; blueprint?: any; error?: string }> {
  const platformState = this.getPlatformState();
  
  if (!platformState.state.session.sessionId || !platformState.state.session.tenantId) {
    throw new Error("Session required to optimize coexistence");
  }

  const execution = await platformState.submitIntent(
    "optimize_coexistence_with_content",
    {
      sop_content: sopContent,
      workflow_content: workflowContent
    }
  );

  const result = await this._waitForExecution(execution, platformState);
  
  if (result.status === "completed" && result.artifacts?.optimized_coexistence) {
    platformState.setRealmState("journey", "operations", {
      ...platformState.getRealmState("journey", "operations") || {},
      optimizedSop: result.artifacts.optimized_coexistence.optimized_sop,
      optimizedWorkflow: result.artifacts.optimized_coexistence.optimized_workflow,
      blueprint: result.artifacts.optimized_coexistence.blueprint,
    });

    return {
      success: true,
      optimized_sop: result.artifacts.optimized_coexistence.optimized_sop,
      optimized_workflow: result.artifacts.optimized_coexistence.optimized_workflow,
      blueprint: result.artifacts.optimized_coexistence.blueprint,
    };
  } else {
    throw new Error(result.error || "Failed to optimize coexistence");
  }
}
```

**Estimated Time:** 2-3 hours

---

## Issue 2: Visualization Data Source ⚠️ **MEDIUM**

### Problem

**Location:** Need to verify all visualizations read from Runtime state

**Anti-Pattern:** Visualizations reading from computed UI state instead of Runtime state

**Impact:**
- Visualization truth not maintained
- State authority drift
- Visualizations may show incorrect data

### Root Cause Analysis

**Current Status:**
- ✅ `YourDataMash.tsx`: Reads from `state.realm.insights.lineageVisualizations`
- ✅ `RelationshipMapping.tsx`: Reads from `state.realm.insights.relationshipMappings`
- ⚠️ `CoexistenceBlueprint/components.tsx`: Uses OperationsService (legacy), stores in realm state but source is legacy API

**Issue:** CoexistenceBlueprint gets data from OperationsService (legacy API) before storing in realm state. This violates the pattern.

### Required Fix

**Action:** Verify all visualizations read from Runtime state (after Issue 1 is fixed)

**Steps:**
1. **After fixing Issue 1:** CoexistenceBlueprint will use JourneyAPIManager (intent-based)
2. Verify all visualizations read from `state.realm.*`
3. Add invariant checks to ensure data comes from Runtime

**Files to Verify:**
- `app/(protected)/pillars/insights/components/YourDataMash.tsx` - ✅ Already correct
- `app/(protected)/pillars/insights/components/RelationshipMapping.tsx` - ✅ Already correct
- `app/(protected)/pillars/journey/components/CoexistenceBlueprint/components.tsx` - ⚠️ Will be fixed when Issue 1 is fixed

**Estimated Time:** 1 hour (mostly verification after Issue 1 fix)

---

## Issue 3: Intent Parameter Validation ⚠️ **MEDIUM**

### Problem

**Location:** API managers may have insufficient parameter validation

**Anti-Pattern:** Missing required parameter validation before `submitIntent()`

**Impact:**
- Runtime may receive invalid intents
- Errors caught late (at Runtime) instead of early (at API manager)
- Poor error messages for users

### Root Cause

Some API managers may not validate required parameters before submission.

### Required Fix

**Action:** Add required parameter validation to all API managers

**Steps:**
1. Audit all `submitIntent()` calls
2. Add validation for required parameters before submission
3. Throw clear errors for missing parameters
4. Document validation in INTENT_PARAMETER_SPECIFICATION.md

**Files to Modify:**
- `shared/managers/ContentAPIManager.ts`
- `shared/managers/InsightsAPIManager.ts`
- `shared/managers/JourneyAPIManager.ts`
- `shared/managers/OutcomesAPIManager.ts`

**Example Pattern:**
```typescript
if (!fileId) {
  throw new Error("file_id is required for visualize_lineage");
}
```

**Estimated Time:** 1-2 hours

---

## Issue 4: Session Validation ⚠️ **LOW** (May be false positive)

### Problem

**Location:** Session validation may be inconsistent

**Anti-Pattern:** Inconsistent session validation patterns

**Impact:**
- Security risk if missing
- Poor error handling if inconsistent
- Inconsistent user experience

### Root Cause Analysis

**Current Status:**
- ✅ All API managers DO have session validation
- ✅ Pattern: `if (!platformState.state.session.sessionId || !platformState.state.session.tenantId) throw new Error("Session required...")`
- ⚠️ May need standardization (helper function)

**Verification:**
- ContentAPIManager: ✅ 6 methods with session validation
- InsightsAPIManager: ✅ 7 methods with session validation
- JourneyAPIManager: ✅ 5 methods with session validation
- OutcomesAPIManager: ✅ 6 methods with session validation

### Required Fix

**Action:** Standardize session validation (optional enhancement)

**Steps:**
1. Create standardized session validation helper
2. Replace inline validation with helper
3. Ensure consistency across all methods

**Files to Modify:**
- Create: `shared/utils/sessionValidation.ts`
- Update all API managers to use helper

**Example Pattern:**
```typescript
// shared/utils/sessionValidation.ts
export function validateSession(platformState: PlatformState, operation: string): void {
  if (!platformState.state.session.sessionId || !platformState.state.session.tenantId) {
    throw new Error(`Session required for ${operation}`);
  }
}

// Usage in API managers
validateSession(platformState, "visualize_lineage");
```

**Estimated Time:** 1 hour (optional enhancement)

---

## Priority Order

### 🔴 Critical (Fix First - Blocks Browser Testing)

1. **Issue 1: Legacy API Calls** - Breaks architectural consistency, violates Phase 4 refactoring
   - **Time:** 2-3 hours
   - **Impact:** High - Affects Journey pillar operations, breaks intent-based architecture
   - **Blocks:** Browser testing (architectural inconsistency)

### ⚠️ Medium (Fix Before Browser Testing)

2. **Issue 3: Intent Parameter Validation** - Prevents early error detection, violates CIO feedback
   - **Time:** 1-2 hours
   - **Impact:** Medium - Better error handling, prevents intent inference
   - **Blocks:** Browser testing (architectural anti-pattern)

3. **Issue 2: Visualization Data Source** - Data integrity (mostly fixed after Issue 1)
   - **Time:** 1 hour (verification after Issue 1)
   - **Impact:** Medium - Visualization truth
   - **Blocks:** Browser testing (data integrity)

### ⚠️ Low (Enhancement - Can Do After)

4. **Issue 4: Session Validation** - Consistency enhancement
   - **Time:** 1 hour
   - **Impact:** Low - Already working, just needs standardization
   - **Does NOT block:** Browser testing (already functional)

---

## Total Estimated Time

**5-8 hours** to fix all issues

---

## Success Criteria

### Issue 1: Legacy API Calls
- ✅ All OperationsService operations use intent-based API
- ✅ No direct `fetch()` calls to `/api/v1/` or `/api/operations/`
- ✅ All operations go through Runtime via `submitIntent()`

### Issue 2: Visualization Data Source
- ✅ All visualizations read from `state.realm.*`
- ✅ No visualizations read from local/computed state
- ✅ Invariant checks added

### Issue 3: Intent Parameter Validation
- ✅ All required parameters validated before `submitIntent()`
- ✅ Clear error messages for missing parameters
- ✅ Validation documented

### Issue 4: Session Validation
- ✅ All API manager methods validate session
- ✅ Standardized session validation helper
- ✅ Consistent error messages

---

## Next Steps

1. ⏭️ **Fix Issue 1** - Migrate OperationsService to intent-based API (CRITICAL - 2-3 hours)
2. ⏭️ **Fix Issue 3** - Add intent parameter validation (MEDIUM - 1-2 hours)
3. ⏭️ **Fix Issue 2** - Verify visualization data sources (MEDIUM - 1 hour, after Issue 1)
4. ⏭️ **Re-run E2E 3D Tests** - Verify all critical issues fixed
5. ⏭️ **Proceed to Browser Testing** - After Issues 1, 2, 3 fixed
6. ⏭️ **Fix Issue 4** - Standardize session validation (LOW - 1 hour, optional enhancement)

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** ⚠️ **ISSUES IDENTIFIED - REQUIRES FIXES BEFORE BROWSER TESTING**
