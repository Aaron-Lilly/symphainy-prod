# Intent Contract: retrieve_artifact_metadata

**Intent:** retrieve_artifact_metadata  
**Intent Type:** `retrieve_artifact_metadata`  
**Journey:** File Management (`journey_content_file_management`)  
**Realm:** Content Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🟡 **PRIORITY 2** - Management intent for Content Realm

---

## 1. Intent Overview

### Purpose
Retrieve metadata for an artifact from the Artifact Index. This is a discovery operation that returns artifact metadata only (not content). For full artifact content, use `retrieve_artifact`.

> **Note:** Original journey contract specified `get_artifact_metadata`. This contract uses `retrieve_artifact_metadata` to align with the actual implementation.

### Intent Flow
```
[User requests artifact details]
    ↓
[retrieve_artifact_metadata intent]
    ↓
[Query Artifact Index (Supabase artifact_index)]
    ↓
[Return artifact metadata]
```

### Expected Observable Artifacts
- `artifact_id` - Artifact identifier
- `artifact_type` - Type of artifact (file, parsed_content, embeddings, etc.)
- `lifecycle_state` - Current lifecycle state
- `semantic_descriptor` - Semantic metadata
- `parent_artifacts` - Lineage information

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `artifact_id` | `string` | Artifact identifier | Required, must exist |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `artifact_type` | `string` | Artifact type filter | `"file"` |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "artifact_metadata": {
      "result_type": "artifact_metadata",
      "semantic_payload": {
        "artifact_id": "file_abc123",
        "artifact_type": "file",
        "lifecycle_state": "READY",
        "created_at": "2026-01-27T10:00:00Z",
        "updated_at": "2026-01-27T10:00:00Z",
        "semantic_descriptor": {
          "schema": "file_v1",
          "record_count": null,
          "parser_type": "pdf",
          "embedding_model": null
        },
        "parent_artifacts": []
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
  "error": "Artifact not found in Artifact Index",
  "error_code": "NOT_FOUND",
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
- Multiple calls return current metadata
- Metadata may change as artifact lifecycle progresses
- Safe to retry

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/content/orchestrators/handlers/artifact_management_handlers.py::ArtifactManagementHandlers.handle_retrieve_artifact_metadata`

### Key Implementation Steps
1. Validate `artifact_id` (required)
2. Get Public Works `RegistryAbstraction`
3. Query `artifact_index` table via `registry_abstraction.get_artifact_metadata()`
4. Transform results to semantic payload format
5. Return structured artifact response

### Dependencies
- **Public Works:** `RegistryAbstraction` (for artifact index queries)
- **Supabase:** `artifact_index` table

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// Direct API call (not via submitIntent) - see listArtifacts()
const response = await fetch('/api/artifact/list', {
  method: 'POST',
  body: JSON.stringify({
    tenant_id: tenantId,
    artifact_type: 'file',
    lifecycle_state: 'READY',
  }),
});
```

### Expected Frontend Behavior
1. User requests artifact details
2. Query artifact metadata
3. Display metadata in UI (type, state, lineage, etc.)

---

## 8. Error Handling

### Validation Errors
- `artifact_id` missing → ValueError

### Runtime Errors
- Public Works not initialized → RuntimeError
- RegistryAbstraction not available → RuntimeError
- Artifact not found → ValueError

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "retrieve_artifact_metadata"
}
```

---

## 9. Testing & Validation

### Happy Path
1. User requests artifact metadata
2. `retrieve_artifact_metadata` intent executes
3. Artifact found in index
4. Metadata returned
5. UI displays artifact details

### Boundary Violations
- Missing `artifact_id` → Validation error
- Artifact not found → Not found error

### Failure Scenarios
- Registry abstraction unavailable → RuntimeError
- Supabase unavailable → RuntimeError

---

## 10. Contract Compliance

### Required Artifacts
- `artifact_metadata` - Required

### Required Events
- None (read-only operation)

### Access Control
- Must validate tenant access (artifact belongs to tenant)

---

## 11. Cross-Reference Analysis

### Journey Contract Says
- Original contract specified `get_artifact_metadata`
- Purpose: Get metadata for artifact management

### Implementation Does
- ✅ Uses intent type `retrieve_artifact_metadata`
- ✅ Queries Artifact Index via RegistryAbstraction
- ✅ Returns artifact metadata with semantic_descriptor and lineage

### Frontend Expects
- Frontend uses direct API call (`/api/artifact/list`) rather than intent
- Could be migrated to intent-based pattern for consistency

### Gaps/Discrepancies
- **NAMING:** Journey contract says `get_artifact_metadata`, implementation uses `retrieve_artifact_metadata`
- **Recommendation:** Standardize on `retrieve_artifact_metadata` (matches REST conventions)

---

**Last Updated:** January 27, 2026  
**Owner:** Content Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
