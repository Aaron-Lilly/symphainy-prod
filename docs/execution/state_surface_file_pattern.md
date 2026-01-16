# State Surface File Access Pattern

**Date:** January 2026  
**Status:** ✅ **ARCHITECTURAL PATTERN CONFIRMED**  
**Purpose:** Document the correct pattern for file access via State Surface

---

## 🎯 Architectural Principle

**State Surface is NOT a file store. It stores file references and metadata.**

| Component | Stores | Purpose |
|-----------|--------|---------|
| **State Surface** | File references, metadata, storage_location | Execution state, governance, observability |
| **FileStorageAbstraction** | Actual file data (bytes) | Durable file storage (GCS, ArangoDB) |

---

## 📋 Correct File Flow

### 1. File Upload Flow

```
User uploads file
  ↓
Content Realm: ingest_file intent
  ↓
FileStorageAbstraction.upload_file()
  ├─> Upload to GCS (file data)
  └─> Store metadata in Supabase
  ↓
Returns: file_id, file_path
  ↓
StateSurface.store_file_reference()
  ├─> Store file_reference: "file:tenant:session:file_id"
  ├─> Store storage_location: "gcs://bucket/path"
  ├─> Store metadata: {filename, size, hash, ui_name}
  └─> NOT storing file data (that's in GCS)
```

### 2. File Parsing Flow

```
Content Realm: parse_content intent
  ↓
Create file_reference: "file:tenant:session:file_id"
  ↓
FileParsingRequest(file_reference=..., state_surface=context.state_surface)
  ↓
Parsing Abstraction.parse_file(request)
  ↓
StateSurface.get_file(file_reference)
  ├─> Get storage_location from State Surface metadata
  └─> FileStorageAbstraction.download_file(storage_location)
  ↓
Parse file data
  ↓
Store parsed result in GCS
  ↓
Register parsed file reference in State Surface
```

---

## 🔧 Implementation Requirements

### StateSurface Methods Needed

1. **`store_file_reference()`**
   - Store file reference in State Surface
   - Store storage_location (GCS path)
   - Store metadata (filename, size, hash, ui_name)
   - **NOT** storing file data

2. **`get_file()`**
   - Get file_reference from State Surface
   - Extract storage_location from metadata
   - Call FileStorageAbstraction.download_file()
   - Return file data (bytes)

3. **`get_file_metadata()`**
   - Get file metadata from State Surface
   - Return metadata dict (filename, size, storage_location, etc.)

### File Reference Format

```
file_reference = f"file:{tenant_id}:{session_id}:{file_id}"
```

Example: `"file:acme_corp:session_123:file_abc123"`

---

## ✅ Benefits

1. **Governance**: All file access goes through Runtime (State Surface)
2. **Observability**: All file operations are logged in State Surface
3. **Replayability**: Execution can be replayed using State Surface references
4. **Separation**: File storage (GCS) separate from execution state (State Surface)
5. **Scalability**: Large files in GCS, small references in State Surface

---

## 🚫 Anti-Patterns to Avoid

❌ **Storing file data in State Surface**
- State Surface should only store references

❌ **Direct GCS access from parsing abstractions**
- All file access should go through State Surface

❌ **Passing file bytes directly to parsing abstractions**
- Use file_reference instead

---

## 📝 Next Steps

1. Add file reference methods to StateSurface
2. Update ingest_file to register file reference
3. Update parsing to use State Surface references
4. Ensure all parsing abstractions use State Surface pattern
