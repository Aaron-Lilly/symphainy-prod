# Intent Contract: archive_file

**Intent:** archive_file  
**Intent Type:** `archive_file`  
**Journey:** File Management (`journey_content_file_management`)  
**Realm:** Content Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🟡 **PRIORITY 2** - Lifecycle management intent for Content Realm

---

## 1. Intent Overview

### Purpose
Archive a file artifact (soft delete). Transitions the file's lifecycle state from READY to ARCHIVED. The file remains in storage but is marked as archived and hidden from normal queries.

### Intent Flow
```
[User requests file archive]
    ↓
[archive_file intent]
    ↓
[Validate file exists in State Surface]
    ↓
[Update metadata to archived status]
    ↓
[Update lifecycle state in State Surface]
    ↓
[Returns archive confirmation]
```

### Expected Observable Artifacts
- `file_id` - Archived file identifier
- `file_reference` - State Surface reference
- `status: "archived"` - New status
- `archived_at` - Timestamp of archive

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `file_id` | `string` | File artifact identifier | Required (or file_reference) |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `file_reference` | `string` | State Surface file reference | Auto-constructed from file_id |
| `reason` | `string` | Archive reason | `"User requested"` |

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
    "file_id": "file_abc123",
    "file_reference": "file:tenant:session:file_abc123",
    "status": "archived",
    "archived_at": "2026-01-27T15:30:00Z"
  },
  "events": [
    {
      "type": "file_archived",
      "file_id": "file_abc123",
      "file_reference": "file:tenant:session:file_abc123",
      "reason": "User requested"
    }
  ]
}
```

### Error Response

```json
{
  "error": "File not found in State Surface",
  "error_code": "NOT_FOUND",
  "execution_id": "exec_abc123"
}
```

---

## 4. Artifact Registration

### State Surface Update
- **Lifecycle Transition:** READY → ARCHIVED
- **Metadata Update:** Add `archived_at`, `archive_reason`, `status: "archived"`
- **Storage:** File remains in GCS (not deleted)

---

## 5. Idempotency

### Idempotency Key
```
archive_fingerprint = hash(file_id + tenant_id)
```

### Scope
- Per file, per tenant
- Multiple archive requests for same file are idempotent

### Behavior
- If file already archived, returns success with existing archived_at
- No duplicate archive operations
- Safe to retry

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/content/orchestrators/content_orchestrator.py::ContentOrchestrator._handle_archive_file`

### Key Implementation Steps
1. Validate `file_id` or `file_reference` (at least one required)
2. Construct `file_reference` if not provided
3. Get file metadata from State Surface
4. Validate storage location exists
5. Update metadata with archive status:
   - `status: "archived"`
   - `archived_at: <timestamp>`
   - `archive_reason: <reason>`
6. Store updated metadata in State Surface
7. Return confirmation

### Dependencies
- **State Surface:** `get_file_metadata()`, `store_file_reference()`
- **Supabase:** Optional update to file index

---

## 7. Frontend Integration

### Frontend Usage
Not directly exposed in ContentAPIManager.ts. Could be added for file management UI.

### Expected Frontend Behavior
1. User selects file to archive
2. User confirms archive action
3. Submit `archive_file` intent
4. Track execution
5. Update UI to remove/hide file from list

---

## 8. Error Handling

### Validation Errors
- Neither `file_id` nor `file_reference` provided → ValueError
- File not found → ValueError
- Storage location not found → ValueError

### Runtime Errors
- State Surface unavailable → RuntimeError
- Metadata update failed → RuntimeError

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "archive_file"
}
```

---

## 9. Testing & Validation

### Happy Path
1. User requests file archive
2. `archive_file` intent executes
3. File metadata updated
4. Lifecycle state changed to ARCHIVED
5. Returns archive confirmation
6. File no longer appears in normal queries

### Boundary Violations
- Missing file_id and file_reference → Validation error
- File not found → Not found error

### Failure Scenarios
- State Surface unavailable → RuntimeError
- Metadata update failure → RuntimeError

---

## 10. Contract Compliance

### Required Artifacts
- Archive confirmation with file_id, status, archived_at - Required

### Required Events
- `file_archived` - Required

### Lifecycle State
- Must transition artifact from READY → ARCHIVED
- Must NOT delete file from storage (soft delete)

### Audit Trail
- Must record archive reason
- Must record archived_at timestamp

---

## 11. Cross-Reference Analysis

### Journey Contract Says
- Archive file for lifecycle management
- Soft delete (file remains recoverable)

### Implementation Does
- ✅ Validates file exists
- ✅ Updates metadata with archive status
- ✅ Preserves file in storage (soft delete)
- ✅ Records archive reason and timestamp

### Frontend Expects
- Not directly used by frontend (could be added)

### Gaps/Discrepancies
- Frontend doesn't currently expose archive functionality
- **Recommendation:** Add archive button to file management UI when needed

---

## 12. Related Intents

### purge_file
Hard delete - permanently removes file from storage. Requires archived state first.

### restore_file
Restore archived file - transitions from ARCHIVED back to READY.

---

**Last Updated:** January 27, 2026  
**Owner:** Content Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
