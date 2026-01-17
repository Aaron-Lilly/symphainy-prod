# File Lifecycle Capability

**Realm:** Content  
**Status:** ✅ Complete  
**Last Updated:** January 2026

---

## Overview

File Lifecycle Management provides operations for managing files throughout their lifecycle: archiving (soft delete), restoration, permanent deletion (purge), validation, preprocessing, search, and metadata updates.

**Business Value:** Enables organizations to manage file lifecycle according to retention policies, compliance requirements, and business needs.

---

## Available Intents

### 1. Archive File

**Intent:** `archive_file`

**Purpose:** Archive a file (soft delete) - preserves file but marks as archived

**Use Case:** Remove file from active use but keep for compliance/audit

**Parameters:**
```python
{
    "file_id": "<file_uuid>",  # Required
    "file_reference": "<file_reference>",  # Optional
    "reason": "<archive_reason>"  # Optional
}
```

**Response:**
```python
{
    "artifacts": {
        "file_id": "<file_uuid>",
        "file_reference": "<file_reference>",
        "status": "archived",
        "archived_at": "<timestamp>",
        "archive_reason": "<reason>"
    },
    "events": [
        {
            "type": "file_archived",
            "file_id": "<file_uuid>",
            "reason": "<reason>"
        }
    ]
}
```

**Example:**
```python
intent = IntentFactory.create_intent(
    intent_type="archive_file",
    tenant_id="tenant_123",
    session_id="session_456",
    solution_id="solution_789",
    parameters={
        "file_id": "abc-123-def-456",
        "reason": "Compliance retention period expired"
    }
)
result = await execution_manager.execute(intent)
```

---

### 2. Restore File

**Intent:** `restore_file`

**Purpose:** Restore an archived file to active status

**Use Case:** Need to access archived file again

**Parameters:**
```python
{
    "file_id": "<file_uuid>",  # Required
    "file_reference": "<file_reference>"  # Optional
}
```

**Response:**
```python
{
    "artifacts": {
        "file_id": "<file_uuid>",
        "file_reference": "<file_reference>",
        "status": "active",
        "restored_at": "<timestamp>"
    },
    "events": [
        {
            "type": "file_restored",
            "file_id": "<file_uuid>"
        }
    ]
}
```

---

### 3. Purge File

**Intent:** `purge_file`

**Purpose:** Permanently delete a file (cannot be undone)

**Use Case:** Remove file completely (GDPR, data minimization)

**Parameters:**
```python
{
    "file_id": "<file_uuid>",  # Required
    "file_reference": "<file_reference>",  # Optional
    "confirm": True  # Required - must be True for permanent deletion
}
```

**Response:**
```python
{
    "artifacts": {
        "file_id": "<file_uuid>",
        "file_reference": "<file_reference>",
        "status": "purged",
        "purged_at": "<timestamp>"
    },
    "events": [
        {
            "type": "file_purged",
            "file_id": "<file_uuid>"
        }
    ]
}
```

**⚠️ Warning:** This operation is permanent and cannot be undone.

---

### 4. Validate File

**Intent:** `validate_file`

**Purpose:** Validate file format, size, and metadata

**Use Case:** Check file before processing, ensure compliance

**Parameters:**
```python
{
    "file_id": "<file_uuid>",  # Required
    "file_reference": "<file_reference>",  # Optional
    "validation_rules": {  # Optional
        "max_size": 10485760,  # 10MB
        "allowed_types": ["pdf", "xlsx", "csv"],
        "required_metadata": ["ui_name", "file_type"]
    }
}
```

**Response:**
```python
{
    "artifacts": {
        "file_id": "<file_uuid>",
        "file_reference": "<file_reference>",
        "validation_results": {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
    },
    "events": []
}
```

---

### 5. Preprocess File

**Intent:** `preprocess_file`

**Purpose:** Preprocess file (normalize, clean, extract metadata)

**Use Case:** Prepare file for processing, normalize format

**Parameters:**
```python
{
    "file_id": "<file_uuid>",  # Required
    "file_reference": "<file_reference>",  # Optional
    "preprocessing_options": {  # Optional
        "normalize": True,
        "clean": True,
        "extract_metadata": True
    }
}
```

