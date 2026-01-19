# Backend Testing Plan: Two-Phase Materialization Flow

## Overview

This document outlines how to test the new two-phase materialization flow:
1. **Upload** → Creates boundary contract (pending materialization)
2. **Save** → Authorizes materialization (active) and registers in materialization index

## Prerequisites

1. **Run SQL Migrations**:
   ```bash
   # Run in order:
   - 003_create_data_boundary_contracts.sql
   - 004_add_boundary_contracts_to_materializations.sql
   - 005_create_default_boundary_contracts_for_existing_data.sql
   - 006_update_existing_contracts_with_workspace_scope.sql
   ```

2. **Start Services**:
   - Runtime service
   - Supabase (for boundary contracts and materialization index)
   - GCS (for file storage)

## Test Scenarios

### Test 1: Upload File (Phase 1 - Pending Materialization)

**Endpoint**: `POST /api/intent/submit`

**Request**:
```json
{
  "tenant_id": "test_tenant",
  "intent_type": "ingest_file",
  "parameters": {
    "ingestion_type": "upload",
    "file_content": "<hex-encoded-file-content>",
    "ui_name": "test_file.csv",
    "file_type": "structured",
    "mime_type": "text/csv"
  }
}
```

**Headers**:
```
X-User-ID: test_user
X-Session-ID: test_session_123
```

**Expected Result**:
- ✅ Execution succeeds
- ✅ Boundary contract created with `contract_status='pending'` and `materialization_allowed=false`
- ✅ File uploaded to GCS
- ✅ Response includes `boundary_contract_id` and `materialization_pending: true`
- ✅ File NOT yet in materialization index (project_files with boundary_contract_id)

**Verify**:
```sql
-- Check boundary contract
SELECT contract_id, contract_status, materialization_allowed, materialization_scope, reference_scope
FROM data_boundary_contracts
WHERE external_source_identifier LIKE '%test_file.csv%'
ORDER BY created_at DESC
LIMIT 1;

-- Should show:
-- contract_status: 'pending'
-- materialization_allowed: false
-- materialization_scope: NULL or {}
-- reference_scope: NULL or {}
```

### Test 2: Save Materialization (Phase 2 - Authorize Materialization)

**Endpoint**: `POST /api/content/save_materialization`

**Request**:
```json
{
  "boundary_contract_id": "<contract_id_from_test_1>",
  "file_id": "<file_id_from_test_1>",
  "tenant_id": "test_tenant"
}
```

**Headers**:
```
X-User-ID: test_user
X-Session-ID: test_session_123
```

**Expected Result**:
- ✅ Execution succeeds
- ✅ Boundary contract updated: `contract_status='active'`, `materialization_allowed=true`
- ✅ Workspace scope set: `materialization_scope` and `reference_scope` populated
- ✅ File registered in materialization index (project_files with boundary_contract_id)
- ✅ Response indicates file is "saved and available for parsing"

**Verify**:
```sql
-- Check boundary contract updated
SELECT contract_id, contract_status, materialization_allowed, 
       materialization_scope, reference_scope, materialization_type
FROM data_boundary_contracts
WHERE contract_id = '<contract_id_from_test_1>';

-- Should show:
-- contract_status: 'active'
-- materialization_allowed: true
-- materialization_scope: {"user_id": "test_user", "session_id": "test_session_123", "scope_type": "workspace"}
-- reference_scope: {"users": ["test_user"], "scope_type": "workspace"}
-- materialization_type: 'full_artifact'

-- Check materialization index
SELECT uuid, boundary_contract_id, representation_type, materialization_scope
FROM project_files
WHERE uuid = '<file_id_from_test_1>';

-- Should show:
-- boundary_contract_id: <contract_id>
-- representation_type: 'full_artifact'
```

### Test 3: List Files (Workspace Scope Filtering)

**Endpoint**: `POST /api/intent/submit`

**Request**:
```json
{
  "tenant_id": "test_tenant",
  "intent_type": "list_files",
  "parameters": {}
}
```

**Headers**:
```
X-User-ID: test_user
X-Session-ID: test_session_123
```

**Expected Result**:
- ✅ Only returns files where:
  - `boundary_contract_id IS NOT NULL` (saved files only)
  - `reference_scope->>'users'` contains current user_id
- ✅ File from Test 2 appears in list
- ✅ File from Test 1 (if not saved) does NOT appear

### Test 4: Parse File (Requires Saved File)

