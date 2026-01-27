# Phase 2: Intent Fixes with Enforcement - Content Realm Progress

**Date:** January 25, 2026  
**Status:** ✅ **IN PROGRESS** - Critical fixes complete, remaining work documented  
**Realm:** Content (Priority 1, Journey 1)

---

## Summary

Phase 2 fixes for Content Realm intents are **partially complete**. All **critical violations** have been fixed. Remaining work focuses on idempotency implementation, proof tests, and negative journey evidence verification.

---

## ✅ Completed Fixes

### 1. **CRITICAL: Fixed `save_materialization` Direct API Call** ✅

**Problem:** `save_materialization` was using direct `fetch()` call, bypassing Runtime and losing observability.

**Solution:**
- Migrated to `submitIntent('save_materialization', ...)`
- Added execution tracking via `platformState.trackExecution(executionId)`
- Implemented execution status polling to extract `materialization_id`
- Updated `SaveMaterializationResponse` interface to include `materialization_id`

**Files Changed:**
- `symphainy-frontend/shared/managers/ContentAPIManager.ts` (lines 217-276)
- `intent_contracts/content/save_materialization.md` (updated status)

**Impact:**
- ✅ All Content Realm intents now use intent-based API
- ✅ Full observability (execution_id, trace continuity)
- ✅ Runtime enforcement active

---

### 2. **Added Missing Parameter Validation** ✅

**Problem:** Several intents lacked parameter validation before `submitIntent`, allowing invalid requests to reach Runtime.

**Solution:**
- Added parameter validation for `parse_content` (fileId, fileReference)
- Added parameter validation for `extract_embeddings` (parsedFileId, parsedFileReference)
- Added parameter validation for `get_parsed_file` (fileId, fileReference)
- Standardized `get_parsed_file` to use `validateSession()` instead of manual check

**Files Changed:**
- `symphainy-frontend/shared/managers/ContentAPIManager.ts`:
  - `parseFile()` - lines 371-377
  - `extractEmbeddings()` - lines 424-430
  - `getParsedFile()` - lines 457-467

**Impact:**
- ✅ All Content Realm intents validate parameters before Runtime submission
- ✅ Clear error messages for invalid inputs
- ✅ Consistent validation pattern across all intents

---

### 3. **Updated Intent Contracts** ✅

**Action:** Updated all affected intent contracts to reflect completed fixes.

**Files Updated:**
- `intent_contracts/content/save_materialization.md` - Direct API call fixed, observability implemented
- `intent_contracts/content/parse_content.md` - Parameter validation added
- `intent_contracts/content/extract_embeddings.md` - Parameter validation added
- `intent_contracts/content/get_parsed_file.md` - Parameter validation added, session validation standardized

**Impact:**
- ✅ Contracts accurately reflect current implementation state
- ✅ Clear documentation of what's fixed vs. what remains

---

## ⏳ Remaining Work

### 1. **Idempotency Implementation** ⏳

**Status:** Not yet implemented (requires backend changes)

**Required for All 7 Content Realm Intents:**
- `ingest_file`: `content_fingerprint = hash(file_content + session_id)`
- `parse_content`: `parsing_fingerprint = hash(file_id + file_reference + parse_options)`
- `save_materialization`: `materialization_fingerprint = hash(file_id + boundary_contract_id + session_id)`
- `extract_embeddings`: `embedding_fingerprint = hash(parsed_file_id + parsed_file_reference + embedding_options)`
- `get_parsed_file`: `query_fingerprint = hash(file_id + file_reference + session_id)`
- `get_semantic_interpretation`: `interpretation_query_fingerprint = hash(file_id + file_reference + session_id)`
- `list_files`: `list_query_fingerprint = hash(tenant_id + session_id)`

**Implementation Requirements:**
1. **Frontend:** Calculate fingerprint before `submitIntent`, pass as parameter
2. **Runtime:** Accept fingerprint, check for existing execution with same fingerprint
3. **Backend:** Return existing artifact IDs if fingerprint matches (memoization)
4. **State:** Store fingerprint → artifact_id mapping in session state

**Complexity:** High (requires Runtime and backend changes)

**Estimated Effort:** 2-3 days (backend + frontend + testing)

---

### 2. **Proof Tests** ⏳

**Status:** Not yet implemented (test files need to be created)

**Required Tests for All 7 Intents:**

**Test 1: Direct API Call Failure**
- `test_<intent>_direct_api_call_fails`
- Verify direct API calls are rejected

**Test 2: Invalid Parameters**
- `test_<intent>_invalid_parameters`
- Verify intent rejects invalid inputs

