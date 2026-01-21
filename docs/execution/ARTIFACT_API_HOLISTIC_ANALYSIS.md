# Artifact API Holistic Analysis

**Date:** January 19, 2026  
**Status:** 🔍 **ANALYSIS COMPLETE**  
**Purpose:** Comprehensive analysis of artifact API to ensure it accommodates all platform usage patterns

---

## Executive Summary

The artifact API needs to handle **multiple artifact patterns** across the platform:
1. **File artifacts** (Content Realm) - Flat structure with `file_id`, `file_path`, `file_reference`
2. **Structured artifacts** (Journey, Outcomes) - Complex objects with nested data
3. **Composite artifacts** - Artifacts with embedded visuals and components
4. **Materialization policy** - Some artifacts persisted, some ephemeral
5. **MVP exceptions** - All artifacts persisted for demo purposes

**Current Gap:** The API assumes artifacts are stored via `ArtifactStorageAbstraction`, but file artifacts use a different pattern (direct file storage).

---

## Current Artifact API Implementation

### Endpoints

**1. GET `/api/artifacts/{artifact_id}`**
- **Purpose:** Retrieve artifact by ID
- **Parameters:**
  - `artifact_id`: Artifact UUID
  - `tenant_id`: Tenant ID (query param)
  - `include_visuals`: Include full visual images (default: False)
- **Returns:** Artifact data dictionary or 404

**2. GET `/api/artifacts/visual/{visual_path}`**
- **Purpose:** Retrieve visual image by storage path
- **Parameters:**
  - `visual_path`: GCS storage path
  - `tenant_id`: Tenant ID (query param)
- **Returns:** PNG image bytes or 404

### Implementation Flow

```
Runtime API → ArtifactStorageAbstraction → Supabase (metadata) + GCS (data)
```

**Current Logic:**
1. Lookup artifact metadata in Supabase by `artifact_id`
2. Verify `tenant_id` matches
3. Verify `artifact_type` is set (distinguishes from regular files)
4. Retrieve artifact JSON from GCS using `storage_path`
5. Optionally retrieve visuals if `include_visuals=True`

---

## Artifact Patterns Across Platform

### Pattern 1: File Artifacts (Content Realm)

**Structure:**
```python
artifacts = {
    "file_id": "uuid",
    "file_path": "tenant/session/file_id/filename.csv",
    "file_reference": "file:tenant:session:file_id",
    "file_metadata": {...},
    "file_contents": <bytes>,  # Optional
    "file_size": 1234
}
```

**Storage:**
- Files stored directly in GCS via `FileStorageAbstraction`
- Metadata stored in Supabase `project_files` table
- **NOT stored via `ArtifactStorageAbstraction`**

**Issue:** Current API expects artifacts to be stored via `ArtifactStorageAbstraction`, but file artifacts use a different path.

### Pattern 2: Structured Artifacts (Journey, Outcomes Realms)

**Structure:**
```python
artifacts = {
    "workflow": {...},  # Full workflow object
    "sop": {...},       # Full SOP object
    "solution": {...},  # Full solution object
    "workflow_visual": {
        "image_base64": "...",
        "storage_path": "artifacts/workflow/tenant/id/visual.png"
    }
}
```

**Storage:**
- Stored via `ArtifactStorageAbstraction` (when materialization policy says "persist")
- Stored at: `artifacts/{artifact_type}/{tenant_id}/{artifact_id}.json`
- Visuals stored separately with references

**Status:** ✅ Works with current API

### Pattern 3: Composite Artifacts

**Structure:**
```python
artifacts = {
    "workflow_artifact_id": "uuid",  # Reference to stored artifact
    "sop_artifact_id": "uuid",       # Reference to stored artifact
    "workflow_visual_path": "path",  # Reference to visual
}
```

**Storage:**
- Artifacts stored via `ArtifactStorageAbstraction`
- Execution status returns artifact IDs, not full artifacts
- Full artifacts retrieved via `/api/artifacts/{artifact_id}` when `include_artifacts=True`

**Status:** ✅ Works with current API (Runtime API handles expansion)

### Pattern 4: Execution Status Artifacts

**Structure (from Runtime API):**
```python
{
    "execution_id": "...",
    "status": "completed",
    "artifacts": {
        # Pattern A: Flat file artifacts
        "file_id": "uuid",
        "file_path": "path",
        
        # Pattern B: Artifact references
        "workflow_artifact_id": "uuid",
        "sop_artifact_id": "uuid",
        
        # Pattern C: Inline artifacts (when include_artifacts=True)
        "workflow": {...},  # Full artifact after expansion
        "sop": {...}        # Full artifact after expansion
    }
}
```

