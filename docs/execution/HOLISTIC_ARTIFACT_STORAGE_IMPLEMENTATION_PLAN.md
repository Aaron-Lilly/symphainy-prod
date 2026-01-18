# Holistic Artifact Storage Implementation Plan

**Date:** January 17, 2026  
**Status:** ⚠️ **SUPERSEDED** - See `MATERIALIZATION_POLICY_REFACTORING_PLAN.md`  
**Goal:** Enable complete artifact storage for all platform deliverables

**⚠️ IMPORTANT:** This plan has been superseded by the Materialization Policy Refactoring Plan. The architectural direction has shifted:
- Artifacts are **ephemeral by default** (not stored)
- **Runtime** (not realms) evaluates Materialization Policy and stores artifacts
- MVP uses **policy override** to persist artifacts (demonstrates policy pattern)

**See:** `docs/execution/MATERIALIZATION_POLICY_REFACTORING_PLAN.md` for the updated plan.

---

## Executive Summary

**Current State:**
- ✅ GCS infrastructure exists (`GCSAdapter`)
- ✅ Supabase infrastructure exists (`SupabaseFileAdapter`)
- ✅ `FileStorageAbstraction` exists (for user-uploaded files)
- ✅ `FileManagementAbstraction` exists (pure infrastructure)
- ❌ **No artifact storage abstraction exists**
- ❌ **Artifacts are not stored anywhere**

**Target State:**
- ✅ Artifact storage abstraction created
- ✅ All artifacts stored in GCS
- ✅ Artifact metadata in Supabase
- ✅ Multi-component artifacts stored as integrated wholes
- ✅ Artifacts retrievable after execution

**Timeline:** 8-12 days  
**Priority:** 🔴 **CRITICAL** - Platform doesn't work without this

---

## Current Infrastructure Review

### What Exists ✅

#### 1. GCS Adapter (`GCSAdapter`)
**Location:** `symphainy_platform/foundations/public_works/adapters/gcs_adapter.py`

**Capabilities:**
- ✅ `upload_file(blob_name, file_data, content_type, metadata) -> bool`
- ✅ `download_file(blob_name) -> Optional[bytes]`
- ✅ `delete_file(blob_name) -> bool`
- ✅ `list_files(prefix) -> List[Dict]`
- ✅ `get_file_metadata(blob_name) -> Optional[Dict]`

**Status:** ✅ Working - Used for user-uploaded files

**Can Reuse:** ✅ Yes - Perfect for artifact storage

---

#### 2. Supabase File Adapter (`SupabaseFileAdapter`)
**Location:** `symphainy_platform/foundations/public_works/adapters/supabase_file_adapter.py`

**Capabilities:**
- ✅ `create_file(file_data) -> Dict` - Creates file metadata
- ✅ `get_file(file_uuid) -> Optional[Dict]` - Gets file metadata
- ✅ `list_files(user_id, tenant_id, filters, limit, offset) -> List[Dict]`
- ✅ `update_file(file_uuid, updates) -> Dict`
- ✅ `delete_file(file_uuid) -> bool`

**Table:** `project_files`

**Schema Fields:**
- `uuid`, `user_id`, `tenant_id`, `ui_name`, `file_path`
- `file_type`, `mime_type`, `file_size`, `file_hash`
- `status`, `created_at`, `updated_at`, `deleted`
- Plus many other fields for file lifecycle

**Status:** ✅ Working - Used for file metadata

**Can Reuse:** ⚠️ **Partially** - Need new table for artifacts OR extend `project_files`

---

#### 3. File Storage Abstraction (`FileStorageAbstraction`)
**Location:** `symphainy_platform/foundations/public_works/abstractions/file_storage_abstraction.py`

**Capabilities:**
- ✅ `upload_file(file_path, file_data, metadata) -> Dict`
- ✅ `download_file(file_path) -> Optional[bytes]`
- ✅ `delete_file(file_path) -> bool`
- ✅ `list_files(prefix, tenant_id, user_id, file_type, limit, offset) -> List[Dict]`
- ✅ `get_file_metadata(file_path) -> Optional[Dict]`
- ✅ `get_file_by_uuid(file_uuid) -> Optional[Dict]`

**Purpose:** Coordinates GCS + Supabase for file storage

**Status:** ✅ Working - Used for user-uploaded files

**Can Reuse:** ⚠️ **Partially** - Designed for files, not artifacts (different metadata needs)

---

#### 4. File Management Abstraction (`FileManagementAbstraction`)
**Location:** `symphainy_platform/foundations/public_works/abstractions/file_management_abstraction.py`

**Capabilities:**
- ✅ `create_file(file_data) -> Dict` - Pure infrastructure
- ✅ `get_file(file_uuid) -> Optional[Dict]`
- ✅ `update_file(file_uuid, updates) -> Dict`
- ✅ `delete_file(file_uuid) -> bool`

**Purpose:** Pure infrastructure layer (no business logic)

**Status:** ✅ Working

**Can Reuse:** ⚠️ **Partially** - Designed for files, not artifacts

---

