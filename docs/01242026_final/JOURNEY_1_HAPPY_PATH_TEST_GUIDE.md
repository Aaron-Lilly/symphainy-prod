# Journey 1 Happy Path Test Guide

**Date:** January 25, 2026  
**Status:** 🚦 **READY TO EXECUTE**  
**Goal:** Run Journey 1 Happy Path test immediately, document failures, fix only what blocks

---

## Test Objective

**Run Journey 1 Happy Path end-to-end and document where it breaks.**

This is the highest leverage move - it will collapse abstract uncertainty into concrete errors.

---

## Test Steps (Manual - Fastest Feedback)

### Prerequisites
- [ ] Application running
- [ ] User logged in
- [ ] Test file ready (small text file, < 1MB)

### Execution Steps

1. **Step 1: Upload File (`ingest_file`)**
   - [ ] Navigate to Content pillar
   - [ ] Click "Upload File"
   - [ ] Select test file
   - [ ] Click "Upload"
   - [ ] **Verify:** File uploads successfully
   - [ ] **Verify:** `file_id` is returned
   - [ ] **Verify:** `boundary_contract_id` is returned
   - [ ] **Verify:** `materialization_pending: true` (file not yet saved)
   - [ ] **Document:** Any errors or unexpected behavior

2. **Step 2: Parse File (`parse_content`)**
   - [ ] Click "Parse" on uploaded file
   - [ ] **Verify:** File parses successfully
   - [ ] **Verify:** `parsed_file_id` is returned
   - [ ] **Verify:** `parsed_file_reference` is returned
   - [ ] **Verify:** Structure/chunks are extracted
   - [ ] **Document:** Any errors or unexpected behavior

3. **Step 3: Extract Embeddings (`extract_embeddings`)**
   - [ ] Click "Extract Embeddings" (or automatic after parsing)
   - [ ] **Verify:** Embeddings extract successfully
   - [ ] **Verify:** `embeddings_id` is returned
   - [ ] **Verify:** `embedding_reference` is returned
   - [ ] **Document:** Any errors or unexpected behavior

4. **Step 4: Save File (`save_materialization`)**
   - [ ] Click "Save" to persist file
   - [ ] **Verify:** File saves successfully
   - [ ] **Verify:** `materialization_id` is returned
   - [ ] **Verify:** `materialization_pending: false` (file is now saved)
   - [ ] **Verify:** File appears in file list (persisted)
   - [ ] **Document:** Any errors or unexpected behavior

5. **Step 5: Get Semantic Interpretation (Optional)**
   - [ ] Click "View Interpretation" (if available)
   - [ ] **Verify:** Interpretation is returned (optional, non-gating)
   - [ ] **Document:** Any errors or unexpected behavior

---

## What to Document

### For Each Step

**If Step Succeeds:**
- ✅ Step completed successfully
- ✅ Observable artifacts returned (file_id, parsed_file_id, etc.)
- ✅ State updated correctly

**If Step Fails:**
- ❌ **Error Message:** [exact error message]
- ❌ **Where It Failed:** [which intent, which line if known]
- ❌ **What Was Expected:** [what should have happened]
- ❌ **What Actually Happened:** [what actually happened]
- ❌ **State After Failure:** [what state is the system in?]
- ❌ **Can User Retry?** [yes/no, and how]

### Overall Journey

**Journey Status:**
- [ ] ✅ Complete (all steps succeeded)
- [ ] ❌ Failed at Step [X]
- [ ] ⚠️ Partial (some steps succeeded, some failed)

**Observations:**
- [ ] All intents used intent-based API (no direct fetch calls)
- [ ] All execution_ids tracked
- [ ] State persisted across steps
- [ ] Journey completed end-to-end

---

## Failure Analysis

### If Happy Path Fails

**Document:**
1. **Which step failed?** (ingest_file, parse_content, extract_embeddings, save_materialization)
2. **What was the error?** (exact error message)
3. **What state is the system in?** (what worked, what didn't)
4. **Can the user retry?** (is state consistent enough to retry?)

**Then:**
- Fix **only** what blocks Journey 1
- Do NOT fix other intents yet
- Do NOT finish other contracts yet
- Fix the blocker, re-run happy path

---

## Success Criteria

**Happy Path is "Complete" when:**
- ✅ File uploads successfully
- ✅ File parses successfully
- ✅ Embeddings extract successfully
- ✅ File saves successfully
- ✅ All intents use intent-based API
- ✅ All execution_ids tracked
- ✅ State persists across steps
- ✅ Journey completes end-to-end

**Note:** `get_semantic_interpretation` is optional and does not gate completion.

---

## Next Steps After Test

### If Happy Path Passes
1. Run one failure scenario (Injected Failure at one step)
2. Verify journey handles failure gracefully
3. Then finish remaining intent contracts (mechanical)

### If Happy Path Fails
1. Document all failures
2. Fix **only** what blocks Journey 1
3. Re-run happy path
4. Repeat until happy path passes

---

## Test Results Template

```markdown
## Journey 1 Happy Path Test Results

**Date:** [date]
**Tester:** [name]
**Test File:** [filename]

### Step 1: ingest_file
- Status: ✅ Pass | ❌ Fail
- file_id: [value or N/A]
- boundary_contract_id: [value or N/A]
- materialization_pending: [true/false or N/A]
- Errors: [none or error message]

### Step 2: parse_content
- Status: ✅ Pass | ❌ Fail
- parsed_file_id: [value or N/A]
- parsed_file_reference: [value or N/A]
- Errors: [none or error message]

### Step 3: extract_embeddings
- Status: ✅ Pass | ❌ Fail
- embeddings_id: [value or N/A]
- embedding_reference: [value or N/A]
- Errors: [none or error message]

### Step 4: save_materialization
- Status: ✅ Pass | ❌ Fail
- materialization_id: [value or N/A]
- materialization_pending: [true/false or N/A]
- Errors: [none or error message]

### Overall Journey
- Status: ✅ Complete | ❌ Failed at Step [X] | ⚠️ Partial
- All intents use intent-based API: ✅ | ❌
- All execution_ids tracked: ✅ | ❌
- State persisted across steps: ✅ | ❌

### Blockers Identified
1. [Blocker 1 description]
2. [Blocker 2 description]
...

### Next Actions
1. [Action 1]
2. [Action 2]
...
```

---

**Last Updated:** January 25, 2026  
**Owner:** Development Team  
**Status:** 🚦 **READY TO EXECUTE**
