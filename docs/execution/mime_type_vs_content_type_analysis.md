# mime_type vs content_type Analysis

**Date:** January 2026  
**Status:** 📋 **CODEBASE ANALYSIS**  
**Purpose:** Determine if mime_type and content_type serve different purposes

---

## 🔍 Current Code Analysis

### What the Code Currently Does

#### 1. Ingestion Flow (content_orchestrator.py)

**Line 175:** Gets `mime_type` from parameters
```python
mime_type = intent.parameters.get("mime_type", "application/octet-stream")
```

**Line 185:** Maps `mime_type` to `content_type` in source_metadata
```python
source_metadata.update({
    "ui_name": ui_name,
    "file_type": file_type,  # structured/unstructured/hybrid
    "content_type": mime_type,  # MIME type (e.g., application/pdf)
    ...
})
```

**Observation:** Code accepts `mime_type` parameter but stores it as `content_type` in metadata.

---

#### 2. File Storage (file_storage_abstraction.py)

**Line 73-86:** Determines `content_type` (MIME type) from metadata or file path
```python
content_type = None
if metadata:
    content_type = metadata.get("content_type")  # Gets from metadata

if not content_type:
    # Try to infer from file path
    if file_path.endswith('.parquet'):
        content_type = 'application/parquet'
    elif file_path.endswith('.json'):
        content_type = 'application/json'
    elif file_path.endswith('.csv'):
        content_type = 'text/csv'
    else:
        content_type = 'application/octet-stream'
```

**Line 116:** Stores `content_type` in Supabase
```python
file_metadata = {
    ...
    "content_type": content_type,  # MIME type stored here
    ...
}
```

**Observation:** `content_type` is used to store MIME type (e.g., `application/pdf`).

---

#### 3. File Type vs Content Type

**Line 174-175 (content_orchestrator.py):**
```python
file_type = intent.parameters.get("file_type", "unstructured")  # structured/unstructured/hybrid
mime_type = intent.parameters.get("mime_type", "application/octet-stream")  # MIME type
```

**Observation:** 
- `file_type` = `structured`/`unstructured`/`hybrid` (parsing pathway)
- `mime_type` = MIME type like `application/pdf` (file format)

**These are DIFFERENT concepts:**
- `file_type` determines parsing pathway (which parser to use)
- `mime_type` determines file format (for rendering, storage, etc.)

---

### Current Schema Constraint Issue

**Current Supabase schema has:**
```sql
constraint project_files_content_type_check check (
    (
      content_type = any (
        array[
          'structured'::text,
          'unstructured'::text,
          'hybrid'::text
        ]
      )
    )
  )
```

**This is WRONG!** The constraint is on `content_type` but checks for `structured`/`unstructured`/`hybrid`, which are `file_type` values, not MIME types.

**The constraint should be on `file_type`, not `content_type`.**

---

## 🎯 Intended Purpose (Based on Your Description)

### content_type (for Parsing Tools) - BUT CODE USES `file_type` INSTEAD
- **Your Intended Purpose:** Determine parsing pathway (structured/unstructured/hybrid)
- **Values:** `structured`, `unstructured`, `hybrid`
- **Usage:** Parsing tools use this to determine which parser to use
- **Current Code Reality:** Code uses `file_type` field for this purpose (line 99, 105 in file_parser_service.py)

### mime_type (for File Format)
- **Purpose:** Track actual MIME type of file
- **Values:** `application/pdf`, `text/csv`, `application/json`, etc.
- **Usage:** Rendering, storage, file format identification
- **Current Code Reality:** Code accepts `mime_type` parameter but stores it as `content_type` (confusing!)

---

## ❌ Current Code Problem

**The code is NOT using them for different purposes:**

1. **`file_type`** is used for structured/unstructured/hybrid (parsing pathway) - **CORRECT**
2. **`mime_type`** parameter is accepted but stored as `content_type` in metadata - **CONFUSING**
3. **`content_type`** in storage is storing MIME type, not parsing pathway - **WRONG NAME**

**The code is conflating:**
- `content_type` in storage = MIME type (should be `mime_type` for clarity)
- `file_type` = parsing pathway (structured/unstructured/hybrid) - **CORRECT**

