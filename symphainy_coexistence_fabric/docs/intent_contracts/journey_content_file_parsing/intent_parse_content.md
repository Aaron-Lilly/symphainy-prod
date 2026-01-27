# Intent Contract: parse_content

**Intent:** parse_content  
**Intent Type:** `parse_content`  
**Journey:** File Parsing (`journey_content_file_parsing`)  
**Realm:** Content Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🔴 **PRIORITY 1** - Foundation intent for Content Realm

---

## 1. Intent Overview

### Purpose
Parse an uploaded file to extract structured content. This intent resumes a pending parsing journey created during `save_materialization`, retrieving the ingest type and file type from the pending intent context.

### Intent Flow
```
[User selects file to parse]
    ↓
[System identifies pending parsing journey for this file]
    ↓
[parse_content intent]
    ↓
[Retrieve ingest type and file type from pending intent context]
    ↓
[Select appropriate parser based on file type]
    ↓
[Parse file content via FileParserService]
    ↓
[Store parsed content in GCS]
    ↓
[Register artifact in State Surface (lifecycle_state: PENDING)]
    ↓
[Index artifact in Supabase with lineage]
    ↓
[Update pending intent status to COMPLETED]
    ↓
[Returns parsed_file_id, parsed_file_reference, parsing_type]
```

### Expected Observable Artifacts
- `parsed_file_id` - Parsed content artifact identifier
- `artifact_type: "parsed_content"`
- `lifecycle_state: "PENDING"` (until explicitly saved)
- `parent_artifacts: [file_artifact_id]` - Lineage to source file
- `parsing_type` - Parser type used (e.g., "pdf", "csv", "binary")
- `record_count` - Number of records parsed
- `materializations` array (GCS JSON storage)

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `file_id` | `string` | File artifact identifier to parse | Required, must exist |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `file_reference` | `string` | State Surface file reference | Auto-constructed from file_id |
| `parsing_type` | `string` | Explicit parsing type override | From pending intent context |
| `parse_options` | `object` | Parser-specific options | `{}` |
| `copybook_reference` | `string` | Copybook reference for binary files | `null` |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `session_id` | `string` | Session identifier | Runtime (required) |
| `user_id` | `string` | User identifier | Runtime (optional) |

### Pending Intent Context (Retrieved Automatically)

When a pending parsing intent exists for the file, these values are retrieved from `intent_executions.context`:

