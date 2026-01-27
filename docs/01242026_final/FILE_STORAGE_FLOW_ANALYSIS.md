# File Storage Flow Analysis & Recommendations

**Date:** January 26, 2026  
**Context:** Resolving 500 error for `extract_embeddings` revealed architectural concerns about file storage flow

---

## 1. What's Happening Today

### Current Storage Flow

#### **parse_content Intent Flow:**
1. **Parse file** → Creates `FileParsingResult` with structured/text content
2. **Store in GCS** → Uploads parsed JSON to `parsed/{tenant_id}/{parsed_file_id}.json`
3. **Register in State Surface** → Stores reference with `storage_location` pointing to GCS path
4. **Track in Supabase** → Stores **metadata/lineage only** (via `_track_parsed_result`)

#### **get_parsed_file Current Implementation (BROKEN):**
```python
# Current broken flow:
1. Query Supabase via FileManagementAbstraction.get_parsed_file()
   → Supabase only has metadata, NOT actual parsed content
   → Returns None or metadata without content
2. Fallback to State Surface
   → State Surface has reference with storage_location
   → But code tries to get "parsed_content" from metadata (doesn't exist)
```

### The Problem

**❌ Architectural Violation:**
- `FileManagementAbstraction.get_parsed_file()` queries Supabase for parsed file **content**
- But Supabase only stores **metadata/lineage** (parsed_file_id, file_id, parser_type, record_count, etc.)
- Actual parsed content is stored in **GCS** at path `parsed/{tenant_id}/{parsed_file_id}.json`
- State Surface has the **reference** with `storage_location` pointing to GCS

**Result:** `get_parsed_file()` fails because it's looking for content in the wrong place.

---

## 2. What Should Be Happening (Correct Architecture)

### Correct Storage Pattern (Per User's Understanding)

```
┌─────────────────────────────────────────────────────────────┐
│                    Storage Architecture                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Supabase (Metadata & Lineage)                               │
│  ├── files table: file_id, ui_name, storage_location, ...   │
│  ├── parsed_data_files: parsed_file_id, file_id,             │
│  │                       parser_type, record_count, ...       │
│  └── embeddings: embedding_id, parsed_file_id, ...           │
│                                                               │
│  GCS (Actual File Content)                                    │
│  ├── files/{file_id}: Original file content                   │
│  └── parsed/{tenant_id}/{parsed_file_id}.json: Parsed data   │
│                                                               │
│  DuckDB (Deterministic Embeddings)                            │
│  └── Schema fingerprints, pattern signatures                 │
│      (Supabase tracks: deterministic_embedding_id, lineage)  │
│                                                               │
│  ArangoDB (Semantic Embeddings)                               │
│  └── Vector embeddings, semantic graph                       │
│      (Supabase tracks: embedding_id, lineage)                │
│                                                               │
│  State Surface (References & Session State)                  │
│  ├── file:{tenant}:{session}:{file_id} → storage_location    │
│  └── parsed:{tenant}:{session}:{parsed_file_id} → storage_location │
└─────────────────────────────────────────────────────────────┘
```

### Correct Retrieval Flow (2-Step Process)

**Step 1: Find WHERE the file is stored**
- Query **Supabase** for metadata/lineage → Get `storage_location` or `parsed_file_id`
- OR Query **State Surface** for reference → Get `storage_location`

**Step 2: Get the ACTUAL file from storage**
- Use `storage_location` to download from **GCS** (for parsed files)
- OR query **DuckDB** (for deterministic embeddings)
- OR query **ArangoDB** (for semantic embeddings)

### Correct `get_parsed_file()` Implementation

```python
async def get_parsed_file(parsed_file_id: str, tenant_id: str, context: ExecutionContext):
    """
    Correct 2-step retrieval:
    1. Get metadata/reference (WHERE it's stored)
    2. Download actual content (FROM storage)
    """
    
    # Step 1: Get storage location from State Surface (preferred) or Supabase
    parsed_file_reference = f"parsed:{tenant_id}:{context.session_id}:{parsed_file_id}"
    state_metadata = await context.state_surface.get_file_metadata(parsed_file_reference)
    
    if not state_metadata:
        # Fallback: Query Supabase for lineage metadata
        # (Supabase has parsed_file_id → storage_location mapping)
        lineage_metadata = await query_supabase_lineage(parsed_file_id)
        storage_location = lineage_metadata.get("storage_location")
    else:
        storage_location = state_metadata.get("storage_location")
    
    if not storage_location:
        raise ValueError(f"Storage location not found for parsed_file_id: {parsed_file_id}")
    
    # Step 2: Download actual content from GCS
    file_storage = context.public_works.get_file_storage_abstraction()
    parsed_content_json = await file_storage.download_file(storage_location)
    
    # Parse JSON content
    import json
    parsed_content = json.loads(parsed_content_json)
    
    return {
        "parsed_file_id": parsed_file_id,
        "parsed_content": parsed_content.get("structured_data") or parsed_content.get("text_content"),
        "metadata": parsed_content.get("metadata", {})
    }
```