#### 5. Public Works Foundation Service
**Location:** `symphainy_platform/foundations/public_works/foundation_service.py`

**Exposes:**
- ✅ `get_file_storage_abstraction() -> FileStorageAbstraction`
- ✅ `get_file_management_abstraction() -> FileManagementAbstraction`

**Status:** ✅ Working

**Needs:** New method `get_artifact_storage_abstraction() -> ArtifactStorageAbstraction`

---

### What's Missing ❌

1. **Artifact Storage Abstraction** - Does not exist
2. **Artifact Storage Protocol** - Does not exist
3. **Supabase Artifact Table** - Does not exist (or need to extend `project_files`)
4. **Artifact Storage Integration** - Orchestrators don't store artifacts

---

## Architecture Decision: Storage Strategy

### Option 1: Extend `project_files` Table (Recommended) ✅

**Strategy:** Use existing `project_files` table for artifact metadata

**Pros:**
- ✅ No new table needed
- ✅ Reuses existing infrastructure
- ✅ Consistent with file storage pattern
- ✅ Can query files and artifacts together

**Cons:**
- ⚠️ Need to distinguish artifacts from files (use `file_type` or new field)
- ⚠️ Some file-specific fields may not apply to artifacts

**Implementation:**
- Add `artifact_type` field to `project_files` (or use `file_type` with artifact types)
- Use `file_path` for GCS storage path
- Use `ui_name` for artifact display name
- Use `metadata` JSONB for artifact-specific metadata

**Schema Extension:**
```sql
-- Add artifact support to project_files
ALTER TABLE project_files ADD COLUMN IF NOT EXISTS artifact_type TEXT;
-- artifact_type: 'workflow', 'sop', 'blueprint', 'solution', 'roadmap', 'poc', NULL (for files)

-- Index for artifact queries
CREATE INDEX IF NOT EXISTS idx_project_files_artifact_type ON project_files(artifact_type) WHERE artifact_type IS NOT NULL;
```

---

### Option 2: New `artifacts` Table

**Strategy:** Create separate `artifacts` table

**Pros:**
- ✅ Clean separation of files vs artifacts
- ✅ Artifact-specific fields
- ✅ No confusion with file metadata

**Cons:**
- ⚠️ New table to maintain
- ⚠️ Duplicate infrastructure
- ⚠️ Can't query files and artifacts together

**Not Recommended:** Unnecessary duplication

---

## Implementation Plan

### Phase 1: Artifact Storage Protocol (Day 1) 🔴

**Create:** `symphainy_platform/foundations/public_works/protocols/artifact_storage_protocol.py`

**Purpose:** Define contract for artifact storage operations

**Methods:**
```python
class ArtifactStorageProtocol(Protocol):
    """Protocol for artifact storage operations."""
    
    async def store_artifact(
        self,
        artifact_type: str,
        artifact_data: Dict[str, Any],
        tenant_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store artifact in GCS and metadata in Supabase.
        
        Returns:
            {"success": True, "artifact_id": "...", "storage_path": "..."}
            or {"success": False, "error": "..."}
        """
        ...
    
    async def get_artifact(
        self,
        artifact_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve artifact from GCS."""
        ...
    
    async def list_artifacts(
        self,
        artifact_type: str,
        tenant_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List artifacts by type and tenant."""
        ...
    
    async def delete_artifact(
        self,
        artifact_id: str,
        tenant_id: str
    ) -> bool:
        """Delete artifact from GCS and metadata from Supabase."""
        ...
    
    async def store_composite_artifact(
        self,
        artifact_type: str,
        artifact_data: Dict[str, Any],
        tenant_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store composite artifact with embedded components.
        Large binary components (visuals) stored separately.
        
        Returns:
            {"success": True, "artifact_id": "...", "storage_path": "...", "visual_paths": {...}}
        """
        ...
```

---

### Phase 2: Artifact Storage Abstraction (Days 2-3) 🔴

**Create:** `symphainy_platform/foundations/public_works/abstractions/artifact_storage_abstraction.py`

**Purpose:** Implement artifact storage using GCS + Supabase

**Dependencies:**
- `GCSAdapter` (reuse)
- `SupabaseFileAdapter` (reuse, extend if needed)
- `FileStorageAbstraction` (reference for patterns)

**Implementation:**

