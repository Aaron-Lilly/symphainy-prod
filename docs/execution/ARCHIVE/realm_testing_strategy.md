# Realm Testing Strategy: Real Functionality & Composability

**Status:** Critical Foundation  
**Created:** January 2026  
**Updated:** January 2026  
**Goal:** Ensure realms deliver REAL working functionality AND remain composable for complex scenarios

---

## ⚠️ IMPORTANT: See Comprehensive Strategy

This document has been **superseded** by a more comprehensive strategy that covers **ALL MVP showcase features**:

- **[Comprehensive Realm Testing Strategy](./comprehensive_realm_testing_strategy.md)** - Complete testing strategy for ALL realms and ALL MVP showcase features
- **[Realm Gap Analysis & Remediation Plan](./realm_gap_analysis.md)** - Detailed gap analysis and remediation plan

---

## Executive Summary

Realm testing is the **"secret sauce"** that makes or breaks the platform. It must validate:

1. **Real Working Functionality** - Not mocks, not stubs, REAL operations
2. **MVP Showcase Delivery** - Frontend showcase must actually work
3. **Composability** - Capabilities must be reusable for 350k policy scenarios

---

## Core Principles

### 1. Real Infrastructure, Real Operations

**NO MOCKS for critical paths:**
- ✅ Real GCS file storage
- ✅ Real Supabase metadata storage
- ✅ Real ArangoDB embeddings storage
- ✅ Real parser execution (COBOL, JSON, CSV, etc.)
- ✅ Real embedding generation

**Why:** If it doesn't work with real infrastructure, it won't work in production.

### 2. End-to-End Flow Validation

**Test the COMPLETE flow:**
```
User Upload → GCS Storage → Supabase Metadata → Parser Execution → 
GCS Results Storage → Supabase Lineage → Embedding Generation → 
ArangoDB Storage → Supabase Embedding Lineage
```

**Why:** Individual components working ≠ system working.

### 3. Lineage & Provenance Tracking

**Verify data lineage is correct:**
- File → Parsed Results (1:many in Supabase)
- File → Embeddings (1:many in Supabase)
- Parsed Results → Embeddings (many:many in Supabase)
- All linked with proper metadata

**Why:** Without lineage, we can't reason about data or enable composability.

### 4. Composability Validation

**Test that capabilities compose:**
- Same parsing logic works for 1 file and 350k files
- Same embedding logic works for single files and batch operations
- Same lineage tracking works at any scale

**Why:** If capabilities don't compose, we'll rebuild for every scenario.

---

## Testing Architecture

### Test Infrastructure Requirements

1. **GCS Bucket** (test bucket, separate from production)
2. **Supabase Database** (test database, isolated)
3. **ArangoDB** (test database, isolated)
4. **Real Parser Files** (COBOL copybooks, sample data files)
5. **Real Embedding Models** (or test embeddings that match format)

### Test Data Strategy

- **Isolated Test Data:** Each test uses unique IDs
- **Cleanup:** Tests clean up after themselves
- **Realistic Data:** Use real COBOL copybooks, real file formats
- **Scale Testing:** Test with 1 file, 10 files, 100 files, 1000 files

---

## Content Realm Testing

### Test Suite: `tests/integration/realms/content/test_content_realm_e2e.py`

#### Test 1: File Upload → GCS → Supabase Metadata

**What it validates:**
- File uploaded via Content Realm
- File stored in GCS with correct path
- File metadata stored in Supabase (file_id, gcs_path, file_type, size, etc.)
- Metadata is queryable

**Test Steps:**
1. Create test file (COBOL copybook, JSON, CSV, etc.)
2. Call Content Realm `ingest_file` intent
3. Verify file exists in GCS
4. Query Supabase for file metadata
5. Verify metadata matches file

#### Test 2: File Parsing → GCS Results → Supabase Lineage

**What it validates:**
- File parsed using REAL parser (custom mainframe, JSON, CSV, etc.)
- Parsed results stored in GCS (JSONL, JSON Chunks, JSON format)
- Lineage record created in Supabase (file_id → parsed_result_id)
- Results are queryable

**Test Steps:**
1. Use file from Test 1
2. Call Content Realm `parse_content` intent
3. Verify parsed results exist in GCS
4. Query Supabase for lineage (file → parsed_result)
5. Verify parsed results match expected format

#### Test 3: Embedding Generation → ArangoDB → Supabase Lineage

**What it validates:**
- Embeddings generated from parsed content
- Embeddings stored in ArangoDB
- Lineage record created in Supabase (file_id → embedding_ids, many:1)
- All embeddings from same file linked to that file

**Test Steps:**
1. Use parsed results from Test 2
2. Call Content Realm `extract_embeddings` intent
3. Verify embeddings exist in ArangoDB
4. Query Supabase for lineage (file → embeddings, many:1)
5. Verify all embeddings from same file are linked

#### Test 4: Complete Flow (Upload → Parse → Embed)

