# Intent Contract: save_materialization

**Intent:** save_materialization  
**Intent Type:** `save_materialization`  
**Journey:** File Upload & Materialization (`journey_content_file_upload_materialization`)  
**Realm:** Content Realm  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Foundation intent for Content Realm

---

## 1. Intent Overview

### Purpose
Explicitly authorize and register materialization of a file that was uploaded via `ingest_file`. Transitions file artifact from Working Material (PENDING) to Records of Fact (READY). **Creates pending parsing journey** with ingest type and file type stored in intent context.

### Intent Flow
```
[User clicks "Save File"]
    ↓
[save_materialization intent]
    ↓
[File artifact lifecycle transition: PENDING → READY]
    ↓
[Materialization registered in materialization index]
    ↓
[Pending parsing journey created (intent_executions table, status: PENDING)]
    ↓
[Ingest type and file type stored in pending intent context]
    ↓
[Returns materialization_id, available_for_parsing: true]
```

### Expected Observable Artifacts
- `materialization_id` - Materialization identifier
- `file_id` - File artifact identifier
- `boundary_contract_id` - Boundary contract identifier
- `status: "saved"` - Materialization status
- `available_for_parsing: true` - File available for parsing
- **Pending parsing journey created** (intent_executions table, status: PENDING)
- **Ingest type and file type stored in pending intent context**

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `file_id` | `string` | File artifact identifier from `ingest_file` | Required, must exist |
| `boundary_contract_id` | `string` | Boundary contract identifier from `ingest_file` | Required, must exist |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `materialization_type` | `string` | Materialization type | Runtime (default: "full_artifact") |
| `materialization_scope` | `object` | Materialization scope | Runtime (default: {}) |
| `materialization_backing_store` | `string` | Backing store (e.g., "gcs") | Runtime (default: "gcs") |
| `user_id` | `string` | User identifier | Runtime (from context) |

### Note on Pending Parsing Journey
According to journey contract, `save_materialization` should:
1. Create pending parsing journey (intent_executions table, status: PENDING)
2. Store ingest type and file type in pending intent context
3. Enable resumable parsing workflow (user can resume later)

