# Comprehensive Testing Plan Update: Phases 1-4 Features

**Date:** January 2026  
**Status:** 📋 **TEST PLAN UPDATE**  
**Purpose:** Update comprehensive testing plan to include all Phase 1-4 features

---

## 🎯 Executive Summary

This document updates the comprehensive testing plan (`comprehensive_testing_plan_updated.md`) to include all new features implemented in Phases 1-4:

- **Phase 1:** Unified ingestion + core file management
- **Phase 2:** Bulk operations with batching and parallel processing
- **Phase 3:** Error handling, retry logic, idempotency, progress tracking
- **Phase 4:** File lifecycle, validation, search, metadata management

**Integration Point:** These tests should be added to the existing test suites in `comprehensive_testing_plan_updated.md` and `comprehensive_e2e_test_plan.md`.

---

## 📋 New Test Suites to Add

### Test Suite A: Content Realm - Unified Ingestion & File Management (Phase 1)

#### Test A.1: Unified Ingestion - Upload

**Purpose:** Verify unified ingestion via `IngestionAbstraction` works for upload type

**Test Steps:**
1. Submit `ingest_file` intent with `ingestion_type="upload"` and `file_content`
2. Verify `IngestionAbstraction.ingest_data()` called with `IngestionRequest`
3. Verify `UploadAdapter` processes the request
4. Verify file stored in GCS via `FileStorageAbstraction`
5. Verify file metadata stored in Supabase
6. Verify file reference registered in State Surface
7. Verify `ui_name` preserved in metadata

**Success Criteria:**
- ✅ File ingested via upload adapter
- ✅ File exists in GCS
- ✅ File metadata exists in Supabase
- ✅ File reference in State Surface
- ✅ `ui_name` matches original filename
- ✅ `ingestion_type` stored as "upload"

**Test Data:**
- File types: TXT, PDF, CSV, XLSX, JSON, BPMN, DOCX
- File sizes: Small (< 1MB), Medium (1-10MB), Large (> 10MB)

---

#### Test A.2: Unified Ingestion - EDI

**Purpose:** Verify unified ingestion works for EDI type

**Test Steps:**
1. Submit `ingest_file` intent with `ingestion_type="edi"`, `edi_data`, and `partner_id`
2. Verify `IngestionAbstraction.ingest_data()` called with EDI `IngestionRequest`
3. Verify `EDIAdapter` processes the request
4. Verify EDI data stored in GCS
5. Verify EDI metadata stored in Supabase (with `partner_id`, `edi_protocol`)
6. Verify file reference registered in State Surface

**Success Criteria:**
- ✅ File ingested via EDI adapter
- ✅ EDI data exists in GCS
- ✅ EDI metadata includes `partner_id` and `edi_protocol`
- ✅ File reference in State Surface
- ✅ `ingestion_type` stored as "edi"

**Test Data:**
- EDI formats: AS2, X12, EDIFACT
- Partner IDs: Various test partner identifiers

---

#### Test A.3: Unified Ingestion - API

**Purpose:** Verify unified ingestion works for API type

**Test Steps:**
1. Submit `ingest_file` intent with `ingestion_type="api"` and `api_payload`
2. Verify `IngestionAbstraction.ingest_data()` called with API `IngestionRequest`
3. Verify `APIAdapter` processes the request
4. Verify API payload converted to file and stored in GCS
5. Verify API metadata stored in Supabase (with `endpoint`, `api_type`)
6. Verify file reference registered in State Surface

**Success Criteria:**
- ✅ File ingested via API adapter
- ✅ API payload converted to file in GCS
- ✅ API metadata includes `endpoint` and `api_type`
- ✅ File reference in State Surface
- ✅ `ingestion_type` stored as "api"

**Test Data:**
- API types: REST, GraphQL, SOAP
- Payload formats: JSON, XML, form-data

---

#### Test A.4: Register File

**Purpose:** Verify `register_file` intent works for existing files

**Test Steps:**
1. Upload file via `ingest_file` (or use existing file in GCS)
2. Submit `register_file` intent with `file_id` and `ui_name`
3. Verify file metadata retrieved from Supabase or GCS
4. Verify file reference registered in State Surface
5. Verify metadata preserved correctly

**Success Criteria:**
- ✅ File registered in State Surface
- ✅ File metadata retrieved correctly
- ✅ `ui_name` preserved
- ✅ File reference accessible via State Surface

