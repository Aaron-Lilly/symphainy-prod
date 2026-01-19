# MVP Refactoring Plan: Simpler Approach with Explicit Save

## Overview

This plan implements workspace-scoped materialization using the existing boundary contract scope system, with an explicit "Save" step in the UI to make materialization decisions visible to users.

## Core Principle

**Use existing scope system. No special modes. Realms work with authorized representations. Materialization is explicit.**

---

## Architecture Flow

### Current (Implicit)
```
Upload → Automatic Materialization → Available for Parsing
```

### New (Explicit)
```
Upload → Boundary Contract Created (pending materialization)
   ↓
User Clicks "Save" → Materialization Authorized → Available for Parsing
```

**Key Change**: Materialization becomes an explicit user action, making the boundary contract visible.

---

## Implementation Plan

### Phase 1: Backend - Scope-Based Materialization

#### 1.1 Update Data Steward Primitives
**File**: `symphainy_platform/civic_systems/smart_city/primitives/data_steward_primitives.py`

**Change**: Extend `authorize_materialization()` to accept context and set scope:

```python
async def authorize_materialization(
    self,
    contract_id: str,
    tenant_id: str,
    requested_type: Optional[str] = None,
    materialization_policy: Optional[Any] = None,
    context: Optional[Dict[str, Any]] = None  # ADD THIS
) -> MaterializationAuthorization:
    """
    Authorize materialization - decide what form and where.
    
    Args:
        contract_id: Boundary contract ID
        tenant_id: Tenant identifier
        requested_type: Requested materialization type
        materialization_policy: MaterializationPolicyStore
        context: Execution context with user_id, session_id, solution_id  # NEW
    """
    # ... existing contract retrieval code ...
    
    # Set materialization_scope from context (for MVP: workspace-scoped)
    materialization_scope = {}
    reference_scope = {}
    
    if context:
        user_id = context.get("user_id")
        session_id = context.get("session_id")
        solution_id = context.get("solution_id")
        
        materialization_scope = {
            "user_id": user_id,
            "session_id": session_id,
            "solution_id": solution_id,
            "scope_type": "workspace"  # MVP default
        }
        
        reference_scope = {
            "users": [user_id] if user_id else [],
            "scope_type": "workspace"
        }
    
    # ... existing materialization decision logic ...
    
    # Update contract with scope
    if self.boundary_contract_store:
        try:
            await self.boundary_contract_store.update_boundary_contract(
                contract_id=contract_id,
                tenant_id=tenant_id,
                updates={
                    "materialization_allowed": True,
                    "materialization_type": materialization_type,
                    "materialization_scope": materialization_scope,  # ADD THIS
                    "reference_scope": reference_scope,  # ADD THIS
                    "materialization_backing_store": materialization_backing_store,
                    "materialization_ttl": ttl_interval,
                    "materialization_expires_at": materialization_expires_at,
                    "materialization_policy_basis": policy_basis,
                    "contract_status": "active",
                    "activated_at": self.clock.now_iso()
                }
            )
        except Exception as e:
            self.logger.error(f"Failed to update boundary contract: {e}", exc_info=True)
    
    return MaterializationAuthorization(
        materialization_allowed=True,
        materialization_type=materialization_type,
        materialization_scope=materialization_scope,  # ADD THIS
        materialization_backing_store=materialization_backing_store,
        materialization_ttl=materialization_ttl,
        policy_basis=policy_basis,
        reason=f"Materialization authorized: {materialization_type}"
    )
```

**Rationale**: Use existing `materialization_scope` and `reference_scope` fields. No schema changes needed.

#### 1.2 Update ExecutionLifecycleManager - Two-Phase Flow
**File**: `symphainy_platform/runtime/execution_lifecycle_manager.py`

**Change**: Split boundary contract enforcement into two phases:

**Phase 1: Upload (request_data_access only)**
- For `ingest_file` intent: Only request data access, don't authorize materialization yet
- Create boundary contract with `contract_status='pending'` and `materialization_allowed=false`
- Return contract_id to frontend

**Phase 2: Save (authorize_materialization)**
- For new `save_materialization` intent: Authorize materialization with workspace scope
- Update contract to `contract_status='active'` and `materialization_allowed=true`
- Set workspace scope from context