```python
class ArtifactStorageAbstraction(ArtifactStorageProtocol):
    """
    Artifact storage abstraction.
    
    Coordinates between GCS (artifact storage) and Supabase (artifact metadata).
    Handles both simple and composite artifacts.
    """
    
    def __init__(
        self,
        gcs_adapter: GCSAdapter,
        supabase_file_adapter: SupabaseFileAdapter,
        bucket_name: str
    ):
        self.gcs = gcs_adapter
        self.supabase = supabase_file_adapter
        self.bucket_name = bucket_name
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
    
    async def store_artifact(
        self,
        artifact_type: str,
        artifact_data: Dict[str, Any],
        tenant_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store artifact in GCS and metadata in Supabase.
        
        Handles:
        - Simple artifacts (single JSON file)
        - Composite artifacts (embedded components)
        - Visual artifacts (stored separately)
        """
        # 1. Generate artifact_id
        artifact_id = generate_event_id()
        
        # 2. Extract visuals (store separately)
        visuals = {}
        artifact_json_data = artifact_data.copy()
        
        for key, value in artifact_data.items():
            if key.endswith("_visual") and isinstance(value, dict):
                if "image_base64" in value:
                    # Store visual separately
                    visual_path = f"artifacts/{artifact_type}/{tenant_id}/{artifact_id}/{key}.png"
                    image_bytes = base64.b64decode(value["image_base64"])
                    
                    upload_result = await self.gcs.upload_file(
                        blob_name=visual_path,
                        file_data=image_bytes,
                        content_type="image/png",
                        metadata={
                            "artifact_id": artifact_id,
                            "artifact_type": artifact_type,
                            "tenant_id": tenant_id,
                            "visual_type": key
                        }
                    )
                    
                    if upload_result:
                        # Replace with reference
                        visuals[key] = {
                            "storage_path": visual_path,
                            "format": "png"
                        }
                        artifact_json_data[key] = visuals[key]
        
        # 3. Serialize artifact to JSON
        artifact_json = json.dumps(artifact_json_data, indent=2, default=str)
        artifact_bytes = artifact_json.encode('utf-8')
        
        # 4. Store in GCS
        artifact_path = f"artifacts/{artifact_type}/{tenant_id}/{artifact_id}.json"
        upload_result = await self.gcs.upload_file(
            blob_name=artifact_path,
            file_data=artifact_bytes,
            content_type="application/json",
            metadata={
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "tenant_id": tenant_id
            }
        )
        
        if not upload_result:
            return {"success": False, "error": "GCS upload failed"}
        
        # 5. Store metadata in Supabase (using project_files table)
        artifact_metadata = {
            "uuid": artifact_id,
            "user_id": metadata.get("user_id") if metadata else None,
            "tenant_id": tenant_id,
            "ui_name": metadata.get("ui_name") or f"{artifact_type}_{artifact_id}",
            "file_path": artifact_path,
            "artifact_type": artifact_type,  # NEW field
            "file_type": "artifact",  # Distinguish from files
            "mime_type": "application/json",
            "file_size": len(artifact_bytes),
            "status": metadata.get("status", "active"),
            "created_at": self.clock.now_iso(),
            "updated_at": self.clock.now_iso(),
            "deleted": False,
            # Store artifact-specific metadata in metadata JSONB field
            "metadata": {
                "execution_id": metadata.get("execution_id"),
                "session_id": metadata.get("session_id"),
                "component_count": len(artifact_data.get("components", {})),
                "has_visuals": len(visuals) > 0,
                "visual_paths": list(visuals.keys()) if visuals else []
            }
        }
        
        try:
            await self.supabase.create_file(artifact_metadata)
            self.logger.info(f"Artifact metadata created in Supabase: {artifact_id}")
        except Exception as meta_error:
            self.logger.warning(f"Artifact stored in GCS but metadata creation failed: {meta_error}")
            # Continue - artifact is stored, metadata can be fixed later
        
        return {
            "success": True,
            "artifact_id": artifact_id,
            "storage_path": artifact_path,
            "visual_paths": visuals
        }
    
    async def get_artifact(
        self,
        artifact_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve artifact from GCS.
        
        For composite artifacts, retrieves all components.
        For artifacts with visuals, retrieves visual references.
        """
        # 1. Get metadata from Supabase
        artifact_metadata = await self.supabase.get_file(artifact_id)
        
        if not artifact_metadata:
            self.logger.warning(f"Artifact metadata not found: {artifact_id}")
            return None
        
        # Verify tenant_id matches
        if artifact_metadata.get("tenant_id") != tenant_id:
            self.logger.warning(f"Artifact {artifact_id} does not belong to tenant {tenant_id}")
            return None
        
        # 2. Get artifact from GCS
        storage_path = artifact_metadata.get("file_path")
        if not storage_path:
            self.logger.warning(f"Artifact {artifact_id} has no storage_path")
            return None
        
        artifact_bytes = await self.gcs.download_file(storage_path)
        if not artifact_bytes:
            self.logger.warning(f"Artifact not found in GCS: {storage_path}")
            return None
        
        # 3. Deserialize artifact
        artifact = json.loads(artifact_bytes.decode('utf-8'))
        
        # 4. Retrieve visuals if referenced
        metadata_obj = artifact_metadata.get("metadata", {})
        if metadata_obj.get("has_visuals"):
            visual_paths = metadata_obj.get("visual_paths", [])
            for visual_key in visual_paths:
                if visual_key in artifact and isinstance(artifact[visual_key], dict):
                    visual_ref = artifact[visual_key]
                    if "storage_path" in visual_ref:
                        visual_bytes = await self.gcs.download_file(visual_ref["storage_path"])
                        if visual_bytes:
                            visual_base64 = base64.b64encode(visual_bytes).decode()
                            artifact[visual_key]["image_base64"] = visual_base64
        
        return artifact
    
    async def list_artifacts(
        self,
        artifact_type: str,
        tenant_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List artifacts by type and tenant."""
        # Query Supabase for artifacts
        filters = {
            "artifact_type": artifact_type,
            "file_type": "artifact"  # Distinguish from files
        }
        
        artifacts = await self.supabase.list_files(
            user_id=None,  # Not filtering by user
            tenant_id=tenant_id,
            filters=filters,
            limit=limit,
            offset=offset
        )
        
        return artifacts
    
    async def delete_artifact(
        self,
        artifact_id: str,
        tenant_id: str
    ) -> bool:
        """Delete artifact from GCS and metadata from Supabase."""
        # 1. Get metadata
        artifact_metadata = await self.supabase.get_file(artifact_id)
        if not artifact_metadata:
            return False
        
        # Verify tenant_id
        if artifact_metadata.get("tenant_id") != tenant_id:
            return False
        
        # 2. Delete from GCS
        storage_path = artifact_metadata.get("file_path")
        if storage_path:
            await self.gcs.delete_file(storage_path)
        
        # 3. Delete visuals if any
        metadata_obj = artifact_metadata.get("metadata", {})
        visual_paths = metadata_obj.get("visual_paths", [])
        for visual_key in visual_paths:
            # Visual paths stored in artifact JSON, need to retrieve first
            # Or store visual paths in metadata
            pass  # TODO: Implement visual deletion
        
        # 4. Soft delete in Supabase
        await self.supabase.update_file(artifact_id, {"deleted": True})
        
        return True
    
    async def store_composite_artifact(
        self,
        artifact_type: str,
        artifact_data: Dict[str, Any],
        tenant_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store composite artifact with embedded components.
        
        This is the same as store_artifact but with explicit handling
        for multi-component artifacts (blueprints, roadmaps, etc.).
        """
        # For now, use same implementation as store_artifact
        # Components are embedded in artifact_data JSON
        return await self.store_artifact(artifact_type, artifact_data, tenant_id, metadata)
```