**FileParserService Analysis (file_parser_service.py):**
- Line 99: Gets `file_type` from metadata (structured/unstructured/hybrid) ✅
- Line 105: Uses `file_type` to determine parsing pathway ✅
- Line 206-257: `_determine_parsing_type` uses `file_type` parameter (structured/unstructured/hybrid) ✅
- Line 259-350: `_get_parsing_abstraction` uses parsing_type + file extension to select specific parser ✅

**Conclusion:** Parsing tools use `file_type` (structured/unstructured/hybrid) correctly. The issue is that MIME type is stored as `content_type` when it should be `mime_type`.

---

## ✅ Recommendation: Use `mime_type` for MIME Type (Industry Standard)

**Rationale:**
- ✅ **Industry standard name** - `mime_type` is what the world expects
- ✅ **Clear separation** - `file_type` for parsing pathway, `mime_type` for file format
- ✅ **Aligns with your intended purpose** - You described them as serving different purposes
- ✅ **Less confusion** - No ambiguity about what each field means

**Schema:**
```sql
file_type TEXT NOT NULL DEFAULT 'unstructured',  -- structured/unstructured/hybrid (parsing pathway)
mime_type TEXT,  -- MIME type (e.g., application/pdf, text/csv) - for rendering, storage
```

**Note:** `content_type` was your original vision for parsing pathway, but code uses `file_type` for that. Since `file_type` works well and is already in use, we should:
- Keep `file_type` for parsing pathway (structured/unstructured/hybrid)
- Use `mime_type` for MIME type (application/pdf, etc.)
- Remove `content_type` (or keep as alias for backward compatibility)

**Code Changes Needed:**
1. Update `file_storage_abstraction.py` to use `mime_type` instead of `content_type`
2. Update Supabase schema to have `mime_type` field
3. Remove `content_type` field (or keep as alias for backward compatibility)

---

---

## 🎯 Final Recommendation

**Use `mime_type` for MIME type** because:

1. ✅ **Industry Standard** - `mime_type` is what the world expects
2. ✅ **Clear Separation** - `file_type` for parsing pathway, `mime_type` for file format
3. ✅ **Your Intended Purpose** - Matches your description (different purposes)
4. ✅ **Less Confusion** - No ambiguity about what each field means
5. ✅ **Code Already Accepts It** - Code accepts `mime_type` parameter, just needs to store it correctly

**Schema:**
```sql
file_type TEXT NOT NULL DEFAULT 'unstructured',  -- structured/unstructured/hybrid (parsing pathway)
mime_type TEXT,  -- MIME type (e.g., application/pdf, text/csv) - for rendering, storage
```

**Constraint Fix:**
```sql
ALTER TABLE project_files ADD CONSTRAINT project_files_file_type_check 
    CHECK (file_type IN ('structured', 'unstructured', 'hybrid'));
```

---

## 📋 Code Updates Needed

### 1. File Storage Abstraction

**Current (line 116):**
```python
"content_type": content_type,  # MIME type
```

**Should be:**
```python
"mime_type": mime_type,  # MIME type
```

### 2. Content Orchestrator

**Current (line 185):**
```python
"content_type": mime_type,  # Maps mime_type param to content_type field
```

**Should be:**
```python
"mime_type": mime_type,  # Store mime_type directly
```

### 3. Supabase Schema

**Remove:**
- `content_type` field (or keep as alias)

**Add/Keep:**
- `mime_type` field
- `file_type` field (with constraint)

---

## ✅ Validation

After changes:

- [ ] **`file_type`** stores `structured`/`unstructured`/`hybrid` (parsing pathway)
- [ ] **`mime_type`** stores MIME type like `application/pdf` (file format)
- [ ] **Constraint** is on `file_type`, not `mime_type`
- [ ] **Code** uses `mime_type` consistently for MIME type
- [ ] **Parsing tools** use `file_type` to determine pathway
- [ ] **Rendering** uses `mime_type` for file format

---

**Status:** 📋 **ANALYSIS COMPLETE - RECOMMENDATION: USE `mime_type` FOR MIME TYPE**
