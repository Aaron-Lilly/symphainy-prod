# Intent Contract: ingest_file

**Intent:** ingest_file  
**Intent Type:** `ingest_file`  
**Journey:** File Upload & Materialization (`journey_content_file_upload_materialization`)  
**Realm:** Content Realm  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Foundation intent for Content Realm

---

## 1. Intent Overview

### Purpose
Upload a file to the platform. File is stored in GCS with materialization pending (Working Material). User must explicitly save via `save_materialization` to transition to Records of Fact.

### Intent Flow
```
[User uploads file]
    ↓
[ingest_file intent]
    ↓
[File stored in GCS]
    ↓
[Artifact registered in State Surface (lifecycle_state: PENDING)]
    ↓
[Artifact indexed in Supabase]
    ↓
[Returns artifact_id, boundary_contract_id, materialization_pending: true]
```

### Expected Observable Artifacts
- `artifact_id` - File artifact identifier
- `artifact_type: "file"`
- `lifecycle_state: "PENDING"` (Working Material)
- `boundary_contract_id` - Boundary contract identifier
- `materialization_pending: true` - Indicates materialization is pending
- `file_reference` - File reference string
- `storage_location` - GCS storage location
- `materializations` array (GCS storage)

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `ui_name` | `string` | User-friendly filename | Required, non-empty |
| `file_content` | `string` (hex-encoded) | File content as hex-encoded bytes | Required for upload type |
| `ingestion_type` | `string` | Ingestion type: "upload", "edi", or "api" | Default: "upload" |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `file_type` | `string` | File type category (e.g., "pdf", "csv", "structured", "unstructured") | "unstructured" |
| `mime_type` | `string` | MIME type (e.g., "application/pdf") | "application/octet-stream" |
| `filename` | `string` | Original filename | Defaults to `ui_name` |
| `user_id` | `string` | User identifier | From context if not provided |
| `source_metadata` | `object` | Source-specific metadata | `{}` |
| `ingestion_options` | `object` | Ingestion-specific options | `{}` |

### EDI-Specific Parameters (when `ingestion_type: "edi"`)

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `edi_data` | `string` (hex-encoded) | EDI data as hex-encoded bytes | Yes |
| `partner_id` | `string` | EDI partner identifier | Yes |
| `edi_protocol` | `string` | EDI protocol (e.g., "as2", "sftp") | No (default: "as2") |

### API-Specific Parameters (when `ingestion_type: "api"`)

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `api_payload` | `object` | API payload data | Yes |
| `endpoint` | `string` | API endpoint | No |
| `api_type` | `string` | API type (e.g., "rest", "graphql") | No (default: "rest") |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `boundary_contract_id` | `string` | Boundary contract identifier | Runtime (required) |
| `materialization_type` | `string` | Materialization type | Runtime (default: "full_artifact") |
| `materialization_backing_store` | `string` | Backing store (e.g., "gcs") | Runtime (default: "gcs") |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "artifact": {
      "result_type": "artifact",
      "semantic_payload": {
        "artifact_id": "file_abc123",
        "artifact_type": "file",
        "lifecycle_state": "PENDING",
        "file_reference": "file:tenant:session:file_abc123",
        "storage_location": "gs://bucket/path/to/file",
        "ui_name": "document.pdf",
        "file_type": "pdf",
        "mime_type": "application/pdf",
        "ingestion_type": "upload",
        "boundary_contract_id": "boundary_xyz789",
        "materialization_pending": true,
        "file_size": 1024000,
        "file_hash": "sha256:abc123...",
        "created_at": "2026-01-27T10:00:00Z"
      },
      "renderings": {}
    }
  },
  "events": [
    {
      "type": "artifact_ingested",
      "artifact_id": "file_abc123",
      "artifact_type": "file",
      "ingestion_type": "upload"
    }
  ]
}
```

### Error Response

```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123"
}
```

---

## 4. Artifact Registration

### State Surface Registration
- **Artifact ID:** Generated from ingestion result
- **Artifact Type:** `"file"`
- **Lifecycle State:** `"PENDING"` (Working Material)
- **Produced By:** `{ intent: "ingest_file", execution_id: "<execution_id>" }`
- **Semantic Descriptor:** `{ schema: "file_v1", record_count: null, parser_type: null, embedding_model: null }`
- **Parent Artifacts:** `[]` (no parents)
- **Materializations:** `[{ materialization_id: "mat_<artifact_id>", storage_type: "gcs", uri: "<storage_location>", format: "<mime_type>", compression: null }]`

### Artifact Index Registration
- Indexed in Supabase `artifact_index` table
- Includes: `artifact_id`, `artifact_type`, `lifecycle_state`, `tenant_id`, `created_at`, `updated_at`
- Enables discovery via `list_artifacts()` queries

---

## 5. Idempotency

### Idempotency Key
```
content_fingerprint = hash(file_content + session_id)
```

### Scope
- Per tenant, per session
- Same file content + same session = same artifact_id
- Prevents duplicate file uploads

### Behavior
- If same file content uploaded in same session, returns existing artifact_id
- No duplicate artifacts created
- No duplicate GCS storage

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/content/orchestrators/handlers/ingestion_handlers.py::IngestionHandlers.handle_ingest_file`