**What it validates:**
- Complete end-to-end flow works
- All components integrate correctly
- Lineage chain is complete (file → parsed → embeddings)

**Test Steps:**
1. Upload file
2. Parse file
3. Generate embeddings
4. Verify complete lineage chain in Supabase
5. Verify all data accessible via proper references

#### Test 5: Multiple Files → Batch Operations

**What it validates:**
- Same capabilities work for multiple files
- Batch operations are efficient
- Lineage tracking works at scale

**Test Steps:**
1. Upload 10 files
2. Parse all 10 files
3. Generate embeddings for all parsed results
4. Verify lineage for all files
5. Verify batch operations completed successfully

#### Test 6: Composability (350k Scenario Preparation)

**What it validates:**
- Same parsing logic works for large-scale scenarios
- Same embedding logic scales
- Same lineage tracking works at scale

**Test Steps:**
1. Upload 100 files (simulating 350k scenario)
2. Parse all files using same logic
3. Generate embeddings using same logic
4. Verify lineage tracking works correctly
5. Verify no reinvention needed

---

## Insights Realm Testing

### Test Suite: `tests/integration/realms/insights/test_insights_realm_e2e.py`

#### Test 1: Semantic Interpretation

**What it validates:**
- Insights Realm can interpret parsed content
- Interpretation results stored properly
- Lineage maintained (file → parsed → interpretation)

#### Test 2: Relationship Mapping

**What it validates:**
- Relationships extracted from content
- Relationships stored in ArangoDB graph
- Lineage maintained

---

## Operations Realm Testing

### Test Suite: `tests/integration/realms/operations/test_operations_realm_e2e.py`

#### Test 1: SOP Generation

**What it validates:**
- Operations Realm can generate SOPs from content
- SOPs stored properly
- Lineage maintained

---

## Outcomes Realm Testing

### Test Suite: `tests/integration/realms/outcomes/test_outcomes_realm_e2e.py`

#### Test 1: Outcome Synthesis

**What it validates:**
- Outcomes Realm can synthesize outcomes from insights
- Outcomes stored properly
- Lineage maintained (content → insights → outcomes)

---

## MVP Showcase Integration Tests

### Test Suite: `tests/e2e/showcase/test_mvp_showcase_e2e.py`

#### Test 1: User Uploads File → Frontend → Backend → Storage

**What it validates:**
- Frontend can upload file
- Backend receives file
- File stored in GCS
- Metadata stored in Supabase
- Frontend receives confirmation

#### Test 2: User Views Parsed Results

**What it validates:**
- Frontend requests parsed results
- Backend retrieves from GCS
- Frontend displays results correctly

#### Test 3: User Views Embeddings

**What it validates:**
- Frontend requests embeddings
- Backend retrieves from ArangoDB
- Frontend displays embeddings correctly

#### Test 4: Complete User Journey

**What it validates:**
- User uploads file
- System parses file
- System generates embeddings
- User views all results
- Everything works end-to-end

---

## Implementation Plan

### Phase 1: Infrastructure Setup
1. ✅ Docker-based test infrastructure (Redis, ArangoDB)
2. ⏳ GCS test bucket setup
3. ⏳ Supabase test database setup
4. ⏳ Test data preparation (COBOL copybooks, sample files)

### Phase 2: Content Realm E2E Tests
1. ⏳ File upload → GCS → Supabase
2. ⏳ File parsing → GCS → Supabase lineage
3. ⏳ Embedding generation → ArangoDB → Supabase lineage
4. ⏳ Complete flow validation
5. ⏳ Batch operations validation

### Phase 3: Other Realms E2E Tests
1. ⏳ Insights Realm tests
2. ⏳ Operations Realm tests
3. ⏳ Outcomes Realm tests

### Phase 4: MVP Showcase Integration
1. ⏳ Frontend → Backend integration tests
2. ⏳ Complete user journey tests

### Phase 5: Composability Validation
1. ⏳ 350k scenario preparation tests
2. ⏳ Scale testing (100, 1000, 10000 files)

---

## Success Criteria

✅ **Real Functionality:**
- All operations use real infrastructure (GCS, Supabase, ArangoDB)
- No mocks for critical paths
- All data persists correctly

✅ **MVP Showcase:**
- Frontend showcase works end-to-end
- Users can upload, parse, view results
- All features functional

✅ **Composability:**
- Same capabilities work for 1 file and 350k files
- No reinvention needed for complex scenarios
- Lineage tracking works at any scale

---

## Critical Notes

1. **This is NOT optional** - Realm testing is the foundation of platform reliability
2. **Real infrastructure required** - Mocks won't catch production issues
3. **Lineage is critical** - Without proper lineage, composability fails
4. **Scale matters** - Test at scale to ensure composability

---

## Next Steps

1. Set up GCS test bucket
2. Set up Supabase test database
3. Implement Content Realm E2E tests
4. Validate MVP showcase functionality
5. Test composability at scale
