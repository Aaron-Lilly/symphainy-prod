# Artifact API Known Limitations

**Date:** January 19, 2026  
**Status:** ⚠️ **KNOWN LIMITATIONS** (Non-blocking for MVP)

---

## Limitation 1: File Artifact Direct API Retrieval

**Issue:** Files stored in GCS but without Supabase metadata cannot be retrieved via direct API call.

**Root Cause:**
- Files are uploaded to GCS successfully
- Supabase metadata creation may fail (logged as warning, but upload continues)
- Direct API lookup (`GET /api/artifacts/{file_id}`) requires Supabase metadata
- File lookup falls back to Supabase UUID lookup, which fails if metadata wasn't created

**Current Workaround:**
- Execution status includes `file_reference` and `file_path` in artifacts
- Tests check for `file_path` as fallback
- Files are retrievable via execution status (which has full context)

**Impact:**
- ✅ **Non-blocking for MVP** - Execution status works, tests pass
- ⚠️ Direct API calls may fail if file metadata not in Supabase
- 🔄 **Future Fix:** Ensure Supabase metadata creation is retried or required

**Solution (Future):**
1. Make Supabase metadata creation required (fail upload if metadata fails)
2. Add retry logic for metadata creation
3. Add file_id → file_reference mapping in State Surface
4. Add fallback to GCS metadata lookup

---

## Limitation 2: File ID to File Reference Mapping

**Issue:** No direct mapping from `file_id` (UUID) to `file_reference` (format: `file:tenant:session:file_id`).

**Impact:**
- Direct API calls need `file_id` but don't have `session_id` context
- Can't construct `file_reference` without session context
- State Surface lookup requires `file_reference`, not `file_id`

**Current Workaround:**
- Execution status provides full context (includes `file_reference`)
- Tests use execution status artifacts, not direct API calls

**Solution (Future):**
- Add `file_id` → `file_reference` index in State Surface
- Or: Store `file_reference` in Supabase metadata
- Or: Make API accept both `file_id` and `file_reference`

---

## Current Status

✅ **All 4 phases implemented and working:**
- Phase 1: Unified artifact retrieval ✅
- Phase 2: Artifact type standardization ✅
- Phase 3: Execution status enhancement ✅
- Phase 4: Materialization policy awareness ✅

✅ **Tests passing:**
- File ingestion test passes
- Execution status expansion works
- Artifact retrieval works via execution status

⚠️ **Known limitations:**
- Direct API calls for files without Supabase metadata may fail
- This is non-blocking as execution status provides full context

---

## Recommendations

1. **Short-term (MVP):**
   - Continue using execution status for artifact retrieval (has full context)
   - Document that direct API calls require Supabase metadata

2. **Medium-term (Post-MVP):**
   - Make Supabase metadata creation required (fail fast)
   - Add retry logic for metadata creation
   - Add file_id → file_reference mapping

3. **Long-term:**
   - Unified file/artifact storage (single source of truth)
   - Enhanced error handling and fallbacks
   - Performance optimization for artifact lookups
