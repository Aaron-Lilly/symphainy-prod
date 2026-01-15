# File Storage Architecture Refactoring Plan

## Issue

State Surface is currently storing **file data** directly, which violates the architecture:
- State Surface should store **metadata/references** only
- File data should be stored in **FileStorageAbstraction** (GCS/ArangoDB/Redis)

## Correct Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    State Surface                        │
│  Stores: File Reference + Metadata + Storage Location  │
│  Example: {"file_ref": "file:tenant:session:id",       │
│            "storage_location": "gcs://bucket/path",     │
│            "filename": "test.bin", "size": 1234}        │
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

## Required Changes

### 1. StateSurface.__init__()
- Add `file_storage: Optional[FileStorageProtocol]` parameter
- Create `InMemoryFileStorage` if `use_memory=True` and no file_storage provided

### 2. StateSurface.store_file()
- Store file data in `FileStorageAbstraction.upload_file()`
- Store only metadata (including `storage_location`) in State Surface
- Remove `file_data` from State Surface storage

### 3. StateSurface.get_file()
- Get `storage_location` from State Surface metadata
- Retrieve file data from `FileStorageAbstraction.download_file()`
- Remove direct file data retrieval from State Surface

### 4. StateSurface.get_file_metadata()
- Include `storage_location` in returned metadata

### 5. StateSurface.delete_file()
- Delete file data from `FileStorageAbstraction.delete_file()`
- Delete metadata from State Surface

### 6. main.py
- Pass `FileStorageAbstraction` to `StateSurface` constructor

### 7. Tests
- `InMemoryFileStorage` will be created automatically when `use_memory=True`

## Implementation Status

- ✅ Created `InMemoryFileStorage` for tests
- ✅ Updated `main.py` to pass FileStorageAbstraction
- ⏳ Need to update StateSurface methods (store_file, get_file, delete_file)
- ⏳ Need to update imports in StateSurface

## Next Steps

1. Update StateSurface imports to include FileStorageProtocol
2. Update StateSurface.__init__() to accept file_storage
3. Refactor store_file() to use FileStorageAbstraction
4. Refactor get_file() to use FileStorageAbstraction
5. Refactor delete_file() to use FileStorageAbstraction
6. Update get_file_metadata() to include storage_location
7. Test the changes