```python
# In execute_intent() method, for ingest_file:
if intent.intent_type == "ingest_file" and self.data_steward_sdk:
    # Phase 1: Request access only (don't materialize yet)
    access_request = await self.data_steward_sdk.request_data_access(
        intent={...},
        context={...},
        external_source_type="file",
        external_source_identifier=f"upload:{intent.intent_id}:{intent.parameters.get('ui_name', 'unknown')}",
        external_source_metadata={...}
    )
    
    if not access_request.access_granted:
        raise ValueError(f"Data access denied: {access_request.access_reason}")
    
    # Store contract_id in context, but DON'T authorize materialization yet
    context.metadata["boundary_contract_id"] = access_request.contract_id
    context.metadata["materialization_pending"] = True  # NEW FLAG
    
    # Continue with ingestion (file uploaded but not materialized)

# For new save_materialization intent:
if intent.intent_type == "save_materialization" and self.data_steward_sdk:
    contract_id = intent.parameters.get("boundary_contract_id")
    if not contract_id:
        raise ValueError("boundary_contract_id is required for save_materialization")
    
    # Phase 2: Authorize materialization with workspace scope
    materialization_auth = await self.data_steward_sdk.authorize_materialization(
        contract_id=contract_id,
        tenant_id=intent.tenant_id,
        context={
            "user_id": context.metadata.get("user_id"),
            "session_id": context.session_id,
            "solution_id": context.metadata.get("solution_id")
        },
        materialization_policy=self.materialization_policy_store
    )
    
    if not materialization_auth.materialization_allowed:
        raise ValueError(f"Materialization not authorized: {materialization_auth.reason}")
    
    # Store materialization info in context
    context.metadata["boundary_contract_id"] = contract_id
    context.metadata["materialization_type"] = materialization_auth.materialization_type
    context.metadata["materialization_scope"] = materialization_auth.materialization_scope
    context.metadata["materialization_backing_store"] = materialization_auth.materialization_backing_store
```

**Rationale**: Two-phase flow makes materialization explicit. Upload creates contract, Save authorizes materialization.

