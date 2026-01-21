# MVP Refactoring Plan: Workspace Materialization Mode

## Overview

This plan enables MVP functionality while maintaining architectural integrity. The key insight: **MVP can behave like a file platform without being one** by introducing "Workspace Materialization Mode" and reframing "files" as "working artifacts."

## Core Concepts

### Source Artifacts (External, Boundary-Governed)
- Client-owned
- Subject to Data Steward policy
- May never persist
- May be referenced only
- May be partially materialized

### Working Artifacts (MVP-Visible, User-Scoped)
- Created *by the platform* for interaction
- Exist to support user workflows, not ownership
- Explicitly ephemeral unless policy says otherwise
- Safe to list, rename, delete, group, etc.
- Scoped to: User, Session, Solution

## Workspace Materialization Mode (MVP Default)

**Declared in policy. Visible in architecture.**

In this mode:
- Source artifacts may be persisted as working artifacts
- Persistence is scoped to:
  - User
  - Session
  - Solution
- Retention is explicit
- Deletion is real
- Nothing becomes a platform-wide fact

This preserves:
- File dashboards ✅
- File lists ✅
- Delete buttons ✅
- Folder metaphors ✅
- Demo clarity ✅

Without poisoning the core architecture.

---

## Implementation Plan

### Phase 1: Backend - Workspace Materialization Support

#### 1.1 Update Boundary Contract Schema
**File**: `migrations/006_add_workspace_materialization_mode.sql`

Add fields to `data_boundary_contracts`:
- `materialization_scope_type`: `'workspace' | 'platform' | 'reference'`
- `workspace_scope`: JSONB with `{ user_id, session_id, solution_id }`
- `workspace_retention_policy`: TEXT (e.g., 'session', 'user', 'solution')

**Rationale**: Explicitly declare workspace-scoped materialization as a policy mode.

#### 1.2 Update Data Steward Primitives
**File**: `symphainy_platform/civic_systems/smart_city/primitives/data_steward_primitives.py`

Add method:
```python
async def authorize_workspace_materialization(
    self,
    contract_id: str,
    tenant_id: str,
    workspace_scope: Dict[str, str],  # { user_id, session_id, solution_id }
    requested_type: Optional[str] = None
) -> MaterializationAuthorization
```

**Behavior**:
- For MVP: Default to `materialization_scope_type='workspace'`
- Set `workspace_scope` from context
- Set `materialization_type='full_artifact'` (MVP default)
- Set `materialization_backing_store='gcs'` (MVP default)
- Set `workspace_retention_policy='user'` (MVP default - user-scoped)

**Rationale**: Explicit workspace materialization authorization separate from platform-wide materialization.

#### 1.3 Update ExecutionLifecycleManager
**File**: `symphainy_platform/runtime/execution_lifecycle_manager.py`

Modify boundary contract enforcement:
- For MVP: Use `authorize_workspace_materialization()` instead of `authorize_materialization()`
- Pass workspace scope: `{ user_id, session_id, solution_id }` from context
- Store workspace scope in execution context metadata

**Rationale**: MVP uses workspace-scoped materialization by default.

