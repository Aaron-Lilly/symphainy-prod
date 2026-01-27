# Phase 1: Cross-Pillar Navigation Test

**Date:** January 24, 2026  
**Status:** ✅ **READY TO RUN**  
**Purpose:** Validate realm state preservation across pillar navigation

---

## Test Overview

This test validates that Phase 1 migration correctly preserves realm state when navigating between pillars, ensuring:
- ✅ Realm state is preserved across navigation
- ✅ State does not leak across realms
- ✅ State correctly rehydrates from Runtime on return
- ✅ No remounted defaults (state restored from PlatformState)

---

## Automated Test

**File:** `symphainy-frontend/__tests__/phase1-cross-pillar-navigation.test.tsx`

**Run Command:**
```bash
cd symphainy-frontend
npm test -- phase1-cross-pillar-navigation
```

**Test Scenarios:**
1. Content → Insights → Content (state preservation)
2. State isolation (no leakage between realms)
3. State rehydration on remount
4. No default state on remount
5. Multiple realms coexist without interference

---

## Manual Validation Checklist

If automated tests are not available, use this manual checklist:

### Test 1: Content → Insights → Content

**Steps:**
1. Navigate to `/pillars/content`
2. Upload a file (or verify files exist)
3. Note the file list state
4. Navigate to `/pillars/insights`
5. Verify Content realm state is NOT visible in Insights
6. Navigate back to `/pillars/content`
7. **Verify:** File list is preserved (same files, same order)

**Expected Result:** ✅ Content realm state preserved

---

### Test 2: Insights → Journey → Insights

**Steps:**
1. Navigate to `/pillars/insights`
2. Perform an analysis (or verify analysis exists)
3. Note the analysis state
4. Navigate to `/pillars/journey`
5. Verify Insights realm state is NOT visible in Journey
6. Navigate back to `/pillars/insights`
7. **Verify:** Analysis state is preserved

**Expected Result:** ✅ Insights realm state preserved

---

### Test 3: Journey → Outcomes → Journey

**Steps:**
1. Navigate to `/pillars/journey`
2. Generate a workflow or SOP (or verify workflow exists)
3. Note the workflow state
4. Navigate to `/pillars/business-outcomes`
5. Verify Journey realm state is NOT visible in Outcomes
6. Navigate back to `/pillars/journey`
7. **Verify:** Workflow state is preserved

**Expected Result:** ✅ Journey realm state preserved

---

### Test 4: Outcomes → Content → Outcomes

**Steps:**
1. Navigate to `/pillars/business-outcomes`
2. Generate a roadmap (or verify roadmap exists)
3. Note the roadmap state
4. Navigate to `/pillars/content`
5. Verify Outcomes realm state is NOT visible in Content
6. Navigate back to `/pillars/business-outcomes`
7. **Verify:** Roadmap state is preserved

**Expected Result:** ✅ Outcomes realm state preserved

---

### Test 5: State Isolation (No Leakage)

**Steps:**
1. Navigate to `/pillars/content`
2. Upload a file with UUID `content-file-1`
3. Navigate to `/pillars/insights`
4. **Verify:** Content files are NOT visible in Insights realm state
5. Navigate to `/pillars/journey`
6. **Verify:** Neither Content nor Insights files are visible in Journey realm state

**Expected Result:** ✅ No state leakage between realms

---

### Test 6: State Rehydration from Runtime

**Steps:**
1. Navigate to `/pillars/content`
2. Upload a file
3. Wait for file to be processed (if applicable)
4. Refresh the page (F5)
5. Navigate to `/pillars/insights`
6. Navigate back to `/pillars/content`
7. **Verify:** File state is rehydrated from Runtime (not lost)

**Expected Result:** ✅ State rehydrates correctly from Runtime

---

### Test 7: No Remounted Defaults

**Steps:**
1. Navigate to `/pillars/content`
2. Upload multiple files (e.g., 3 files)
3. Navigate to `/pillars/insights`
4. Navigate back to `/pillars/content`
5. **Verify:** All 3 files are still present (not reset to empty/default)

**Expected Result:** ✅ No default state on remount

---

## Validation Criteria

### ✅ Pass Criteria

All tests must pass:
- ✅ State preserved across navigation
- ✅ No state leakage between realms
- ✅ State rehydrates from Runtime
- ✅ No remounted defaults

### ❌ Fail Criteria

If any of the following occur, Phase 1 is NOT complete:
- ❌ State lost when navigating away and back
- ❌ State from one realm visible in another realm
- ❌ State not rehydrating from Runtime
- ❌ Components reset to default/empty state on remount

---

## How to Verify State

### Using Browser DevTools

1. Open Browser DevTools (F12)
2. Go to Console tab
3. Type: `window.__PLATFORM_STATE__` (if exposed)
4. Or check React DevTools for PlatformStateProvider state

### Using Component Inspection

1. Open React DevTools
2. Find `PlatformStateProvider` component
3. Inspect `state.realm` object
4. Verify realm-specific state keys:
   - `state.realm.content.*`
   - `state.realm.insights.*`
   - `state.realm.journey.*`
   - `state.realm.outcomes.*`

---

## Common Issues and Fixes

### Issue: State Lost on Navigation

**Symptom:** Files/analysis/workflow disappears when navigating back

**Possible Causes:**
- State not being saved to PlatformStateProvider
- State being cleared on unmount
- Incorrect realm state key usage

**Fix:**
- Verify `setRealmState()` is called before navigation
- Check that state is read from `getRealmState()` on mount
- Ensure realm state keys are consistent

---

### Issue: State Leakage Between Realms

**Symptom:** Content files visible in Insights realm

**Possible Causes:**
- Incorrect realm key usage
- Shared state object reference
- State not being scoped to realm

**Fix:**
- Verify realm keys: `content/files`, `insights/analysis`, etc.
- Ensure state objects are not shared between realms
- Use realm-specific state keys

---

### Issue: State Not Rehydrating

**Symptom:** State lost on page refresh

**Possible Causes:**
- State not syncing with Runtime
- Runtime sync not working
- State not persisted to backend

**Fix:**
- Verify Runtime sync is working (check WebSocket)
- Check `syncWithRuntime()` in PlatformStateProvider
- Verify backend persistence

---

## Test Results Template

```
Date: [DATE]
Tester: [NAME]
Environment: [DEV/STAGING/PROD]

Test 1: Content → Insights → Content
  Result: [PASS/FAIL]
  Notes: [ANY ISSUES]

Test 2: Insights → Journey → Insights
  Result: [PASS/FAIL]
  Notes: [ANY ISSUES]

Test 3: Journey → Outcomes → Journey
  Result: [PASS/FAIL]
  Notes: [ANY ISSUES]

Test 4: Outcomes → Content → Outcomes
  Result: [PASS/FAIL]
  Notes: [ANY ISSUES]

Test 5: State Isolation
  Result: [PASS/FAIL]
  Notes: [ANY ISSUES]

Test 6: State Rehydration
  Result: [PASS/FAIL]
  Notes: [ANY ISSUES]

Test 7: No Remounted Defaults
  Result: [PASS/FAIL]
  Notes: [ANY ISSUES]

Overall Result: [PASS/FAIL]
```

---

## Next Steps After Test Passes

1. ✅ Mark Phase 1 as complete
2. ✅ Update Phase 1 completion document
3. ✅ Proceed to Phase 2: Backend Core Services

---

**Last Updated:** January 24, 2026  
**Status:** ✅ **READY TO RUN**
