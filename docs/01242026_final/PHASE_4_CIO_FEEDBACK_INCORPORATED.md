# Phase 4 Plan - CIO Feedback Incorporated

**Date:** January 25, 2026  
**Status:** ✅ **READY FOR IMPLEMENTATION**  
**CIO Feedback:** ✅ **FULLY INCORPORATED**

---

## Executive Summary

CIO provided detailed, actionable feedback on all Phase 4 questions. All answers are grounded in what's already validated in Phase 3. This document incorporates that feedback into the Phase 4 implementation plan.

**Key Principle (from CIO):**
> "Phase 4 isn't about inventing behavior — it's about making the frontend finally obey what the backend already proved."

---

## CIO Answers Incorporated

### 1. Intent Mapping ✅

**CIO Answer:** Yes — but it lives in the backend, not in documentation yet. Phase 4.7 is where you extract the canonical mapping, not invent it.

**Action Taken:**
- ✅ Created `INTENT_MAPPING.md` extracted from realm registries
- ✅ Mapped all legacy endpoints to canonical intents
- ✅ Validated against Phase 3 E2E tests
- ✅ Source of truth: `realms/*/realm.py::declare_intents()`

**Canonical Mappings (Extracted):**
- `/api/v1/*/upload-file` → `ingest_file` ✅
- `/api/v1/insights-solution/*` → `analyze_structured_data` ✅
- `/api/v1/journey/guide-agent/*` → `analyze_coexistence` ✅
- `/api/v1/business-outcomes-*` → `generate_roadmap`, `create_poc`, `create_blueprint` ✅

**Rule:** If an intent is registered in realm and used in Phase 3 E2E tests, it's canonical.

---

### 2. File Upload Pattern ✅

**CIO Answer:** ✅ Two-phase approach — upload first, then submit intent with `file_id`.

**Why:**
- Keeps intents small and semantic
- Preserves file lifecycle, lineage, and retries
- Aligns with GCS / FileManagementAbstraction
- Already exercised by `test_e2e_parsing_produces_real_results`

**What NOT to do:**
- ❌ Base64 / hex blobs inside intent parameters
- ❌ Multipart form data via intent endpoint

**Implementation Pattern:**
```typescript
// Phase 1: Upload file to GCS
const uploadResponse = await fetch('/api/content/upload', {
  method: 'POST',
  body: formData
});
const { file_id, boundary_contract_id } = await uploadResponse.json();

// Phase 2: Submit intent with file_id
await submitIntent({
  intent_type: 'ingest_file',
  parameters: {
    file_id: file_id,
    boundary_contract_id: boundary_contract_id,
    ui_name: fileName,
    file_type: fileType,
    mime_type: mimeType
  }
});
```

---

### 3. State Persistence (setRealmState) ✅

**CIO Answer:** Defer Runtime persistence of frontend state to Phase 5.

**Why:**
- Runtime authority is already enforced via intents and artifacts
- Persisting UI state directly risks contaminating domain logic
- No semantic contract yet for "realm UI state" persistence

**What Phase 4 Should Do:**
- ✅ Leave the TODO in place
- ✅ Clarify intent with a comment: "Frontend-only continuity, state persisted via intents/artifacts"
- ✅ Ensure state is derived from artifacts wherever possible

**Key Principle:**
> "State is persisted by doing work (intents), not by syncing UI memory."

**Where Persistence Already Happens:**
- ExecutionLifecycleManager
- Intent handlers
- Artifact storage (ArangoDB / Redis)

---

### 4. Error Handling During Migration ✅

**CIO Answer:** Recommended posture for Phase 4

**What to Do:**
- ✅ User-friendly error messages: Yes (clear, immediate, actionable)
- ✅ Migration warnings / logging: Yes (console warnings in dev, optional structured logging)
- ❌ Retry logic: Not yet (retries belong in Runtime policies, not UI glue)

**Migration Rule:**
When replacing a legacy endpoint:
1. Remove it completely
2. Replace with intent submission
3. On failure:
   - Show error
   - Do NOT silently fallback
   - Do NOT call legacy paths

**Where to Look for Patterns:**
- ServiceLayerAPI
- InteractiveChat
- Existing intent submit error handling

---

### 5. Testing Strategy ✅

**CIO Answer:** Layered validation, not more complexity.

**What to Do:**
- ✅ Test each pillar after migration (required)
  - Migrate one pillar
  - Run it end-to-end
  - Stop if anything smells off

- ✅ Re-run Phase 3 E2E tests (required)
  - These are regression lock
  - If one fails, fix before proceeding

- ➖ Add new E2E tests? (optional)
  - Only if:
    - You introduce new intent types
    - You change artifact semantics
  - Otherwise, reuse existing suite

**Rule of Thumb:**
> "If frontend migration requires new backend E2E tests, something is wrong."

---

## Team Recommendations - CIO Validation

### ✅ Start with Task 4.7 (Audit)
**CIO:** Yes — this is the right first move. It prevents drift and bikeshedding.

**Status:** ✅ **COMPLETE** - Intent mapping extracted from realm registries

---

### ✅ Migration Helper Utility
**CIO:** Good idea, with one constraint:
- Thin wrapper only
- No semantic abstraction
- Don't hide intent types or parameters

**Status:** ✅ **COMPLETE** - Created `intentSubmissionHelper.ts` (thin wrapper only)

---

### ✅ Validate Runtime Authority
**CIO:** Yes — re-run the Phase 0 overwrite test once, after the first pillar migration.

