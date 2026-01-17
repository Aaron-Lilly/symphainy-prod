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

### 1. Register File

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

### 4. List Files

**Intent:** `list_files`

**Purpose:** List files for a tenant/session with optional filtering

**Use Case:** Display file list in UI, find files by type, paginate through files

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

### 5. Get File By ID

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

### Use Case 1: Display File List
**Scenario:** User wants to see all their uploaded files

**Flow:**
1. Call `list_files` with tenant_id
2. Display files in UI
3. User clicks on file → Call `retrieve_file_metadata` to show details

### Use Case 2: Verify File Exists
**Scenario:** Before processing a file, verify it exists

**Flow:**
1. Call `get_file_by_id` with file_id
2. Check if file exists
3. If exists, proceed with processing

### Use Case 3: Download File
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

## Related Capabilities

- [Data Ingestion](data_ingestion.md) - Upload files
- [File Lifecycle](file_lifecycle.md) - Archive, restore, purge files
- [File Parsing](file_parsing.md) - Parse file contents

---

## API Reference

For complete API contracts, see [API Contracts](../execution/api_contracts_frontend_integration.md).

---

**Status:** ✅ Complete and Operational
