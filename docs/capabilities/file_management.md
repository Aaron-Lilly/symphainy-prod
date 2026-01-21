# File Management Capability

**Realm:** Content  
**Status:** ✅ Complete  
**Last Updated:** January 2026

---

## Overview

File Management provides core operations for working with files in the platform: registering existing files, retrieving file metadata and contents, listing files, and getting files by ID.

**Business Value:** Enables users to manage their files, retrieve information about files, and discover files in the system.

---

## Available Intents

### 1. Save Materialization (Two-Phase Flow - Phase 2)

**Intent:** `save_materialization`

**Purpose:** Explicitly save (materialize) a file that was uploaded. This is the second phase of the two-phase materialization flow. Files must be saved before they are available for parsing and other activities.

**Use Case:** After uploading a file (Phase 1), user must explicitly save it to authorize materialization and make it available for parsing.

**Parameters:**
```python
{
    "boundary_contract_id": "<contract_uuid>",  # Required - from upload response
    "file_id": "<file_uuid>"  # Required - from upload response
}
```

**Response:**
```python
{
    "success": True,
    "file_id": "<file_uuid>",
    "boundary_contract_id": "<contract_uuid>",
    "execution_id": "<execution_id>",
    "artifacts": {
        "materialization": {
            "result_type": "materialization",
            "semantic_payload": {
                "boundary_contract_id": "<contract_uuid>",
                "file_id": "<file_uuid>",
                "materialization_type": "full_artifact",
                "materialization_scope": {
                    "user_id": "<user_id>",
                    "session_id": "<session_id>",
                    "solution_id": "<solution_id>",
                    "scope_type": "workspace"
                },
                "status": "saved",
                "available_for_parsing": True
            }
        }
    },
    "message": "File saved and available for parsing"
}
```

**Example:**
```python
# After upload (Phase 1), get boundary_contract_id and file_id
# Then call save_materialization (Phase 2)
intent = IntentFactory.create_intent(
    intent_type="save_materialization",
    tenant_id="tenant_123",
    session_id="session_456",
    solution_id="solution_789",
    parameters={
        "boundary_contract_id": "contract-abc-123",
        "file_id": "file-xyz-789"
    }
)
result = await execution_manager.execute(intent)
```

**Note:** For MVP purposes, files must be explicitly saved after upload to enable parsing and other activities. This is part of the workspace-scoped materialization pattern.

---

### 2. Register File

**Intent:** `register_file`

**Purpose:** Register an existing file that's already in storage (e.g., uploaded via direct GCS access or EDI)

**Use Case:** When a file exists in storage but isn't registered in the platform's metadata system

**Parameters:**
```python
{
    "file_id": "<file_uuid>",  # Required
    "ui_name": "<user_friendly_filename>",  # Required
    "storage_location": "<gcs_path>",  # Optional (will try to get from Supabase)
    "file_type": "<file_type>",  # Optional
    "mime_type": "<mime_type>"  # Optional
}
```

**Response:**
```python
{
    "artifacts": {
        "file_id": "<file_uuid>",
        "file_reference": "file:<tenant_id>:<session_id>:<file_id>",
        "status": "registered"
    },
    "events": [
        {
            "type": "file_registered",
            "file_id": "<file_uuid>",
            "ui_name": "<ui_name>"
        }
    ]
}
```

**Example:**
```python
intent = IntentFactory.create_intent(
    intent_type="register_file",
    tenant_id="tenant_123",
    session_id="session_456",
    solution_id="solution_789",
    parameters={
        "file_id": "abc-123-def-456",
        "ui_name": "insurance_policy_001.pdf",
        "file_type": "unstructured",
        "mime_type": "application/pdf"
    }
)
result = await execution_manager.execute(intent)
```

---

### 2. Retrieve File Metadata

**Intent:** `retrieve_file_metadata`

**Purpose:** Get metadata about a file without downloading the file contents

**Use Case:** Display file information in UI, check file status, validate file exists

**Parameters:**
```python
{
    "file_id": "<file_uuid>"  # Required
}
```

**Response:**
```python
{
    "artifacts": {
        "file_id": "<file_uuid>",
        "file_metadata": {
            "ui_name": "<filename>",
            "file_type": "<type>",
            "mime_type": "<mime>",
            "file_size": <size>,
            "file_hash": "<hash>",
            "status": "<status>",
            "created_at": "<timestamp>",
            # ... other metadata fields
        },
        "file_reference": "file:<tenant_id>:<session_id>:<file_id>"
    },
    "events": []
}
```

**Example:**
```python
intent = IntentFactory.create_intent(
    intent_type="retrieve_file_metadata",
    tenant_id="tenant_123",
    session_id="session_456",
    solution_id="solution_789",
    parameters={
        "file_id": "abc-123-def-456"
    }
)
result = await execution_manager.execute(intent)
metadata = result.artifacts["file_metadata"]
```

---

### 3. Retrieve File

**Intent:** `retrieve_file`

**Purpose:** Get file contents (optionally) along with metadata

**Use Case:** Download file, display file contents, process file data

**Parameters:**
```python
{
    "file_id": "<file_uuid>",  # Required
    "include_contents": True  # Optional, default: False
}
```

**Response:**
```python
{
    "artifacts": {
        "file_id": "<file_uuid>",
        "file_reference": "file:<tenant_id>:<session_id>:<file_id>",
        "file_metadata": {
            # File metadata
        },
        "file_contents": <bytes>,  # If include_contents=True
        "file_size": <size>  # If include_contents=True
    },
    "events": []
}
```

