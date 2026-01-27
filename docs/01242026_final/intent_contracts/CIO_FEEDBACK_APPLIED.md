# CIO Feedback Applied: `ingest_file` Contract Updates

**Date:** January 25, 2026  
**Status:** ✅ **UPDATED** - All four critical fixes applied  
**Intent:** `ingest_file`

---

## Summary

The CIO provided detailed feedback identifying **four critical failure points** that would break in production. All four have been incorporated into the `ingest_file` contract.

---

## Fixes Applied

### ✅ Fix 1: Redefined Idempotency Key (CRITICAL)

**Problem:** Using `execution_id` as idempotency key fails because:
- Retries get new execution_ids
- Clients reconnect
- Gateways retry
- Users double-click
- Jobs resume

**Solution:** Changed to semantic identity:
- **Primary Key:** `content_fingerprint`
- **Derived From:** `hash(file_content) + session_id`
- **Scope:** `per session, per file`

**Impact:** Enables safe retries, safe resumes, safe concurrency

---

### ✅ Fix 2: Made file_id Deterministic (CRITICAL)

**Problem:** `file_id` generated during execution means:
- Cannot dedupe before writing
- Cannot safely retry without side effects
- Cannot detect "same file, same session" replays

**Solution:** Added to Guaranteed Outputs:
- `file_id` is deterministic for identical `content_fingerprint` within same session
- `file_id` is reused if `content_fingerprint` already exists in session

**Impact:** Enables idempotency guarantees

---

### ✅ Fix 3: Added Payload Size Gate (CRITICAL)

**Problem:** Hex-encoded file content in intent payload will:
- Blow memory (large files)
- Break logs
- Break retries
- Kill observability

**Solution:** Added Payload Size Enforcement section:
- Max file_content size: 100 MB
- Action if exceeded: Reject intent immediately
- Proof test: `test_ingest_file_large_payload_rejected`

**Impact:** Prevents silent production death

---

### ✅ Fix 4: Enforced Two-Phase Persistence at Runtime (CRITICAL)

**Problem:** "Forbidden behaviors" were policy, not enforcement:
- Nothing proves persistence can't happen
- Nothing proves state can't flip
- Nothing proves storage can't finalize early

**Solution:** Added Forbidden State Transitions section:
- `ingest_file` MUST NOT write to persistent storage
- `ingest_file` MUST NOT flip `materialization_pending` to `false`
- Runtime must reject any attempt to materialize during `ingest_file`
- Proof test: `test_ingest_file_cannot_materialize`

**Impact:** Converts policy → enforcement

---

## Updated Contract Sections

### Section 1: Intent Contract
- ✅ Added Boundary Constraints (file size limit)
- ✅ Added Forbidden State Transitions (two-phase enforcement)
- ✅ Updated Guaranteed Outputs (deterministic file_id, content_fingerprint)

### Section 2: Runtime Enforcement
- ✅ Added Payload Size Enforcement
- ✅ Added three proof tests (direct API, large payload, cannot materialize)

### Section 4: Idempotency & Re-entrancy
- ✅ Changed idempotency key from `execution_id` to `content_fingerprint`
- ✅ Added Canonical Artifact Identity requirements
- ✅ Updated proof test to use `content_fingerprint`

### Section 6: Violations Found
- ✅ Updated to reflect critical issues (not just "potential")

### Section 7: Fixes Applied
- ✅ Added all four critical fixes to blockers list

### Section 9: Gate Status
- ✅ Updated blockers to reflect all four critical fixes required

---

## Current Status

**Contract Status:** ⏳ **IN PROGRESS** (not COMPLETE)

**Blockers:**
1. **CRITICAL:** Idempotency key implementation (content_fingerprint)
2. **CRITICAL:** Deterministic file_id implementation
3. **CRITICAL:** Payload size enforcement (100MB limit)
4. **CRITICAL:** Two-phase persistence enforcement (runtime check)
5. All proof tests not implemented

**Next Steps:**
1. Use this updated contract as template for remaining Content Realm intents
2. Implement fixes in Phase 2 (Intent Fixes with Enforcement)
3. Implement all proof tests

---

## Template for Remaining Intents

This updated `ingest_file` contract now serves as the **production-grade template** for all remaining intent contracts. Key elements to replicate:

1. **Semantic idempotency** (content_fingerprint, not execution_id)
2. **Deterministic artifact identity** (memoized IDs)
3. **Payload size gates** (where applicable)
4. **Forbidden state transitions** (where applicable)
5. **Multiple proof tests** (not just one)

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** ✅ **UPDATED** - Ready to use as template
