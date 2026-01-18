# API Contracts for Frontend Integration - Phases 1-4

**Date:** January 2026  
**Status:** 📋 **API CONTRACTS**  
**Purpose:** Document API contracts for frontend team integration testing

---

## 🎯 Executive Summary

This document provides API contracts for all Phase 1-4 features to enable frontend integration testing. All operations are available via Runtime intents and follow the standard intent pattern.

---

## 📋 Intent-Based API Pattern

All operations use the **Intent** pattern via the Runtime Execution Manager:

```python
intent = IntentFactory.create_intent(
    intent_type="<intent_name>",
    tenant_id="<tenant_id>",
    session_id="<session_id>",
    solution_id="<solution_id>",
    parameters={
        # Intent-specific parameters
    }
)

result = await execution_manager.execute(intent)
```

**Response Format:**
```python
{
    "artifacts": {
        # Operation-specific results
    },
    "events": [
        {
            "type": "<event_type>",
            # Event-specific data
        }
    ]
}
```

---

## 🔌 Phase 1: Unified Ingestion & File Management

### 1.1 Ingest File (Upload)

**Intent:** `ingest_file`

**Parameters:**
```python
{
    "ingestion_type": "upload",  # Required: "upload", "edi", or "api"
    "file_content": "<hex_encoded_file_content>",  # Required for upload
    "ui_name": "<user_friendly_filename>",  # Required
    "file_type": "<file_type>",  # Optional, default: "unstructured"
    "mime_type": "<mime_type>",  # Optional, default: "application/octet-stream"
    "filename": "<filename>",  # Optional, defaults to ui_name
    "user_id": "<user_id>",  # Optional
    "source_metadata": {},  # Optional
    "ingestion_options": {}  # Optional
}
```

**Response:**
```python
{
    "artifacts": {
        "file_id": "<file_uuid>",
        "file_reference": "file:<tenant_id>:<session_id>:<file_id>",
        "file_path": "<gcs_path>",
        "ui_name": "<ui_name>",
        "file_type": "<file_type>",
        "ingestion_type": "upload",
        "status": "ingested"
    },
    "events": [
        {
            "type": "file_ingested",
            "file_id": "<file_uuid>",
            "file_reference": "<file_reference>",
            "ui_name": "<ui_name>",
            "ingestion_type": "upload"
        }
    ]
}
```

### 1.2 Ingest File (EDI)

**Intent:** `ingest_file`

**Parameters:**
```python
{
    "ingestion_type": "edi",  # Required
    "edi_data": "<hex_encoded_edi_data>",  # Required
    "partner_id": "<partner_id>",  # Required
    "ui_name": "<user_friendly_filename>",  # Required
    "edi_protocol": "<protocol>",  # Optional, default: "as2"
    "file_type": "<file_type>",  # Optional
    "mime_type": "<mime_type>",  # Optional
    "source_metadata": {},  # Optional
    "ingestion_options": {}  # Optional
}
```

**Response:** Same as upload, with `ingestion_type: "edi"`

### 1.3 Ingest File (API)

**Intent:** `ingest_file`

**Parameters:**
```python
{
    "ingestion_type": "api",  # Required
    "api_payload": "<api_payload>",  # Required (dict or JSON string)
    "ui_name": "<user_friendly_filename>",  # Required
    "endpoint": "<endpoint>",  # Optional
    "api_type": "<api_type>",  # Optional, default: "rest"
    "file_type": "<file_type>",  # Optional
    "mime_type": "<mime_type>",  # Optional
    "source_metadata": {},  # Optional
    "ingestion_options": {}  # Optional
}
```

**Response:** Same as upload, with `ingestion_type: "api"`

### 1.4 Register File

**Intent:** `register_file`

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
        "storage_location": "<gcs_path>",
        "ui_name": "<ui_name>"
    },
    "events": [
        {
            "type": "file_registered",
            "file_id": "<file_uuid>",
            "file_reference": "<file_reference>"
        }
    ]
}
```

### 1.5 Retrieve File Metadata

**Intent:** `retrieve_file_metadata`

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
            # Supabase file record
            "uuid": "<file_uuid>",
            "ui_name": "<ui_name>",
            "file_type": "<file_type>",
            "file_size": <size>,
            "file_hash": "<hash>",
            "created_at": "<iso_timestamp>",
            # ... other metadata fields
        },
        "file_reference": "file:<tenant_id>:<session_id>:<file_id>"
    },
    "events": []
}
```