**Status:** ⚠️ **PENDING** - Will validate after first pillar migration

---

### ✅ Incremental Migration
**CIO:** Correct — one pillar at a time is non-negotiable here.

**Status:** ✅ **PLANNED** - Will migrate one pillar at a time

---

### ✅ Document Intent Types
**CIO:** Yes — and generate it from the backend, not the frontend.

**Status:** ✅ **COMPLETE** - `INTENT_MAPPING.md` extracted from backend realm registries

---

## Updated Phase 4 Implementation Plan

### Task 4.7: Audit All Pillars ✅ **COMPLETE**

**Status:** ✅ Complete
- Extracted canonical intent mapping from realm registries
- Created `INTENT_MAPPING.md` with all mappings
- Validated against Phase 3 E2E tests

**Deliverable:** `docs/01242026_final/INTENT_MAPPING.md`

---

### Task 4.6: Migrate Legacy Endpoints to Intent-Based API ⚠️ **READY**

**Status:** Ready to start
**Order:** Content → Insights → Journey → Outcomes (one pillar at a time)

**Migration Pattern:**
1. Remove legacy endpoint call completely
2. Replace with `submitIntent()` from `intentSubmissionHelper.ts`
3. Use canonical intent type from `INTENT_MAPPING.md`
4. Use two-phase upload pattern for file uploads
5. Show user-friendly error messages
6. Log migration warnings in dev
7. Test end-to-end
8. Re-run Phase 3 E2E tests

**Files to Migrate (Content Pillar First):**
- `ContentPillarUpload.tsx` - File upload (two-phase pattern)
- `file-processing.ts` - File processing service
- `ContentAPIManager.ts` - Content API manager
- `FileDashboard.tsx` - File listing
- `DataMash.tsx` - File listing
- `ParsePreview.tsx` - File listing
- `MetadataExtractor.tsx` - File metadata

---

### Task 4.1: Fix State Management Placeholders ⚠️ **READY**

**Status:** Ready to start

**Files:**
- `components/content/FileUploader.tsx`
- `components/operations/CoexistenceBluprint.tsx`
- `components/insights/VARKInsightsPanel.tsx`

**Action:**
1. Replace placeholders with `usePlatformState()`
2. Add comment: "Frontend-only continuity, state persisted via intents/artifacts"
3. Leave TODO for Runtime persistence (Phase 5)

---

### Task 4.2: Fix Mock User ID ⚠️ **READY**

**Status:** Ready to start

**File:** `components/content/FileUploader.tsx`

**Action:**
1. Use `useSessionBoundary()` to get actual user ID
2. Replace all `"mock-user"` with actual user ID
3. Test with authenticated and anonymous sessions

---

### Task 4.3: Fix File Upload Mock Fallback ⚠️ **READY**

**Status:** Ready to start

**File:** `components/content/FileUploader.tsx`

**Action:**
1. Remove mock file creation code
2. Add proper error handling (user-friendly messages)
3. Use two-phase upload pattern
4. Test with invalid session

---

### Task 4.4: Implement Business Outcomes Handlers ⚠️ **READY**

**Status:** Ready to start

**File:** `app/(protected)/pillars/business-outcomes/page.tsx`

**Action:**
1. Use `submitIntent()` helper with canonical intents:
   - `create_blueprint` (from Outcomes realm)
   - `create_poc` (from Outcomes realm) ✅ Validated
   - `generate_roadmap` (from Outcomes realm) ✅ Validated
   - `synthesize_outcome` (from Outcomes realm)
2. Connect to Outcomes realm endpoints via intent-based API
3. Test end-to-end flow

---

### Task 4.5: Remove All Direct API Calls ⚠️ **READY**

**Status:** Ready to start (after Task 4.6)

**Action:**
1. Find all direct `fetch()` calls to `/api/*`
2. Replace with `submitIntent()` helper
3. Test after each replacement

---

## Implementation Order (Per CIO Feedback)

1. ✅ **Task 4.7:** Audit and extract intent mapping (COMPLETE)
2. ✅ **Migration Helper:** Create thin wrapper utility (COMPLETE)
3. **Task 4.6:** Migrate legacy endpoints (Content pillar first)
4. **Task 4.1-4.3:** Fix state management, mocks, placeholders
5. **Task 4.4:** Implement Business Outcomes handlers
6. **Task 4.5:** Remove all direct API calls

---

## Success Criteria (Updated)

- ✅ All legacy endpoints replaced with intent-based API
- ✅ All operations go through Runtime/ExecutionLifecycleManager
- ✅ Boundary contracts created automatically
- ✅ Two-phase upload pattern used for file uploads
- ✅ User-friendly error messages (no silent fallbacks)
- ✅ Migration warnings logged in dev
- ✅ All tests pass (including Phase 3 E2E tests)
- ✅ No direct API calls remain
- ✅ State management placeholders fixed (with Phase 5 TODO)
- ✅ All mocks removed

---

## Key Principles (From CIO)

1. **Phase 4 isn't about inventing behavior** — it's about making the frontend finally obey what the backend already proved.

2. **State is persisted by doing work (intents), not by syncing UI memory.**

3. **If frontend migration requires new backend E2E tests, something is wrong.**

4. **One pillar at a time is non-negotiable.**

5. **Extract canonical mapping, don't invent it.**

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** ✅ **READY FOR IMPLEMENTATION - CIO FEEDBACK INCORPORATED**