**Test Data:**
- Files already in GCS (not yet in State Surface)
- Files in Supabase (need State Surface registration)

---

#### Test A.5: Retrieve File Metadata

**Purpose:** Verify `retrieve_file_metadata` intent works

**Test Steps:**
1. Upload file via `ingest_file`
2. Submit `retrieve_file_metadata` intent with `file_id`
3. Verify Supabase record retrieved
4. Verify metadata returned correctly

**Success Criteria:**
- ✅ File metadata retrieved from Supabase
- ✅ Metadata includes all expected fields
- ✅ `ui_name` present in metadata

---

#### Test A.6: Retrieve File

**Purpose:** Verify `retrieve_file` intent works

**Test Steps:**
1. Upload file via `ingest_file`
2. Submit `retrieve_file` intent with `file_id` and `include_contents=True`
3. Verify file contents retrieved from GCS
4. Verify file metadata returned
5. Verify file contents match original

**Success Criteria:**
- ✅ File contents retrieved from GCS
- ✅ File metadata returned
- ✅ File contents match original upload
- ✅ File size matches

---

#### Test A.7: List Files

**Purpose:** Verify `list_files` intent works

**Test Steps:**
1. Upload multiple files via `ingest_file`
2. Submit `list_files` intent with `tenant_id` and `session_id`
3. Verify files listed correctly
4. Test pagination with `limit` and `offset`
5. Test filtering by `file_type`

**Success Criteria:**
- ✅ Files listed correctly
- ✅ Pagination works
- ✅ Filtering by `file_type` works
- ✅ Results limited correctly

---

#### Test A.8: Get File By ID

**Purpose:** Verify `get_file_by_id` intent works

**Test Steps:**
1. Upload file via `ingest_file`
2. Submit `get_file_by_id` intent with `file_id`
3. Verify file metadata retrieved
4. Verify file reference status checked
5. Verify `registered_in_state_surface` flag correct

**Success Criteria:**
- ✅ File metadata retrieved
- ✅ File reference status correct
- ✅ `registered_in_state_surface` flag accurate

---

### Test Suite B: Content Realm - Bulk Operations (Phase 2)

#### Test B.1: Bulk Ingest Files

**Purpose:** Verify `bulk_ingest_files` works with batching and parallel processing

**Test Steps:**
1. Prepare list of files (10-100 files)
2. Submit `bulk_ingest_files` intent with `files` list, `batch_size`, `max_parallel`
3. Verify files processed in batches
4. Verify parallel processing within batches
5. Verify all files ingested successfully
6. Verify results and errors returned

**Success Criteria:**
- ✅ All files ingested successfully
- ✅ Batching works correctly
- ✅ Parallel processing works (verify via timing)
- ✅ Results include success/error counts
- ✅ Individual file results returned

**Test Data:**
- 10 files (small batch)
- 100 files (medium batch)
- 1000 files (large batch, if time permits)
- Mix of file types and sizes

---

#### Test B.2: Bulk Parse Files

**Purpose:** Verify `bulk_parse_files` works with parallel processing

**Test Steps:**
1. Upload multiple files via `bulk_ingest_files`
2. Submit `bulk_parse_files` intent with `file_ids` list
3. Verify files parsed in parallel
4. Verify all files parsed successfully
5. Verify parsed results stored correctly

**Success Criteria:**
- ✅ All files parsed successfully
- ✅ Parallel processing works
- ✅ Parsed results stored in GCS
- ✅ Parsed metadata stored in Supabase
- ✅ Results include success/error counts

**Test Data:**
- 10 files (small batch)
- 50 files (medium batch)
- Mix of file types (structured, unstructured, hybrid)

---

#### Test B.3: Bulk Extract Embeddings

**Purpose:** Verify `bulk_extract_embeddings` works with parallel processing

**Test Steps:**
1. Upload and parse multiple files
2. Submit `bulk_extract_embeddings` intent with `parsed_result_ids` list
3. Verify embeddings extracted in parallel
4. Verify all embeddings extracted successfully
5. Verify embeddings stored correctly

**Success Criteria:**
- ✅ All embeddings extracted successfully
- ✅ Parallel processing works
- ✅ Embeddings stored in ArangoDB
- ✅ Embedding metadata stored in Supabase
- ✅ Results include success/error counts

**Test Data:**
- 10 parsed files (small batch)
- 50 parsed files (medium batch)
- Mix of structured and unstructured files

---

#### Test B.4: Bulk Interpret Data

