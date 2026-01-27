# Intent Contract: parse_content

**Intent:** parse_content  
**Intent Type:** `parse_content`  
**Journey:** Journey Content File Parsing (`journey_content_file_parsing`)  
**Realm:** Content Realm  
**Status:** IN PROGRESS  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
Resume a pending parsing journey and parse an uploaded file. The ingest type and file type are retrieved from the pending intent context (created during `save_materialization`), so the user does not need to re-select them. This enables resumable parsing workflows.

### Intent Flow
```
[User selects uploaded file from dropdown]
    ↓
[System identifies pending parsing journey for this file]
    ↓
[System retrieves ingest type and file type from pending intent context]
    ↓
[parse_content intent executes]
    ↓
[Pending intent status updated to "in_progress"]
    ↓
[File parsed using appropriate parser (based on ingest type and file type)]
    ↓
[Parsed content artifact created (lifecycle_state: PENDING → READY)]
    ↓
[Artifact registered in State Surface with lineage (parent: file_artifact_id)]
    ↓
[Artifact indexed in Supabase with lineage metadata]
    ↓
[Parsed content stored in GCS (JSON format)]
    ↓
[Pending parsing journey status: COMPLETED]
    ↓
[Returns parsed_file_id, parsed_content, preview]
```

### Expected Observable Artifacts
- `parsed_file_id` - Parsed content artifact identifier
- `artifact_type: "parsed_content"`
- `lifecycle_state: "READY"` (transitions from PENDING)
- `parent_artifacts: [file_artifact_id]` (lineage)
- `parsed_file_reference` - State Surface reference
- `parsing_type` - Parser type used (from pending intent context)
- `parsing_status: "success"`
- `record_count` - Number of records parsed
- `materializations` array (GCS JSON storage)
- `parsed_data` - Full parsed content (in renderings)
- `parsed_data_preview` - Preview of parsed content (first 10 items)

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `file_id` | `string` | File artifact identifier (from uploaded file) | Required, must exist in State Surface |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `file_reference` | `string` | State Surface file reference (format: `file:{tenant_id}:{session_id}:{file_id}`) | Constructed from file_id if not provided |
| `parsing_type` | `string` | Explicit parsing type (overrides pending intent context) | Retrieved from pending intent context |
| `parse_options` | `object` | Parsing options (parser-specific configuration) | `{}` (or from pending intent context) |
| `copybook_reference` | `string` | Copybook reference for binary files (COBOL, etc.) | From pending intent context if available |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `pending_intent_id` | `string` | Pending parsing intent identifier | Intent Registry (retrieved by file_id) |
| `ingestion_profile` | `string` | Ingestion profile (from pending intent context) | Pending Intent Context |
| `file_type` | `string` | File type (from pending intent context) | Pending Intent Context |
| `parse_options` | `object` | Parse options (from pending intent context) | Pending Intent Context |
| `copybook_reference` | `string` | Copybook reference (from pending intent context) | Pending Intent Context |