#### 1.4 Update Content Realm
**File**: `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

Update `_handle_ingest_file()`:
- Check for `workspace_scope` in context metadata
- Include `workspace_scope` in structured artifact `semantic_payload`
- Add `artifact_type='working_artifact'` to semantic payload
- Add `workspace_retention_policy` to semantic payload

**Rationale**: Mark artifacts as "working artifacts" with workspace scope.

#### 1.5 Update Materialization Index (Supabase)
**File**: `migrations/007_add_workspace_fields_to_materializations.sql`

Add to `project_files` (materializations index):
- `workspace_scope`: JSONB `{ user_id, session_id, solution_id }`
- `artifact_type`: TEXT `'source_artifact' | 'working_artifact'`
- `workspace_retention_policy`: TEXT

**Rationale**: Track workspace scope in materialization index.

---

### Phase 2: Backend - API Updates

#### 2.1 Update Runtime API Responses
**File**: `runtime_main.py` or `symphainy_platform/runtime/runtime_api.py`

Update artifact responses to include:
- `boundary_contract_id`
- `artifact_type` ('working_artifact' for MVP)
- `workspace_scope`
- `materialization_type`
- `workspace_retention_policy`

**Rationale**: Frontend needs to know these are "working artifacts" not "client data."

#### 2.2 Update File List API
**File**: API endpoint for `list_files`

Filter by workspace scope:
- Default: Show only working artifacts for current user/session
- Include `artifact_type` in response
- Include `workspace_scope` in response

**Rationale**: Users only see their workspace artifacts, not all platform data.

---

### Phase 3: Frontend - Terminology & Labels

#### 3.1 Update FileDashboard Component
**File**: `frontend/components/content/FileDashboard.tsx`

**Changes**:
- Change "file(s) uploaded" → "working artifact(s)" or "workspace item(s)"
- Change "No Data Files Found" → "No Working Artifacts" or "No Workspace Items"
- Add tooltip/help text: "Working artifacts are created for your workspace. They are scoped to your session and can be deleted."
- Update table headers if needed (optional - keep "Filename" is fine)

**Rationale**: Reframe UI to reflect "working artifacts" not "client files."

#### 3.2 Update FileUploader Component
**File**: `frontend/components/content/FileUploader.tsx`

**Changes**:
- Update upload button text: "Upload File" → "Create Working Artifact" (or keep "Upload" but add subtitle)
- Add info text: "Files are materialized as working artifacts for your workspace"
- Update success message: "File uploaded" → "Working artifact created" (or keep "uploaded" but clarify)

**Rationale**: Users understand they're creating workspace artifacts, not storing client data.

#### 3.3 Update File Types/Interfaces
**File**: `frontend/shared/types/file.ts` or similar

**Changes**:
- Add `artifact_type?: 'source_artifact' | 'working_artifact'`
- Add `workspace_scope?: { user_id?: string, session_id?: string, solution_id?: string }`
- Add `boundary_contract_id?: string`
- Add `workspace_retention_policy?: string`

**Rationale**: TypeScript types reflect new architecture.

#### 3.4 Update API Client
**File**: `frontend/lib/api/fms.ts` or similar

**Changes**:
- Update API calls to handle new fields
- Add comments explaining "working artifacts" vs "source artifacts"
- No breaking changes to existing API calls (backwards compatible)

**Rationale**: API client understands new semantics.

---

### Phase 4: Frontend - Optional Enhancements

#### 4.1 Add Workspace Scope Indicator
**File**: New component or update existing

**Feature**:
- Show workspace scope badge: "User Workspace" or "Session Workspace"
- Show retention policy: "Retained for session" or "Retained for user"
- Show boundary contract status (optional, for advanced users)

**Rationale**: Users understand workspace scoping (optional, can be hidden for MVP).

#### 4.2 Update Delete Confirmation
**File**: `FileDashboard.tsx` (delete modal)

**Changes**:
- Update confirmation text: "Are you sure you want to delete this working artifact?"
- Add: "This will remove it from your workspace. Source data remains external."

**Rationale**: Clarify that deletion removes workspace artifact, not source data.

---

### Phase 5: Documentation & Configuration

#### 5.1 Update Materialization Policy Config
**File**: `config/mvp_materialization_policy.yaml`

**Add**:
```yaml
workspace_materialization_mode:
  enabled: true
  default_scope_type: 'workspace'
  default_retention_policy: 'user'
  default_materialization_type: 'full_artifact'
  default_backing_store: 'gcs'