### 1.6 Retrieve File

**Intent:** `retrieve_file`

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

### 1.7 List Files

**Intent:** `list_files`

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
                # File metadata objects
            }
        ],
        "count": <count>,
        "tenant_id": "<tenant_id>",
        "session_id": "<session_id>"
    },
    "events": []
}
```

### 1.8 Get File By ID

**Intent:** `get_file_by_id`

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
            # Supabase file record
        },
        "file_reference": "file:<tenant_id>:<session_id>:<file_id>",
        "registered_in_state_surface": True/False
    },
    "events": []
}
```

---

## 🔌 Phase 2: Bulk Operations

### 2.1 Bulk Ingest Files

**Intent:** `bulk_ingest_files`

**Parameters:**
```python
{
    "files": [  # Required: List of file objects
        {
            "ingestion_type": "upload",  # "upload", "edi", or "api"
            "file_content": "<hex>",  # For upload
            "edi_data": "<hex>",  # For EDI
            "api_payload": {},  # For API
            "ui_name": "<filename>",  # Required
            "file_type": "<type>",  # Optional
            "mime_type": "<mime>",  # Optional
            # ... other ingestion-specific fields
        }
    ],
    "batch_size": 10,  # Optional, default: 10
    "max_parallel": 5,  # Optional, default: 5
    "operation_id": "<operation_id>",  # Optional (for resume)
    "resume_from_batch": 0  # Optional (for resume)
}
```

**Response:**
```python
{
    "artifacts": {
        "total_files": <count>,
        "success_count": <count>,
        "error_count": <count>,
        "results": [
            {
                "success": True,
                "index": <index>,
                "file_id": "<file_uuid>",
                "file_reference": "<file_reference>",
                "ui_name": "<ui_name>",
                "ingestion_type": "<type>"
            }
        ],
        "errors": [
            {
                "success": False,
                "index": <index>,
                "error": "<error_message>"
            }
        ],
        "batch_size": <batch_size>,
        "max_parallel": <max_parallel>,
        "operation_id": "<operation_id>"
    },
    "events": [
        {
            "type": "bulk_ingestion_complete",
            "total_files": <count>,
            "success_count": <count>,
            "error_count": <count>,
            "operation_id": "<operation_id>"
        }
    ]
}
```

### 2.2 Bulk Parse Files

**Intent:** `bulk_parse_files`

**Parameters:**
```python
{
    "file_ids": ["<file_id1>", "<file_id2>", ...],  # Required
    "batch_size": 10,  # Optional, default: 10
    "max_parallel": 5,  # Optional, default: 5
    "parse_options": {}  # Optional
}
```

**Response:** Similar structure to bulk_ingest_files

### 2.3 Bulk Extract Embeddings

**Intent:** `bulk_extract_embeddings`

**Parameters:**
```python
{
    "parsed_result_ids": ["<parsed_id1>", "<parsed_id2>", ...],  # Required
    "batch_size": 10,  # Optional, default: 10
    "max_parallel": 5  # Optional, default: 5
}
```

**Response:** Similar structure to bulk_ingest_files

### 2.4 Bulk Interpret Data

**Intent:** `bulk_interpret_data`

**Parameters:**
```python
{
    "parsed_result_ids": ["<parsed_id1>", "<parsed_id2>", ...],  # Required
    "batch_size": 10,  # Optional, default: 10
    "max_parallel": 5,  # Optional, default: 5
    "interpretation_options": {}  # Optional
}
```

**Response:** Similar structure to bulk_ingest_files

---

## 🔌 Phase 3: Error Handling & Resilience

### 3.1 Idempotency

**Usage:** Add `idempotency_key` to Intent object:

```python
intent = IntentFactory.create_intent(...)
intent.idempotency_key = "unique_key_123"
```

