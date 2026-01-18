# `ingest_file` Intent Analysis - Root Cause Investigation

**Status:** Root Cause Analysis  
**Date:** January 2026  
**Issue:** Tests calling `ingest_file` for files that already exist

---

## What's Actually Happening

### Test Flow

1. **Test Data Seeder** (`test_data_utils.py`):
   ```python
   # Step 1: Upload file to GCS
   blob_path = await test_data_seeder.upload_test_file("permit_oil_gas.pdf", test_id="permit_test")
   # Returns: "test/permit_test/permit_oil_gas.pdf"
   
   # Step 2: Create Supabase record
   file_id = await test_data_seeder.seed_source_file(
       file_id="permit_001",
       gcs_blob_path=blob_path,
       tenant_id="permit_test_tenant",
       session_id="permit_test_session",
       file_name="permit_oil_gas.pdf",
       file_type="application/pdf"
   )
   # Returns: "permit_001" (now in Supabase `source_files` table)
   ```

2. **Test then calls `ingest_file`**:
   ```python
   intent = IntentFactory.create_intent(
       intent_type="ingest_file",
       parameters={
           "file_path": blob_path,      # Already in GCS
           "file_id": file_id,          # Already in Supabase
           "ui_name": "permit_oil_gas.pdf",
           "file_type": "application/pdf"
       }
   )
   ```

3. **What `ingest_file` does** (Mode 2 - existing file):
   ```python
   # Mode 2: Register existing file
   elif file_id:
       # File already exists in storage, just register it
       actual_file_path = file_path
       
       # Register file reference in State Surface (for governed file access)
       file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
       
       await context.state_surface.store_file_reference(
           session_id=context.session_id,
           tenant_id=context.tenant_id,
           file_reference=file_reference,
           storage_location=actual_file_path,
           filename=filename,
           metadata={...}
       )
   ```

### The Problem

**`ingest_file` is doing THREE separate concerns:**

1. ✅ **Upload to GCS** (via `FileStorageAbstraction`) - Infrastructure layer
2. ✅ **Create Supabase record** (in `files` or `source_files` table) - Metadata tracking
3. ✅ **Register in State Surface** (via `store_file_reference`) - Governed access layer

**When a file already exists:**
- File is already in GCS ✅
- File is already in Supabase ✅
- File needs to be registered in State Surface ❌ (this is what the test is trying to do)

**The test is calling `ingest_file` just to do step 3 (State Surface registration), but `ingest_file` is meant for step 1 (new uploads).**

---

## What's Missing

### Current Content Realm Intents

```python
def declare_intents(self) -> List[str]:
    return [
        "ingest_file",              # Upload NEW file
        "parse_content",            # Parse existing file
        "extract_embeddings",       # Create embeddings
        "get_parsed_file",          # Get parsed results
        "get_semantic_interpretation"  # Get semantic interpretation
    ]
```

### Missing Intents

1. **`register_file`** - Register existing file in State Surface (for governed access)
   - Use case: File exists in GCS/Supabase, needs to be registered for session access
   - Parameters: `file_id`, `ui_name`, `file_type`
   - Action: Call `state_surface.store_file_reference()`

2. **`retrieve_file`** - Get file metadata and/or contents
   - Use case: Get file info for display, download, or processing
   - Parameters: `file_id` or `file_reference`
   - Returns: File metadata, contents (optional), storage location

3. **`list_files`** - List files for a tenant/session
   - Use case: Display files in UI, show file browser
   - Parameters: `tenant_id`, `session_id` (optional), filters
   - Returns: List of file metadata with `ui_name`, `file_type`, `created_at`, etc.

4. **`get_file_metadata`** - Get file metadata only (no contents)
   - Use case: Display file info without downloading
   - Parameters: `file_id`
   - Returns: File metadata (size, type, ui_name, etc.)

---

## Architecture Analysis

### File Lifecycle

```
1. User uploads file
   → ingest_file (NEW file)
   → Uploads to GCS
   → Creates Supabase record
   → Registers in State Surface
   → Returns file_id

2. File already exists (from EDI/API/previous upload)
   → register_file (EXISTING file)
   → Registers in State Surface only
   → Returns file_reference

3. User wants to see files
   → list_files
   → Queries Supabase for tenant files
   → Returns list with ui_name, file_type, etc.

4. User wants file details
   → retrieve_file or get_file_metadata
   → Gets from Supabase + State Surface
   → Returns metadata/contents

5. Process file
   → parse_content (uses file_id)
   → extract_embeddings (uses parsed_result_id)
   → etc.
```