#### 1.3 Update Content Realm - Handle Pending Materialization
**File**: `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

**Change**: Update `_handle_ingest_file()` to handle pending materialization:

```python
async def _handle_ingest_file(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    # ... existing ingestion code ...
    
    # Check if materialization is pending
    materialization_pending = context.metadata.get("materialization_pending", False)
    boundary_contract_id = context.metadata.get("boundary_contract_id")
    
    # Create structured artifact
    semantic_payload = {
        "file_id": ingestion_result.file_id,
        "file_reference": file_reference,
        "boundary_contract_id": boundary_contract_id,
        "materialization_pending": materialization_pending,  # NEW
        "storage_location": ingestion_result.storage_location,
        "ui_name": ui_name,
        # ... rest of payload
    }
    
    # If materialization is pending, don't store in materialization index yet
    if not materialization_pending:
        # Materialization already authorized, include scope
        semantic_payload["materialization_type"] = context.metadata.get("materialization_type")
        semantic_payload["materialization_scope"] = context.metadata.get("materialization_scope")
        semantic_payload["materialization_backing_store"] = context.metadata.get("materialization_backing_store")
    
    structured_artifact = create_structured_artifact(
        result_type="file",
        semantic_payload=semantic_payload,
        renderings={}
    )
    
    return {
        "artifacts": {
            "file": structured_artifact
        },
        "events": [...]
    }
```

**Add new handler for save_materialization**:

```python
async def _handle_save_materialization(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Handle save_materialization intent - explicitly authorize materialization.
    
    Intent parameters:
    - boundary_contract_id: str (REQUIRED) - Boundary contract from upload
    - file_id: str (REQUIRED) - File ID from upload
    """
    boundary_contract_id = intent.parameters.get("boundary_contract_id")
    file_id = intent.parameters.get("file_id")
    
    if not boundary_contract_id or not file_id:
        raise ValueError("boundary_contract_id and file_id are required")
    
    # Materialization authorization already happened in ExecutionLifecycleManager
    # We just need to register it in the materialization index
    
    materialization_type = context.metadata.get("materialization_type", "full_artifact")
    materialization_scope = context.metadata.get("materialization_scope", {})
    materialization_backing_store = context.metadata.get("materialization_backing_store", "gcs")
    
    # Get file metadata from state surface
    file_metadata = await context.state_surface.get_file_metadata(
        session_id=context.session_id,
        tenant_id=context.tenant_id,
        file_reference=f"file:{context.tenant_id}:{context.session_id}:{file_id}"
    )
    
    # Register in materialization index (Supabase project_files)
    # This is where the file becomes "saved" and available for parsing
    if self.public_works:
        file_storage = self.public_works.get_file_storage_abstraction()
        if file_storage:
            # Update or create materialization record
            await file_storage.register_materialization(
                file_id=file_id,
                boundary_contract_id=boundary_contract_id,
                materialization_type=materialization_type,
                materialization_scope=materialization_scope,
                materialization_backing_store=materialization_backing_store,
                tenant_id=context.tenant_id,
                user_id=context.metadata.get("user_id"),
                session_id=context.session_id,
                metadata=file_metadata
            )
    
    return {
        "artifacts": {
            "materialization": {
                "boundary_contract_id": boundary_contract_id,
                "file_id": file_id,
                "materialization_type": materialization_type,
                "materialization_scope": materialization_scope,
                "status": "saved"
            }
        },
        "events": [
            {
                "type": "materialization_saved",
                "file_id": file_id,
                "boundary_contract_id": boundary_contract_id,
                "materialization_type": materialization_type
            }
        ]
    }
```

**Rationale**: Upload creates contract but doesn't materialize. Save explicitly authorizes and registers materialization.

#### 1.4 Update File Storage Abstraction - Register Materialization
**File**: `symphainy_platform/foundations/public_works/abstractions/file_storage_abstraction.py`

**Add method**:

```python
async def register_materialization(
    self,
    file_id: str,
    boundary_contract_id: str,
    materialization_type: str,
    materialization_scope: Dict[str, Any],
    materialization_backing_store: str,
    tenant_id: str,
    user_id: str,
    session_id: str,
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Register materialization in materialization index (Supabase project_files).
    
    This is called when user explicitly saves a file, making it available for parsing.
    """
    # Implementation: Insert/update project_files with boundary_contract_id and scope
    # This is the "save" operation that makes the file available
```

**Rationale**: Explicit registration of materialization in the index.

---

### Phase 2: Backend - API Updates

#### 2.1 Add Save Materialization Endpoint
**File**: `runtime_main.py` or `symphainy_platform/runtime/runtime_api.py`

**Add endpoint**:

```python
@app.post("/api/content/save_materialization")
async def save_materialization(
    boundary_contract_id: str,
    file_id: str,
    tenant_id: str,
    user_id: str = Header(...),
    session_id: str = Header(...)
):
    """
    Explicitly save (materialize) a file that was uploaded.
    
    This is the second step after upload:
    1. Upload → creates boundary contract (pending)
    2. Save → authorizes materialization (active)
    """
    intent = Intent(
        intent_type="save_materialization",
        tenant_id=tenant_id,
        parameters={
            "boundary_contract_id": boundary_contract_id,
            "file_id": file_id
        }
    )
    
    context = ExecutionContext(
        tenant_id=tenant_id,
        session_id=session_id,
        metadata={"user_id": user_id}
    )
    
    result = await execution_lifecycle_manager.execute(intent)
    return result
```

#### 2.2 Update List Files API - Filter by Scope
**File**: API endpoint for listing files

**Change**: Filter by `reference_scope`:

```python
@app.get("/api/content/files")
async def list_files(
    tenant_id: str,
    user_id: str = Header(...),
    session_id: str = Header(...)
):
    """
    List materialized files (saved files) for current user.
    
    Only returns files where reference_scope includes current user_id.
    """
    # Query project_files where:
    # 1. boundary_contract_id exists (file is saved/materialized)
    # 2. reference_scope->>'users' contains current user_id
    # OR query via boundary_contracts table and join
    
    # Implementation: Filter by workspace scope
    files = await file_storage.list_materializations(
        tenant_id=tenant_id,
        user_id=user_id,
        session_id=session_id
    )
    return files
```

**Rationale**: Only show files that user has access to (workspace-scoped).

#### 2.3 Update Delete API - Remove Materialization
**File**: API endpoint for deleting files

**Change**: Delete removes materialization, not source:

```python
@app.delete("/api/content/files/{file_id}")
async def delete_file(
    file_id: str,
    tenant_id: str,
    user_id: str = Header(...)
):
    """
    Delete a materialized file (remove from workspace).
    
    This removes the materialization, not the source data.
    """
    # Implementation:
    # 1. Get boundary_contract_id from materialization index
    # 2. Update boundary contract: materialization_allowed=false, contract_status='revoked'
    # 3. Mark materialization as deleted in project_files
    # 4. Optionally purge from backing store if TTL expired
```

**Rationale**: Delete removes workspace materialization, source stays external.

---

### Phase 3: Frontend - Explicit Save Flow

#### 3.1 Update FileUploader Component
**File**: `frontend/components/content/FileUploader.tsx`

**Change**: Two-phase upload flow:

```typescript
// Phase 1: Upload
const handleUpload = async (file: File) => {
  // Upload file (creates boundary contract, pending materialization)
  const uploadResult = await uploadFile(file);
  
  // Store boundary_contract_id and file_id
  setUploadedFile({
    boundary_contract_id: uploadResult.boundary_contract_id,
    file_id: uploadResult.file_id,
    ui_name: file.name,
    materialization_pending: true
  });
  
  // Show "Save" button instead of immediate success
  setShowSaveButton(true);
};

// Phase 2: Save
const handleSave = async () => {
  if (!uploadedFile) return;
  
  // Explicitly save (authorize materialization)
  await saveMaterialization(
    uploadedFile.boundary_contract_id,
    uploadedFile.file_id
  );
  
  // File is now saved and available for parsing
  setShowSaveButton(false);
  toast.success("File saved and available for parsing");
  
  // Refresh file list
  onFileSaved?.();
};
```

**UI Changes**:
- After upload: Show "File uploaded. Click 'Save' to make it available for parsing."
- Show "Save" button with note: "Files must be saved for parsing and other activities (MVP requirement)"
- After save: Show success message

#### 3.2 Add Save Materialization API Call
**File**: `frontend/lib/api/fms.ts` or similar

**Add function**:

```typescript
export async function saveMaterialization(
  boundary_contract_id: string,
  file_id: string,
  token: string
): Promise<{ success: boolean; file_id: string }> {
  const response = await fetch(`${API_BASE_URL}/api/content/save_materialization`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      'X-Tenant-ID': getTenantId(),
      'X-User-ID': getUserId(),
      'X-Session-ID': getSessionId()
    },
    body: JSON.stringify({
      boundary_contract_id,
      file_id
    })
  });
  
  if (!response.ok) {
    throw new Error('Failed to save materialization');
  }
  
  return response.json();
}
```

#### 3.3 Update FileDashboard Component
**File**: `frontend/components/content/FileDashboard.tsx`

**Changes**:
- Only show saved files (materialized files)
- Add status indicator: "Saved" vs "Pending" (if we show pending files)
- Update terminology: "Materialized Files" or keep "Files" with tooltip
- Add note: "Files must be saved before parsing (MVP requirement)"

#### 3.4 Update File Types
**File**: `frontend/shared/types/file.ts`

**Add fields**:

```typescript
interface FileMetadata {
  // ... existing fields ...
  boundary_contract_id?: string;
  materialization_pending?: boolean;
  materialization_type?: 'reference' | 'partial_extraction' | 'deterministic' | 'semantic_embedding' | 'full_artifact';
  materialization_scope?: {
    user_id?: string;
    session_id?: string;
    solution_id?: string;
    scope_type?: 'workspace' | 'platform' | 'reference';
  };
}
```

---

### Phase 4: Database - Optional Denormalization

#### 4.1 Add Scope to Materialization Index (Optional)
**File**: `migrations/008_denormalize_scope_to_materializations.sql` (optional)

**Rationale**: If querying scope from boundary_contracts is too slow, denormalize:

```sql
ALTER TABLE project_files 
    ADD COLUMN IF NOT EXISTS materialization_scope JSONB,
    ADD COLUMN IF NOT EXISTS reference_scope JSONB;

