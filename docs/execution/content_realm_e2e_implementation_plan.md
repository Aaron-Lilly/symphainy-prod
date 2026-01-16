# Content Realm E2E Implementation Plan

**Date:** January 2026  
**Status:** 📋 **IN PROGRESS**  
**Purpose:** Implement real Content Realm functionality and comprehensive E2E tests

---

## 🎯 Goals

1. **Platform Infrastructure Requirements**: Platform should fail if required adapters (GCS, Supabase, ArangoDB) are not available
2. **Real Functionality**: Implement actual file upload, parsing, previews, embeddings, and lineage
3. **Comprehensive Testing**: Verify all Content Realm features work end-to-end

---

## 📋 Implementation Tasks

### 1. Fix Infrastructure Requirements

**Task:** Make GCS adapter required (platform fails if not available)

**Changes:**
- Remove graceful degradation in `PublicWorksFoundationService._create_adapters()`
- Raise exception if GCS adapter cannot be created
- Ensure GCS credentials are properly configured

**Files:**
- `symphainy_platform/foundations/public_works/foundation_service.py`

---

### 2. Implement Real File Upload Flow

**Task:** Implement actual file upload to Supabase (metadata) and GCS (binary)

**Requirements:**
- Upload file binary to GCS
- Store file metadata in Supabase `project_files` table
- Preserve `ui_name` (user-friendly filename) throughout
- Return file UUID and metadata

**Files:**
- `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`
- `symphainy_platform/realms/content/enabling_services/file_parser_service.py`

**Integration:**
- Use `FileManagementAbstraction.create_file()` (already exists)
- Ensure `ui_name` is preserved in metadata

---

### 3. Implement Real File Parsing

**Task:** Implement parsing for all file types

**File Types to Support:**
- **Structured**: CSV, Excel (XLSX), JSON, Binary (with copybook)
- **Unstructured**: PDF, Word (DOCX), Text (TXT), HTML, Images
- **Hybrid**: Excel with text
- **Workflow**: BPMN, DrawIO, JSON (workflow format)
- **SOP**: Markdown, DOCX, PDF, TXT (SOP format)

**Requirements:**
- Use Public Works parsing abstractions
- Store parsed results in GCS (JSON format)
- Store parsed metadata in Supabase `parsed_data_files` table
- Link to original file via `file_id`
- Preserve `ui_name` in parsed metadata

**Files:**
- `symphainy_platform/realms/content/enabling_services/file_parser_service.py`

**Parsing Abstractions to Use:**
- `PdfProcessingAbstraction`
- `WordProcessingAbstraction`
- `ExcelProcessingAbstraction`
- `CsvProcessingAbstraction`
- `JsonProcessingAbstraction`
- `TextProcessingAbstraction`
- `ImageProcessingAbstraction`
- `HtmlProcessingAbstraction`
- `MainframeProcessingAbstraction` (for binary)
- `KreuzbergProcessingAbstraction` (for structured parsing)

---

### 4. Implement Parsing Preview Generation

**Task:** Generate previews of parsed content

**Requirements:**
- Generate preview JSON for structured data (sample rows, schema)
- Generate preview JSON for unstructured data (text chunks, metadata)
- Generate preview JSON for hybrid data (both structured and unstructured parts)
- Generate preview JSON for workflow data (nodes, edges, metadata)
- Generate preview JSON for SOP data (sections, steps, metadata)
- Store preview in GCS alongside parsed data
- Return preview in API response

**Files:**
- `symphainy_platform/realms/content/enabling_services/file_parser_service.py`

---

### 5. Implement Deterministic Embeddings (Insights Pillar Integration)

**Task:** Generate deterministic embeddings from parsed files

**Requirements:**
- Support user-provided data models (PSO/permits use case)
- Support default pattern (our own embeddings)
- Generate embeddings for structured data (column-level)
- Generate embeddings for unstructured data (chunk-level)
- Generate embeddings for workflow/SOP data (node/step-level)
- Store embeddings in ArangoDB
- Register embeddings in Supabase `embedding_files` table for lineage

**Files:**
- `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`
- Integration with Insights Realm (future)

**Note:** Embeddings moved to Insights pillar, but Content Realm coordinates the flow

---

### 6. Implement ArangoDB Embedding Storage & Supabase Lineage

**Task:** Store embeddings in ArangoDB and register with Supabase

**Requirements:**
- Store embeddings in ArangoDB collections:
  - `structured_embeddings` (for structured data)
  - `semantic_graph_nodes` (for unstructured data)
  - `semantic_graph_edges` (for relationships)