**Purpose:** Verify `bulk_interpret_data` works with parallel processing

**Test Steps:**
1. Upload, parse, and extract embeddings for multiple files
2. Submit `bulk_interpret_data` intent with `parsed_result_ids` list
3. Verify interpretations created in parallel
4. Verify all interpretations created successfully
5. Verify interpretation results stored correctly

**Success Criteria:**
- ✅ All interpretations created successfully
- ✅ Parallel processing works
- ✅ Interpretation results stored
- ✅ Results include success/error counts

**Test Data:**
- 10 parsed results with embeddings
- 50 parsed results with embeddings
- Mix of structured and unstructured files

---

### Test Suite C: Content Realm - Error Handling & Resilience (Phase 3)

#### Test C.1: Idempotency

**Purpose:** Verify idempotency prevents duplicate operations

**Test Steps:**
1. Submit `bulk_ingest_files` intent with `idempotency_key`
2. Verify operation completes successfully
3. Submit same intent again with same `idempotency_key`
4. Verify previous result returned (no duplicate processing)
5. Verify `operation_id` matches

**Success Criteria:**
- ✅ First execution processes normally
- ✅ Second execution returns previous result
- ✅ No duplicate file ingestion
- ✅ Same `operation_id` returned

**Test Data:**
- Various `idempotency_key` values
- Different operation types (bulk_ingest, bulk_parse, etc.)

---

#### Test C.2: Retry Logic

**Purpose:** Verify retry logic works for transient failures

**Test Steps:**
1. Simulate transient failure (network timeout, temporary GCS error)
2. Submit `bulk_ingest_files` intent
3. Verify retry logic triggers
4. Verify exponential backoff applied
5. Verify operation succeeds after retry

**Success Criteria:**
- ✅ Retry logic triggers on failure
- ✅ Exponential backoff applied
- ✅ Operation succeeds after retry
- ✅ Retry attempts logged

**Test Data:**
- Simulated network failures
- Simulated GCS temporary errors
- Different ingestion types (upload, EDI, API)

---

#### Test C.3: Progress Tracking

**Purpose:** Verify progress tracking works for bulk operations

**Test Steps:**
1. Submit `bulk_ingest_files` intent with large file list (50+ files)
2. Query `get_operation_status` during execution
3. Verify progress updates after each batch
4. Verify progress includes: total, processed, succeeded, failed, current_batch
5. Verify final status is "completed"

**Success Criteria:**
- ✅ Progress tracked correctly
- ✅ Progress updates after each batch
- ✅ Progress percentage calculated correctly
- ✅ Final status is "completed"

**Test Data:**
- 50+ files for bulk operations
- Query progress at different stages

---

#### Test C.4: Get Operation Status

**Purpose:** Verify `get_operation_status` intent works

**Test Steps:**
1. Submit `bulk_ingest_files` intent (get `operation_id`)
2. Submit `get_operation_status` intent with `operation_id`
3. Verify status returned correctly
4. Verify progress details included
5. Test with non-existent `operation_id` (should return "not_found")

**Success Criteria:**
- ✅ Status returned correctly
- ✅ Progress details included
- ✅ "not_found" returned for non-existent operation
- ✅ Status updates as operation progresses

---

#### Test C.5: Resume Capability

**Purpose:** Verify resume from last successful batch works

**Test Steps:**
1. Submit `bulk_ingest_files` intent with large file list
2. Simulate failure mid-execution (kill process, network error)
3. Submit same intent again with `resume_from_batch` parameter
4. Verify operation resumes from last successful batch
5. Verify already-processed batches skipped
6. Verify final results combine previous and new results

**Success Criteria:**
- ✅ Operation resumes from last successful batch
- ✅ Already-processed batches skipped
- ✅ Final results combine previous and new results
- ✅ No duplicate processing

**Test Data:**
- 100+ files for bulk operations
- Simulate failure at batch 3, resume from batch 3

---

### Test Suite D: Content Realm - File Lifecycle & Advanced Features (Phase 4)

#### Test D.1: Archive File

**Purpose:** Verify `archive_file` intent works (soft delete)

**Test Steps:**
1. Upload file via `ingest_file`
2. Submit `archive_file` intent with `file_id` and `reason`
3. Verify file status changed to "archived" in State Surface
4. Verify `archived_at` timestamp set
5. Verify `archive_reason` stored
6. Verify file still exists in GCS (not deleted)

