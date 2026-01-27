# Intent Contract: list_artifacts

**Intent:** list_artifacts  
**Intent Type:** `list_artifacts`  
**Journey:** File Management (`journey_content_file_management`)  
**Realm:** Content Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🟡 **PRIORITY 2** - Management intent for Content Realm

---

## 1. Intent Overview

### Purpose
List artifacts for a tenant and session. Returns artifact metadata (not content) for UI display. Artifacts are workspace-scoped (filtered by user_id, session_id, solution_id) for security.

> **Note:** Current backend implementation uses `list_files`. This contract specifies `list_artifacts` to align with the artifact-centric vocabulary. Backend should be updated to use `list_artifacts`.

### Intent Flow
```
[User navigates to artifact list]
    ↓
[list_artifacts intent]
    ↓
[Query Artifact Index (Supabase)]
    ↓
[Apply workspace scope filter (user_id, session_id)]
    ↓
[Return artifact metadata list]
```

### Expected Observable Artifacts
- `artifacts` - Array of artifact metadata objects
- `count` - Total number of artifacts returned
- `tenant_id` - Tenant identifier
- `session_id` - Session identifier

---

## 2. Intent Parameters

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `tenant_id` | `string` | Tenant identifier | From context |
| `session_id` | `string` | Session identifier | From context |
| `artifact_type` | `string` | Filter by artifact type (file, parsed_content, embeddings) | `null` (no filter) |
| `lifecycle_state` | `string` | Filter by lifecycle state | `"READY"` |
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
    "artifact_list": {
      "result_type": "artifact_list",
      "semantic_payload": {
        "artifacts": [
          {
            "artifact_id": "file_abc123",
            "artifact_type": "file",
            "lifecycle_state": "READY",
            "ui_name": "document.pdf",
            "mime_type": "application/pdf",
            "file_size": 1024000,
            "storage_location": "gs://bucket/path/to/file",
            "created_at": "2026-01-27T10:00:00Z",
            "updated_at": "2026-01-27T10:00:00Z",
            "parent_artifacts": []
          }
        ],
        "count": 1,
        "tenant_id": "tenant_123",
        "session_id": "session_456",
        "limit": 100,
        "offset": 0,
        "artifact_type_filter": null
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
- **Query Source:** Artifact Index (Supabase `artifact_index` table)

---

## 5. Idempotency

### Idempotency Key
N/A - This is a read-only query operation

### Behavior
- Multiple calls return current state of artifacts
- Results may change as artifacts are added/removed
- Safe to retry

---

## 6. Implementation Details

### Handler Location
**Current:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py::ContentOrchestrator._handle_list_files`
**Target:** Rename to `_handle_list_artifacts` for artifact-centric vocabulary

### Key Implementation Steps
1. Extract parameters (tenant_id, session_id, artifact_type, lifecycle_state, limit, offset)
2. Get user_id from context for workspace-scoped filtering
3. Query Artifact Index via Registry Abstraction
4. Transform results to semantic payload format
5. Return structured artifact response

### Dependencies
- **Public Works:** `RegistryAbstraction` (for artifact index queries)
- **Supabase:** `artifact_index` table

### Workspace Scope Security
Artifacts are filtered by workspace scope (user_id + session_id + solution_id) to ensure users only see their own artifacts.

---

## 7. Frontend Integration

### Frontend Usage (ContentAPIManager.ts)
```typescript
// ContentAPIManager.listArtifacts() - to be updated
const executionId = await platformState.submitIntent(
  "list_artifacts",
  {
    tenant_id: platformState.state.session.tenantId,
    session_id: platformState.state.session.sessionId,
    artifact_type: "file",  // optional filter
    lifecycle_state: "READY",  // optional filter
  }
);
```

### Expected Frontend Behavior
1. User navigates to artifact list page
2. Submit `list_artifacts` intent via `submitIntent()`
3. Track execution via `trackExecution()`
4. Wait for execution completion
5. Extract `artifacts` array from execution artifacts
6. Display artifacts in UI (table, grid, etc.)

---

## 8. Error Handling

### Validation Errors
- None expected - all parameters are optional with defaults

### Runtime Errors
- Registry abstraction unavailable → RuntimeError
- Database query failed → RuntimeError
- Database timeout → RuntimeError

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "list_artifacts"
}
```

---

## 9. Testing & Validation

### Happy Path
1. User requests artifact list
2. `list_artifacts` intent executes
3. Artifact Index query succeeds
4. Artifacts returned with metadata
5. UI displays artifact list

### Boundary Violations
- None expected - gracefully handles empty results

### Failure Scenarios
- Artifact Index unavailable → RuntimeError
- Query timeout → RuntimeError

---

## 10. Contract Compliance

### Required Artifacts
- `artifact_list` - Required with artifacts array

### Required Events
- None (read-only operation)

### Security Requirements
- Must filter by workspace scope (user_id)
- Must not expose artifacts from other users/workspaces

---

## 11. Cross-Reference Analysis

### Journey Contract Says
- `list_artifacts` - List artifacts for management
- Artifact-centric vocabulary

### Implementation Does
- ⚠️ Currently uses `list_files` intent type
- ✅ Queries Supabase for artifact metadata
- ✅ Applies workspace scope filter
- ✅ Returns artifact metadata list

### Frontend Expects
- ⚠️ Currently uses `list_files` intent type
- Should be updated to `list_artifacts` for consistency

### Gaps/Discrepancies
- **NAMING:** Backend uses `list_files`, contract specifies `list_artifacts`
- **Recommendation:** Update backend and frontend to use `list_artifacts` for artifact-centric vocabulary consistency

### Migration Path
1. Add `list_artifacts` handler in backend (can alias to existing logic)
2. Update frontend to use `list_artifacts`
3. Deprecate `list_files` over time

---

**Last Updated:** January 27, 2026  
**Owner:** Content Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