| Context Key | Type | Description |
|-------------|------|-------------|
| `ingestion_profile` | `string` | Ingest type (upload/edi/api) |
| `file_type` | `string` | File type category |
| `parse_options` | `object` | Saved parse options |
| `copybook_reference` | `string` | Copybook reference (if binary) |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "parsed_file": {
      "result_type": "parsed_content",
      "semantic_payload": {
        "parsed_file_id": "parsed_abc123",
        "parsed_file_reference": "parsed:tenant:session:parsed_abc123",
        "file_id": "file_abc123",
        "parsing_type": "pdf",
        "parsing_status": "success",
        "record_count": 150,
        "parse_options": {}
      },
      "renderings": {
        "parsed_data": [...],
        "parsed_data_preview": [...]
      }
    }
  },
  "events": [
    {
      "type": "content_parsed",
      "parsed_file_id": "parsed_abc123",
      "file_id": "file_abc123",
      "parsing_type": "pdf",
      "record_count": 150
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
- **Artifact ID:** Generated `parsed_file_id`
- **Artifact Type:** `"parsed_content"`
- **Lifecycle State:** `"PENDING"` (until embedding creation)
- **Produced By:** `{ intent: "parse_content", execution_id: "<execution_id>" }`
- **Parent Artifacts:** `[file_id]` (lineage to source file)
- **Semantic Descriptor:** `{ schema: "parsed_content_v1", record_count: <count>, parser_type: "<type>", embedding_model: null }`
- **Materializations:** `[{ materialization_id: "mat_<parsed_file_id>", storage_type: "gcs", uri: "parsed/<tenant_id>/<parsed_file_id>.json", format: "application/json" }]`

### Artifact Index Registration
- Indexed in Supabase `parsed_results` table
- Includes: `parsed_file_id`, `file_id`, `parser_type`, `record_count`, `status`
- Enables lineage tracking and discovery

---

## 5. Idempotency

### Idempotency Key
```
parsing_fingerprint = hash(file_id + ingestion_profile + file_type + session_id)
```

### Scope
- Per file, per parse configuration, per session
- Same file + same config = same parsed content artifact

### Behavior
- If same file already parsed with same config, returns existing `parsed_file_id`
- No duplicate parsing operations
- No duplicate GCS storage

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/content/orchestrators/content_orchestrator.py::ContentOrchestrator._handle_parse_content`

### Key Implementation Steps
1. Validate `file_id` (required)
2. Construct `file_reference` if not provided (lookup from Supabase)
3. Check for pending intent in `intent_executions` table
4. If pending intent exists:
   - Update status to `in_progress`
   - Extract `ingestion_profile`, `file_type`, `parse_options` from context
5. Call `FileParserService.parse_file()` with parameters
6. Track parsed result in Supabase (`parsed_results` table)
7. Register artifact in State Surface (lifecycle_state: PENDING)
8. Add GCS materialization to artifact
9. Index artifact in Supabase artifact_index
10. Return structured artifact response

### Dependencies
- **Public Works:** `FileStorageAbstraction` (for GCS storage)
- **State Surface:** `register_artifact()`, `add_materialization()`
- **Registry Abstraction:** `get_pending_intents()`, `update_intent_status()`
- **FileParserService:** `parse_file()`
- **Supabase:** `parsed_results` table (lineage tracking)

---

## 7. Frontend Integration

### Frontend Usage (ContentAPIManager.ts)
```typescript
// ContentAPIManager.parseFile()
const executionId = await platformState.submitIntent(
  "parse_content",
  {
    file_id: fileId,
    file_reference: fileReference,
    copybook_reference: copybookReference,
    parse_options: parseOptions,
  }
);
```

### Expected Frontend Behavior
1. User selects file from dropdown
2. System shows pending parsing journey (if exists)
3. User clicks "Parse File"
4. Submit `parse_content` intent via `submitIntent()`
5. Track execution via `trackExecution()`
6. Wait for execution completion
7. Extract `parsed_file_id` from execution artifacts
8. Update UI with parsed data preview

---

## 8. Error Handling

### Validation Errors
- `file_id` missing → ValueError
- File not found → ValueError
- Invalid `parsing_type` → ValueError

### Runtime Errors
- Public Works not initialized → RuntimeError
- FileParserService not available → RuntimeError
- Parser failed → RuntimeError (with parser error message)
- GCS storage failed → RuntimeError
- Artifact registration failed → RuntimeError

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "parse_content"
}
```

---

## 9. Testing & Validation

### Happy Path
1. User selects uploaded file
2. System identifies pending parsing journey
3. `parse_content` intent executes
4. File parsed successfully
5. Parsed content stored in GCS
6. Artifact registered (lifecycle_state: PENDING)
7. Artifact indexed in Supabase with lineage
8. Pending intent status updated to COMPLETED
9. Returns parsed_file_id and parsed data

### Boundary Violations
- Missing `file_id` → Validation error
- File not found → Validation error
- Unsupported file type → Parser error
- Missing copybook for binary file → Validation error

### Failure Scenarios
- Parser failure → RuntimeError (parser-specific message)
- GCS storage failure → RuntimeError
- State Surface registration failure → RuntimeError
- Supabase indexing failure → Logged but non-blocking

---

## 10. Contract Compliance

### Required Artifacts
- `parsed_file` (parsed content artifact) - Required

### Required Events
- `content_parsed` - Required

### Lifecycle State
- Must create artifact with `lifecycle_state: "PENDING"`
- Must set `parent_artifacts: [file_id]` for lineage
- Must track in Supabase `parsed_results` for lineage

### Pending Intent Handling
- Must check for pending intent before parsing
- Must update pending intent status to `in_progress` when starting
- Must update pending intent status to `completed` on success

---

## 11. Cross-Reference Analysis

### Journey Contract Says
- Parse file using ingest type and file type from intent context
- Create parsed_content artifact with lineage to file
- Mark pending parsing journey as COMPLETED

### Implementation Does
- ✅ Checks for pending intent and retrieves context
- ✅ Uses `ingestion_profile` and `file_type` from pending intent context
- ✅ Creates parsed_content artifact with parent_artifacts lineage
- ✅ Updates pending intent status

### Frontend Expects
- ✅ `parsed_file_id` in response
- ✅ `parsed_data` or `parsed_data_preview` in renderings
- ✅ Execution tracking via `trackExecution()`

### Gaps/Discrepancies
- None identified - implementation aligns with contract and frontend

---

**Last Updated:** January 27, 2026  
**Owner:** Content Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