**Implementation Note:** This may require integration with Journey Realm orchestrator or Intent Registry to create pending intents.

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "materialization": {
      "result_type": "materialization",
      "semantic_payload": {
        "boundary_contract_id": "boundary_xyz789",
        "file_id": "file_abc123",
        "file_reference": "file:tenant:session:file_abc123",
        "materialization_type": "full_artifact",
        "materialization_scope": {},
        "materialization_backing_store": "gcs",
        "status": "saved",
        "available_for_parsing": true
      },
      "renderings": {
        "message": "File saved and available for parsing"
      }
    }
  },
  "events": [
    {
      "type": "materialization_saved",
      "file_id": "file_abc123",
      "boundary_contract_id": "boundary_xyz789",
      "materialization_type": "full_artifact",
      "materialization_scope": {}
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

## 4. Artifact Lifecycle Transition

### State Surface Update
- **Artifact ID:** `file_id` (from parameters)
- **Lifecycle State Transition:** `"PENDING"` → `"READY"` (Working Material → Records of Fact)
- **Update Method:** `update_artifact_lifecycle()` or equivalent
- **Artifact Index:** Updated in Supabase (lifecycle_state: READY)

### Materialization Registration
- **Materialization Index:** Registered in Supabase `project_files` table (via FileStorageAbstraction)
- **Materialization Type:** From context metadata (default: "full_artifact")
- **Materialization Scope:** From context metadata (default: {})
- **Materialization Backing Store:** From context metadata (default: "gcs")

### Pending Parsing Journey Creation
- **Intent Executions Table:** Create pending intent record
- **Intent Type:** `"parse_content"`
- **Target Artifact ID:** `file_id`
- **Status:** `"PENDING"`
- **Context:** `{ "ingestion_profile": "<ingest_type>", "file_type": "<file_type>", "parse_options": {} }`
- **Enables:** Resumable parsing workflow

---

## 5. Idempotency

### Idempotency Key
```
materialization_fingerprint = hash(artifact_id + boundary_contract_id + session_id)
```

### Scope
- Per artifact, per boundary contract
- Same file + same boundary contract + same session = same materialization
- Prevents duplicate materialization registrations

### Behavior
- If same file + boundary contract + session, returns existing materialization_id
- No duplicate materialization registrations
- No duplicate pending parsing journeys

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/content/orchestrators/content_orchestrator.py::ContentOrchestrator._handle_save_materialization`

### Key Implementation Steps
1. Validate `boundary_contract_id` and `file_id` (required)
2. Get materialization metadata from context
3. Retrieve file metadata from State Surface (optional)
4. Register materialization in materialization index (Supabase project_files)
5. **Create pending parsing journey** (intent_executions table, status: PENDING)
6. **Store ingest type and file type in pending intent context**
7. Return structured artifact response

### Dependencies
- **Public Works:** `FileStorageAbstraction` (for materialization registration)
- **State Surface:** `get_file_metadata()` (optional, for file metadata)
- **Intent Registry:** `create_pending_intent()` (for pending parsing journey creation)
- **Runtime:** `ExecutionContext` with materialization metadata

### Pending Parsing Journey Creation
According to journey contract, this intent should:
1. Call `create_pending_parse_intent()` or equivalent
2. Store ingest type and file type in pending intent context
3. Set status to PENDING
4. Enable resumable parsing workflow

**Implementation Note:** May require integration with Journey Realm orchestrator or Intent Registry.

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// ContentAPIManager.saveMaterialization()
const executionId = await platformState.submitIntent(
  "save_materialization",
  {
    file_id: fileId,
    boundary_contract_id: boundaryContractId,
  }
);
```

### Expected Frontend Behavior
1. Submit `save_materialization` intent via `submitIntent()`
2. Track execution via `trackExecution()`
3. Wait for execution completion
4. Extract `materialization_id` from execution artifacts
5. Update UI: Remove "Save" button, show "Parsed" status
6. Enable parsing workflow (pending journey ready to be resumed)

---

## 8. Error Handling

### Validation Errors
- `boundary_contract_id` missing → ValueError
- `file_id` missing → ValueError
- File artifact not found → ValueError

### Runtime Errors
- Public Works not initialized → RuntimeError
- FileStorageAbstraction not available → RuntimeError (logged, non-blocking)
- Materialization registration failed → RuntimeError (logged, non-blocking)
- Pending parsing journey creation failed → RuntimeError (logged, non-blocking)

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "save_materialization"
}
```

---

## 9. Testing & Validation

### Happy Path
1. User clicks "Save File"
2. `save_materialization` intent executes
3. File artifact lifecycle transitions (PENDING → READY)
4. Materialization registered in materialization index
5. **Pending parsing journey created** (status: PENDING)
6. **Ingest type and file type stored in pending intent context**
7. Returns materialization_id, available_for_parsing: true

### Boundary Violations
- Missing `boundary_contract_id` → Validation error
- Missing `file_id` → Validation error
- File artifact not found → Validation error

### Failure Scenarios
- Materialization registration failure → Logged but non-blocking
- Pending parsing journey creation failure → Logged but non-blocking
- State Surface update failure → Runtime error

---

## 10. Contract Compliance

### Required Artifacts
- `materialization` (materialization artifact) - Required

### Required Events
- `materialization_saved` - Required

### Lifecycle State
- Must transition file artifact from `"PENDING"` → `"READY"`
- Must NOT create new artifacts (only updates existing)

### Pending Parsing Journey
- Must create pending parsing journey (intent_executions table)
- Must store ingest type and file type in pending intent context
- Must set status to PENDING
- Must enable resumable parsing workflow

---

**Last Updated:** January 27, 2026  
**Owner:** Content Realm Solution Team  
**Status:** ⏳ **IN PROGRESS**
