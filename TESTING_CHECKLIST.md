# Backend Testing Checklist

## Pre-Testing Setup

- [ ] Run SQL migrations in order:
  - [ ] `003_create_data_boundary_contracts.sql`
  - [ ] `004_add_boundary_contracts_to_materializations.sql`
  - [ ] `005_create_default_boundary_contracts_for_existing_data.sql`
  - [ ] `006_update_existing_contracts_with_workspace_scope.sql`

- [ ] Verify services are running:
  - [ ] Runtime service
  - [ ] Supabase
  - [ ] GCS (or GCS adapter configured)

## Quick Test Sequence

### 1. Upload File (Phase 1)
```bash
curl -X POST http://localhost:8000/api/intent/submit \
  -H "Content-Type: application/json" \
  -H "x-user-id: test_user" \
  -H "x-session-id: test_session_123" \
  -d '{
    "tenant_id": "test_tenant",
    "intent_type": "ingest_file",
    "parameters": {
      "ingestion_type": "upload",
      "file_content": "48656c6c6f20576f726c64",
      "ui_name": "test.txt",
      "file_type": "unstructured",
      "mime_type": "text/plain"
    }
  }'
```

**Check**:
- [ ] Response includes `boundary_contract_id`
- [ ] Response includes `materialization_pending: true`
- [ ] File uploaded to GCS
- [ ] Boundary contract created in DB with `contract_status='pending'`

### 2. Save Materialization (Phase 2)
```bash
# Use boundary_contract_id and file_id from step 1
curl -X POST http://localhost:8000/api/content/save_materialization \
  -H "Content-Type: application/json" \
  -H "x-user-id: test_user" \
  -H "x-session-id: test_session_123" \
  -d '{
    "boundary_contract_id": "<from_step_1>",
    "file_id": "<from_step_1>",
    "tenant_id": "test_tenant"
  }'
```

**Check**:
- [ ] Response indicates success
- [ ] Boundary contract updated: `contract_status='active'`, `materialization_allowed=true`
- [ ] Workspace scope set in contract
- [ ] File registered in `project_files` with `boundary_contract_id`

### 3. List Files
```bash
curl -X POST http://localhost:8000/api/intent/submit \
  -H "Content-Type: application/json" \
  -H "x-user-id: test_user" \
  -H "x-session-id: test_session_123" \
  -d '{
    "tenant_id": "test_tenant",
    "intent_type": "list_files",
    "parameters": {}
  }'
```

**Check**:
- [ ] Saved file appears in list
- [ ] Unsaved files do NOT appear
- [ ] Only files scoped to current user appear

## Database Verification

```sql
-- Check boundary contracts
SELECT contract_id, contract_status, materialization_allowed, 
       materialization_scope, reference_scope
FROM data_boundary_contracts
ORDER BY created_at DESC
LIMIT 5;

-- Check materializations
SELECT uuid, ui_name, boundary_contract_id, representation_type
FROM project_files
WHERE deleted = false AND boundary_contract_id IS NOT NULL
ORDER BY created_at DESC
LIMIT 5;
```

## Expected Behavior

✅ Upload creates pending contract (not materialized yet)
✅ Save authorizes materialization with workspace scope
✅ List only shows saved files (filtered by scope)
✅ Files available for parsing only after save

## Issues to Watch For

- [ ] Header case sensitivity (x-user-id vs X-User-ID)
- [ ] Missing boundary_contract_id column in project_files (migration needed)
- [ ] Supabase connection issues
- [ ] Context not passed correctly to authorize_materialization

## Next Steps

If all tests pass → Proceed with frontend implementation
If issues found → Fix backend issues first
