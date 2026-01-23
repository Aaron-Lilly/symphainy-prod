# Content Orchestrator File Retrieval Issue - Analysis & Fix

**Date:** January 2026  
**Status:** 🔍 **ANALYSIS**  
**Issue:** Content Orchestrator uses `state_surface.get_file()` which violates architectural boundaries

---

## The Issue

Content Orchestrator has **3 instances** where it uses `state_surface.get_file()` to retrieve file content:

### Instance 1: `_handle_retrieve_file()` - Line 1491

**Context:**
```python
# Get file contents if requested
if include_contents:
    file_contents = None
    # ✅ CORRECT: Try FileStorageAbstraction first
    if storage_location and hasattr(self, 'public_works') and self.public_works:
        file_storage = self.public_works.get_file_storage_abstraction()
        if file_storage:
            try:
                file_contents = await file_storage.download_file(storage_location)
            except Exception as e:
                self.logger.debug(f"Direct file download failed: {e}")
    
    # ❌ ANTI-PATTERN: Fallback to state_surface
    if not file_contents and file_reference:
        try:
            file_contents = await context.state_surface.get_file(file_reference)
        except Exception as e:
            self.logger.debug(f"State Surface file retrieval failed: {e}")
```

**Problem:**
- Uses `state_surface.get_file()` as a fallback
- Even though Content Realm SHOULD retrieve files, it should use FileManagementAbstraction/FileStorageAbstraction directly
- `state_surface` is for metadata/queries, not content retrieval

---

### Instance 2: `_handle_preprocess_file()` - Line 2225

**Context:**
```python
# Get file metadata
file_metadata = await context.state_surface.get_file_metadata(file_reference)  # ✅ OK - metadata query
if not file_metadata:
    raise ValueError(f"File not found in State Surface: {file_reference}")

storage_location = file_metadata.get("storage_location")
if not storage_location:
    raise ValueError(f"Storage location not found for file: {file_reference}")

# ❌ ANTI-PATTERN: Direct content retrieval from state_surface
file_contents = await context.state_surface.get_file(file_reference)
if not file_contents:
    raise ValueError(f"File contents not found: {file_reference}")
```

**Problem:**
- Gets metadata from state_surface (✅ OK)
- Gets storage_location from metadata (✅ OK)
- But then retrieves content from state_surface instead of using storage_location with FileStorageAbstraction (❌ WRONG)

---

### Instance 3: `_handle_get_semantic_interpretation()` - Line 2766

**Context:**
```python
parsed_file_reference = intent.parameters.get("parsed_file_reference")
if not parsed_file_reference:
    parsed_file_reference = f"parsed:{context.tenant_id}:{context.session_id}:{parsed_file_id}"

# ❌ ANTI-PATTERN: Direct content retrieval from state_surface
parsed_file_data = await context.state_surface.get_file(parsed_file_reference)
if not parsed_file_data:
    raise ValueError(f"Parsed file not found: {parsed_file_reference}")

# Parse JSON data
import json
parsed_result = json.loads(parsed_file_data.decode('utf-8'))
```

**Problem:**
- Should use `FileParserService.get_parsed_file()` (which we just fixed!)
- Or use FileManagementAbstraction directly
- Not state_surface.get_file()

---

## Why This Is An Issue

**Architectural Principle:**
> **Runtime records reality. Smart City governs access. Realms touch data. Agents never retrieve files directly.**

**The Problem:**
1. **Content Realm IS allowed to retrieve files** - it's the realm responsible for file operations
2. **BUT it should use FileManagementAbstraction/FileStorageAbstraction directly** - not state_surface
3. **state_surface is for metadata/queries** - "Is file available?", "What's the storage location?", etc.
4. **state_surface.get_file() collapses boundaries** - Runtime shouldn't hold/retrieve client data

**The Nuance:**
- Content Orchestrator is part of Content Realm, so it CAN retrieve files
- But it should use the proper abstractions (FileManagementAbstraction, FileStorageAbstraction)
- Not state_surface, which is a Runtime construct for metadata/state

---

## The Fix

### Fix #1: `_handle_retrieve_file()` - Remove state_surface fallback

