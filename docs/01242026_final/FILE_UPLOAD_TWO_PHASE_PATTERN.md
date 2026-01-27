# File Upload Two-Phase Pattern - CTO Clarification

**Date:** January 25, 2026  
**Status:** ✅ **CLARIFIED BY CTO**  
**Source:** CTO Guidance

---

## Executive Summary

There are **TWO separate two-phase patterns** at play:

1. **User Approval Pattern:** Upload → User Approval → Persistence
2. **Persistence Pattern:** Metadata to Supabase → File to GCS

---

## Pattern 1: User Approval (Upload → Save)

### Phase 1: Upload File (Temporary, Not Persisted)

**Action:** Upload file to temporary storage
**Result:** File is uploaded but NOT persisted
**Returns:** `file_id`, `boundary_contract_id` (pending materialization)

**UI State:** File is "uploaded" but not "saved"
**User Action Required:** User must explicitly click "Save" to persist

### Phase 2: User Clicks "Save" (Explicit Opt-In)

**Action:** User explicitly approves persistence
**Triggers:** Persistence flow (Pattern 2)

**UI Requirement:** 
- Show "Save" button after upload
- Make it clear file is not persisted until user clicks "Save"
- May require UI updates to enable this pattern

---

## Pattern 2: Persistence (Metadata → File)

### Phase 1: Metadata to Supabase

**Action:** Register file metadata in Supabase `project_files` table
**Intent:** `save_materialization` (or part of `ingest_file` if called on "Save")
**Result:** File metadata stored, boundary contract activated

### Phase 2: File to GCS

**Action:** Upload file to GCS (if not already there)
**Result:** File persisted in GCS
**Status:** File is now "saved" and available for parsing

---

## Corrected Flow

### Step 1: User Uploads File

```typescript
// Upload file to temporary storage (NOT persisted)
// This should be a simple file upload endpoint that:
// - Accepts file
// - Stores temporarily
// - Returns file_id and boundary_contract_id
// - Does NOT persist to GCS or Supabase

const formData = new FormData();
formData.append("file", file);

const uploadResponse = await fetch("/api/content/upload-temporary", {
  method: "POST",
  body: formData
});

const { file_id, boundary_contract_id } = await uploadResponse.json();

// UI shows: "File uploaded. Click Save to persist."
```

### Step 2: User Clicks "Save" (Explicit Opt-In)

```typescript
// User explicitly approves persistence
// This triggers the full persistence flow

// Option A: Call ingest_file intent (uploads to GCS, creates boundary contract)
// Then call save_materialization (registers in Supabase)

// Option B: Call save_materialization which handles both (if file already in temp storage)
```

---

## Implementation Approach

### Option A: Separate Temporary Upload Endpoint

1. **Create `/api/content/upload-temporary` endpoint**
   - Accepts file
   - Stores in temporary storage (not GCS)
   - Creates boundary contract (pending)
   - Returns `file_id`, `boundary_contract_id`
   - Does NOT persist

2. **User clicks "Save"**
   - Call `ingest_file` intent with `file_id` (moves from temp to GCS)
   - Call `save_materialization` intent (registers in Supabase)

### Option B: Modify ingest_file to Support "Temporary" Mode

1. **Initial upload**
   - Call `ingest_file` with `persist: false` flag
   - File goes to temporary storage
   - Boundary contract created (pending)
   - Returns `file_id`, `boundary_contract_id`

2. **User clicks "Save"**
   - Call `save_materialization` intent
   - This moves file from temp to GCS
   - Registers metadata in Supabase

---

## Recommended Approach

**Option A is cleaner** - separates concerns:
- Temporary upload endpoint = just upload
- `ingest_file` intent = persist to GCS
- `save_materialization` intent = register in Supabase

But we need to check if temporary upload endpoint exists, or if we should create it.

---

## Questions to Resolve

1. **Does temporary file upload endpoint exist?**
   - If yes, use it
   - If no, create it or use Option B

2. **When should `ingest_file` be called?**
   - On initial upload (Option B)?
   - On "Save" click (Option A)?

3. **UI Changes Required:**
   - Add "Save" button after upload
   - Show file status ("Uploaded" vs "Saved")
   - Make persistence explicit

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** ⚠️ **NEEDS CLARIFICATION ON IMPLEMENTATION APPROACH**