**Current Behavior:**
- Runtime API expands `*_artifact_id` references when `include_artifacts=True`
- Calls `ArtifactStorageAbstraction.get_artifact()` for each reference
- **Issue:** Doesn't handle file artifacts (which don't use artifact storage)

---

## Materialization Policy Impact

### MVP Policy (Current)

**File:** `config/mvp_materialization_policy.yaml`

```yaml
materialization_policy:
  # Platform-native (always persisted)
  intent: persist
  journey: persist
  state_transition: persist
  governance_decision: persist
  
  # Derived artifacts (MVP persists for demo)
  workflow: persist
  sop: persist
  blueprint: persist
  solution: persist
  roadmap: persist
  poc: persist
  visual: persist
```

**Impact:**
- All artifacts are persisted (MVP exception)
- File artifacts are always persisted (via file storage)
- Structured artifacts persisted via `ArtifactStorageAbstraction`

### Future Policy (Post-MVP)

**Default Policy:**
- Platform-native records: Always persist
- Derived artifacts: Ephemeral by default (discard)
- Client overrides: Can persist specific artifact types

**Impact on API:**
- API must handle cases where artifacts don't exist (were discarded)
- API must distinguish between "not found" and "not persisted"
- API should support querying what artifacts exist vs. what were persisted

---

## Current Issues & Gaps

### Issue 1: File Artifacts Not Retrievable via Artifact API

**Problem:**
- File artifacts stored via `FileStorageAbstraction`, not `ArtifactStorageAbstraction`
- Artifact API only queries `ArtifactStorageAbstraction`
- File artifacts have different metadata structure

**Example:**
```python
# File artifact structure
{
    "file_id": "uuid",
    "file_path": "tenant/session/file_id/file.csv",
    "file_reference": "file:tenant:session:file_id"
}

# API tries to find in Supabase with artifact_type, but files don't have artifact_type
```

**Impact:**
- Test failures when trying to retrieve file artifacts
- Inconsistent API behavior between file and structured artifacts

### Issue 2: Artifact Type Ambiguity

**Problem:**
- File artifacts don't have `artifact_type` field
- Structured artifacts have `artifact_type` field
- API can't distinguish between "file artifact" and "regular file"

**Current Workaround:**
- Test checks for `file_path` as fallback
- Not a proper solution

### Issue 3: Execution Status Artifact Expansion

**Problem:**
- Runtime API expands `*_artifact_id` references
- Doesn't expand file artifacts (which use `file_id`, not `file_artifact_id`)
- Inconsistent behavior

**Current Code:**
```python
# Only expands *_artifact_id patterns
if key.endswith("_artifact_id"):
    artifact_id = value
    # Retrieve via ArtifactStorageAbstraction
```

**Missing:**
- Expansion of `file_id` to full file artifact
- Expansion of other artifact reference patterns

### Issue 4: Visual Retrieval

**Problem:**
- Visuals stored separately with `storage_path` references
- API endpoint `/api/artifacts/visual/{visual_path}` works
- But visual paths in artifacts may not be consistently structured

**Example:**
```python
# Pattern A: Direct path
"visual_path": "artifacts/workflow/tenant/id/visual.png"

# Pattern B: Nested in object
"workflow_visual": {
    "storage_path": "artifacts/workflow/tenant/id/visual.png"
}
```

---

## Recommendations

### Recommendation 1: Unified Artifact Retrieval

**Create unified artifact retrieval that handles both patterns:**

```python
async def get_artifact_unified(
    self,
    artifact_id: str,
    tenant_id: str,
    include_visuals: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Unified artifact retrieval that handles:
    1. Structured artifacts (via ArtifactStorageAbstraction)
    2. File artifacts (via FileStorageAbstraction)
    3. Fallback to direct GCS lookup
    """
    # Try ArtifactStorageAbstraction first (structured artifacts)
    artifact = await self.artifact_storage.get_artifact(...)
    if artifact:
        return artifact
    
    # Try FileStorageAbstraction (file artifacts)
    file_artifact = await self.file_storage.get_file_metadata(...)
    if file_artifact:
        return self._format_file_as_artifact(file_artifact)
    
    # Fallback: Direct GCS lookup
    return await self._get_artifact_from_gcs_fallback(...)
```