---

### Phase 3: Supabase Schema Extension (Day 1, Parallel) 🟡

**File:** `migrations/002_add_artifact_support_to_project_files.sql`

**Changes:**
```sql
-- Add artifact_type column to project_files
ALTER TABLE project_files ADD COLUMN IF NOT EXISTS artifact_type TEXT;
-- artifact_type: 'workflow', 'sop', 'blueprint', 'solution', 'roadmap', 'poc', 'hybrid_embeddings', NULL (for files)

-- Add index for artifact queries
CREATE INDEX IF NOT EXISTS idx_project_files_artifact_type 
ON project_files(artifact_type) 
WHERE artifact_type IS NOT NULL;

-- Add composite index for artifact queries
CREATE INDEX IF NOT EXISTS idx_project_files_artifact_tenant 
ON project_files(artifact_type, tenant_id) 
WHERE artifact_type IS NOT NULL;
```

**Alternative:** Use existing `file_type` field with artifact types:
- `file_type` = 'artifact'
- Use `metadata` JSONB for `artifact_type` ('workflow', 'sop', etc.)

**Recommendation:** Add `artifact_type` column for clarity and query performance.

---

### Phase 4: Public Works Integration (Day 2) 🟡

**Update:** `symphainy_platform/foundations/public_works/foundation_service.py`

**Changes:**
1. Create `ArtifactStorageAbstraction` in `_create_abstractions()`
2. Add `get_artifact_storage_abstraction() -> ArtifactStorageAbstraction`

**Code:**
```python
# In _create_abstractions()
from .abstractions.artifact_storage_abstraction import ArtifactStorageAbstraction

# Create artifact storage abstraction
if self.gcs_adapter and self.supabase_file_adapter:
    self.artifact_storage_abstraction = ArtifactStorageAbstraction(
        gcs_adapter=self.gcs_adapter,
        supabase_file_adapter=self.supabase_file_adapter,
        bucket_name=self.config.get("gcs", {}).get("bucket_name", "symphainy-bucket-2025")
    )
    self.logger.info("Artifact Storage Abstraction created")
else:
    self.logger.warning("GCS or Supabase adapter not available, Artifact Storage Abstraction not created")

# Add getter method
def get_artifact_storage_abstraction(self) -> Optional[ArtifactStorageAbstraction]:
    """Get artifact storage abstraction."""
    return self.artifact_storage_abstraction
```

---

### Phase 5: Orchestrator Integration (Days 4-6) 🔴

**Update Orchestrators to Store Artifacts:**

#### 5.1 Journey Orchestrator (Day 4)

**File:** `symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py`

**Changes:**

1. **Inject Artifact Storage:**
```python
def __init__(self, public_works: Optional[Any] = None):
    # ... existing code ...
    self.artifact_storage = None
    if public_works:
        self.artifact_storage = public_works.get_artifact_storage_abstraction()
```

