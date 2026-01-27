# Phase 5 Updated Plan

**Date:** January 25, 2026  
**Status:** 📋 **UPDATED**  
**Purpose:** Complete Phase 5 with all legacy API migrations

---

## Executive Summary

After audit, we've identified that **NONE of the legacy API managers are acceptable**. We need to add **Task 5.6: Complete Legacy API Migration** to Phase 5 to achieve true 100% intent-based architecture.

---

## ✅ Completed Tasks

### Task 5.3: Purpose-Bound Outcomes Lifecycle
- ✅ Complete

### Task 5.4: Code Quality & Documentation
- ✅ Complete

### Task 5.5: Final Anti-Pattern Fix
- ✅ Complete (save_materialization)

---

## ⏳ Remaining Tasks

### Task 5.6: Complete Legacy API Migration (NEW - CRITICAL)

**Priority:** 🔴 **CRITICAL** - Must fix before testing

**Scope:**
1. **OperationsService Migration** (CRITICAL)
   - Still used in Journey pillar (`page-updated.tsx`, `WizardActive/hooks.ts`)
   - 7 OperationsService calls need migration
   - Estimated: 3-5 hours

2. **SessionAPIManager Migration** (HIGH)
   - Session management should use intent-based API
   - Estimated: 2-3 hours

3. **GuideAgentAPIManager Migration** (HIGH)
   - Guide agent should use intent-based API
   - Estimated: 2-3 hours

4. **LiaisonAgentsAPIManager Migration** (HIGH)
   - Liaison agents should use intent-based API
   - Estimated: 2-3 hours

5. **AdminAPIManager Migration** (MEDIUM)
   - Admin operations should use intent-based API
   - Estimated: 4-6 hours

6. **OperationsAPIManager Deprecation** (LOW)
   - Document as deprecated
   - Estimated: 1 hour

7. **BusinessOutcomesAPIManager Deprecation** (LOW)
   - Document as deprecated
   - Estimated: 1 hour

**Total Critical/High Priority:** 9-14 hours (1.5-2 days)

---

### Task 5.2: Records of Fact Promotion
- **Status:** Ready to begin
- **Time:** 4-7 hours

### Task 5.1: TTL Enforcement
- **Status:** Ready to begin
- **Time:** 4-7 hours

---

## Updated Priority Order

### 🔴 Critical (Fix Before Testing)
1. **Task 5.6.1: OperationsService Migration** - Still used in Journey pillar!

### ⚠️ High Priority (Fix Before Testing)
2. **Task 5.6.2: SessionAPIManager Migration**
3. **Task 5.6.3: GuideAgentAPIManager Migration**
4. **Task 5.6.4: LiaisonAgentsAPIManager Migration**

### ⚠️ Medium Priority (Can Do After Testing)
5. **Task 5.6.5: AdminAPIManager Migration**

### ⚠️ Low Priority (Documentation)
6. **Task 5.6.6: OperationsAPIManager Deprecation**
7. **Task 5.6.7: BusinessOutcomesAPIManager Deprecation**

### Backend Tasks (Can Do in Parallel)
8. **Task 5.2: Records of Fact Promotion**
9. **Task 5.1: TTL Enforcement**

---

## Recommendation

**Add Task 5.6 to Phase 5** with focus on:
1. **Critical:** OperationsService migration (3-5 hours)
2. **High:** Infrastructure managers migration (6-9 hours)
3. **Medium/Low:** Can be done after testing or in parallel

**Total Critical/High Priority Time:** 9-14 hours

This ensures we have **true 100% intent-based architecture** before testing.

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** 📋 **PLAN UPDATED - AWAITING APPROVAL**