**Example:**
```python
intent = IntentFactory.create_intent(
    intent_type="retrieve_file",
    tenant_id="tenant_123",
    session_id="session_456",
    solution_id="solution_789",
    parameters={
        "file_id": "abc-123-def-456",
        "include_contents": True
    }
)
result = await execution_manager.execute(intent)
file_contents = result.artifacts["file_contents"]
```

---

### 5. List Files

**Intent:** `list_files`

**Purpose:** List files for a tenant/session with optional filtering. **Only returns saved files (workspace-scoped filtering).**

**Use Case:** Display file list in UI, find files by type, paginate through files. Only shows files that have been saved (materialized).

**Security:** Files are filtered by workspace scope (user_id, session_id, solution_id). Users can only see files they've materialized.

**Parameters:**
```python
{
    "tenant_id": "<tenant_id>",  # Optional, defaults to context.tenant_id
    "session_id": "<session_id>",  # Optional, defaults to context.session_id
    "file_type": "<file_type>",  # Optional filter
    "limit": 100,  # Optional, default: 100
    "offset": 0  # Optional, default: 0
}
```

**Response:**
```python
{
    "artifacts": {
        "files": [
            {
                "file_id": "<file_uuid>",
                "ui_name": "<filename>",
                "file_type": "<type>",
                "mime_type": "<mime>",
                "file_size": <size>,
                "status": "<status>",
                # ... other metadata
            }
        ],
        "count": <count>,
        "tenant_id": "<tenant_id>",
        "session_id": "<session_id>"
    },
    "events": []
}
```

**Example:**
```python
intent = IntentFactory.create_intent(
    intent_type="list_files",
    tenant_id="tenant_123",
    session_id="session_456",
    solution_id="solution_789",
    parameters={
        "file_type": "unstructured",
        "limit": 50,
        "offset": 0
    }
)
result = await execution_manager.execute(intent)
files = result.artifacts["files"]
```

---

### 6. Get File By ID

**Intent:** `get_file_by_id`

**Purpose:** Get file information by ID, checking both Supabase and State Surface

**Use Case:** Verify file exists, get file information for display

**Parameters:**
```python
{
    "file_id": "<file_uuid>"  # Required
}
```

**Response:**
```python
{
    "artifacts": {
        "file_id": "<file_uuid>",
        "file_metadata": {
            # Supabase file record or State Surface metadata
        },
        "file_reference": "file:<tenant_id>:<session_id>:<file_id>",
        "registered_in_state_surface": True/False
    },
    "events": []
}
```

**Example:**
```python
intent = IntentFactory.create_intent(
    intent_type="get_file_by_id",
    tenant_id="tenant_123",
    session_id="session_456",
    solution_id="solution_789",
    parameters={
        "file_id": "abc-123-def-456"
    }
)
result = await execution_manager.execute(intent)
file_info = result.artifacts
```

---

## Business Use Cases

### Use Case 1: Two-Phase File Upload and Save
**Scenario:** User uploads a file and saves it for parsing

**Flow:**
1. Upload file via `ingest_file` intent (Phase 1)
   - Creates pending boundary contract
   - Returns `boundary_contract_id` and `file_id`
   - File status: `materialization_pending: true`
2. User explicitly saves file via `save_materialization` intent (Phase 2)
   - Authorizes materialization
   - Updates contract status to `active`
   - Registers file in materialization index
   - File status: `available_for_parsing: true`
3. File now appears in `list_files` and is available for parsing

### Use Case 2: Display File List
**Scenario:** User wants to see all their saved files

**Flow:**
1. Call `list_files` with tenant_id (only returns saved files)
2. Display files in UI
3. User clicks on file → Call `retrieve_file_metadata` to show details

**Note:** Only saved files appear in the list (workspace-scoped filtering).

### Use Case 2: Verify File Exists
**Scenario:** Before processing a file, verify it exists

**Flow:**
1. Call `get_file_by_id` with file_id
2. Check if file exists
3. If exists, proceed with processing

### Use Case 4: Download File
**Scenario:** User wants to download a file

**Flow:**
1. Call `retrieve_file` with `include_contents=True`
2. Return file contents to user
3. User downloads file

---

## Error Handling

All intents return proper error responses:

```python
{
    "success": False,
    "error": "File not found: <file_id>",
    "artifacts": {},
    "events": []
}
```

**Common Errors:**
- `File not found` - File doesn't exist
- `Invalid file_id` - File ID format is invalid
- `Access denied` - User doesn't have access to file

---

## Two-Phase Materialization Flow

The file management capability implements a **two-phase materialization flow** for workspace-scoped security:

1. **Phase 1: Upload** (`ingest_file` intent)
   - Creates pending boundary contract
   - File is uploaded but not yet materialized
   - Status: `materialization_pending: true`

2. **Phase 2: Save** (`save_materialization` intent)
   - User explicitly saves the file
   - Materialization is authorized
   - File is registered in materialization index
   - Status: `available_for_parsing: true`

**Why Two-Phase?**
- Explicit user control over materialization
- Workspace-scoped security (user_id, session_id, solution_id)
- Files only available for parsing after explicit save
- Aligns with Data Boundary Contract architecture

## Related Capabilities

- [Data Ingestion](data_ingestion.md) - Upload files (Phase 1)
- [File Lifecycle](file_lifecycle.md) - Archive, restore, purge files
- [File Parsing](file_parsing.md) - Parse file contents (requires saved files)

---

## API Reference

For complete API contracts, see [API Contracts](../execution/api_contracts_frontend_integration.md).

---

**Status:** ✅ Complete and Operational
