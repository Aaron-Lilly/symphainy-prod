# Test Execution Results

**Date:** [Date/Time]  
**Phase:** [Phase Number or "All"]  
**Status:** [Pass/Fail/Partial]  
**Executed By:** [Name]

---

## Executive Summary

**Total Tests:** [X]  
**Passed:** [Y]  
**Failed:** [Z]  
**Skipped:** [W]  
**Pass Rate:** [Y/X * 100]%

**Overall Status:** [✅ Pass / ❌ Fail / ⚠️ Partial]

---

## Phase Results

### Phase 1: Infrastructure Health & Connectivity

**Status:** [Pass/Fail/Partial]  
**Tests Run:** [X]  
**Passed:** [Y]  
**Failed:** [Z]

#### Test Results

| Test Name | Status | Notes |
|-----------|--------|-------|
| Service Startup | [✅/❌] | [Notes] |
| Infrastructure Health | [✅/❌] | [Notes] |
| Basic Connectivity | [✅/❌] | [Notes] |

#### Failures

**Test:** [Test Name]  
- **Location:** `tests/path/to/test.py::test_name`
- **Expected:** [Expected behavior]
- **Actual:** [Actual behavior]
- **Error:** [Error message]
- **Impact:** [Critical/High/Medium/Low]
- **Root Cause:** [Hypothesis]
- **Priority:** [1-5, where 1 is highest]
- **Logs:** [Relevant log excerpts]

---

### Phase 2: Core Flows (API Contracts & Realm Flows)

**Status:** [Pass/Fail/Partial]  
**Tests Run:** [X]  
**Passed:** [Y]  
**Failed:** [Z]

#### Test Results

| Test Name | Status | Notes |
|-----------|--------|-------|
| API Contracts | [✅/❌] | [Notes] |
| Experience API | [✅/❌] | [Notes] |
| Realm Flows | [✅/❌] | [Notes] |
| Cross-Realm Flows | [✅/❌] | [Notes] |

#### Failures

[Same format as Phase 1]

---

### Phase 3: Data Integrity & Resilience

**Status:** [Pass/Fail/Partial]  
**Tests Run:** [X]  
**Passed:** [Y]  
**Failed:** [Z]

#### Test Results

| Test Name | Status | Notes |
|-----------|--------|-------|
| State Abstraction | [✅/❌] | [Notes] |
| Artifact Storage | [✅/❌] | [Notes] |
| Write-Ahead Log | [✅/❌] | [Notes] |
| Error Handling | [✅/❌] | [Notes] |

#### Failures

[Same format as Phase 1]

---

### Phase 4: Performance & Pressure Tests

**Status:** [Pass/Fail/Partial]  
**Tests Run:** [X]  
**Passed:** [Y]  
**Failed:** [Z]

#### Test Results

| Test Name | Status | Notes |
|-----------|--------|-------|
| Performance Tests | [✅/❌] | [Notes] |

#### Failures

[Same format as Phase 1]

---

### Phase 5: Authentication & Authorization

**Status:** [Pass/Fail/Partial]  
**Tests Run:** [X]  
**Passed:** [Y]  
**Failed:** [Z]

#### Test Results

| Test Name | Status | Notes |
|-----------|--------|-------|
| Security Tests | [✅/❌] | [Notes] |
| Auth & WebSocket | [✅/❌] | [Notes] |

#### Failures

[Same format as Phase 1]

---

## Critical Issues Summary

### 🔴 Critical (Must Fix Before Browser Testing)

1. **[Issue Name]**
   - **Test:** [Test Name]
   - **Impact:** [Description]
   - **Fix Priority:** 1

### 🟡 High (Should Fix Before Browser Testing)

1. **[Issue Name]**
   - **Test:** [Test Name]
   - **Impact:** [Description]
   - **Fix Priority:** 2

### 🟢 Medium (Can Fix During Browser Testing)

1. **[Issue Name]**
   - **Test:** [Test Name]
   - **Impact:** [Description]
   - **Fix Priority:** 3

---

## Recommendations

### Before Browser Testing

1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

### During Browser Testing

1. [Recommendation 1]
2. [Recommendation 2]

---

## Next Steps

- [ ] Fix critical issues
- [ ] Re-run failed tests
- [ ] Verify fixes
- [ ] Proceed to browser testing

---

## Environment Details

**Platform Version:** [Version]  
**Test Environment:** [Local/VM/Cloud]  
**Infrastructure:** [Docker Compose/Kubernetes/etc]  
**Services Running:** [List services]

---

## Notes

[Any additional notes, observations, or context]
