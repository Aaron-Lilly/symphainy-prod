# Quick Test Guide: Two-Phase Materialization

## Prerequisites

✅ All migrations run in Supabase
✅ Runtime service running on `http://localhost:8000`
✅ Services connected (Supabase, GCS, etc.)

## Quick Test (Using Test Script)

```bash
# Run the automated test script
python test_two_phase_materialization.py
```

This will test:
1. Upload file → Creates pending boundary contract
2. Save materialization → Authorizes with workspace scope
3. List files → Filters by workspace scope

## Manual Test (Using curl)

### Step 1: Upload File

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

**Expected**: Response includes `execution_id`. Get status to find `boundary_contract_id` and `file_id`.

### Step 2: Get Execution Status

```bash
# Use execution_id from Step 1
curl "http://localhost:8000/api/execution/{execution_id}/status?tenant_id=test_tenant"
```

**Look for**:
- `artifacts.file.semantic_payload.boundary_contract_id`
- `artifacts.file.semantic_payload.file_id`
- `artifacts.file.semantic_payload.materialization_pending: true`

### Step 3: Save Materialization

```bash
# Use boundary_contract_id and file_id from Step 2
curl -X POST http://localhost:8000/api/content/save_materialization \
  -H "Content-Type: application/json" \
  -H "x-user-id: test_user" \
  -H "x-session-id: test_session_123" \
  -d '{
    "boundary_contract_id": "YOUR_CONTRACT_ID",
    "file_id": "YOUR_FILE_ID",
    "tenant_id": "test_tenant"
  }'
```

**Expected**: `{"success": true, "message": "File saved and available for parsing"}`

### Step 4: List Files

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

**Expected**: Saved file appears in list (only saved files, filtered by workspace scope)

## Database Verification

Run in Supabase SQL Editor:

```sql
-- Check boundary contract was created and updated
SELECT 
    contract_id,
    contract_status,
    materialization_allowed,
    materialization_scope,
    reference_scope,
    created_at,
    activated_at
FROM data_boundary_contracts
ORDER BY created_at DESC
LIMIT 5;

-- Check materialization was registered
SELECT 
    uuid,
    ui_name,
    boundary_contract_id,
    representation_type,
    materialization_scope,
    created_at
FROM project_files
WHERE deleted = false
  AND boundary_contract_id IS NOT NULL
ORDER BY created_at DESC
LIMIT 5;
```

## Expected Results

### After Upload (Phase 1):
- ✅ Boundary contract created with `contract_status='pending'`
- ✅ `materialization_allowed=false`
- ✅ `materialization_scope` and `reference_scope` are NULL or empty
- ✅ File uploaded to GCS
- ✅ File NOT in materialization index yet

### After Save (Phase 2):
- ✅ Boundary contract updated: `contract_status='active'`
- ✅ `materialization_allowed=true`
- ✅ `materialization_scope` populated: `{"user_id": "...", "session_id": "...", "scope_type": "workspace"}`
- ✅ `reference_scope` populated: `{"users": ["..."], "scope_type": "workspace"}`
- ✅ File registered in `project_files` with `boundary_contract_id`

### After List (Phase 3):
- ✅ Only files with `boundary_contract_id IS NOT NULL` appear
- ✅ Only files where `reference_scope->>'users'` contains current user_id
- ✅ Saved file appears in list

## Troubleshooting

### Issue: "boundary_contract_id column does not exist"
**Solution**: Run migration 004: `004_add_boundary_contracts_to_materializations.sql`

### Issue: "data_boundary_contracts table does not exist"
**Solution**: Run migration 003: `003_create_data_boundary_contracts.sql`

### Issue: "Header x-user-id not found"
**Solution**: Check header case - should be lowercase: `x-user-id` not `X-User-ID`

### Issue: "Materialization not authorized"
**Solution**: Check that boundary contract exists and access was granted

### Issue: "File not appearing in list"
**Solution**: 
- Verify file was saved (boundary_contract_id in project_files)
- Check reference_scope includes current user_id
- Verify user_id matches in list_files request

## Next Steps

If all tests pass:
- ✅ Backend implementation is working
- ✅ Proceed with frontend implementation
- ✅ Update UI to show "Save" step

If tests fail:
- Check logs for specific errors
- Verify migrations ran successfully
- Check database state with SQL queries above
