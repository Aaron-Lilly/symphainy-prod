# Bulk Operations Capability

**Realm:** Content  
**Status:** ✅ Complete  
**Last Updated:** January 2026

---

## Overview

Bulk Operations enable processing of thousands of files efficiently through batching, parallel processing, progress tracking, and resume capability. This is essential for production workloads like processing 350k insurance policies.

**Business Value:** Enables organizations to process large volumes of data efficiently without overwhelming the system or losing progress on failures.

---

## Available Intents

### 1. Bulk Ingest Files

**Intent:** `bulk_ingest_files`

**Purpose:** Ingest multiple files in a single operation with batching and parallel processing

**Use Case:** Upload 1000+ files, process EDI batch, import API data in bulk

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

**Example:**
```python
files = []
for i in range(100):
    with open(f"file_{i}.pdf", "rb") as f:
        file_content_hex = f.read().hex()
    files.append({
        "ingestion_type": "upload",
        "file_content": file_content_hex,
        "ui_name": f"file_{i}.pdf",
        "file_type": "unstructured",
        "mime_type": "application/pdf"
    })

intent = IntentFactory.create_intent(
    intent_type="bulk_ingest_files",
    tenant_id="tenant_123",
    session_id="session_456",
    solution_id="solution_789",
    parameters={
        "files": files,
        "batch_size": 10,
        "max_parallel": 5
    }
)
result = await execution_manager.execute(intent)
print(f"Success: {result.artifacts['success_count']}/{result.artifacts['total_files']}")
```

---

### 2. Bulk Parse Files

**Intent:** `bulk_parse_files`

**Purpose:** Parse multiple files in bulk

**Use Case:** Parse 1000 uploaded files

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

**Example:**
```python
intent = IntentFactory.create_intent(
    intent_type="bulk_parse_files",
    tenant_id="tenant_123",
    session_id="session_456",
    solution_id="solution_789",
    parameters={
        "file_ids": ["file_1", "file_2", "file_3", ...],
        "batch_size": 10,
        "max_parallel": 5
    }
)
result = await execution_manager.execute(intent)
```

---

### 3. Bulk Extract Embeddings

**Intent:** `bulk_extract_embeddings`

**Purpose:** Extract embeddings from multiple parsed files

**Use Case:** Generate embeddings for 1000 parsed files

**Parameters:**
```python
{
    "parsed_result_ids": ["<parsed_id1>", "<parsed_id2>", ...],  # Required
    "batch_size": 10,  # Optional, default: 10
    "max_parallel": 5  # Optional, default: 5
}
```

**Response:** Similar structure to bulk_ingest_files

---

### 4. Bulk Interpret Data

**Intent:** `bulk_interpret_data`

**Purpose:** Interpret multiple parsed files

**Use Case:** Interpret 1000 parsed files for analysis

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

## Progress Tracking

### Get Operation Status

**Intent:** `get_operation_status`

**Purpose:** Get progress of a long-running bulk operation

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
        "status": "in_progress",  # "in_progress", "completed", "failed"
        "total_batches": 10,
        "completed_batches": 5,
        "current_batch": 5,
        "progress_percent": 50.0,
        "results": [...],
        "errors": [...],
        "started_at": "<timestamp>",
        "updated_at": "<timestamp>"
    },
    "events": []
}
```

**Example:**
```python
# Start bulk operation
result = await execution_manager.execute(bulk_intent)
operation_id = result.artifacts["operation_id"]

# Check progress
status_intent = IntentFactory.create_intent(
    intent_type="get_operation_status",
    tenant_id="tenant_123",
    session_id="session_456",
    solution_id="solution_789",
    parameters={
        "operation_id": operation_id
    }
)
status_result = await execution_manager.execute(status_intent)
progress = status_result.artifacts["progress_percent"]
print(f"Progress: {progress}%")
```

---

## Resume Capability

Bulk operations support resume from a specific batch:

```python
# Resume from batch 5
intent = IntentFactory.create_intent(
    intent_type="bulk_ingest_files",
    tenant_id="tenant_123",
    session_id="session_456",
    solution_id="solution_789",
    parameters={
        "files": files,
        "operation_id": "previous_operation_id",
        "resume_from_batch": 5  # Resume from batch 5
    }
)
```

---

## Retry Logic

Bulk operations include automatic retry logic:
- **Upload:** 3 retries with exponential backoff
- **EDI:** 5 retries with longer delays (network issues)
- **API:** 4 retries with moderate delays

Failed items are tracked in the `errors` array and can be retried individually.

---

## Business Use Cases

### Use Case 1: Insurance Policy Migration
**Scenario:** Migrate 350k insurance policies from legacy system

**Flow:**
1. Export policies from legacy system
2. Prepare file list (350k files)
3. Call `bulk_ingest_files` with large batch size
4. Monitor progress via `get_operation_status`
5. Handle errors and retry failed items
6. Complete migration

### Use Case 2: Daily EDI Batch
**Scenario:** Process daily EDI batch of 1000 transactions

**Flow:**
1. Receive EDI batch from partner
2. Call `bulk_ingest_files` with EDI files
3. Process in batches of 50
4. Track progress
5. Notify partner of completion

### Use Case 3: API Data Import
**Scenario:** Import data from external API (10k records)

**Flow:**
1. Fetch data from API
2. Convert to file format
3. Call `bulk_ingest_files` with API payloads
4. Process in parallel (max_parallel=10)
5. Complete import

---

## Performance Considerations

### Batch Size
- **Small batches (5-10):** Better for error recovery, slower overall
- **Large batches (50-100):** Faster overall, harder error recovery
- **Recommended:** 10-20 for most use cases

### Parallel Processing
- **Low parallelism (2-3):** Safer, less resource intensive
- **High parallelism (10+):** Faster, more resource intensive
- **Recommended:** 5 for most use cases

### For 350k Policies
- **Batch size:** 20-50
- **Max parallel:** 10-20
- **Estimated time:** Depends on file size and infrastructure

---

## Error Handling

Bulk operations handle errors gracefully:
- Individual file failures don't stop the operation
- Errors are tracked in the `errors` array
- Failed items can be retried individually
- Operation status shows error count

---

## Related Capabilities

- [Data Ingestion](data_ingestion.md) - Single file ingestion
- [File Parsing](file_parsing.md) - Parse files
- [File Management](file_management.md) - Manage files

---

## API Reference

For complete API contracts, see [API Contracts](../execution/api_contracts_frontend_integration.md).

---

**Status:** ✅ Complete and Operational