**Success Criteria:**
- ✅ File status changed to "archived"
- ✅ `archived_at` timestamp set
- ✅ `archive_reason` stored
- ✅ File still exists in GCS
- ✅ File metadata updated in State Surface

---

#### Test D.2: Purge File

**Purpose:** Verify `purge_file` intent works (permanent delete)

**Test Steps:**
1. Upload file via `ingest_file`
2. Submit `purge_file` intent with `file_id` and `confirm=True`
3. Verify file deleted from GCS
4. Verify file removed from State Surface
5. Verify `confirm=False` fails (requires confirmation)
6. Verify file cannot be retrieved after purge

**Success Criteria:**
- ✅ File deleted from GCS
- ✅ File removed from State Surface
- ✅ `confirm=False` fails
- ✅ File cannot be retrieved after purge

---

#### Test D.3: Restore File

**Purpose:** Verify `restore_file` intent works

**Test Steps:**
1. Upload file via `ingest_file`
2. Archive file via `archive_file`
3. Submit `restore_file` intent with `file_id`
4. Verify file status changed to "active"
5. Verify `restored_at` timestamp set
6. Verify archive-specific metadata removed
7. Verify file accessible again

**Success Criteria:**
- ✅ File status changed to "active"
- ✅ `restored_at` timestamp set
- ✅ Archive-specific metadata removed
- ✅ File accessible again

---

#### Test D.4: Validate File

**Purpose:** Verify `validate_file` intent works

**Test Steps:**
1. Upload file via `ingest_file`
2. Submit `validate_file` intent with `file_id` and `validation_rules`
3. Verify validation results returned
4. Test with valid file (should pass)
5. Test with invalid file (should fail with errors)
6. Verify validation includes: size, type, metadata, storage existence

**Success Criteria:**
- ✅ Validation results returned
- ✅ Valid file passes validation
- ✅ Invalid file fails with errors
- ✅ Validation includes all checks

**Test Data:**
- Valid files (within size/type limits)
- Invalid files (exceeds size, wrong type, missing metadata)

---

#### Test D.5: Preprocess File

**Purpose:** Verify `preprocess_file` intent works

**Test Steps:**
1. Upload file via `ingest_file`
2. Submit `preprocess_file` intent with `file_id` and `preprocessing_options`
3. Verify preprocessing results returned
4. Test with different options: `normalize`, `clean`, `extract_metadata`
5. Verify preprocessing changes tracked

**Success Criteria:**
- ✅ Preprocessing results returned
- ✅ Different options work correctly
- ✅ Preprocessing changes tracked

**Test Data:**
- Files needing normalization
- Files needing cleaning
- Files needing metadata extraction

---

#### Test D.6: Search Files

**Purpose:** Verify `search_files` intent works

**Test Steps:**
1. Upload multiple files with different names
2. Submit `search_files` intent with `query` and `search_type`
3. Verify matching files returned
4. Test search by name (`search_type="name"`)
5. Test search by content (`search_type="content"`)
6. Test search both (`search_type="both"`)
7. Test pagination with `limit` and `offset`

**Success Criteria:**
- ✅ Matching files returned
- ✅ Search by name works
- ✅ Search by content works (if implemented)
- ✅ Search both works
- ✅ Pagination works

**Test Data:**
- Files with various names
- Files with various content types

---

#### Test D.7: Query Files

**Purpose:** Verify `query_files` intent works with filters

**Test Steps:**
1. Upload multiple files with different types, sizes, dates
2. Submit `query_files` intent with `filters`
3. Test filter by `file_type`
4. Test filter by `status` (active, archived)
5. Test filter by `min_size` and `max_size`
6. Test filter by `created_after` and `created_before`
7. Test pagination with `limit` and `offset`

**Success Criteria:**
- ✅ Filter by `file_type` works
- ✅ Filter by `status` works
- ✅ Filter by size works
- ✅ Filter by date works
- ✅ Pagination works

**Test Data:**
- Files with various types, sizes, dates
- Mix of active and archived files

---

#### Test D.8: Update File Metadata

**Purpose:** Verify `update_file_metadata` intent works

**Test Steps:**
1. Upload file via `ingest_file`
2. Submit `update_file_metadata` intent with `file_id` and `metadata_updates`
3. Verify metadata updated in State Surface
4. Verify `updated_at` timestamp set
5. Verify existing metadata preserved
6. Verify new metadata added

