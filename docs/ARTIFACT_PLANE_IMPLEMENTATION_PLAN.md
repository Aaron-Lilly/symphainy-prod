# Artifact Plane Implementation Plan

**Date:** January 19, 2026  
**Status:** 🚀 **Full Implementation - Do It Right**

---

## Overview

Implementing the Derived Artifact Plane as a first-class architectural layer. This is a breaking change that will properly separate artifacts from execution state.

---

## Architecture

### Artifact Plane Components

1. **Artifact Plane Abstraction** - Core interface for artifact lifecycle
2. **Artifact Registry** - Metadata storage (via StateManagementProtocol)
3. **Artifact Payload Storage** - Binary storage (via FileStorageProtocol)
4. **Artifact Lineage** - Graph relationships (via Arango)
5. **Artifact Policy** - Governance via Data Steward

### Infrastructure Mapping

- **GCS** → `FileStorageProtocol` (payloads: PDFs, images, diagrams)
- **Supabase/Postgres** → `StateManagementProtocol` (artifact registry metadata)
- **Arango** → Existing graph (lineage relationships)
- **Redis** → Existing cache (transient working memory)

---

## Implementation Steps

### Step 1: Create Artifact Plane Abstraction

**File:** `symphainy_platform/civic_systems/artifact_plane/artifact_plane.py`

**Responsibilities:**
- Artifact creation (register + store payload)
- Artifact retrieval (by artifact_id)
- Artifact lifecycle (create, update, delete)
- Artifact lineage tracking

**Interface:**
```python
class ArtifactPlane:
    async def create_artifact(
        self,
        artifact_type: str,  # "roadmap", "poc", "blueprint", etc.
        artifact_id: str,
        payload: Dict[str, Any],  # Full artifact data
        metadata: Dict[str, Any],  # Ownership, policy, etc.
        context: ExecutionContext
    ) -> Dict[str, Any]
    
    async def get_artifact(
        self,
        artifact_id: str,
        tenant_id: str,
        include_payload: bool = True
    ) -> Optional[Dict[str, Any]]
    
    async def register_lineage(
        self,
        artifact_id: str,
        source_execution_id: str,
        source_intent: str,
        context: ExecutionContext
    ) -> bool
```

---

### Step 2: Artifact Registry Schema

**Storage:** Via `StateManagementProtocol` (Supabase/Postgres)

**Schema:**
```python
{
    "artifact_id": str,  # Primary key
    "artifact_type": str,  # "roadmap", "poc", "blueprint", etc.
    "tenant_id": str,
    "session_id": str,
    "solution_id": str,
    "realm": str,  # Which realm created it
    "intent_type": str,  # Which intent created it
    "execution_id": str,  # Execution that created it
    "created_at": datetime,
    "updated_at": datetime,
    "payload_storage_path": str,  # GCS path if stored
    "payload_artifact_id": Optional[str],  # If stored in artifact storage
    "regenerable": bool,
    "retention_policy": str,
    "metadata": Dict[str, Any]  # Additional metadata
}
```

**Storage Key:** `artifact:{tenant_id}:{artifact_id}`

---

### Step 3: Update Outcomes Realm

**Files to Update:**
- `outcomes_orchestrator.py` - Use Artifact Plane for roadmap/POC creation
- `_handle_create_solution` - Retrieve from Artifact Plane

**Changes:**
1. When creating roadmap/POC:
   - Create artifact via Artifact Plane
   - Store payload in GCS (via FileStorageProtocol)
   - Register in artifact registry
   - Return artifact_id (not full artifact in execution state)

2. When creating solution:
   - Retrieve artifact from Artifact Plane using artifact_id
   - Use artifact data for solution creation

---

### Step 4: Update Runtime Integration

**Files to Update:**
- `execution_lifecycle_manager.py` - Artifact Plane integration
- `runtime_api.py` - Artifact retrieval endpoints

**Changes:**
1. After realm execution:
   - If artifacts are created, register with Artifact Plane
   - Store artifact_id in execution state (reference, not full artifact)
   - Link execution_id → artifact_id for lineage

2. Artifact retrieval:
   - New endpoint: `GET /api/artifact/{artifact_id}`
   - Retrieve from Artifact Plane, not execution state

---

### Step 5: Update Other Realms

**Realms to Update:**
- Journey Realm (blueprints, SOPs, workflows)
- Content Realm (analysis results, visualizations)
- Insights Realm (interpretations, quality reports)

**Pattern:**
- Replace artifact storage in execution state with Artifact Plane
- Return artifact_id in execution artifacts
- Full artifact retrieved from Artifact Plane

---

### Step 6: Update Tests

**Test Updates:**
- Update artifact retrieval in tests
- Use Artifact Plane for artifact creation
- Test artifact lifecycle (create, retrieve, delete)
- Test cross-realm artifact access

---

## File Structure

```
symphainy_platform/
├── civic_systems/
│   └── artifact_plane/
│       ├── __init__.py
│       ├── artifact_plane.py          # Core Artifact Plane
│       ├── artifact_registry.py       # Registry operations
│       ├── artifact_storage.py        # Payload storage
│       └── artifact_lineage.py        # Lineage tracking
├── foundations/
│   └── public_works/
│       └── abstractions/
│           └── artifact_storage_abstraction.py  # If needed
```

---

## Migration Strategy

### Breaking Changes

1. **Execution State:** Artifacts no longer stored in execution state
   - Only artifact_id references stored
   - Full artifacts retrieved from Artifact Plane

2. **API Changes:**
   - New artifact endpoints
   - Execution status may return artifact_id instead of full artifact
   - Frontend needs to retrieve artifacts separately

3. **Realm Contracts:**
   - Realms return artifact_id, not full artifacts
   - Artifact Plane handles storage

### Backward Compatibility

**Option:** Keep execution state storage as fallback during transition
- Check Artifact Plane first
- Fall back to execution state if not found
- Migrate artifacts on retrieval

**Recommendation:** Clean break - update all callers at once

---

## Implementation Order

1. ✅ Create Artifact Plane abstraction
2. ✅ Implement artifact registry (via StateManagementProtocol)
3. ✅ Implement payload storage (via FileStorageProtocol)
4. ✅ Update Outcomes Realm (roadmaps/POCs)
5. ✅ Update solution creation
6. ✅ Update Runtime integration
7. ✅ Update other realms
8. ✅ Update tests
9. ✅ Update frontend (if needed)

---

## Success Criteria

1. ✅ Artifacts stored in Artifact Plane, not execution state
2. ✅ Artifacts retrievable by artifact_id
3. ✅ Solution creation works with Artifact Plane
4. ✅ All tests pass
5. ✅ No artifacts in execution state (only references)
6. ✅ Artifact lineage tracked
7. ✅ Policy governance working

---

**Let's do this right!** 🚀