**Note:** The intent first checks for a pending parsing journey associated with the `file_id`. If found, it retrieves `ingestion_profile`, `file_type`, and `parse_options` from the pending intent context. If no pending intent exists, it uses the parameters provided directly.

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "artifact_type": {
      "result_type": "artifact",
      "semantic_payload": {
        // Artifact data
      },
      "renderings": {}
    }
  },
  "events": [
    {
      "type": "event_type",
      // Event data
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
- **Artifact ID:** [How artifact_id is generated]
- **Artifact Type:** `"artifact_type"`
- **Lifecycle State:** `"PENDING"` or `"READY"`
- **Produced By:** `{ intent: "parse_content", execution_id: "<execution_id>" }`
- **Semantic Descriptor:** [Descriptor details]
- **Parent Artifacts:** [List of parent artifact IDs]
- **Materializations:** [List of materializations]

### Artifact Index Registration
- Indexed in Supabase `artifact_index` table
- Includes: [List of indexed fields]

---

## 5. Idempotency

### Idempotency Key
```
idempotency_key = hash(file_id + parsing_type + file_type + parse_options)
```

### Scope
- Per artifact, per parse configuration
- Same file + same parsing type + same file type + same parse options = same parsed content artifact

### Behavior
- If a parsed content artifact already exists for the same file_id with the same parsing configuration, the existing artifact is returned
- Prevents duplicate parsing of the same file with the same configuration
- Different parsing configurations (different parsing_type or parse_options) create different parsed content artifacts

---

## 6. Implementation Details

### Handler Location
- **Old Implementation:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py` (method: `_handle_parse_content`, line ~2713)
- **New Implementation:** `symphainy_platform/realms/content/intent_services/parse_content_service.py` (to be created)

### Key Implementation Steps
1. **Validate Parameters:** Ensure `file_id` is provided
2. **Resolve File Reference:** Construct `file_reference` from `file_id` (format: `file:{tenant_id}:{session_id}:{file_id}`)
   - If `file_reference` not provided, look up file metadata from Supabase to get correct `session_id`
3. **Check for Pending Intent:** Query Intent Registry for pending `parse_content` intent associated with `file_id`
   - If found, retrieve `ingestion_profile`, `file_type`, and `parse_options` from pending intent context
   - Update pending intent status to "in_progress"
4. **Select Parser:** Use `parsing_type` (from pending intent context or parameters) to select appropriate parser
5. **Parse File:** Call `FileParserService.parse_file()` with:
   - `file_id`, `file_reference`, `parsing_type`, `parse_options`, `copybook_reference`
6. **Create Parsed Content Artifact:**
   - Generate `parsed_file_id` (UUID format)
   - Register artifact in State Surface with:
     - `artifact_type: "parsed_content"`
     - `lifecycle_state: "PENDING"` (initially)
     - `parent_artifacts: [file_id]` (lineage)
     - `semantic_descriptor` (schema, record_count, parser_type)
   - Add GCS materialization (`parsed/{tenant_id}/{parsed_file_id}.json`)
   - Update lifecycle state to `"READY"`
7. **Track Parsed Result:** Store in Supabase `parsed_results` table for lineage
8. **Index Artifact:** Index in Supabase `artifact_index` table with lineage metadata
9. **Complete Pending Intent:** Update pending intent status to "COMPLETED"
10. **Return Structured Artifact:** Return parsed content with full data and preview

### Dependencies
- **Public Works:**
  - `RegistryAbstraction` - For retrieving pending intents
  - `FileParserService` - For parsing file content
  - `FileStorageAbstraction` - For GCS storage
- **State Surface:**
  - `register_artifact()` - Register parsed content artifact
  - `add_materialization()` - Add GCS materialization
  - `update_artifact_lifecycle()` - Update lifecycle state
- **Runtime:**
  - `ExecutionContext` - Tenant, session, execution context
  - `Intent Registry` - For pending intent management

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// From ContentAPIManager.ts
async parseFile(
  fileId: string,
  fileReference: string,
  copybookReference?: string
): Promise<ParseResponse> {
  // Validate session
  const sessionValid = await validateSession();
  if (!sessionValid) {
    throw new Error("Session invalid");
  }

  // Submit parse_content intent
  const executionId = await platformState.submitIntent(
    'parse_content',
    {
      file_id: fileId,
      file_reference: fileReference,
      copybook_reference: copybookReference
    }
  );

  // Track execution
  await platformState.trackExecution(executionId);

  // Wait for completion and return result
  // ...
}
```

### Expected Frontend Behavior
1. **User selects file from dropdown** - Frontend shows list of uploaded files (lifecycle_state: "READY")
2. **System identifies pending parsing journey** - Frontend checks for pending intents for selected file
3. **User clicks "Parse File"** - Frontend submits `parse_content` intent with `file_id`
4. **Frontend tracks execution** - Uses `platformState.trackExecution()` to monitor progress
5. **Frontend displays parsed content** - Shows parsed data preview and full content when available
6. **Frontend updates UI** - Updates file status to "parsed", shows parsed content in preview
7. **Frontend enables next step** - Enables "Create Embeddings" button for parsed file

---

## 8. Error Handling

### Validation Errors
- **Missing file_id:** `ValueError("file_id is required for parse_content intent")` -> Returns error response with `ERROR_CODE: "MISSING_PARAMETER"`
- **File not found:** File does not exist in State Surface -> Returns error response with `ERROR_CODE: "FILE_NOT_FOUND"`
- **Invalid file_reference:** Cannot construct valid file reference -> Returns error response with `ERROR_CODE: "INVALID_FILE_REFERENCE"`

### Runtime Errors
- **Parser unavailable:** Selected parser not available or not configured -> Returns error response with `ERROR_CODE: "PARSER_UNAVAILABLE"`
- **Parsing failure:** File parsing fails (unsupported format, corrupted file, etc.) -> Returns error response with `ERROR_CODE: "PARSING_FAILED"` and details
- **Storage failure:** GCS storage fails -> Returns error response with `ERROR_CODE: "STORAGE_FAILED"`
- **Pending intent not found:** No pending parsing journey exists (should not happen in normal flow) -> Falls back to using parameters directly, logs warning
- **Copybook validation failure:** Binary file requires copybook but copybook invalid -> Returns error response with `ERROR_CODE: "COPYBOOK_INVALID"`

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "parse_content",
  "file_id": "file_xyz789",
  "details": {
    "parsing_type": "structured",
    "reason": "Parser unavailable"
  }
}
```

---

## 9. Testing & Validation

### Happy Path
1. User selects uploaded file (file_id: "file_abc123")
2. System identifies pending parsing journey (intent_id: "intent_xyz789", status: "PENDING")
3. System retrieves ingest type ("structured") and file type ("csv") from pending intent context
4. User clicks "Parse File"
5. `parse_content` intent executes with `file_id: "file_abc123"`
6. Pending intent status updated to "in_progress"
7. File parsed using structured parser
8. Parsed content artifact created (parsed_file_id: "parsed_def456", lifecycle_state: "READY")
9. Artifact registered in State Surface with lineage (parent: "file_abc123")
10. Artifact indexed in Supabase
11. Parsed content stored in GCS (parsed/tenant_123/parsed_def456.json)
12. Pending parsing journey status: COMPLETED
13. Returns parsed_file_id, parsed_content, preview

### Boundary Violations
- **File not uploaded:** File does not exist in State Surface -> Returns `ERROR_CODE: "FILE_NOT_FOUND"`
- **File already parsed:** Parsed content artifact already exists for same configuration -> Returns existing artifact (idempotent)
- **Invalid parsing type:** Parsing type not supported -> Returns `ERROR_CODE: "PARSER_UNAVAILABLE"`
- **Missing copybook for binary file:** Binary file requires copybook but not provided -> Returns `ERROR_CODE: "COPYBOOK_REQUIRED"`

### Failure Scenarios
- **Parser failure:** Parser crashes or throws exception -> Returns `ERROR_CODE: "PARSING_FAILED"` with details, pending intent remains in PENDING status (can retry)
- **Storage failure:** GCS write fails -> Returns `ERROR_CODE: "STORAGE_FAILED"`, artifact not created, pending intent remains in PENDING status
- **Network timeout:** Long-running parse operation times out -> Returns `ERROR_CODE: "TIMEOUT"`, pending intent remains in PENDING status
- **State Surface failure:** Artifact registration fails -> Returns `ERROR_CODE: "REGISTRATION_FAILED"`, parsed content may be stored but not registered

---

## 10. Contract Compliance

### Required Artifacts
- `parsed_content` - Required (parsed content artifact)

### Required Events
- `parsing_completed` - Required (emitted when parsing succeeds)

### Lifecycle State
- **Initial State:** `"PENDING"` (when artifact first registered)
- **Final State:** `"READY"` (after parsed content stored in GCS)
- **Transition:** `"PENDING"` → `"READY"` (automatic after storage)

### Contract Validation
- ✅ Artifact must have `parent_artifacts: [file_artifact_id]` (lineage)
- ✅ Artifact must have `materializations` array with GCS storage
- ✅ Artifact must have `semantic_descriptor` with `record_count` and `parser_type`
- ✅ Pending intent must be updated to "COMPLETED" status
- ✅ Parsed result must be tracked in `parsed_results` table

---

**Last Updated:** January 27, 2026  
**Owner:** Content Realm Solution Team  
**Status:** ✅ **ENHANCED** - Ready for implementation