**Endpoint**: `POST /api/intent/submit`

**Request**:
```json
{
  "tenant_id": "test_tenant",
  "intent_type": "parse_content",
  "parameters": {
    "file_id": "<file_id_from_test_2>",
    "file_reference": "file:test_tenant:test_session_123:<file_id>"
  }
}
```

**Expected Result**:
- ✅ Parsing succeeds (file is saved and available)
- ✅ Parsed content returned

### Test 5: Upload Without Save (Should Not Appear in List)

**Steps**:
1. Upload file (Test 1)
2. List files (Test 3)
3. Verify uploaded file does NOT appear (not saved yet)

### Test 6: Delete File (Remove Materialization)

**Endpoint**: `POST /api/intent/submit` (or direct delete endpoint if exists)

**Expected Result**:
- ✅ Materialization removed (boundary contract revoked or materialization_allowed=false)
- ✅ File marked as deleted in materialization index
- ✅ File no longer appears in list
- ✅ Source data in GCS may remain (depending on purge policy)

## Error Cases to Test

### Error 1: Save Without Upload
- Try to save with invalid `boundary_contract_id`
- Expected: Error - contract not found

### Error 2: Save Twice
- Save same file twice
- Expected: Should be idempotent (no error, same result)

### Error 3: List Files Different User
- Upload and save file as user A
- List files as user B
- Expected: File does NOT appear (workspace scope filtering)

## Manual Testing Commands

### Using curl:

```bash
# 1. Upload file
curl -X POST http://localhost:8000/api/intent/submit \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test_user" \
  -H "X-Session-ID: test_session_123" \
  -d '{
    "tenant_id": "test_tenant",
    "intent_type": "ingest_file",
    "parameters": {
      "ingestion_type": "upload",
      "file_content": "48656c6c6f20576f726c64",  # "Hello World" in hex
      "ui_name": "test.txt",
      "file_type": "unstructured",
      "mime_type": "text/plain"
    }
  }'

# Extract boundary_contract_id and file_id from response

# 2. Save materialization
curl -X POST http://localhost:8000/api/content/save_materialization \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test_user" \
  -H "X-Session-ID: test_session_123" \
  -d '{
    "boundary_contract_id": "<contract_id>",
    "file_id": "<file_id>",
    "tenant_id": "test_tenant"
  }'

# 3. List files
curl -X POST http://localhost:8000/api/intent/submit \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test_user" \
  -H "X-Session-ID: test_session_123" \
  -d '{
    "tenant_id": "test_tenant",
    "intent_type": "list_files",
    "parameters": {}
  }'
```

## Database Verification Queries

```sql
-- Check all boundary contracts
SELECT 
    contract_id,
    contract_status,
    materialization_allowed,
    materialization_type,
    materialization_scope,
    reference_scope,
    created_at
FROM data_boundary_contracts
ORDER BY created_at DESC
LIMIT 10;

-- Check materializations (saved files)
SELECT 
    uuid,
    ui_name,
    boundary_contract_id,
    representation_type,
    user_id,
    created_at
FROM project_files
WHERE deleted = false
  AND boundary_contract_id IS NOT NULL
ORDER BY created_at DESC
LIMIT 10;

-- Check workspace scope filtering
SELECT 
    pf.uuid,
    pf.ui_name,
    dbc.reference_scope
FROM project_files pf
JOIN data_boundary_contracts dbc ON pf.boundary_contract_id = dbc.contract_id
WHERE pf.deleted = false
  AND dbc.reference_scope->>'users' @> '["test_user"]'::jsonb;
```

## Success Criteria

✅ Upload creates pending boundary contract
✅ Save authorizes materialization with workspace scope
✅ List files filters by workspace scope
✅ Files only available for parsing after save
✅ Migration updates existing data correctly
✅ No breaking changes to existing functionality (backwards compatible)

## Known Issues / Notes

1. **Schema Migration**: If `boundary_contract_id` column doesn't exist in `project_files` yet, the `register_materialization` method will log a warning but continue (materialization is authorized, just not registered in index).

2. **Backwards Compatibility**: Existing files (created before this change) will be migrated to have default boundary contracts with workspace scope.

3. **Error Handling**: If Supabase is unavailable, materialization authorization still succeeds (authorized in contract), but registration in index may fail gracefully.

## Next Steps After Testing

1. If all tests pass → Proceed with frontend implementation
2. If issues found → Fix backend issues first
3. Document any edge cases or additional error handling needed