**Current:**
```python
# Fallback: Try via State Surface
if not file_contents and file_reference:
    try:
        file_contents = await context.state_surface.get_file(file_reference)
    except Exception as e:
        self.logger.debug(f"State Surface file retrieval failed: {e}")
```

**Fixed:**
```python
# If FileStorageAbstraction failed, try FileManagementAbstraction
if not file_contents and file_reference:
    try:
        file_management = self.public_works.get_file_management_abstraction()
        if file_management:
            # Get file via FileManagementAbstraction (governed access)
            file_contents = await file_management.get_file_by_reference(file_reference)
    except Exception as e:
        self.logger.debug(f"FileManagementAbstraction retrieval failed: {e}")

# If still no file_contents, raise error (don't use state_surface)
if not file_contents:
    raise ValueError(f"Could not retrieve file contents: {file_reference}")
```

---

### Fix #2: `_handle_preprocess_file()` - Use FileStorageAbstraction

**Current:**
```python
storage_location = file_metadata.get("storage_location")
if not storage_location:
    raise ValueError(f"Storage location not found for file: {file_reference}")

# ❌ Get file contents from state_surface
file_contents = await context.state_surface.get_file(file_reference)
```

**Fixed:**
```python
storage_location = file_metadata.get("storage_location")
if not storage_location:
    raise ValueError(f"Storage location not found for file: {file_reference}")

# ✅ Get file contents from FileStorageAbstraction (using storage_location)
if not self.public_works:
    raise ValueError("Public Works required for file retrieval")

file_storage = self.public_works.get_file_storage_abstraction()
if not file_storage:
    raise ValueError("FileStorageAbstraction not available")

file_contents = await file_storage.download_file(storage_location)
if not file_contents:
    raise ValueError(f"File contents not found at storage location: {storage_location}")
```

---

### Fix #3: `_handle_get_semantic_interpretation()` - Use FileParserService

**Current:**
```python
# ❌ Get parsed file data from State Surface
parsed_file_data = await context.state_surface.get_file(parsed_file_reference)
if not parsed_file_data:
    raise ValueError(f"Parsed file not found: {parsed_file_reference}")

# Parse JSON data
import json
parsed_result = json.loads(parsed_file_data.decode('utf-8'))
```

**Fixed:**
```python
# ✅ Get parsed file via FileParserService (governed access, consistent with other services)
parsed_file = await self.file_parser_service.get_parsed_file(
    parsed_file_id=parsed_file_id,
    tenant_id=context.tenant_id,
    context=context
)

parsed_result = parsed_file.get("parsed_content")
if not parsed_result:
    raise ValueError(f"Parsed file content not found: {parsed_file_id}")
```

**Why This Is Better:**
- Uses the same pattern as other services (StructuredExtractionAgent, DataQualityService, etc.)
- Goes through FileParserService which uses FileManagementAbstraction
- Consistent architecture across the platform

---

## Summary

**The Issue:**
- Content Orchestrator uses `state_surface.get_file()` in 3 places
- Even though Content Realm SHOULD retrieve files, it should use proper abstractions
- `state_surface` is for metadata/queries, not content retrieval

**The Fix:**
1. **Instance 1:** Remove state_surface fallback, use FileManagementAbstraction as fallback
2. **Instance 2:** Use FileStorageAbstraction with storage_location (already have it!)
3. **Instance 3:** Use FileParserService.get_parsed_file() (consistent with other services)

**Key Principle:**
> Content Realm CAN retrieve files (it's the realm responsible for it), but it should use FileManagementAbstraction/FileStorageAbstraction directly, not state_surface.

---

## Architectural Clarity

**What's OK:**
- ✅ Content Realm using FileManagementAbstraction
- ✅ Content Realm using FileStorageAbstraction
- ✅ Content Realm using FileParserService
- ✅ state_surface.get_file_metadata() (metadata queries)

**What's NOT OK:**
- ❌ Content Realm using state_surface.get_file() (content retrieval)
- ❌ Any realm/agent using state_surface.get_file() (content retrieval)
- ❌ state_surface holding/retrieving client data

**The Boundary:**
- **state_surface** = Metadata, state, queries ("Is file available?", "What's the storage location?")
- **FileManagementAbstraction/FileStorageAbstraction** = Actual file content retrieval
- **Content Realm** = The realm that uses these abstractions to retrieve files