### State Surface Purpose

According to the architecture:
- **State Surface** = Governed file access (Runtime-owned)
- Files must be registered in State Surface for execution context access
- State Surface stores file references, NOT file data
- File data is in GCS, metadata is in Supabase

**So the test is correct** - it needs to register the file in State Surface, but it's using the wrong intent.

---

## Solution Options

### Option 1: Add `register_file` Intent (Recommended)

**Pros:**
- Clear separation of concerns
- `ingest_file` only for new uploads
- `register_file` for existing files
- Follows single responsibility principle

**Implementation:**
```python
async def _handle_register_file(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Handle register_file intent - register existing file in State Surface.
    
    Use case: File already exists in GCS/Supabase, needs to be registered
    for governed access in this execution context.
    
    Intent parameters:
    - file_id: str (REQUIRED) - File identifier (must exist in Supabase)
    - ui_name: str (REQUIRED) - User-friendly filename for display
    - file_type: str (optional) - File type
    - mime_type: str (optional) - MIME type
    """
    file_id = intent.parameters.get("file_id")
    if not file_id:
        raise ValueError("file_id is required for register_file intent")
    
    ui_name = intent.parameters.get("ui_name")
    if not ui_name:
        raise ValueError("ui_name is required for register_file intent")
    
    # Get file metadata from Supabase
    file_metadata = await self._get_file_metadata(file_id, context.tenant_id)
    if not file_metadata:
        raise ValueError(f"File not found: {file_id}")
    
    # Get storage location from metadata
    storage_location = file_metadata.get("gcs_blob_path") or file_metadata.get("storage_path")
    if not storage_location:
        raise ValueError(f"Storage location not found for file: {file_id}")
    
    # Register in State Surface
    file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
    
    await context.state_surface.store_file_reference(
        session_id=context.session_id,
        tenant_id=context.tenant_id,
        file_reference=file_reference,
        storage_location=storage_location,
        filename=file_metadata.get("file_name", ui_name),
        metadata={
            "ui_name": ui_name,
            "file_type": intent.parameters.get("file_type", file_metadata.get("file_type")),
            "content_type": intent.parameters.get("mime_type", file_metadata.get("file_type")),
            "size": file_metadata.get("size"),
            "file_hash": file_metadata.get("file_hash"),
            "file_id": file_id
        }
    )
    
    return {
        "artifacts": {
            "file_id": file_id,
            "file_reference": file_reference,
            "storage_location": storage_location,
            "ui_name": ui_name
        },
        "events": [
            {
                "type": "file_registered",
                "file_id": file_id,
                "file_reference": file_reference
            }
        ]
    }
```

### Option 2: Keep `ingest_file` Dual-Mode (Not Recommended)

**Pros:**
- No new intent needed
- Tests work as-is

**Cons:**
- Violates single responsibility
- Creates circular logic
- Confusing API (same intent for new vs existing)

### Option 3: Auto-Register on Supabase Query (Alternative)

**Pros:**
- Files automatically available when queried
- No explicit registration needed

**Cons:**
- Loses explicit control
- May register files that shouldn't be accessible
- Doesn't follow governed access pattern

---

## Recommended Solution

**Add `register_file` intent to Content Realm:**

1. **Add to `declare_intents()`:**
   ```python
   return [
       "ingest_file",              # Upload NEW file
       "register_file",            # Register EXISTING file in State Surface
       "retrieve_file",            # Get file metadata/contents
       "list_files",               # List files for tenant/session
       "parse_content",
       "extract_embeddings",
       "get_parsed_file",
       "get_semantic_interpretation"
   ]
   ```

2. **Update tests to use `register_file`:**
   ```python
   # Instead of:
   intent = IntentFactory.create_intent(
       intent_type="ingest_file",
       parameters={"file_id": file_id, "file_path": blob_path, ...}
   )
   
   # Use:
   intent = IntentFactory.create_intent(
       intent_type="register_file",
       parameters={"file_id": file_id, "ui_name": "permit_oil_gas.pdf"}
   )
   ```