2. **Store Workflow After Creation:**
```python
async def _handle_create_workflow(...):
    # ... existing workflow creation code ...
    
    artifacts = {
        "workflow": workflow_result,
        "sop_id": sop_id
    }
    
    if visual_result and visual_result.get("success"):
        artifacts["workflow_visual"] = {
            "image_base64": visual_result.get("image_base64"),
            "storage_path": visual_result.get("storage_path")
        }
    
    # Store artifact
    if self.artifact_storage:
        try:
            storage_result = await self.artifact_storage.store_composite_artifact(
                artifact_type="workflow",
                artifact_data=artifacts,
                tenant_id=context.tenant_id,
                metadata={
                    "execution_id": context.execution_id,
                    "session_id": context.session_id,
                    "sop_id": sop_id
                }
            )
            
            if storage_result.get("success"):
                artifacts["artifact_id"] = storage_result["artifact_id"]
                artifacts["storage_path"] = storage_result["storage_path"]
                self.logger.info(f"Workflow artifact stored: {storage_result['artifact_id']}")
        except Exception as e:
            self.logger.warning(f"Failed to store workflow artifact: {e}")
            # Continue - artifact still returned in execution result
    
    return {
        "artifacts": artifacts,
        "events": [...]
    }
```

3. **Store SOP After Generation:**
```python
async def _handle_generate_sop(...):
    # ... existing SOP generation code ...
    
    artifacts = {
        "sop": sop_result,
        "workflow_id": workflow_id
    }
    
    if visual_result and visual_result.get("success"):
        artifacts["sop_visual"] = {...}
    
    # Store artifact
    if self.artifact_storage:
        try:
            storage_result = await self.artifact_storage.store_composite_artifact(
                artifact_type="sop",
                artifact_data=artifacts,
                tenant_id=context.tenant_id,
                metadata={
                    "execution_id": context.execution_id,
                    "session_id": context.session_id,
                    "workflow_id": workflow_id
                }
            )
            
            if storage_result.get("success"):
                artifacts["artifact_id"] = storage_result["artifact_id"]
                artifacts["storage_path"] = storage_result["storage_path"]
        except Exception as e:
            self.logger.warning(f"Failed to store SOP artifact: {e}")
    
    return {
        "artifacts": artifacts,
        "events": [...]
    }
```

4. **Store Blueprint After Creation:**
```python
async def _handle_create_blueprint(...):
    # ... existing blueprint creation code ...
    
    # Blueprint is already a composite artifact with 4 components
    # Store as-is (components embedded)
    
    if self.artifact_storage:
        try:
            storage_result = await self.artifact_storage.store_composite_artifact(
                artifact_type="blueprint",
                artifact_data=blueprint,
                tenant_id=context.tenant_id,
                metadata={
                    "execution_id": context.execution_id,
                    "session_id": context.session_id,
                    "workflow_id": workflow_id
                }
            )
            
            if storage_result.get("success"):
                blueprint["artifact_id"] = storage_result["artifact_id"]
                blueprint["storage_path"] = storage_result["storage_path"]
        except Exception as e:
            self.logger.warning(f"Failed to store blueprint artifact: {e}")
    
    return {
        "artifacts": {"blueprint": blueprint},
        "events": [...]
    }
```

---

#### 5.2 Outcomes Orchestrator (Day 5)

**File:** `symphainy_platform/realms/outcomes/orchestrators/outcomes_orchestrator.py`

**Changes:**

1. **Inject Artifact Storage:**
```python
def __init__(self, public_works: Optional[Any] = None):
    # ... existing code ...
    self.artifact_storage = None
    if public_works:
        self.artifact_storage = public_works.get_artifact_storage_abstraction()
```

2. **Store Solution After Synthesis:**
```python
async def _handle_synthesize_outcome(...):
    # ... existing synthesis code ...
    
    artifacts = {
        "synthesis": summary_result,
        "content_summary": content_summary,
        "insights_summary": insights_summary,
        "journey_summary": journey_summary
    }
    
    if visual_result and visual_result.get("success"):
        artifacts["summary_visual"] = {...}
    
    # Store artifact
    if self.artifact_storage:
        try:
            storage_result = await self.artifact_storage.store_composite_artifact(
                artifact_type="solution",
                artifact_data=artifacts,
                tenant_id=context.tenant_id,
                metadata={
                    "execution_id": context.execution_id,
                    "session_id": context.session_id
                }
            )
            
            if storage_result.get("success"):
                artifacts["artifact_id"] = storage_result["artifact_id"]
                artifacts["storage_path"] = storage_result["storage_path"]
        except Exception as e:
            self.logger.warning(f"Failed to store solution artifact: {e}")
    
    return {
        "artifacts": artifacts,
        "events": [...]
    }
```