**Response:**
```python
{
    "artifacts": {
        "file_id": "<file_uuid>",
        "file_reference": "<file_reference>",
        "preprocessing_results": {
            "preprocessed": True,
            "changes": [...]
        }
    },
    "events": []
}
```

---

### 6. Search Files

**Intent:** `search_files`

**Purpose:** Search files by name or content

**Use Case:** Find files by keyword, search file contents

**Parameters:**
```python
{
    "query": "<search_query>",  # Required
    "search_type": "name",  # Optional: "name", "content", or "both" (default: "name")
    "limit": 100,  # Optional, default: 100
    "offset": 0  # Optional, default: 0
}
```

**Response:**
```python
{
    "artifacts": {
        "query": "<search_query>",
        "search_type": "<search_type>",
        "files": [
            {
                "file_id": "<file_uuid>",
                "ui_name": "<filename>",
                # ... file metadata
            }
        ],
        "count": <count>
    },
    "events": []
}
```

---

### 7. Query Files

**Intent:** `query_files`

**Purpose:** Query files with filters (type, status, size, date)

**Use Case:** Find files by criteria, filter file lists

**Parameters:**
```python
{
    "filters": {  # Required
        "file_type": "unstructured",  # Optional
        "status": "active",  # Optional: "active", "archived"
        "min_size": 1000,  # Optional (bytes)
        "max_size": 10485760,  # Optional (bytes)
        "created_after": "2026-01-01T00:00:00Z",  # Optional (ISO timestamp)
        "created_before": "2026-12-31T23:59:59Z"  # Optional (ISO timestamp)
    },
    "limit": 100,  # Optional, default: 100
    "offset": 0  # Optional, default: 0
}
```

**Response:**
```python
{
    "artifacts": {
        "filters": {...},
        "files": [...],
        "count": <count>
    },
    "events": []
}
```

---

### 8. Update File Metadata

**Intent:** `update_file_metadata`

**Purpose:** Update file metadata fields

**Use Case:** Add tags, update description, modify metadata

**Parameters:**
```python
{
    "file_id": "<file_uuid>",  # Required
    "file_reference": "<file_reference>",  # Optional
    "metadata_updates": {  # Required
        "description": "Updated description",
        "tags": ["tag1", "tag2"],
        "custom_field": "value"
    }
}
```

**Response:**
```python
{
    "artifacts": {
        "file_id": "<file_uuid>",
        "file_reference": "<file_reference>",
        "updated_metadata": {
            # Updated metadata
        },
        "status": "updated"
    },
    "events": []
}
```

---

## File Lifecycle States

### State Transitions

```
active → archived (via archive_file)
archived → active (via restore_file)
active → purged (via purge_file, permanent)
archived → purged (via purge_file, permanent)
```

### State Descriptions

- **active** - File is active and available for use
- **archived** - File is archived (soft deleted), preserved for compliance
- **purged** - File is permanently deleted (cannot be restored)

---

## Business Use Cases

### Use Case 1: Compliance Retention
**Scenario:** Archive files after retention period expires

**Flow:**
1. Identify files past retention period
2. Call `archive_file` for each file
3. Files are preserved but not accessible
4. Can be restored if needed for audit

### Use Case 2: GDPR Data Minimization
**Scenario:** Permanently delete files per GDPR request

**Flow:**
1. User requests data deletion
2. Verify request is valid
3. Call `purge_file` with `confirm=True`
4. File is permanently deleted
5. Confirm deletion to user

### Use Case 3: File Search
**Scenario:** Find files by keyword

**Flow:**
1. User enters search query
2. Call `search_files` with query
3. Display matching files
4. User selects file to view

### Use Case 4: Metadata Management
**Scenario:** Add tags to files for organization

**Flow:**
1. User selects file
2. User adds tags
3. Call `update_file_metadata` with tags
4. Metadata is updated
5. File appears in tag-based searches

---

## Error Handling

All lifecycle operations return proper error responses:

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
- `File already archived` - File is already in archived state
- `Cannot purge archived file` - Must restore before purging (if applicable)

---

## Related Capabilities

- [File Management](file_management.md) - Core file operations
- [Data Ingestion](data_ingestion.md) - Upload files
- [Bulk Operations](bulk_operations.md) - Bulk lifecycle operations

---

## API Reference

For complete API contracts, see [API Contracts](../execution/api_contracts_frontend_integration.md).

---

**Status:** ✅ Complete and Operational