3. **Revert `ingest_file` to only handle new uploads:**
   - Remove Mode 2 (existing file registration)
   - Only accept `file_content` (hex-encoded)
   - Upload to GCS, create Supabase record, register in State Surface

---

## Additional Intents to Consider

### `retrieve_file` Intent

```python
async def _handle_retrieve_file(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Handle retrieve_file intent - get file metadata and/or contents.
    
    Intent parameters:
    - file_id: str (REQUIRED) - File identifier
    - include_contents: bool (optional) - Whether to return file contents
    """
    file_id = intent.parameters.get("file_id")
    if not file_id:
        raise ValueError("file_id is required for retrieve_file intent")
    
    include_contents = intent.parameters.get("include_contents", False)
    
    # Get file metadata from Supabase
    file_metadata = await self._get_file_metadata(file_id, context.tenant_id)
    
    # Get file reference from State Surface (if registered)
    file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
    file_ref_metadata = await context.state_surface.get_file_metadata(file_reference)
    
    artifacts = {
        "file_id": file_id,
        "file_metadata": file_metadata,
        "file_reference": file_reference if file_ref_metadata else None
    }
    
    if include_contents:
        # Get file contents from GCS
        storage_location = file_metadata.get("gcs_blob_path")
        if storage_location:
            file_contents = await context.state_surface.get_file(file_reference)
            artifacts["file_contents"] = file_contents
    
    return {
        "artifacts": artifacts,
        "events": []
    }
```

### `list_files` Intent

```python
async def _handle_list_files(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Handle list_files intent - list files for tenant/session.
    
    Intent parameters:
    - tenant_id: str (optional, defaults to context.tenant_id)
    - session_id: str (optional, defaults to context.session_id)
    - file_type: str (optional) - Filter by file type
    - limit: int (optional) - Limit results
    - offset: int (optional) - Pagination offset
    """
    tenant_id = intent.parameters.get("tenant_id", context.tenant_id)
    session_id = intent.parameters.get("session_id", context.session_id)
    file_type = intent.parameters.get("file_type")
    limit = intent.parameters.get("limit", 100)
    offset = intent.parameters.get("offset", 0)
    
    # Query Supabase for files
    files = await self._list_files_from_supabase(
        tenant_id=tenant_id,
        session_id=session_id,
        file_type=file_type,
        limit=limit,
        offset=offset
    )
    
    return {
        "artifacts": {
            "files": files,
            "count": len(files),
            "tenant_id": tenant_id,
            "session_id": session_id
        },
        "events": []
    }
```

---

## Implementation Plan

### Phase 1: Add `register_file` Intent (Priority: High)

1. Add `register_file` to `declare_intents()`
2. Implement `_handle_register_file()` in Content Orchestrator
3. Update tests to use `register_file` instead of `ingest_file` for existing files
4. Revert `ingest_file` to only handle new uploads

### Phase 2: Add `retrieve_file` Intent (Priority: Medium)

1. Add `retrieve_file` to `declare_intents()`
2. Implement `_handle_retrieve_file()` in Content Orchestrator
3. Add helper method `_get_file_metadata()` to query Supabase

### Phase 3: Add `list_files` Intent (Priority: Medium)

1. Add `list_files` to `declare_intents()`
2. Implement `_handle_list_files()` in Content Orchestrator
3. Add helper method `_list_files_from_supabase()` to query Supabase

---

## Success Criteria

✅ **Clear separation of concerns:**
- `ingest_file` only for new uploads
- `register_file` for existing files
- `retrieve_file` for getting file info
- `list_files` for displaying files

✅ **Tests use correct intents:**
- New file uploads → `ingest_file`
- Existing files → `register_file`
- File info → `retrieve_file`
- File listing → `list_files`

✅ **No circular logic:**
- Files aren't "ingested" if they already exist
- Clear intent for each operation

---

## References

- [Platform Rules](../PLATFORM_RULES.md)
- [Content Realm Architecture](../../symphainy_platform/realms/content/content_realm.py)
- [State Surface Architecture](../../symphainy_platform/runtime/state_surface.py)
