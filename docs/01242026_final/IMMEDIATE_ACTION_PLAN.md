# Immediate Action Plan: Complete Architectural Compliance

**Date:** January 25, 2026  
**Status:** 🔴 **CRITICAL - STARTING NOW**  
**Priority:** 🔴 **HIGHEST** - Full architectural compliance required

---

## Problem Statement

**Phase 4 claimed "100% Frontend Coverage" but we found:**
- **28 direct API calls** still exist
- **9 files** with legacy endpoint patterns
- **Multiple anti-patterns** that should have been caught

**CIO/CTO Expectation:**
- **Absolute architectural compliance** - not just "critical" issues
- **Real working code** that does not persist anti-patterns
- **Willing to "break and fix"** to catch ALL anti-patterns

**Current Reality:**
- Phase 5 is doing work Phase 4 should have done
- Phase 4's audit was incomplete/superficial
- We need to fix **EVERYTHING**, not just "critical" issues

---

## Files with Direct API Calls (9 files)

### Critical Files (In Active Use)

1. **`shared/services/operations/operations-service-updated.ts`**
   - Direct calls to `/api/operations/health`
   - **Status:** ⚠️ Still in use
   - **Action:** Migrate to intent-based API or deprecate

2. **`shared/agui/GuideAgentProvider.tsx`**
   - Direct call to `/api/v1/solution/create`
   - **Status:** ⚠️ Active component
   - **Action:** Migrate to intent-based API

3. **`shared/managers/BusinessOutcomesAPIManager.ts`**
   - Direct call to `/api/v1/business-outcomes-pillar/get-journey-visualization`
   - **Status:** ⚠️ Marked as deprecated but still has code
   - **Action:** Remove or migrate

### Legacy Library Files (Need Verification)

4. **`lib/api/operations.ts`**
   - Multiple direct calls to `/api/operations/*`
   - **Status:** ❓ Need to verify if used
   - **Action:** Migrate or remove if unused

5. **`lib/api/content.ts`**
   - Direct call to `/api/v1/data-solution/get-mash-context`
   - **Status:** ❓ Need to verify if used
   - **Action:** Migrate or remove if unused

6. **`lib/api/global.ts`**
   - Direct calls to `/api/v1/session/create-user-session` and `/api/operations/files`
   - **Status:** ❓ Need to verify if used
   - **Action:** Migrate or remove if unused

7. **`lib/api/unified-client.ts`**
   - Direct calls to `/api/operations/sop-builder`, `/api/operations/workflow-builder`
   - **Status:** ❓ Need to verify if used
   - **Action:** Migrate or remove if unused

8. **`lib/api/experience-layer-client.ts`**
   - Direct calls to `/api/operations/*`
   - **Status:** ❓ Need to verify if used
   - **Action:** Migrate or remove if unused

9. **`lib/api/insights.ts`**
   - Multiple direct calls to `/api/v1/insights-solution/*`
   - **Status:** ❓ Need to verify if used
   - **Action:** Migrate or remove if unused

---

## Comprehensive Fix Strategy

### Step 1: Verify Usage (1 hour)

**Goal:** Determine which files are actually used

**Commands:**
```bash
# Check imports of each file
grep -r "from.*lib/api/operations" symphainy-frontend
grep -r "from.*lib/api/content" symphainy-frontend
grep -r "from.*lib/api/global" symphainy-frontend
grep -r "from.*lib/api/unified-client" symphainy-frontend
grep -r "from.*lib/api/experience-layer-client" symphainy-frontend
grep -r "from.*lib/api/insights" symphainy-frontend
grep -r "operations-service-updated" symphainy-frontend
grep -r "GuideAgentProvider" symphainy-frontend
grep -r "BusinessOutcomesAPIManager" symphainy-frontend
```

**Action:**
- If used → Migrate to intent-based API
- If unused → Remove file
- If partially used → Migrate used parts, remove unused

---

### Step 2: Fix Active Files (4-6 hours)

**Priority Order:**

1. **`shared/agui/GuideAgentProvider.tsx`** (HIGH)
   - Active component
   - Migrate `/api/v1/solution/create` to intent-based API
   - Use appropriate API manager

2. **`shared/services/operations/operations-service-updated.ts`** (HIGH)
   - Still in use
   - Migrate `/api/operations/health` to intent-based API
   - Or deprecate if not needed

3. **`shared/managers/BusinessOutcomesAPIManager.ts`** (MEDIUM)
   - Marked as deprecated
   - Remove direct API call
   - Or migrate if still needed

---

### Step 3: Fix or Remove Legacy Files (2-3 hours)

**For each `lib/api/*` file:**

1. **If used:**
   - Migrate all direct API calls to intent-based API
   - Update all callers
   - Verify with tests

2. **If unused:**
   - Remove file
   - Remove all imports
   - Verify nothing breaks

3. **If partially used:**
   - Migrate used parts
   - Remove unused parts
   - Update callers

---

### Step 4: Comprehensive Verification (1-2 hours)

**Goal:** Verify 0 violations

**Commands:**
```bash
# Verify 0 direct API calls
grep -r "fetch.*\/api\/v1\/\|fetch.*\/api\/operations\/" symphainy-frontend --include="*.ts" --include="*.tsx" | grep -v "node_modules\|\.next\|\.git" | wc -l
# Should be 0

# Verify all API managers use intent-based API
grep -r "submitIntent\|submit_intent" symphainy-frontend/shared/managers/ --include="*.ts" | wc -l
# Should match number of API managers

# Run E2E 3D tests
./scripts/e2e_3d_test_suite.sh
# Should be 0 warnings
```

---

## Success Criteria

### Must Have (Non-Negotiable)

- ✅ **0 direct API calls** to `/api/v1/` or `/api/operations/`
- ✅ **0 legacy endpoint patterns**
- ✅ **100% intent-based API** for all operations
- ✅ **0 E2E test warnings**
- ✅ **All unused files removed**
- ✅ **All active files migrated**

### Verification

**Automated:**
- Code search: 0 violations
- E2E 3D tests: 0 warnings
- Linter: 0 violations

**Manual:**
- CTO/CIO code review
- Independent audit

---

## Timeline

**Total Estimated Time:** 8-12 hours

**Breakdown:**
- Step 1: Verify Usage - 1 hour
- Step 2: Fix Active Files - 4-6 hours
- Step 3: Fix/Remove Legacy Files - 2-3 hours
- Step 4: Verification - 1-2 hours

**Priority:** 🔴 **HIGHEST** - Start immediately

---

## Next Steps

1. ✅ **Acknowledge problem** - Phase 4 was incomplete
2. ⏭️ **Run usage verification** - Determine what's actually used
3. ⏭️ **Fix active files first** - Critical path
4. ⏭️ **Fix or remove legacy files** - Clean up
5. ⏭️ **Verify 0 violations** - Comprehensive testing
6. ⏭️ **CTO/CIO review** - Independent verification

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** 🔴 **CRITICAL - STARTING IMMEDIATELY**