-- Copy from boundary contracts
UPDATE project_files pf
SET 
    materialization_scope = dbc.materialization_scope,
    reference_scope = dbc.reference_scope
FROM data_boundary_contracts dbc
WHERE pf.boundary_contract_id = dbc.contract_id;
```

**Rationale**: Performance optimization. Can query directly from project_files instead of joining.

---

## Migration Strategy

### Existing Data
1. Run migration `005_create_default_boundary_contracts_for_existing_data.sql` (already created)
2. Update contracts to have workspace scope:
   ```sql
   UPDATE data_boundary_contracts
   SET 
       materialization_scope = jsonb_build_object(
           'user_id', user_id,
           'scope_type', 'workspace'
       ),
       reference_scope = jsonb_build_object(
           'users', jsonb_build_array(user_id),
           'scope_type', 'workspace'
       ),
       contract_status = 'active',
       materialization_allowed = true
   WHERE contract_terms->>'legacy' = 'true';
   ```
3. Mark all existing files as "saved" (materialization already happened)

### New Data Flow
1. Upload → Creates boundary contract (pending)
2. User clicks "Save" → Authorizes materialization (active)
3. File available for parsing

---

## Breaking Changes

### API Changes
- `POST /api/content/ingest_file` now returns `boundary_contract_id` and `materialization_pending: true`
- New endpoint: `POST /api/content/save_materialization` (required to make file available)
- `GET /api/content/files` only returns saved files (filtered by scope)

### Frontend Changes
- Upload no longer immediately makes file available
- User must explicitly click "Save" after upload
- File list only shows saved files

### Backward Compatibility
- Existing files are automatically marked as "saved" during migration
- Old API calls still work but return pending status
- Frontend can handle both old and new flows during transition

---

## Testing Plan

### Backend Tests
1. Test upload creates boundary contract (pending)
2. Test save authorizes materialization (active)
3. Test list files filters by scope
4. Test delete removes materialization
5. Test parsing only works on saved files

### Frontend Tests
1. Test upload flow shows "Save" button
2. Test save makes file available
3. Test file list only shows saved files
4. Test parsing requires saved file
5. Test delete removes from workspace

### Integration Tests
1. End-to-end: Upload → Save → List → Parse → Delete
2. Verify boundary contracts created with workspace scope
3. Verify materialization index updated correctly
4. Verify scope filtering works

---

## Success Criteria

1. ✅ Upload creates boundary contract (pending materialization)
2. ✅ Save explicitly authorizes materialization (active)
3. ✅ Files only available for parsing after save
4. ✅ File list filtered by workspace scope
5. ✅ Delete removes materialization (not source)
6. ✅ UI clearly shows save step with MVP note
7. ✅ All existing functionality preserved (list, delete, parse)
8. ✅ Architecture integrity maintained (scope-based, no special modes)

---

## Timeline Estimate

- **Phase 1 (Backend)**: 2-3 days
- **Phase 2 (API)**: 1-2 days
- **Phase 3 (Frontend)**: 2-3 days
- **Phase 4 (Optional)**: 1 day
- **Testing**: 2 days
- **Total**: ~8-11 days

---

## Files to Create/Modify

### SQL Migrations
- `migrations/008_denormalize_scope_to_materializations.sql` (optional)

### Backend Code
- `symphainy_platform/civic_systems/smart_city/primitives/data_steward_primitives.py` (extend authorize_materialization)
- `symphainy_platform/runtime/execution_lifecycle_manager.py` (two-phase flow)
- `symphainy_platform/realms/content/orchestrators/content_orchestrator.py` (handle save_materialization)
- `symphainy_platform/foundations/public_works/abstractions/file_storage_abstraction.py` (register_materialization)
- `runtime_main.py` or `runtime_api.py` (save_materialization endpoint)

### Frontend Code
- `frontend/components/content/FileUploader.tsx` (two-phase flow)
- `frontend/components/content/FileDashboard.tsx` (show saved files only)
- `frontend/lib/api/fms.ts` (saveMaterialization function)
- `frontend/shared/types/file.ts` (add scope fields)

---

## Next Steps

1. Review and approve this plan
2. Implement Phase 1 (Backend two-phase flow)
3. Implement Phase 2 (API endpoints)
4. Implement Phase 3 (Frontend explicit save)
5. Test end-to-end
6. Deploy