### Key Implementation Steps
1. Validate `boundary_contract_id` from context metadata (required)
2. Get `IngestionAbstraction` from Public Works
3. Determine ingestion type (upload/edi/api)
4. Prepare `IngestionRequest` based on type
5. Execute ingestion via `IngestionAbstraction.ingest_data()`
6. Register artifact in State Surface (lifecycle_state: PENDING)
7. Add GCS materialization to artifact
8. Index artifact in Supabase (artifact_index)
9. Return structured artifact response

### Dependencies
- **Public Works:** `IngestionAbstraction` (for file storage)
- **State Surface:** `register_artifact()`, `add_materialization()`
- **Artifact Index:** `_index_artifact()` helper
- **Runtime:** `ExecutionContext` with `boundary_contract_id` in metadata

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// ContentAPIManager.uploadFile()
const executionId = await platformState.submitIntent(
  "ingest_file",
  {
    ingestion_type: 'upload',
    file_content: fileContentHex,  // Hex-encoded file bytes
    ui_name: file.name,
    file_type: fileTypeCategory || 'unstructured',
    mime_type: file.type,
    filename: file.name
  },
  {
    ui_name: file.name,
    original_filename: file.name,
  }
);
```

### Expected Frontend Behavior
1. Convert file to hex-encoded bytes
2. Submit `ingest_file` intent via `submitIntent()`
3. Track execution via `trackExecution()`
4. Wait for execution completion
5. Extract `file_id` and `boundary_contract_id` from execution artifacts
6. Display file with "Save" button (materialization_pending: true)

---

## 8. Error Handling

### Validation Errors
- `boundary_contract_id` missing → ValueError
- `ui_name` missing → ValueError
- `file_content` missing (for upload type) → ValueError
- Invalid `ingestion_type` → ValueError
- Invalid hex-encoded `file_content` → ValueError

### Runtime Errors
- Public Works not initialized → RuntimeError
- IngestionAbstraction not available → RuntimeError
- Ingestion failed → RuntimeError (with error message from ingestion result)
- Artifact registration failed → RuntimeError

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "ingest_file"
}
```

---

## 9. Testing & Validation

### Happy Path
1. User uploads file
2. `ingest_file` intent executes
3. File stored in GCS
4. Artifact registered (lifecycle_state: PENDING)
5. Artifact indexed in Supabase
6. Returns artifact_id, boundary_contract_id, materialization_pending: true

### Boundary Violations
- Missing `ui_name` → Validation error
- Missing `file_content` (upload type) → Validation error
- Missing `boundary_contract_id` → Runtime error
- Invalid hex-encoded `file_content` → Validation error

### Failure Scenarios
- GCS storage failure → Runtime error
- State Surface registration failure → Runtime error
- Supabase indexing failure → Logged but non-blocking

---

## 10. Contract Compliance

### Required Artifacts
- `artifact` (file artifact) - Required

### Required Events
- `artifact_ingested` - Required

### Lifecycle State
- Must create artifact with `lifecycle_state: "PENDING"`
- Must NOT transition to `"READY"` (that's `save_materialization` responsibility)

### Materialization
- Must create GCS materialization
- Must set `materialization_pending: true` in response

---

**Last Updated:** January 27, 2026  
**Owner:** Content Realm Solution Team  
**Status:** ⏳ **IN PROGRESS**