**Behavior:**
- First execution: Processes normally, stores result
- Subsequent executions: Returns previous result immediately (no duplicate processing)

### 3.2 Get Operation Status

**Intent:** `get_operation_status`

**Parameters:**
```python
{
    "operation_id": "<operation_id>"  # Required
}
```

**Response:**
```python
{
    "artifacts": {
        "operation_id": "<operation_id>",
        "status": "running" | "completed" | "failed" | "not_found",
        "total": <total>,
        "processed": <processed>,
        "succeeded": <succeeded>,
        "failed": <failed>,
        "current_batch": <batch_num>,
        "last_successful_batch": <batch_num>,
        "progress_percentage": <percentage>,
        "updated_at": "<iso_timestamp>"
    },
    "events": []
}
```

---

## 🔌 Phase 4: File Lifecycle & Advanced Features

### 4.1 Archive File

**Intent:** `archive_file`

**Parameters:**
```python
{
    "file_id": "<file_uuid>",  # Required (or file_reference)
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
        "archived_at": "<iso_timestamp>"
    },
    "events": [
        {
            "type": "file_archived",
            "file_id": "<file_uuid>",
            "file_reference": "<file_reference>",
            "reason": "<reason>"
        }
    ]
}
```

### 4.2 Purge File

**Intent:** `purge_file`

**Parameters:**
```python
{
    "file_id": "<file_uuid>",  # Required (or file_reference)
    "file_reference": "<file_reference>",  # Optional
    "confirm": True  # Required (must be True for permanent deletion)
}
```

**Response:**
```python
{
    "artifacts": {
        "file_id": "<file_uuid>",
        "file_reference": "<file_reference>",
        "status": "purged",
        "purged_at": "<iso_timestamp>"
    },
    "events": [
        {
            "type": "file_purged",
            "file_id": "<file_uuid>",
            "file_reference": "<file_reference>"
        }
    ]
}
```

### 4.3 Restore File

**Intent:** `restore_file`

**Parameters:**
```python
{
    "file_id": "<file_uuid>",  # Required (or file_reference)
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
        "restored_at": "<iso_timestamp>"
    },
    "events": [
        {
            "type": "file_restored",
            "file_id": "<file_uuid>",
            "file_reference": "<file_reference>"
        }
    ]
}
```

### 4.4 Validate File

**Intent:** `validate_file`

**Parameters:**
```python
{
    "file_id": "<file_uuid>",  # Required (or file_reference)
    "file_reference": "<file_reference>",  # Optional
    "validation_rules": {
        "max_size": <bytes>,  # Optional
        "allowed_types": ["<type1>", "<type2>"],  # Optional
        "required_metadata": ["<field1>", "<field2>"]  # Optional
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
            "valid": True/False,
            "errors": ["<error1>", "<error2>"],
            "warnings": ["<warning1>", "<warning2>"]
        }
    },
    "events": []
}
```

### 4.5 Search Files

**Intent:** `search_files`

**Parameters:**
```python
{
    "query": "<search_query>",  # Required
    "search_type": "name" | "content" | "both",  # Optional, default: "name"
    "limit": 100,  # Optional, default: 100
    "offset": 0  # Optional, default: 0
}
```

**Response:**
```python
{
    "artifacts": {
        "query": "<query>",
        "search_type": "<type>",
        "files": [
            {
                # File metadata objects
            }
        ],
        "count": <count>
    },
    "events": []
}
```

### 4.6 Query Files

**Intent:** `query_files`

**Parameters:**
```python
{
    "filters": {  # Required
        "file_type": "<type>",  # Optional
        "status": "active" | "archived",  # Optional
        "min_size": <bytes>,  # Optional
        "max_size": <bytes>,  # Optional
        "created_after": "<iso_timestamp>",  # Optional
        "created_before": "<iso_timestamp>"  # Optional
    },
    "limit": 100,  # Optional, default: 100
    "offset": 0  # Optional, default: 0
}
```

**Response:**
```python
{
    "artifacts": {
        "filters": {
            # Applied filters
        },
        "files": [
            {
                # File metadata objects
            }
        ],
        "count": <count>
    },
    "events": []
}
```

### 4.7 Update File Metadata