3. **Store Roadmap After Generation:**
```python
async def _handle_generate_roadmap(...):
    # ... existing roadmap generation code ...
    
    artifacts = {
        "roadmap": roadmap_result,
        "roadmap_id": roadmap_result.get("roadmap_id"),
        "strategic_plan": roadmap_result.get("strategic_plan")
    }
    
    if visual_result and visual_result.get("success"):
        artifacts["roadmap_visual"] = {...}
    
    # Store artifact (roadmap is multi-phase, components embedded)
    if self.artifact_storage:
        try:
            storage_result = await self.artifact_storage.store_composite_artifact(
                artifact_type="roadmap",
                artifact_data=artifacts,
                tenant_id=context.tenant_id,
                metadata={
                    "execution_id": context.execution_id,
                    "session_id": context.session_id
                }
            )
            
            if storage_result.get("success"):
                artifacts["artifact_id"] = storage_result["artifact_id"]
                artifacts["storage_path"] = storage_result["storage_path"]
        except Exception as e:
            self.logger.warning(f"Failed to store roadmap artifact: {e}")
    
    return {
        "artifacts": artifacts,
        "events": [...]
    }
```

4. **Store POC After Creation:**
```python
async def _handle_create_poc(...):
    # ... existing POC creation code ...
    
    # Store artifact
    if self.artifact_storage:
        try:
            storage_result = await self.artifact_storage.store_composite_artifact(
                artifact_type="poc",
                artifact_data=artifacts,
                tenant_id=context.tenant_id,
                metadata={
                    "execution_id": context.execution_id,
                    "session_id": context.session_id
                }
            )
            
            if storage_result.get("success"):
                artifacts["artifact_id"] = storage_result["artifact_id"]
                artifacts["storage_path"] = storage_result["storage_path"]
        except Exception as e:
            self.logger.warning(f"Failed to store POC artifact: {e}")
    
    return {
        "artifacts": artifacts,
        "events": [...]
    }
```

---

#### 5.3 Operations Orchestrator (Day 6)

**File:** `symphainy_platform/realms/operations/orchestrators/operations_orchestrator.py`

**Changes:**

1. **Inject Artifact Storage:**
```python
def __init__(self, public_works: Optional[Any] = None):
    # ... existing code ...
    self.artifact_storage = None
    if public_works:
        self.artifact_storage = public_works.get_artifact_storage_abstraction()
```

2. **Store Workflow After Creation:**
```python
async def _handle_create_workflow(...):
    # ... existing workflow creation code ...
    
    # Store artifact (same pattern as Journey Orchestrator)
    if self.artifact_storage:
        try:
            storage_result = await self.artifact_storage.store_composite_artifact(
                artifact_type="workflow",
                artifact_data=artifacts,
                tenant_id=context.tenant_id,
                metadata={
                    "execution_id": context.execution_id,
                    "session_id": context.session_id,
                    "workflow_file_path": workflow_file_path
                }
            )
            
            if storage_result.get("success"):
                artifacts["artifact_id"] = storage_result["artifact_id"]
                artifacts["storage_path"] = storage_result["storage_path"]
        except Exception as e:
            self.logger.warning(f"Failed to store workflow artifact: {e}")
    
    return {
        "artifacts": artifacts,
        "events": [...]
    }
```

---

### Phase 6: Visual Storage Fix (Day 7) 🟡

**Update:** `symphainy_platform/foundations/public_works/abstractions/visual_generation_abstraction.py`

**Issues:**
- Storage is optional (`if self.file_storage:`)
- Exceptions are caught and ignored
- May not be executing

**Fixes:**

1. **Make Storage Required:**
```python
# Before
if result.success and self.file_storage:
    try:
        # Store visualization
    except Exception as e:
        self.logger.warning(f"Failed to store workflow visualization: {e}")

# After
if result.success:
    if not self.file_storage:
        self.logger.error("File storage not available, cannot store visualization")
        # Still return result, but log error
    else:
        try:
            # Store visualization
            visual_path = f"visuals/{tenant_id}/workflows/{workflow_data.get('id', 'unknown')}.png"
            image_bytes = base64.b64decode(result.image_base64)
            
            upload_result = await self.file_storage.upload_file(
                file_path=visual_path,
                file_data=image_bytes,
                metadata={
                    "visualization_type": "workflow",
                    "tenant_id": tenant_id,
                    "workflow_id": workflow_data.get("id")
                }
            )
            
            if upload_result.get("success"):
                result.metadata["storage_path"] = visual_path
            else:
                self.logger.error(f"Failed to store workflow visualization: {upload_result.get('error')}")
        except Exception as e:
            self.logger.error(f"Failed to store workflow visualization: {e}", exc_info=True)
            # Don't fail entire operation, but log error
```

2. **Ensure File Storage is Available:**
```python
# In VisualGenerationAbstraction.__init__
def __init__(
    self,
    visual_generation_adapter: VisualGenerationAdapter,
    file_storage_abstraction: Optional[FileStorageAbstraction] = None
):
    # ... existing code ...
    
    # Make file_storage required (or at least warn if missing)
    if not file_storage_abstraction:
        self.logger.warning("File storage abstraction not provided - visuals will not be persisted")
    
    self.file_storage = file_storage_abstraction
```

3. **Update Public Works to Provide File Storage:**
```python
# In foundation_service.py, when creating VisualGenerationAbstraction
self.visual_generation_abstraction = VisualGenerationAbstraction(
    visual_generation_adapter=self.visual_generation_adapter,
    file_storage_abstraction=self.file_storage_abstraction  # Ensure this is set
)
```

