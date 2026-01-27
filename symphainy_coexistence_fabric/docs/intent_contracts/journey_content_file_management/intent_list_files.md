# Intent Contract: list_files

**Intent:** list_files  
**Intent Type:** `list_files`  
**Journey:** File Management (`journey_content_file_management`)  
**Realm:** Content Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🟡 **PRIORITY 2** - Management intent for Content Realm

---

## 1. Intent Overview

### Purpose
List files for a tenant and session. Returns file metadata (not content) for UI display. Files are workspace-scoped (filtered by user_id, session_id, solution_id) for security.

> **Note:** Original journey contract specified `list_artifacts`. This contract uses `list_files` to align with the actual implementation and frontend usage.

### Intent Flow
```
[User navigates to file list]
    ↓
[list_files intent]
    ↓
[Query Supabase project_files table]
    ↓
[Apply workspace scope filter (user_id, session_id)]
    ↓
[Return file metadata list]
```

### Expected Observable Artifacts
- `files` - Array of file metadata objects
- `count` - Total number of files returned
- `tenant_id` - Tenant identifier
- `session_id` - Session identifier

---

## 2. Intent Parameters

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `tenant_id` | `string` | Tenant identifier | From context |
| `session_id` | `string` | Session identifier | From context |
| `file_type` | `string` | Filter by file type | `null` (no filter) |
| `limit` | `integer` | Limit results | `100` |
| `offset` | `integer` | Pagination offset | `0` |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `session_id` | `string` | Session identifier | Runtime (required) |
| `user_id` | `string` | User identifier | Runtime (for workspace scope) |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "file_list": {
      "result_type": "file_list",
      "semantic_payload": {
        "files": [
          {
            "file_id": "file_abc123",
            "file_name": "document.pdf",
            "file_type": "pdf",
            "mime_type": "application/pdf",
            "file_size": 1024000,
            "file_hash": "sha256:abc123...",
            "storage_location": "gs://bucket/path/to/file",
            "created_at": "2026-01-27T10:00:00Z",
            "updated_at": "2026-01-27T10:00:00Z"
          }
        ],
        "count": 1,
        "tenant_id": "tenant_123",
        "session_id": "session_456",
        "limit": 100,
        "offset": 0,
        "file_type_filter": null
      },
      "renderings": {}
    }
  },
  "events": []
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

### State Surface Access
- **Read-Only:** This intent does not create or modify artifacts
- **Query Source:** Supabase `project_files` table

---

## 5. Idempotency

### Idempotency Key
N/A - This is a read-only query operation

### Behavior
- Multiple calls return current state of files
- Results may change as files are added/removed
- Safe to retry

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/content/orchestrators/content_orchestrator.py::ContentOrchestrator._handle_list_files`

### Key Implementation Steps
1. Extract parameters (tenant_id, session_id, file_type, limit, offset)
2. Get user_id from context for workspace-scoped filtering
3. Query Supabase `project_files` table via `_list_files_from_supabase()`
4. Transform results to semantic payload format
5. Return structured artifact response

### Dependencies
- **Supabase:** `project_files` table (file index)
- **Public Works:** Not required (direct Supabase query)

### Workspace Scope Security
Files are filtered by workspace scope (user_id + session_id + solution_id) to ensure users only see their own files.

---

## 7. Frontend Integration

### Frontend Usage (ContentAPIManager.ts)
```typescript
// ContentAPIManager.listFiles()
const executionId = await platformState.submitIntent(
  "list_files",
  {
    tenant_id: platformState.state.session.tenantId,
    session_id: platformState.state.session.sessionId,
  }
);
```

### Expected Frontend Behavior
1. User navigates to file list page
2. Submit `list_files` intent via `submitIntent()`
3. Track execution via `trackExecution()`
4. Wait for execution completion
5. Extract `files` array from execution artifacts
6. Display files in UI (table, grid, etc.)

---

## 8. Error Handling

### Validation Errors
- None expected - all parameters are optional with defaults

### Runtime Errors
- Supabase query failed → RuntimeError
- Database timeout → RuntimeError

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "list_files"
}
```

---

## 9. Testing & Validation

### Happy Path
1. User requests file list
2. `list_files` intent executes
3. Supabase query succeeds
4. Files returned with metadata
5. UI displays file list

### Boundary Violations
- None expected - gracefully handles empty results

### Failure Scenarios
- Supabase unavailable → RuntimeError
- Query timeout → RuntimeError

---

## 10. Contract Compliance

### Required Artifacts
- `file_list` - Required with files array

### Required Events
- None (read-only operation)

### Security Requirements
- Must filter by workspace scope (user_id)
- Must not expose files from other users/workspaces

---

## 11. Cross-Reference Analysis

### Journey Contract Says
- Original contract specified `list_artifacts`
- Purpose: List artifacts for management

### Implementation Does
- ✅ Uses intent type `list_files` (content-realm specific)
- ✅ Queries Supabase project_files table
- ✅ Applies workspace scope filter
- ✅ Returns file metadata list

### Frontend Expects
- ✅ Intent type: `list_files`
- ✅ Returns `files` array with metadata
- ✅ Execution tracking via `trackExecution()`

### Gaps/Discrepancies
- **NAMING:** Journey contract says `list_artifacts`, implementation uses `list_files`
- **Recommendation:** Keep `list_files` for Content Realm (more specific), use `list_artifacts` for cross-realm artifact discovery

---

**Last Updated:** January 27, 2026  
**Owner:** Content Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