**Success Criteria:**
- ✅ Metadata updated in State Surface
- ✅ `updated_at` timestamp set
- ✅ Existing metadata preserved
- ✅ New metadata added

**Test Data:**
- Various metadata updates (description, tags, custom fields)

---

## 📊 Integration with Existing Test Plans

### Where to Add These Tests

1. **`comprehensive_testing_plan_updated.md`:**
   - Add Test Suite A (Phase 1) to **Phase 3: Realm Integration → Test 3.1: Content Realm**
   - Add Test Suite B (Phase 2) as new subsection under Content Realm
   - Add Test Suite C (Phase 3) as new subsection under Content Realm
   - Add Test Suite D (Phase 4) as new subsection under Content Realm

2. **`comprehensive_e2e_test_plan.md`:**
   - Add Test Suite A (Phase 1) to **Test Suite 1: Content Realm E2E**
   - Add Test Suite B (Phase 2) as new test cases
   - Add Test Suite C (Phase 3) as new test cases
   - Add Test Suite D (Phase 4) as new test cases

### Test Execution Priority

**High Priority (Must Have):**
- Test A.1: Unified Ingestion - Upload
- Test A.4: Register File
- Test A.5: Retrieve File Metadata
- Test A.6: Retrieve File
- Test B.1: Bulk Ingest Files
- Test C.1: Idempotency
- Test C.3: Progress Tracking
- Test D.1: Archive File
- Test D.3: Restore File

**Medium Priority (Should Have):**
- Test A.2: Unified Ingestion - EDI
- Test A.3: Unified Ingestion - API
- Test A.7: List Files
- Test A.8: Get File By ID
- Test B.2: Bulk Parse Files
- Test B.3: Bulk Extract Embeddings
- Test C.2: Retry Logic
- Test C.4: Get Operation Status
- Test D.2: Purge File
- Test D.4: Validate File
- Test D.8: Update File Metadata

**Low Priority (Nice to Have):**
- Test B.4: Bulk Interpret Data
- Test C.5: Resume Capability
- Test D.5: Preprocess File
- Test D.6: Search Files
- Test D.7: Query Files

---

## 🎯 Success Criteria for All Phases

### Phase 1 Success Criteria
- ✅ All ingestion types work (upload, EDI, API)
- ✅ All file management intents work
- ✅ Files accessible via State Surface
- ✅ Metadata preserved correctly

### Phase 2 Success Criteria
- ✅ Bulk operations process 100+ files
- ✅ Batching works correctly
- ✅ Parallel processing improves performance
- ✅ Results and errors tracked correctly

### Phase 3 Success Criteria
- ✅ Idempotency prevents duplicate operations
- ✅ Retry logic handles transient failures
- ✅ Progress tracking provides visibility
- ✅ Operations can be queried for status

### Phase 4 Success Criteria
- ✅ File lifecycle operations work (archive, purge, restore)
- ✅ Validation works correctly
- ✅ Search and query work
- ✅ Metadata updates work

---

## 📝 Test Implementation Notes

### Test Data Requirements

1. **File Types:**
   - Structured: CSV, XLSX, JSON
   - Unstructured: PDF, TXT, DOCX
   - Hybrid: Excel with text
   - Workflow: BPMN, DrawIO
   - Binary: Mainframe files (ASCII, EBCDIC)

2. **File Sizes:**
   - Small: < 1MB
   - Medium: 1-10MB
   - Large: > 10MB

3. **Test Scenarios:**
   - Single file operations
   - Bulk operations (10, 50, 100+ files)
   - Error scenarios (network failures, invalid files)
   - Edge cases (empty files, very large files, special characters)

### Test Infrastructure

- Use existing test fixtures (`phase1_setup`, `test_data_seeder`)
- Use docker-compose for infrastructure
- Use real GCS emulator, Supabase, ArangoDB
- Clean up test data after each test

---

## 🔗 References

- [Phase 1 Implementation Summary](./phase1_validation_results.md)
- [Phase 2 Implementation Summary](./phase2_implementation_summary.md)
- [Phase 3 Implementation Summary](./phase3_implementation_summary.md)
- [Phase 4 Implementation Summary](./phase4_implementation_summary.md)
- [E2E Data Flow Audit](./e2e_data_flow_audit.md)
- [Comprehensive Testing Plan (Updated)](./comprehensive_testing_plan_updated.md)
- [Comprehensive E2E Test Plan](./comprehensive_e2e_test_plan.md)