---

### Phase 7: Hybrid Embeddings Correlation Map (Day 8) 🟡

**Update:** Hybrid embedding storage to include correlation map

**File:** `symphainy_platform/realms/content/enabling_services/embedding_service.py` (or wherever hybrid embeddings are stored)

**Changes:**

1. **Store Correlation Map:**
```python
async def store_hybrid_embeddings(
    file_id: str,
    structured_embeddings: List[Dict],
    unstructured_embeddings: List[Dict],
    correlation_map: Dict[str, Any],
    tenant_id: str,
    artifact_storage: ArtifactStorageAbstraction
) -> Dict[str, Any]:
    """
    Store hybrid embeddings with correlation map.
    
    Structured and unstructured embeddings stored in ArangoDB.
    Correlation map stored as artifact in GCS.
    """
    # Store correlation map as artifact
    artifact_data = {
        "file_id": file_id,
        "correlation_map": correlation_map,
        "components": {
            "structured": {
                "storage": "arango",
                "collection": "embeddings",
                "query": {"hybrid_file_id": file_id, "hybrid_part_type": "structured"}
            },
            "unstructured": {
                "storage": "arango",
                "collection": "embeddings",
                "query": {"hybrid_file_id": file_id, "hybrid_part_type": "unstructured"}
            }
        }
    }
    
    storage_result = await artifact_storage.store_composite_artifact(
        artifact_type="hybrid_embeddings",
        artifact_data=artifact_data,
        tenant_id=tenant_id,
        metadata={
            "file_id": file_id
        }
    )
    
    return storage_result
```

---

### Phase 8: Artifact Retrieval API (Days 9-10) 🟢

**Create:** Runtime API endpoint for artifact retrieval

**File:** `symphainy_platform/runtime/runtime_api.py`

**Endpoint:** `GET /api/artifacts/{artifact_id}?tenant_id={tenant_id}`

**Implementation:**
```python
@app.get("/api/artifacts/{artifact_id}")
async def get_artifact(
    artifact_id: str,
    tenant_id: str,
    runtime_api: RuntimeAPI = Depends(get_runtime_api)
):
    """Get artifact by ID."""
    artifact = await runtime_api.get_artifact(artifact_id, tenant_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact

# Add to RuntimeAPI class
async def get_artifact(
    self,
    artifact_id: str,
    tenant_id: str
) -> Optional[Dict[str, Any]]:
    """Get artifact by ID."""
    if not self.artifact_storage:
        raise HTTPException(status_code=500, detail="Artifact storage not available")
    
    artifact = await self.artifact_storage.get_artifact(artifact_id, tenant_id)
    return artifact
```

---

## Storage Structure

### GCS Bucket Organization

```
GCS Bucket: symphainy-bucket-2025
├── artifacts/
│   ├── workflows/
│   │   └── {tenant_id}/
│   │       └── {workflow_id}.json
│   ├── sops/
│   │   └── {tenant_id}/
│   │       └── {sop_id}.json
│   ├── blueprints/
│   │   └── {tenant_id}/
│   │       └── {blueprint_id}.json
│   ├── solutions/
│   │   └── {tenant_id}/
│   │       └── {solution_id}.json
│   ├── roadmaps/
│   │   └── {tenant_id}/
│   │       └── {roadmap_id}.json
│   ├── pocs/
│   │   └── {tenant_id}/
│   │       └── {poc_id}.json
│   ├── hybrid_embeddings/
│   │   └── {tenant_id}/
│   │       └── {artifact_id}/
│   │           ├── manifest.json
│   │           └── correlation.json
│   └── visuals/
│       ├── workflows/
│       │   └── {tenant_id}/
│       │       └── {workflow_id}/
│       │           └── workflow_visual.png
│       ├── sops/
│       │   └── {tenant_id}/
│       │       └── {sop_id}/
│       │           └── sop_visual.png
│       ├── blueprints/
│       │   └── {tenant_id}/
│       │       └── {blueprint_id}/
│       │           ├── current_state_chart.png
│       │           └── coexistence_state_chart.png
│       ├── solutions/
│       │   └── {tenant_id}/
│       │       └── {solution_id}/
│       │           └── summary_visual.png
│       └── roadmaps/
│           └── {tenant_id}/
│               └── {roadmap_id}/
│                   └── roadmap_visual.png
```

### Supabase Metadata Structure

**Table:** `project_files` (extended)

**Artifact Record:**
```json
{
  "uuid": "artifact_123",
  "user_id": "user_456",
  "tenant_id": "tenant_789",
  "ui_name": "workflow_123",
  "file_path": "artifacts/workflows/tenant_789/workflow_123.json",
  "artifact_type": "workflow",
  "file_type": "artifact",
  "mime_type": "application/json",
  "file_size": 10240,
  "status": "active",
  "metadata": {
    "execution_id": "exec_123",
    "session_id": "session_456",
    "component_count": 2,
    "has_visuals": true,
    "visual_paths": ["workflow_visual"]
  },
  "created_at": "2026-01-17T...",
  "updated_at": "2026-01-17T...",
  "deleted": false
}
```

