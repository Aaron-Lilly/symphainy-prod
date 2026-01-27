# CIO-Guided Execution Plan: Journey 1 as Forcing Function

**Date:** January 25, 2026  
**Status:** 🔴 **ACTIVE EXECUTION PLAN**  
**Principle:** Journey 1 execution drives all work, not contracts or infrastructure

---

## Executive Summary

**Journey 1 is the primary unit of work.**  
Intent contracts, idempotency, and test infrastructure exist *only* to make Journey 1 pass.

This plan follows CIO guidance to:
1. Freeze Journey 1 contract (with 3 surgical edits - ✅ DONE)
2. Run ONE test (Happy Path) immediately
3. Let failures dictate work order
4. Only then finish remaining intent contracts

---

## Core Principle

> **Journey 1 execution is the forcing function.**
> 
> Everything else (intent contracts, idempotency, tests) exists to make Journey 1 pass.
> 
> We fix what blocks Journey 1, not what's "pending" in contracts.

---

## Step 1: Freeze Journey 1 Contract ✅ COMPLETE

**Status:** ✅ **FROZEN** (with 3 surgical edits applied)

### Edit 1: `get_semantic_interpretation` Non-Gating ✅
- Added explicit note: "must not block journey completion"
- Clarified it tolerates partial upstream state
- Marked as optional, non-gating

### Edit 2: Idempotency Scope Per Intent ✅
- Added explicit table of idempotency keys per intent
- Prevents philosophical debates during implementation
- Clear scope definition

### Edit 3: Journey Completion Definition ✅
- Explicitly defined: "Journey 1 is complete when file is materialized OR user abandons"
- Clarified: "Completion ≠ semantic interpretation displayed"
- Protects from UI-driven false failures

**Journey contract is now FROZEN. No further changes until Happy Path passes.**

---

## Step 2: Run ONE Test - Happy Path (IMMEDIATE)

**Goal:** Run Journey 1 Happy Path test immediately, even if it fails spectacularly.

**Why:**
- Exposes which intent contracts are actually incomplete
- Reveals whether test helpers are right-sized
- Collapses abstract uncertainty into concrete errors
- **Highest leverage move**

### Execution

**Option A: Manual Test (Fastest)**
1. Start application
2. Upload a file
3. Click "Parse"
4. Click "Extract Embeddings"
5. Click "Save"
6. Document where it breaks

**Option B: Automated Test (More Rigorous)**
1. Run `npm test -- journey_1_file_upload_processing.test.ts`
2. Focus on "Scenario 1: Happy Path" test
3. Document all failures
4. Fix only what blocks the happy path

**Recommended:** Start with **Option A (Manual)** for fastest feedback, then create automated test based on what we learn.

### What We're Looking For

- ✅ Does `ingest_file` work?
- ✅ Does `parse_content` work?
- ✅ Does `extract_embeddings` work?
- ✅ Does `save_materialization` work?
- ✅ Do intents flow correctly?
- ✅ Does state persist across steps?
- ✅ Are execution_ids tracked?

### Expected Outcome

**We expect failures.** That's the point. The failures will tell us:
- Which intent needs deeper work
- Which boundary assumption is wrong
- Which state transition is leaky

**This is the system teaching us.**

---

## Step 3: Let Failures Dictate Work Order

**Principle:** Do NOT finish remaining intent contracts "because they're pending."

**Instead:**
1. Run happy path
2. Note where it breaks
3. Fix **only what blocks Journey 1**

### Example Failure-Driven Workflow

**If happy path fails at `parse_content`:**
- Fix `parse_content` intent contract
- Fix `parse_content` implementation
- Verify `parse_content` works in journey context
- **Do NOT** fix `extract_embeddings` or `get_semantic_interpretation` yet

**If happy path fails at `save_materialization`:**
- Fix `save_materialization` idempotency (if needed)
- Fix `save_materialization` state transitions
- Verify `save_materialization` works in journey context
- **Do NOT** fix other intents yet

### What We'll Likely Discover

- One intent needs deeper idempotency than expected
- One boundary assumption is wrong
- One state transition is leaky
- One integration point is broken

**That's the system teaching us. We listen.**

---

## Step 4: Only Then Finish Remaining Intent Contracts

**Gate:** Journey 1 happy path passes + one failure scenario passes

**After gate passes:**
- Finish remaining 3 intent verifications (mechanical, not cognitive)
- Formalize proof tests (we know what works)
- Lock idempotency patterns (we know what's needed)

**At this point, intent work becomes mechanical, not cognitive.**

---

## What We're NOT Doing Yet (Explicitly Deferred)

### Deferred (Multipliers, Not Foundations)
- ❌ Full chaos testing
- ❌ Browser-only tests (hard refresh, network throttling, session expiration)
- ❌ CI polish
- ❌ Exhaustive negative matrices
- ❌ Complete test infrastructure for all intents
- ❌ All 5 journey scenarios (only Happy Path + one failure)

**Why:** These are *multipliers*, not foundations. Right now we're still pouring concrete.

**When:** After Journey 1 happy path passes and we understand what actually works.

---

## Updated Work Sequence

### Immediate (Today)
1. ✅ Freeze Journey 1 contract (DONE)
2. 🚦 **Run Happy Path test** (manual or automated)
3. 📝 Document all failures
4. 🔧 Fix **only** what blocks Journey 1

### Short Term (After Happy Path Passes)
1. Run one failure scenario (Injected Failure at one step)
2. Fix what breaks
3. Verify journey recovers

### Medium Term (After Journey 1 Works)
1. Finish remaining intent contracts (mechanical)
2. Formalize proof tests
3. Lock idempotency patterns

### Long Term (After Foundation Solid)
1. Full test infrastructure
2. All 5 journey scenarios
3. 3D testing (Functional, Architectural, SRE)
4. Browser-only tests
5. Chaos testing

---

## Success Criteria

### Journey 1 Happy Path is "Complete" when:
- ✅ File uploads successfully (`ingest_file`)
- ✅ File parses successfully (`parse_content`)
- ✅ Embeddings extract successfully (`extract_embeddings`)
- ✅ File saves successfully (`save_materialization`)
- ✅ All intents use intent-based API
- ✅ All execution_ids tracked
- ✅ State persists across steps
- ✅ Journey completes end-to-end

**Note:** `get_semantic_interpretation` is optional and does not gate completion.

---

## Key Insights from CIO Feedback

### 1. Journey 1 is the Spine
- Not contracts
- Not infrastructure
- Not idempotency
- **Journey 1 execution**

### 2. Failures Are Teachers
- Run happy path even if it fails
- Failures reveal what's actually broken
- Fix only what blocks Journey 1

### 3. Sequence Matters
- Happy path first
- One failure scenario second
- Then finish contracts (mechanical)
- Then multipliers (chaos, browser tests, etc.)

### 4. We're Not Drifting
- This feels heavy because we're treating platform like platform
- Not over-engineering, this is minimum for platform
- Convergence, not drift

---

## Next Action

**🚦 IMMEDIATE: Run Journey 1 Happy Path Test**

**Options:**
1. **Manual:** Start app, upload file, parse, extract, save - document failures
2. **Automated:** Run test, fix test infrastructure, document failures

**Recommended:** Start with manual for fastest feedback, then automate based on learnings.

---

**Last Updated:** January 25, 2026  
**Owner:** Development Team  
**Status:** 🔴 **ACTIVE** - Ready to execute Happy Path test