---

## 3. Path Forward

### Immediate Fixes Required

#### **Fix 1: Remove `get_parsed_file()` from FileManagementAbstraction**
- **Why:** FileManagementAbstraction should coordinate GCS + Supabase for **file operations**, not parsed file retrieval
- **Action:** Remove the method I incorrectly added

#### **Fix 2: Fix `file_parser_service.get_parsed_file()`**
- **Current:** Tries to get content from Supabase (wrong)
- **Correct:** 
  1. Get `storage_location` from State Surface or Supabase metadata
  2. Download actual content from GCS using `storage_location`
  3. Parse JSON and return

#### **Fix 3: Clarify FileManagementAbstraction Role**
- **Purpose:** Coordinate file operations (create, update, delete) between GCS and Supabase
- **NOT for:** Retrieving parsed files, embeddings, or other derived artifacts
- **For parsed files:** Use `file_parser_service.get_parsed_file()` which knows the 2-step flow

### Recommended Implementation

```python
# In file_parser_service.py
async def get_parsed_file(self, parsed_file_id: str, tenant_id: str, context: ExecutionContext):
    """
    Correct 2-step retrieval:
    1. Get storage_location from State Surface (has reference) or Supabase (has lineage)
    2. Download actual parsed content from GCS
    """
    
    # Step 1: Get storage location
    parsed_file_reference = f"parsed:{tenant_id}:{context.session_id}:{parsed_file_id}"
    state_metadata = await context.state_surface.get_file_metadata(parsed_file_reference)
    
    storage_location = None
    if state_metadata:
        storage_location = state_metadata.get("storage_location")
    else:
        # Fallback: Query Supabase for lineage (has storage_location in metadata)
        # This is metadata-only query, not content retrieval
        if self.public_works and self.public_works.supabase_adapter:
            lineage_query = await self.public_works.supabase_adapter.query(
                "parsed_data_files",
                filters={"parsed_file_id": parsed_file_id},
                columns=["storage_location", "parsed_file_id"]
            )
            if lineage_query:
                storage_location = lineage_query[0].get("storage_location")
    
    if not storage_location:
        raise ValueError(f"Storage location not found for parsed_file_id: {parsed_file_id}")
    
    # Step 2: Download actual content from GCS
    if not self.file_storage_abstraction:
        raise ValueError("FileStorageAbstraction not available")
    
    parsed_content_json_bytes = await self.file_storage_abstraction.download_file(storage_location)
    if not parsed_content_json_bytes:
        raise ValueError(f"Parsed file content not found at: {storage_location}")
    
    # Parse JSON
    import json
    parsed_content_json = json.loads(parsed_content_json_bytes.decode('utf-8'))
    
    return {
        "parsed_file_id": parsed_file_id,
        "parsed_content": parsed_content_json.get("structured_data") or parsed_content_json.get("text_content"),
        "metadata": parsed_content_json.get("metadata", {})
    }
```

### Architectural Principles

1. **Supabase = Metadata & Lineage Only**
   - Never stores actual file content
   - Stores references, IDs, counts, types, lineage relationships

2. **GCS = Actual File Storage**
   - Original files: `files/{file_id}`
   - Parsed files: `parsed/{tenant_id}/{parsed_file_id}.json`

3. **State Surface = Session References**
   - Maps references to `storage_location`
   - Fast lookup for session-scoped operations

4. **2-Step Retrieval Pattern**
   - Step 1: Query metadata (Supabase/State Surface) → Get `storage_location`
   - Step 2: Download from storage (GCS/DuckDB/ArangoDB) → Get actual content

---

## 4. Action Items

- [ ] **Remove** `get_parsed_file()` from `FileManagementAbstraction` (incorrect addition)
- [ ] **Fix** `file_parser_service.get_parsed_file()` to use 2-step retrieval (State Surface → GCS)
- [ ] **Add** fallback to Supabase lineage query if State Surface doesn't have reference
- [ ] **Document** the 2-step retrieval pattern for all artifact types
- [ ] **Verify** `create_deterministic_embeddings` uses correct retrieval pattern

---

## 5. Verification

After fixes, verify:
1. `parse_content` stores in GCS and registers in State Surface ✅
2. `get_parsed_file` retrieves from GCS using State Surface reference ✅
3. `create_deterministic_embeddings` can retrieve parsed content ✅
4. Supabase only stores metadata, never content ✅