**Test 3: Cross-Tenant Access** (for query intents)
- `test_<intent>_cross_tenant_access`
- Verify authorization enforcement

**Test 4: Idempotency** (after idempotency implementation)
- `test_<intent>_idempotency`
- Verify same fingerprint returns same result

**Total Tests Needed:** ~28 tests (4 per intent × 7 intents)

**Implementation Requirements:**
1. Create test directory structure
2. Set up test framework (Jest/Vitest)
3. Mock Runtime and platform state
4. Implement all 28 tests
5. Add to CI/CD pipeline

**Complexity:** Medium (test infrastructure + test implementation)

**Estimated Effort:** 1-2 days

---

### 3. **Negative Journey Evidence Verification** ⏳

**Status:** Partially verified (some intents verified, others need testing)

**Current Status:**
- ✅ `ingest_file` - Verified (ContentAPIManager line 114-116)
- ✅ `save_materialization` - Verified (ContentAPIManager line 233-235)
- ✅ `get_semantic_interpretation` - Verified (ContentAPIManager line 523-528)
- ✅ `list_files` - Verified (ContentAPIManager line 288)
- ⏳ `parse_content` - Needs verification
- ⏳ `extract_embeddings` - Needs verification
- ⏳ `get_parsed_file` - Needs verification

**Implementation Requirements:**
1. Test each intent with missing required parameters
2. Verify clear error messages
3. Verify no state corruption
4. Document results in intent contracts

**Complexity:** Low (manual testing + documentation)

**Estimated Effort:** 0.5 days

---

## 📊 Progress Summary

### Content Realm Intents (7 total)

| Intent | Direct API Call | Parameter Validation | Idempotency | Proof Tests | Negative Evidence | Status |
|--------|----------------|---------------------|-------------|-------------|-------------------|--------|
| `ingest_file` | ✅ Fixed | ✅ Complete | ⏳ Pending | ⏳ Pending | ✅ Verified | 🟡 In Progress |
| `parse_content` | ✅ Fixed | ✅ Complete | ⏳ Pending | ⏳ Pending | ⏳ Pending | 🟡 In Progress |
| `save_materialization` | ✅ **FIXED** | ✅ Complete | ⏳ Pending | ⏳ Pending | ✅ Verified | 🟡 In Progress |
| `extract_embeddings` | ✅ Fixed | ✅ Complete | ⏳ Pending | ⏳ Pending | ⏳ Pending | 🟡 In Progress |
| `get_parsed_file` | ✅ Fixed | ✅ Complete | ⏳ Pending | ⏳ Pending | ⏳ Pending | 🟡 In Progress |
| `get_semantic_interpretation` | ✅ Fixed | ✅ Complete | ⏳ Pending | ⏳ Pending | ✅ Verified | 🟡 In Progress |
| `list_files` | ✅ Fixed | ✅ Complete | ⏳ Pending | ⏳ Pending | ✅ Verified | 🟡 In Progress |

**Legend:**
- ✅ Complete
- ⏳ Pending
- 🟡 In Progress
- 🔴 Blocked

---

## 🎯 Next Steps

### Immediate (High Priority)
1. **Verify negative journey evidence** for remaining 3 intents (0.5 days)
   - `parse_content`
   - `extract_embeddings`
   - `get_parsed_file`

### Short Term (Medium Priority)
2. **Implement proof tests** (1-2 days)
   - Set up test infrastructure
   - Implement all 28 tests
   - Add to CI/CD

### Medium Term (High Priority, Complex)
3. **Implement idempotency** (2-3 days)
   - Design fingerprint calculation approach
   - Implement frontend fingerprint calculation
   - Coordinate with backend team for Runtime/backend changes
   - Test idempotency behavior

---

## 📝 Notes

### Critical Achievement
**All Content Realm intents now use intent-based API.** This was the most critical violation and is now completely resolved.

### Remaining Complexity
**Idempotency implementation** is the most complex remaining task, as it requires:
- Frontend changes (fingerprint calculation)
- Runtime changes (fingerprint acceptance and memoization)
- Backend changes (artifact ID memoization)
- State management (fingerprint → artifact_id mapping)

This should be coordinated with the backend team to ensure proper implementation.

### Test Strategy
Proof tests should be implemented **after** idempotency is complete, as idempotency tests are part of the proof test suite. However, the first 3 test types (direct API call, invalid parameters, cross-tenant) can be implemented now.

---

**Last Updated:** January 25, 2026  
**Owner:** Development Team  
**Status:** ✅ **Critical Fixes Complete** - Ready for next phase