### Recommendation 2: Artifact Type Standardization

**Add `artifact_type` to all artifacts, including files:**

```python
# File artifacts should have:
{
    "artifact_type": "file",  # NEW
    "file_id": "uuid",
    "file_path": "...",
    ...
}

# This allows API to distinguish artifacts from regular files
```

### Recommendation 3: Execution Status Artifact Expansion Enhancement

**Enhance artifact expansion to handle all patterns:**

```python
# Expand all artifact reference patterns
artifact_patterns = [
    ("_artifact_id", self.artifact_storage),  # Structured artifacts
    ("_id", self._expand_id_reference),       # Generic ID references
    ("file_id", self.file_storage),           # File artifacts
    ("file_reference", self.file_storage),    # File references
]
```

### Recommendation 4: Materialization Policy Awareness

**API should be aware of materialization policy:**

```python
async def get_artifact(
    self,
    artifact_id: str,
    tenant_id: str,
    include_visuals: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Get artifact, with materialization policy awareness.
    
    Returns:
        - Artifact if persisted
        - None if not found
        - Raises ArtifactNotPersistedError if ephemeral (future)
    """
    # Check if artifact was persisted (via materialization policy)
    # If ephemeral and not found, return appropriate error
```

### Recommendation 5: Artifact Metadata Enhancement

**Enhance artifact metadata to support all patterns:**

```python
# Unified artifact metadata structure
{
    "artifact_id": "uuid",
    "artifact_type": "file" | "workflow" | "sop" | "solution" | ...,
    "tenant_id": "tenant",
    "storage_type": "artifact_storage" | "file_storage",  # NEW
    "storage_path": "...",
    "created_at": "...",
    "metadata": {
        "execution_id": "...",
        "session_id": "...",
        "intent_type": "...",
        ...
    }
}
```

---

## Implementation Plan

### Phase 1: File Artifact Support (Priority: HIGH)

**Goal:** Make file artifacts retrievable via artifact API

**Tasks:**
1. Add `artifact_type: "file"` to file artifacts
2. Create unified artifact retrieval method
3. Update Runtime API to use unified retrieval
4. Update tests to validate file artifact retrieval

**Estimated:** 2-3 hours

### Phase 2: Artifact Type Standardization (Priority: MEDIUM)

**Goal:** Standardize artifact type across all artifacts

**Tasks:**
1. Add `artifact_type` to all artifact creation points
2. Update artifact storage to require `artifact_type`
3. Update API to validate `artifact_type`
4. Update documentation

**Estimated:** 4-6 hours

### Phase 3: Execution Status Enhancement (Priority: MEDIUM)

**Goal:** Enhance artifact expansion in execution status

**Tasks:**
1. Add file artifact expansion
2. Add generic ID reference expansion
3. Add visual path normalization
4. Update tests

**Estimated:** 3-4 hours

### Phase 4: Materialization Policy Integration (Priority: LOW - Future)

**Goal:** Make API aware of materialization policy

**Tasks:**
1. Add materialization policy checks to API
2. Add "not persisted" error handling
3. Add artifact existence queries
4. Update documentation

**Estimated:** 6-8 hours (post-MVP)

---

## Testing Requirements

### Test Cases Needed

1. **File Artifact Retrieval**
   - Retrieve file artifact by `file_id`
   - Verify file contents included
   - Verify metadata structure

2. **Structured Artifact Retrieval**
   - Retrieve workflow artifact
   - Retrieve SOP artifact
   - Retrieve solution artifact

3. **Composite Artifact Retrieval**
   - Retrieve artifact with visuals
   - Verify visual references
   - Verify visual retrieval endpoint

4. **Execution Status Expansion**
   - Verify `*_artifact_id` expansion
   - Verify `file_id` expansion
   - Verify inline vs. reference modes

5. **Materialization Policy**
   - Verify persisted artifacts retrievable
   - Verify ephemeral artifacts not retrievable (future)
   - Verify policy override behavior

---

## Conclusion

The artifact API needs **unified retrieval** that handles:
- ✅ Structured artifacts (current - works)
- ❌ File artifacts (gap - needs fix)
- ⚠️ Composite artifacts (partial - needs enhancement)
- ⚠️ Materialization policy (future - needs planning)

**Priority:** Fix file artifact retrieval first (blocks tests), then enhance for consistency.