**Intent:** `update_file_metadata`

**Parameters:**
```python
{
    "file_id": "<file_uuid>",  # Required (or file_reference)
    "file_reference": "<file_reference>",  # Optional
    "metadata_updates": {  # Required
        "description": "<description>",
        "tags": ["<tag1>", "<tag2>"],
        # ... any metadata fields to update
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
            # Complete updated metadata
        }
    },
    "events": [
        {
            "type": "file_metadata_updated",
            "file_id": "<file_uuid>",
            "file_reference": "<file_reference>",
            "updates": {
                # Fields that were updated
            }
        }
    ]
}
```

---

## 🔌 Error Handling

### Error Response Format

```python
{
    "error": {
        "type": "<error_type>",
        "message": "<error_message>",
        "code": "<error_code>",
        "details": {}
    }
}
```

### Common Error Codes

- `VALIDATION_ERROR`: Invalid parameters
- `NOT_FOUND`: Resource not found
- `PERMISSION_DENIED`: Insufficient permissions
- `STORAGE_ERROR`: Storage operation failed
- `PROCESSING_ERROR`: Processing operation failed

---

## 🔌 Frontend Integration Notes

### 1. File Upload Flow

```python
# Step 1: Upload file
intent = IntentFactory.create_intent(
    intent_type="ingest_file",
    parameters={
        "ingestion_type": "upload",
        "file_content": file_content_hex,
        "ui_name": filename
    }
)
result = await execution_manager.execute(intent)
file_id = result["artifacts"]["file_id"]

# Step 2: Track upload progress (for large files, use bulk_ingest_files with progress tracking)
# Step 3: Retrieve file metadata if needed
# Step 4: Display file in UI
```

### 2. Bulk Upload Flow

```python
# Step 1: Prepare files list
files = [{"ingestion_type": "upload", "file_content": hex, "ui_name": name}, ...]

# Step 2: Execute bulk ingestion
intent = IntentFactory.create_intent(
    intent_type="bulk_ingest_files",
    parameters={"files": files, "batch_size": 10, "max_parallel": 3}
)
intent.idempotency_key = "unique_key"  # Prevent duplicates
result = await execution_manager.execute(intent)
operation_id = result["artifacts"]["operation_id"]

# Step 3: Poll for progress
status_intent = IntentFactory.create_intent(
    intent_type="get_operation_status",
    parameters={"operation_id": operation_id}
)
status = await execution_manager.execute(status_intent)
progress = status["artifacts"]["progress_percentage"]
```

### 3. File Lifecycle Flow

```python
# Archive
archive_intent = IntentFactory.create_intent(
    intent_type="archive_file",
    parameters={"file_id": file_id, "reason": "User requested"}
)
await execution_manager.execute(archive_intent)

# Restore
restore_intent = IntentFactory.create_intent(
    intent_type="restore_file",
    parameters={"file_id": file_id}
)
await execution_manager.execute(restore_intent)

# Purge (with confirmation)
purge_intent = IntentFactory.create_intent(
    intent_type="purge_file",
    parameters={"file_id": file_id, "confirm": True}
)
await execution_manager.execute(purge_intent)
```

---

## 📝 Testing Checklist for Frontend

- [ ] Upload single file (upload ingestion)
- [ ] Upload multiple files (bulk ingestion)
- [ ] Track bulk upload progress
- [ ] Retrieve file metadata
- [ ] Retrieve file contents
- [ ] List files with pagination
- [ ] Search files by name
- [ ] Query files with filters
- [ ] Update file metadata
- [ ] Archive file
- [ ] Restore archived file
- [ ] Validate file
- [ ] Handle errors gracefully
- [ ] Test idempotency (duplicate operations)

---

## 🔗 References

- [Phase 1 Implementation Summary](./phase1_validation_results.md)
- [Phase 2 Implementation Summary](./phase2_implementation_summary.md)
- [Phase 3 Implementation Summary](./phase3_implementation_summary.md)
- [Phase 4 Implementation Summary](./phase4_implementation_summary.md)
- [Comprehensive Testing Plan Phases 1-4 Update](./comprehensive_testing_plan_phases_1_4_update.md)