- Create entry in Supabase `embedding_files` table:
  - Links to `parsed_data_files` via `parsed_file_id`
  - Links to `project_files` via `file_id`
  - Stores `ui_name` = `"Embeddings: {original_file_name}"`
  - Stores `embeddings_count`
- Use `SemanticDataAbstraction` for ArangoDB operations
- Use `FileManagementAbstraction` (or direct Supabase adapter) for lineage registration

**Files:**
- `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

---

### 7. Preserve UI Name Throughout Flow

**Task:** Ensure `ui_name` (user-friendly filename) is preserved

**Requirements:**
- `ui_name` stored in `project_files` table (original file)
- `ui_name` stored in `parsed_data_files` table (parsed file)
- `ui_name` stored in `embedding_files` table (embeddings)
- `ui_name` included in all API responses
- Frontend can use `ui_name` for display

**Verification:**
- Check all database operations include `ui_name`
- Check all API responses include `ui_name`
- Check lineage links preserve `ui_name`

---

### 8. Comprehensive E2E Tests

**Task:** Create tests that verify all functionality

**Test Categories:**

#### 8.1 File Upload Tests
- ✅ Upload file to GCS
- ✅ Store metadata in Supabase
- ✅ Preserve `ui_name`
- ✅ Return file UUID

#### 8.2 File Parsing Tests (All Types)
- ✅ Parse structured files (CSV, Excel, JSON, Binary)
- ✅ Parse unstructured files (PDF, Word, Text, HTML, Images)
- ✅ Parse hybrid files (Excel with text)
- ✅ Parse workflow files (BPMN, DrawIO, JSON workflow)
- ✅ Parse SOP files (Markdown, DOCX, PDF, TXT SOP)
- ✅ Store parsed results in GCS
- ✅ Store parsed metadata in Supabase
- ✅ Link to original file

#### 8.3 Preview Generation Tests
- ✅ Generate preview for structured data
- ✅ Generate preview for unstructured data
- ✅ Generate preview for hybrid data
- ✅ Generate preview for workflow data
- ✅ Generate preview for SOP data
- ✅ Store preview in GCS
- ✅ Return preview in API response

#### 8.4 Embedding Tests
- ✅ Generate deterministic embeddings
- ✅ Store embeddings in ArangoDB
- ✅ Register embeddings in Supabase
- ✅ Link embeddings to parsed file and original file
- ✅ Preserve `ui_name` in embedding metadata

#### 8.5 Lineage Tests
- ✅ Verify `project_files` → `parsed_data_files` link
- ✅ Verify `parsed_data_files` → `embedding_files` link
- ✅ Verify `project_files` → `embedding_files` link
- ✅ Verify all `ui_name` fields are preserved

#### 8.6 Integration Tests
- ✅ Full flow: Upload → Parse → Preview → Embed → Lineage
- ✅ Multiple file types in sequence
- ✅ Error handling (invalid files, missing adapters, etc.)

---

## 📁 File Structure

```
symphainy_platform/realms/content/
├── content_realm.py              # Realm service (already exists)
├── orchestrators/
│   └── content_orchestrator.py   # Update with real functionality
├── enabling_services/
│   └── file_parser_service.py    # Implement real parsing
└── agents/
    └── __init__.py               # Content Liaison Agent (already exists)

tests/integration/
├── test_content_realm_e2e.py    # Comprehensive E2E tests
└── fixtures/
    └── test_files/               # Test files for all types
        ├── structured/
        ├── unstructured/
        ├── hybrid/
        ├── workflow/
        └── sop/
```

---

## 🔧 Implementation Order

1. **Fix GCS Requirement** (Critical - blocks everything)
2. **Implement File Upload** (Foundation)
3. **Implement File Parsing** (Core functionality)
4. **Implement Preview Generation** (User experience)
5. **Implement Embeddings** (Insights integration)
6. **Implement Lineage** (Traceability)
7. **Create Comprehensive Tests** (Validation)

---

## ✅ Success Criteria

- ✅ Platform fails fast if GCS/Supabase/ArangoDB are not available
- ✅ Files upload to GCS and metadata to Supabase
- ✅ All file types can be parsed
- ✅ Previews are generated for all parsed files
- ✅ Embeddings are generated and stored
- ✅ Lineage is tracked across all stages
- ✅ `ui_name` is preserved throughout
- ✅ All E2E tests pass

---

## 📝 Notes

- **Embeddings**: Moved to Insights pillar, but Content Realm coordinates the flow
- **UI Name**: This is the user-friendly filename (was called UIID in old world)
- **Lineage**: Three Supabase tables (`project_files`, `parsed_data_files`, `embedding_files`) track the full lifecycle
- **Storage**: Binary files in GCS, metadata in Supabase, embeddings in ArangoDB
