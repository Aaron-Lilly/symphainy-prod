# Ingestion Architecture Corrections

**Date:** January 2026  
**Status:** ✅ **CORRECTIONS APPLIED**

---

## Changes Made

### 1. Added `store_file_reference()` to StateSurface

**Location:** `symphainy_platform/runtime/state_surface.py`

**Purpose:** Store file reference when file is already in FileStorageAbstraction (used by ingestion services).

**Signature:**
```python
async def store_file_reference(
    self,
    session_id: str,
    tenant_id: str,
    file_reference: str,
    storage_location: str,
    filename: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str
```

### 2. Updated StateSurface Class Docstring

Added explicit documentation about architectural principles and file storage patterns.

---

## Updated Ingestion Service Implementation

**Corrected Implementation:**

```python
# Step 2: Store file reference in State Surface
# File already stored by adapter, just register the reference
await self.state_surface.store_file_reference(
    session_id=request.session_id,
    tenant_id=request.tenant_id,
    file_reference=ingestion_result.file_reference,
    storage_location=ingestion_result.storage_location,  # From adapter
    filename=ingestion_result.ingestion_metadata.get("original_filename", ingestion_result.file_id),
    metadata=ingestion_result.ingestion_metadata
)
```

---

## Required Updates to Ingestion Architecture Design

### Update `IngestionResult` Dataclass

**Add `storage_location` field:**

```python
@dataclass
class IngestionResult:
    """Unified ingestion result."""
    success: bool
    file_id: str
    file_reference: str
    storage_location: str  # ← ADD THIS
    ingestion_metadata: Dict[str, Any]
    error: Optional[str] = None
```

### Update Adapters to Return `storage_location`

**UploadAdapter:**
```python
return IngestionResult(
    success=True,
    file_id=result["file_id"],
    file_reference=result.get("file_reference", result["file_id"]),
    storage_location=file_path,  # ← The path used in upload_file()
    ingestion_metadata={
        "ingestion_type": "upload",
        "original_filename": filename
    }
)
```

**EDIAdapter:**
```python
return IngestionResult(
    success=True,
    file_id=result["file_id"],
    file_reference=result.get("file_reference", result["file_id"]),
    storage_location=file_path,  # ← The path used in upload_file()
    ingestion_metadata={
        "ingestion_type": "edi",
        "edi_protocol": edi_protocol,
        "partner_id": partner_id,
        "transaction_type": transaction_type
    }
)
```

**APIAdapter:**
```python
return IngestionResult(
    success=True,
    file_id=result["file_id"],
    file_reference=result.get("file_reference", result["file_id"]),
    storage_location=file_path,  # ← The path used in upload_file()
    ingestion_metadata={
        "ingestion_type": "api",
        "api_type": api_type,
        "endpoint": endpoint
    }
)
```

---

## Summary

✅ **StateSurface compliance:** Fully compliant with guiding principles  
✅ **Ingestion architecture:** Design is sound, API corrections applied  
✅ **Ready for implementation:** All corrections documented

**Next Steps:**
1. Update `EXTENSIBLE_INGESTION_ARCHITECTURE.md` with corrected API calls
2. Implement Phase 1 (Foundation) with corrected signatures
3. Test with existing upload flow
