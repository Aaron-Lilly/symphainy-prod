# File Storage Architecture Fix

## Issue Identified

State Surface is currently storing **file data** directly, which is an architectural anti-pattern. 

**Current (Wrong):**
- State Surface stores `file_data: bytes` directly
- Files stored in Redis/State Surface memory
- Not scalable for large files
- Mixes file storage with state management

**Correct Architecture:**
- **State Surface**: Stores file **metadata/references** only (where file is stored)
- **FileStorageAbstraction**: Stores actual **file data** in GCS/ArangoDB
- **State Surface** stores: `{"storage_location": "gcs://bucket/path", "filename": "...", "size": 123}`

## Architecture Pattern

```
┌─────────────────────────────────────────────────────────┐
│                    State Surface                        │
│  Stores: File Reference + Metadata + Storage Location  │
│  Example: {"file_ref": "file:tenant:session:id",       │
│            "storage_location": "gcs://bucket/path",     │
│            "filename": "test.bin", "size": 1234}          │
└─────────────────────────────────────────────────────────┘
                        │
                        │ references
                        ▼
┌─────────────────────────────────────────────────────────┐
│              FileStorageAbstraction                     │
│  Stores: Actual file data                              │
│  Backends: GCS (large files), ArangoDB (documents),    │
│            Redis (hot/cache for small files)           │
└─────────────────────────────────────────────────────────┘
```

## Implementation Plan

### 1. Update StateSurface.store_file()

**Before:**
```python
file_state = {
    "file_data": file_data,  # ❌ WRONG: Storing file data
    "filename": filename,
    ...
}
```

**After:**
```python
# Store file in FileStorageAbstraction (GCS/ArangoDB)
storage_location = await self.file_storage.upload_file(
    file_path=file_path,
    file_data=file_data,
    metadata=metadata
)

# Store only metadata/reference in State Surface
file_state = {
    "storage_location": storage_location,  # ✅ CORRECT: Reference only
    "filename": filename,
    "size": len(file_data),
    "file_hash": file_hash,
    "metadata": metadata or {},
    "created_at": self.clock.now_iso()
}
```

### 2. Update StateSurface.get_file()

**Before:**
```python
return file_state.get("file_data")  # ❌ WRONG: Getting from State Surface
```

**After:**
```python
# Get storage location from State Surface
storage_location = file_state.get("storage_location")

# Retrieve actual file from FileStorageAbstraction
file_data = await self.file_storage.download_file(storage_location)
return file_data
```

### 3. Update StateSurface.__init__()

Add FileStorageAbstraction dependency:
```python
def __init__(
    self,
    state_abstraction: Optional[StateManagementProtocol] = None,
    file_storage: Optional[FileStorageProtocol] = None,  # NEW
    use_memory: bool = False
):
    self.file_storage = file_storage
    # For tests: use in-memory file storage if no FileStorageAbstraction
    if not file_storage and use_memory:
        self.file_storage = InMemoryFileStorage()  # Mock for tests
```

### 4. Create InMemoryFileStorage for Tests

For testing without GCS/Supabase:
```python
class InMemoryFileStorage:
    """In-memory file storage for testing."""
    def __init__(self):
        self._files: Dict[str, bytes] = {}
    
    async def upload_file(self, file_path: str, file_data: bytes, ...) -> str:
        self._files[file_path] = file_data
        return file_path  # Return storage location
    
    async def download_file(self, file_path: str) -> Optional[bytes]:
        return self._files.get(file_path)
```

## Benefits

1. **Scalability**: Large files stored in GCS, not Redis
2. **Separation of Concerns**: State Surface = metadata, FileStorage = data
3. **Architecture Compliance**: Files go through proper storage abstraction
4. **Testability**: In-memory file storage for tests (no GCS needed)

## Migration Steps

1. ✅ Document the issue (this document)
2. ⏳ Update StateSurface to use FileStorageAbstraction
3. ⏳ Create InMemoryFileStorage for tests
4. ⏳ Update all file storage/retrieval calls
5. ⏳ Update tests to use new architecture