```

**Rationale**: Explicit policy configuration for workspace mode.

#### 5.2 Update Architecture Documentation
**File**: Architecture docs

**Add**:
- Section on "Workspace Materialization Mode"
- Distinction between "Source Artifacts" and "Working Artifacts"
- Explanation of workspace scoping

**Rationale**: Document the architectural pattern.

---

## Migration Strategy

### Existing Data
- Run migration `005_create_default_boundary_contracts_for_existing_data.sql` (already created)
- Update existing `project_files` to have:
  - `artifact_type='working_artifact'`
  - `workspace_scope` from existing `user_id` and `session_id`
  - `workspace_retention_policy='user'` (default)

### New Data
- All new file uploads automatically get workspace-scoped boundary contracts
- All new materializations marked as `working_artifact`
- Workspace scope set from execution context

---

## Testing Plan

### Backend Tests
1. Test workspace materialization authorization
2. Test workspace scope filtering in file list API
3. Test boundary contract creation with workspace scope
4. Test deletion removes workspace artifact (not source)

### Frontend Tests
1. Test file list shows workspace artifacts
2. Test upload creates working artifact
3. Test delete removes workspace artifact
4. Test UI labels reflect "working artifacts"

### Integration Tests
1. End-to-end: Upload → List → Delete flow
2. Verify boundary contracts created with workspace scope
3. Verify materialization index updated correctly

---

## Rollout Plan

### Step 1: Backend (No Breaking Changes)
- Add workspace materialization support
- Keep existing API responses (add new fields, don't remove old)
- Deploy backend changes

### Step 2: Database Migrations
- Run migrations 006 and 007
- Migrate existing data
- Verify data integrity

### Step 3: Frontend (Gradual)
- Update terminology in UI (can be done incrementally)
- Test with existing API
- Deploy frontend changes

### Step 4: Full Enforcement (Future)
- Once stable, can make workspace mode explicit requirement
- Can add UI indicators for workspace scope
- Can add advanced features (workspace management, etc.)

---

## Success Criteria

1. ✅ MVP functionality preserved (file lists, upload, delete all work)
2. ✅ Architecture integrity maintained (boundary contracts enforced)
3. ✅ UI reflects "working artifacts" semantics (terminology updated)
4. ✅ Workspace scoping implemented (user/session/solution scope)
5. ✅ No breaking changes (backwards compatible)
6. ✅ Documentation updated (architecture and user-facing)

---

## Files to Create/Modify

### SQL Migrations
- `migrations/006_add_workspace_materialization_mode.sql` (NEW)
- `migrations/007_add_workspace_fields_to_materializations.sql` (NEW)

### Backend Code
- `symphainy_platform/civic_systems/smart_city/primitives/data_steward_primitives.py` (MODIFY)
- `symphainy_platform/runtime/execution_lifecycle_manager.py` (MODIFY)
- `symphainy_platform/realms/content/orchestrators/content_orchestrator.py` (MODIFY)
- `config/mvp_materialization_policy.yaml` (MODIFY)

### Frontend Code
- `frontend/components/content/FileDashboard.tsx` (MODIFY)
- `frontend/components/content/FileUploader.tsx` (MODIFY)
- `frontend/shared/types/file.ts` (MODIFY)
- `frontend/lib/api/fms.ts` (MODIFY)

### Documentation
- Architecture docs (UPDATE)
- User-facing docs (UPDATE - optional)

---

## Risk Mitigation

### Risk: Breaking Existing Functionality
**Mitigation**: All changes backwards compatible, existing API calls still work

### Risk: User Confusion
**Mitigation**: Terminology changes are subtle, can be gradual, existing UX preserved

### Risk: Performance Impact
**Mitigation**: Workspace scoping actually improves performance (smaller result sets)

### Risk: Migration Complexity
**Mitigation**: Existing data gets default workspace scope, no data loss

---

## Timeline Estimate

- **Phase 1 (Backend)**: 2-3 days
- **Phase 2 (API)**: 1 day
- **Phase 3 (Frontend)**: 2-3 days
- **Phase 4 (Enhancements)**: 1-2 days (optional)
- **Phase 5 (Documentation)**: 1 day
- **Testing**: 2 days
- **Total**: ~10-12 days

---

## Next Steps

1. Review and approve this plan
2. Create SQL migrations (006, 007)
3. Implement backend workspace materialization support
4. Update frontend terminology
5. Test end-to-end
6. Deploy incrementally
