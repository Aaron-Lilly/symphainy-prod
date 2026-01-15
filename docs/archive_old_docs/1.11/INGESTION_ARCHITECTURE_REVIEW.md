# Extensible Ingestion Architecture Review

**Date:** January 2026  
**Status:** ⚠️ **NEEDS CORRECTION** (API signature mismatch)

---

## ✅ Overall Assessment

The architecture design is **sound and well-thought-out**. The approach of converging all ingestion methods at File Storage before parsing is correct and preserves the existing flow.

---

## ⚠️ Issues Found

### Issue 1: `store_file()` API Mismatch

**Location:** `docs/EXTENSIBLE_INGESTION_ARCHITECTURE.md` lines 529-534

**Problem:**
The ingestion service calls `store_file()` with incorrect parameters:

```python
# ❌ WRONG (from design doc)
await self.state_surface.store_file(
    file_id=ingestion_result.file_id,
    file_reference=ingestion_result.file_reference,
    tenant_id=request.tenant_id,
    metadata=ingestion_result.ingestion_metadata
)
```

**Actual `store_file()` signature:**
```python
async def store_file(
    self,
    session_id: str,
    tenant_id: str,
    file_data: bytes,  # ← Required!
    filename: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str
```

**Root Cause:**
The ingestion adapters already store files via `FileStorageAbstraction.upload_file()`. We don't need to call `store_file()` again - we just need to store the **reference** in State Surface.

**Solution:**
Create a new method `store_file_reference()` that stores only the metadata/reference (no file data):

```python
async def store_file_reference(
    self,
    session_id: str,
    tenant_id: str,
    file_reference: str,
    storage_location: str,
    filename: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Store file reference in State Surface (file already stored in FileStorageAbstraction).
    
    Use this when the file has already been stored via FileStorageAbstraction
    and you just need to register the reference in State Surface.
    
    Args:
        session_id: Session identifier
        tenant_id: Tenant identifier
        file_reference: File reference string (e.g., "file:tenant:session:id")
        storage_location: Where file is stored (GCS path, ArangoDB doc ID, etc.)
        filename: Original filename
        metadata: Optional file metadata
    
    Returns:
        File reference string (same as input)
    """
    # Store only metadata/reference in State Surface
    file_state = {
        "storage_location": storage_location,
        "filename": filename,
        "size": metadata.get("size") if metadata else None,
        "file_hash": metadata.get("file_hash") if metadata else None,
        "metadata": metadata or {},
        "created_at": self.clock.now_iso()
    }
    
    # Store metadata in State Surface
    state_id = file_reference
    success = await self.state_abstraction.store_state(
        state_id=state_id,
        state_data=file_state,
        metadata={
            "backend": "redis",
            "strategy": "hot",
            "type": "file_metadata",
            "tenant_id": tenant_id,
            "session_id": session_id
        },
        ttl=86400
    ) if self.state_abstraction else False
    
    if not success and not self.use_memory:
        self._memory_store[state_id] = file_state
        self.logger.warning(f"State abstraction failed, using in-memory storage for file metadata: {file_reference}")
    elif self.use_memory:
        self._memory_store[state_id] = file_state
    
    self.logger.debug(f"File reference stored: {file_reference} -> {storage_location}")
    return file_reference
```

**Updated Ingestion Service:**
```python
# Step 2: Store file reference in State Surface
# File already stored by adapter, just register the reference
await self.state_surface.store_file_reference(
    session_id=request.session_id,
    tenant_id=request.tenant_id,
    file_reference=ingestion_result.file_reference,
    storage_location=ingestion_result.ingestion_metadata.get("storage_location"),  # From adapter
    filename=ingestion_result.ingestion_metadata.get("original_filename", ingestion_result.file_id),
    metadata=ingestion_result.ingestion_metadata
)
```

---

## ✅ What's Good

1. **Architecture Pattern** - Converging at File Storage is correct
2. **Preserves Existing Flow** - Upload pathway unchanged
3. **Extensible Design** - Easy to add new adapters
4. **Protocol-Based** - Clean abstraction layers
5. **Unified Interface** - Single abstraction for all methods

---

## 📋 Recommendations

### 1. Update Ingestion Adapters to Return `storage_location`

**Current:**
```python
# IngestionResult doesn't include storage_location
@dataclass
class IngestionResult:
    success: bool
    file_id: str
    file_reference: str
    ingestion_metadata: Dict[str, Any]
    error: Optional[str] = None
```

**Recommended:**
```python
@dataclass
class IngestionResult:
    success: bool
    file_id: str
    file_reference: str
    storage_location: str  # ← ADD THIS
    ingestion_metadata: Dict[str, Any]
    error: Optional[str] = None
```

**Update adapters to return storage_location:**
```python
# In UploadAdapter, EDIAdapter, APIAdapter
return IngestionResult(
    success=True,
    file_id=result["file_id"],
    file_reference=result.get("file_reference", result["file_id"]),
    storage_location=file_path,  # ← The path used in upload_file()
    ingestion_metadata={...}
)
```

### 2. Add `store_file_reference()` to StateSurface

As described above - this method stores only the reference when the file is already in FileStorageAbstraction.

### 3. Update Ingestion Service Implementation

Use `store_file_reference()` instead of `store_file()` since files are already stored by adapters.

---

## 🔄 Corrected Flow

```
Ingestion Adapter
  ↓ (stores file via FileStorageAbstraction.upload_file())
  ↓ (returns IngestionResult with storage_location)
Ingestion Service
  ↓ (calls state_surface.store_file_reference())
  ↓ (stores only metadata/reference in State Surface)
Content Orchestrator
  ↓ (uses file_reference to parse)
Parse → Data Mash
```

---

## ✅ Summary

**Overall:** ✅ **GOOD DESIGN** (needs API correction)

**Issues:**
1. ⚠️ `store_file()` API mismatch - needs `store_file_reference()` method
2. ⚠️ `IngestionResult` should include `storage_location`

**Action Items:**
1. Add `store_file_reference()` to StateSurface
2. Update `IngestionResult` to include `storage_location`
3. Update ingestion adapters to return `storage_location`
4. Update ingestion service to use `store_file_reference()`

**No architectural changes needed** - just API corrections.
