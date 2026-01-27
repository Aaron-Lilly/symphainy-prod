# Intent Contract: get_parsed_file

**Intent:** get_parsed_file  
**Intent Type:** `get_parsed_file`  
**Journey:** File Parsing (`journey_content_file_parsing`)  
**Realm:** Content Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🟡 **PRIORITY 2** - Retrieval intent for Content Realm

---

## 1. Intent Overview

### Purpose
Retrieve previously parsed file content. This is a read-only operation that fetches parsed content from GCS storage without re-parsing the file. Used by frontend to display parsed data after initial parsing is complete.

### Intent Flow
```
[User requests parsed file content]
    ↓
[get_parsed_file intent]
    ↓
[Resolve artifact via State Surface]
    ↓
[Retrieve content from GCS materialization]
    ↓
[Returns parsed content and preview]
```

### Expected Observable Artifacts
- `parsed_file_id` - Parsed content artifact identifier
- `parsed_content` - Full parsed content data
- `preview` - Preview of parsed content (first N records)

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `file_id` | `string` | File artifact identifier | Required, must exist |
| `file_reference` | `string` | State Surface file reference | Required |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `include_preview` | `boolean` | Include preview in response | `true` |
| `preview_limit` | `integer` | Number of records in preview | `10` |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `session_id` | `string` | Session identifier | Runtime (required) |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "parsed_content": {
      "result_type": "parsed_content",
      "semantic_payload": {
        "parsed_file_id": "parsed_abc123",
        "file_id": "file_abc123",
        "parsing_type": "pdf",
        "record_count": 150
      },
      "renderings": {
        "parsed_data": [...],
        "preview": [...]
      }
    }
  },
  "events": []
}
```

### Error Response

```json
{
  "error": "Parsed file not found",
  "error_code": "NOT_FOUND",
  "execution_id": "exec_abc123"
}
```

---

## 4. Artifact Registration

### State Surface Access
- **Read-Only:** This intent does not create or modify artifacts
- **Resolution:** Uses `State Surface.resolve_artifact()` for authoritative lookup
- **Materialization:** Retrieves content from GCS materialization

---

## 5. Idempotency

### Idempotency Key
N/A - This is a read-only operation

### Behavior
- Multiple calls return same data (until underlying content changes)
- No side effects
- Safe to retry

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/content/orchestrators/content_orchestrator.py::ContentOrchestrator._handle_get_parsed_file`

### Key Implementation Steps
1. Validate `file_id` and `file_reference` (required)
2. Lookup parsed result in Supabase by file_id
3. Retrieve parsed content from GCS storage
4. Build preview (first N records)
5. Return structured artifact response

### Dependencies
- **Public Works:** `FileStorageAbstraction` (for GCS retrieval)
- **State Surface:** `resolve_artifact()` (optional validation)
- **Supabase:** `parsed_results` table (lookup)
- **GCS:** Parsed content storage

---

## 7. Frontend Integration

### Frontend Usage (ContentAPIManager.ts)
```typescript
// ContentAPIManager.getParsedFile()
const executionId = await platformState.submitIntent(
  "get_parsed_file",
  {
    file_id: fileId,
    file_reference: fileReference,
  }
);
```

### Expected Frontend Behavior
1. User navigates to parsed file view
2. Submit `get_parsed_file` intent
3. Track execution via `trackExecution()`
4. Extract `parsed_content` from artifacts
5. Display parsed data in UI (data grid, preview, etc.)

---

## 8. Error Handling

### Validation Errors
- `file_id` missing → ValueError
- `file_reference` missing → ValueError

### Runtime Errors
- Parsed file not found → ValueError
- GCS retrieval failed → RuntimeError
- Content not accessible → RuntimeError

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "get_parsed_file"
}
```

---

## 9. Testing & Validation

### Happy Path
1. User requests parsed file
2. `get_parsed_file` intent executes
3. Parsed content retrieved from GCS
4. Returns parsed data and preview
5. UI displays content

### Boundary Violations
- Missing `file_id` → Validation error
- Missing `file_reference` → Validation error
- Parsed file not found → Not found error

### Failure Scenarios
- GCS retrieval failure → RuntimeError
- Parse result not indexed → Not found error

---

## 10. Contract Compliance

### Required Artifacts
- `parsed_content` - Required

### Required Events
- None (read-only operation)

### Lifecycle State
- Must validate artifact is accessible (READY or PENDING)
- Does not modify lifecycle state

---

## 11. Cross-Reference Analysis

### Journey Contract Says
- Not explicitly defined in journey contract (retrieval pattern)
- Part of file parsing workflow for displaying results

### Implementation Does
- ✅ Retrieves parsed content from GCS
- ✅ Returns structured artifact with renderings
- ✅ Provides preview for UI display

### Frontend Expects
- ✅ `parsed_content` in artifacts
- ✅ `preview` in renderings
- ✅ Execution tracking via `trackExecution()`

### Gaps/Discrepancies
- **Recommendation:** Add `get_parsed_file` to File Parsing journey contract as optional retrieval step

---

**Last Updated:** January 27, 2026  
**Owner:** Content Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
