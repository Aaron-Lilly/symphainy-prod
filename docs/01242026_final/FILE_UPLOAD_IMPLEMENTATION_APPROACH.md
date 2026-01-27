# File Upload Implementation Approach - CTO Guidance

**Date:** January 25, 2026  
**Status:** ✅ **APPROACH DEFINED**  
**Based On:** CTO Clarification

---

## Two Separate Two-Phase Patterns

### Pattern 1: User Approval (Upload → Save)
1. **Upload File** → Temporary storage, NOT persisted
2. **User Clicks "Save"** → Explicit opt-in to persistence

### Pattern 2: Persistence (Metadata → File)
1. **Metadata to Supabase** → Register in `project_files`
2. **File to GCS** → Persist file content

---

## Implementation Approach

### Current Architecture

- `ingest_file` intent → Uploads file to GCS, creates boundary contract (pending materialization)
- `save_materialization` intent → Authorizes materialization, registers in Supabase

### Proposed Flow

**Step 1: Initial Upload (Temporary, Not Persisted)**

```typescript
// Upload file - store file content temporarily (in memory or temp storage)
// Do NOT call ingest_file yet
// Just get file ready for user approval

const formData = new FormData();
formData.append("file", file);

// Simple upload endpoint that:
// - Accepts file
// - Stores file content temporarily (for later use)
// - Creates boundary contract (pending)
// - Returns file_id, boundary_contract_id, and file content reference

const uploadResponse = await fetch("/api/content/upload-temporary", {
  method: "POST",
  body: formData
});

const { 
  file_id, 
  boundary_contract_id,
  file_content_ref  // Reference to temporarily stored file
} = await uploadResponse.json();

// UI State: File is "uploaded" but not "saved"
// Show "Save" button
```

**Step 2: User Clicks "Save" (Explicit Opt-In)**

```typescript
// User explicitly approves persistence
// Now we persist: file to GCS + metadata to Supabase

// Option A: Call ingest_file with file_content from temp storage
// Then call save_materialization

// Option B: If ingest_file can accept file_id from temp storage,
// call it with file_id, then save_materialization
```

---

## Implementation Options

### Option A: Create Temporary Upload Endpoint (Recommended)

**Pros:**
- Clean separation of concerns
- Temporary storage is explicit
- Easy to understand flow

**Cons:**
- Requires new endpoint
- Need to manage temporary storage

**Implementation:**
1. Create `/api/content/upload-temporary` endpoint
2. Stores file in temporary storage (Redis or memory)
3. Creates boundary contract (pending)
4. Returns `file_id`, `boundary_contract_id`, `file_content_ref`
5. On "Save": Retrieve file from temp, call `ingest_file`, then `save_materialization`

### Option B: Use Existing Upload with "Pending" State

**Pros:**
- Uses existing infrastructure
- No new endpoint needed

**Cons:**
- File goes to GCS immediately (not truly "temporary")
- Need to handle "pending" state

**Implementation:**
1. Call existing upload endpoint (file goes to GCS, but materialization is "pending")
2. UI shows "Save" button
3. On "Save": Call `save_materialization` intent (activates materialization, registers in Supabase)

---

## Recommended: Option B (Simpler for MVP)

Since `ingest_file` already creates boundary contracts with "pending" materialization, we can:

1. **Initial Upload:**
   - Call `ingest_file` intent (file goes to GCS, boundary contract is "pending")
   - File is uploaded but materialization is NOT authorized yet
   - UI shows: "File uploaded. Click Save to make it available for parsing."

2. **User Clicks "Save":**
   - Call `save_materialization` intent
   - This authorizes materialization and registers in Supabase
   - File becomes "saved" and available for parsing

**This matches the existing architecture:**
- `ingest_file` → File to GCS, boundary contract (pending)
- `save_materialization` → Metadata to Supabase, materialization authorized

---

## UI Changes Required

1. **After Upload:**
   - Show file in "Uploaded" state (not "Saved")
   - Display "Save" button prominently
   - Make it clear file is not persisted until user clicks "Save"

2. **After Save:**
   - Show file in "Saved" state
   - File is now available for parsing
   - "Save" button becomes disabled or changes to "Saved ✓"

---

## Updated Migration Pattern

### ContentPillarUpload.tsx

```typescript
// Step 1: Upload file (temporary - materialization pending)
const handleUpload = async () => {
  // Convert file to hex for ingest_file intent
  const fileBuffer = await file.arrayBuffer();
  const fileContentHex = Buffer.from(fileBuffer).toString('hex');
  
  // Submit ingest_file intent (file goes to GCS, but materialization is pending)
  const response = await submitIntent({
    intent_type: 'ingest_file',
    tenant_id: sessionState.tenantId,
    session_id: sessionState.sessionId,
    parameters: {
      ingestion_type: 'upload',
      file_content: fileContentHex,
      ui_name: file.name,
      file_type: fileType,
      mime_type: file.type
    }
  });
  
  // Extract file_id and boundary_contract_id from execution result
  const executionStatus = await getExecutionStatus(response.execution_id);
  const file_id = executionStatus.artifacts?.file?.semantic_payload?.file_id;
  const boundary_contract_id = executionStatus.artifacts?.file?.semantic_payload?.boundary_contract_id;
  
  // UI State: File is "uploaded" but not "saved"
  setUploadState({
    ...uploadState,
    uploading: false,
    success: true,
    file_id,
    boundary_contract_id,
    materialization_pending: true  // ✅ Key: Materialization is pending
  });
  
  // Show "Save" button
};

// Step 2: User clicks "Save" (explicit opt-in)
const handleSave = async () => {
  if (!uploadState.file_id || !uploadState.boundary_contract_id) {
    setError("File must be uploaded before saving");
    return;
  }
  
  setSaving(true);
  
  try {
    // Submit save_materialization intent (authorizes materialization, registers in Supabase)
    const response = await submitIntent({
      intent_type: 'save_materialization',
      tenant_id: sessionState.tenantId,
      session_id: sessionState.sessionId,
      parameters: {
        boundary_contract_id: uploadState.boundary_contract_id,
        file_id: uploadState.file_id
      }
    });
    
    // File is now "saved" and available for parsing
    setUploadState({
      ...uploadState,
      saving: false,
      materialization_pending: false,  // ✅ Materialization authorized
      saved: true
    });
    
    toast.success("File saved successfully!", {
      description: "File is now available for parsing"
    });
  } catch (error) {
    setError(error.message);
    setSaving(false);
  }
};
```

---

## Key Changes

1. **Upload Flow:**
   - Call `ingest_file` intent on upload (file goes to GCS, materialization pending)
   - Store `file_id` and `boundary_contract_id` in component state
   - Show "Save" button (file is not "saved" yet)

2. **Save Flow:**
   - User clicks "Save" button
   - Call `save_materialization` intent
   - File becomes "saved" and available for parsing

3. **UI Updates:**
   - Show file status: "Uploaded" vs "Saved"
   - "Save" button only appears after upload
   - Make persistence explicit and opt-in

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** ✅ **READY FOR IMPLEMENTATION**