---

## Implementation Checklist

### Phase 1: Foundation (Days 1-3)
- [ ] Create `ArtifactStorageProtocol`
- [ ] Create `ArtifactStorageAbstraction`
- [ ] Implement `store_artifact()` method
- [ ] Implement `get_artifact()` method
- [ ] Implement `list_artifacts()` method
- [ ] Implement `delete_artifact()` method
- [ ] Implement `store_composite_artifact()` method
- [ ] Add Supabase schema extension (artifact_type column)
- [ ] Integrate with Public Works Foundation Service
- [ ] Test artifact storage and retrieval

### Phase 2: Orchestrator Integration (Days 4-6)
- [ ] Update Journey Orchestrator (workflows, SOPs, blueprints)
- [ ] Update Outcomes Orchestrator (solutions, roadmaps, POCs)
- [ ] Update Operations Orchestrator (workflows)
- [ ] Test artifact storage after creation
- [ ] Verify artifacts are retrievable

### Phase 3: Visual Storage Fix (Day 7)
- [ ] Fix `VisualGenerationAbstraction` storage
- [ ] Make storage required (not optional)
- [ ] Ensure file_storage is always available
- [ ] Test visual storage
- [ ] Verify visuals are stored correctly

### Phase 4: Hybrid Embeddings (Day 8)
- [ ] Verify correlation map storage
- [ ] Store correlation map as artifact
- [ ] Link to ArangoDB embeddings
- [ ] Test hybrid embedding retrieval

### Phase 5: API & Testing (Days 9-10)
- [ ] Create artifact retrieval API endpoint
- [ ] Test artifact retrieval
- [ ] Update execution completion tests
- [ ] Verify all artifacts are stored
- [ ] Verify all artifacts are retrievable

---

## Testing Strategy

### Unit Tests
- Test `ArtifactStorageAbstraction` methods
- Test composite artifact storage
- Test visual extraction and storage
- Test artifact retrieval

### Integration Tests
- Test artifact storage after intent execution
- Test artifact retrieval after execution
- Test multi-component artifacts (blueprints, roadmaps)
- Test visual storage and retrieval

### E2E Tests
- Test complete workflow: Create → Store → Retrieve
- Test blueprint storage and retrieval
- Test solution synthesis storage and retrieval

---

## Success Criteria

### Phase 1 Complete When:
- ✅ Artifact storage abstraction created
- ✅ Can store and retrieve artifacts
- ✅ Supabase schema extended
- ✅ Integrated with Public Works

### Phase 2 Complete When:
- ✅ All orchestrators store artifacts
- ✅ All artifacts have artifact_id
- ✅ All artifacts have storage_path
- ✅ Artifacts persist after execution

### Phase 3 Complete When:
- ✅ Visuals are stored correctly
- ✅ Visuals are retrievable
- ✅ Visual storage is required (not optional)

### Phase 4 Complete When:
- ✅ Hybrid embeddings correlation map stored
- ✅ Correlation map links to ArangoDB embeddings
- ✅ Hybrid embeddings retrievable as integrated whole

### Phase 5 Complete When:
- ✅ Artifact retrieval API working
- ✅ All tests passing
- ✅ Platform validated to store and retrieve artifacts

---

## Risk Mitigation

### Risk 1: Supabase Schema Changes
**Mitigation:** Use migration script, test in dev first

### Risk 2: GCS Storage Costs
**Mitigation:** Monitor usage, implement cleanup for old artifacts

### Risk 3: Large Artifacts
**Mitigation:** Use composite pattern, store large components separately

### Risk 4: Visual Storage Failures
**Mitigation:** Make storage required, proper error handling

---

## Timeline Summary

| Phase | Days | Deliverables |
|-------|------|--------------|
| Phase 1: Foundation | 1-3 | Protocol, Abstraction, Schema, Integration |
| Phase 2: Orchestrators | 4-6 | Journey, Outcomes, Operations integration |
| Phase 3: Visual Fix | 7 | Visual storage fixes |
| Phase 4: Hybrid Embeddings | 8 | Correlation map storage |
| Phase 5: API & Testing | 9-10 | API endpoint, tests |
| **Total** | **8-10** | **Complete artifact storage** |

---

## Dependencies

### Required
- ✅ GCS Adapter (exists)
- ✅ Supabase File Adapter (exists)
- ✅ Public Works Foundation Service (exists)

### New
- ❌ Artifact Storage Protocol (create)
- ❌ Artifact Storage Abstraction (create)
- ❌ Supabase schema extension (create migration)

---

## Next Steps

1. **Review this plan** - Ensure alignment with architecture
2. **Begin Phase 1** - Create protocol and abstraction
3. **Test incrementally** - Test each phase before moving to next
4. **Integrate systematically** - Update orchestrators one at a time

---

**Last Updated:** January 17, 2026  
**Status:** 📋 **READY FOR IMPLEMENTATION**  
**Priority:** 🔴 **CRITICAL**
