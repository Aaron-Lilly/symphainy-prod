# Comprehensive E2E Test Plan for All 3 Realms

**Date:** January 2026  
**Status:** 📋 **TEST PLAN**  
**Purpose:** Comprehensive end-to-end testing strategy for Content, Insights, and Operations Realms

---

## 🎯 Executive Summary

This test plan ensures all 3 realms work correctly end-to-end, validating:
- Runtime Participation Contract compliance
- State Surface file pattern (governed, observable, replayable)
- Public Works abstraction usage
- Intent flow from Experience → Runtime → Realms
- Cross-realm interactions (via Runtime intents)

---

## 📋 Test Structure

### Test Organization

```
tests/
├── integration/
│   ├── test_content_realm_e2e.py          # Content Realm E2E tests
│   ├── test_insights_realm_e2e.py         # Insights Realm E2E tests
│   ├── test_operations_realm_e2e.py       # Operations Realm E2E tests
│   ├── test_cross_realm_e2e.py            # Cross-realm interaction tests
│   └── test_runtime_integration_e2e.py   # Full Runtime integration tests
```

---

## 🧪 Test Suite 1: Content Realm E2E

### Test 1.1: File Upload Flow

**Purpose:** Verify file upload works end-to-end (GCS + Supabase + State Surface)

**Test Steps:**
1. Create session via Runtime API
2. Submit `ingest_file` intent with file content
3. Verify file stored in GCS
4. Verify file metadata stored in Supabase
5. Verify file reference registered in State Surface
6. Verify `ui_name` preserved in metadata

**Success Criteria:**
- ✅ File exists in GCS (verify via GCS adapter)
- ✅ File metadata exists in Supabase (verify via FileManagementAbstraction)
- ✅ File reference exists in State Surface (verify via `context.state_surface.get_file_metadata()`)
- ✅ `ui_name` matches original filename
- ✅ File hash matches uploaded content

**Test Data:**
- File types: TXT, PDF, CSV, XLSX, JSON, BPMN, Markdown
- File sizes: Small (< 1MB), Medium (1-10MB), Large (> 10MB)

---

### Test 1.2: File Parsing Flow

**Purpose:** Verify file parsing works for all types via State Surface

**Test Steps:**
1. Upload file (via Test 1.1)
2. Submit `parse_content` intent with `file_id`
3. Verify parsing abstraction called (via State Surface file reference)
4. Verify parsed result stored in GCS
5. Verify parsed metadata stored in Supabase
6. Verify parsed file reference registered in State Surface
7. Verify preview generated

**Success Criteria:**
- ✅ Parsed file exists in GCS (JSON format)
- ✅ Parsed metadata exists in Supabase (`parsed_data_files` table)
- ✅ Parsed file reference exists in State Surface
- ✅ Parsing type correctly determined (structured, unstructured, hybrid, workflow, SOP)
- ✅ Preview data generated and accessible
- ✅ Original file linked via `file_id`

**Test Data:**
- Structured: CSV, XLSX, JSON
- Unstructured: PDF, TXT, DOCX
- Hybrid: Excel with text
- Workflow: BPMN, DrawIO
- SOP: Markdown

---

### Test 1.3: Semantic Interpretation Flow

**Purpose:** Verify 3-layer semantic interpretation works

**Test Steps:**
1. Upload and parse file (via Tests 1.1, 1.2)
2. Submit `get_semantic_interpretation` intent with `parsed_file_id`
3. Verify Layer 1 (metadata) extracted from parsed file
4. Verify Layer 2 (meaning) retrieved from SemanticDataAbstraction (if embeddings exist)
5. Verify Layer 3 (context) retrieved from semantic graph (if graph exists)
6. Verify interpretation returned in correct format

**Success Criteria:**
- ✅ Layer 1 metadata extracted (parsing_type, schema, structure)
- ✅ Layer 2 meaning retrieved (if embeddings exist)
- ✅ Layer 3 context retrieved (if semantic graph exists)
- ✅ Interpretation follows 3-layer structure
- ✅ All layers present even if some are empty

**Test Data:**
- Files with embeddings: Structured files with semantic embeddings
- Files without embeddings: New files (Layer 1 only)
- Files with semantic graph: Files with relationship mappings

---

### Test 1.4: Extract Embeddings Flow (Future)

**Purpose:** Verify embedding generation and storage (when implemented)

**Test Steps:**
1. Upload and parse file (via Tests 1.1, 1.2)
2. Submit `extract_embeddings` intent with `parsed_file_id`
3. Verify embeddings generated (deterministic)
4. Verify embeddings stored in ArangoDB (via SemanticDataAbstraction)
5. Verify embedding metadata stored in Supabase (lineage)
6. Verify embedding file reference registered in State Surface

**Success Criteria:**
- ✅ Embeddings generated (deterministic for same input)
- ✅ Embeddings stored in ArangoDB (`structured_embeddings` collection)
- ✅ Embedding metadata in Supabase (`embedding_files` table)
- ✅ Lineage traceability (file_id → parsed_file_id → embedding_file_id)
- ✅ Embedding file reference in State Surface

**Test Data:**
- Structured files: CSV, XLSX (column embeddings)
- Unstructured files: PDF, TXT (text embeddings)

---

## 🧪 Test Suite 2: Insights Realm E2E

### Test 2.1: Analyze Content Flow

**Purpose:** Verify content analysis works end-to-end

**Test Steps:**
1. Upload and parse file (via Content Realm tests)
2. Submit `analyze_content` intent with `parsed_file_id`
3. Verify DataAnalyzerService called
4. Verify analysis results returned
5. Verify analysis artifacts stored (if applicable)

**Success Criteria:**
- ✅ Analysis completed successfully
- ✅ Analysis results follow expected structure
- ✅ Analysis artifacts returned in response
- ✅ Analysis event emitted

**Test Data:**
- Structured files: CSV, XLSX (data analysis)
- Unstructured files: PDF, TXT (text analysis)

---

### Test 2.2: Interpret Data Flow

**Purpose:** Verify data interpretation works end-to-end

**Test Steps:**
1. Upload and parse file (via Content Realm tests)
2. Submit `interpret_data` intent with `parsed_file_id`
3. Verify DataAnalyzerService.interpret_data() called
4. Verify interpretation results returned
5. Verify semantic mapping generated (if applicable)

**Success Criteria:**
- ✅ Interpretation completed successfully
- ✅ Interpretation results follow expected structure
- ✅ Semantic mapping generated (if applicable)
- ✅ Interpretation event emitted

**Test Data:**
- Structured files: CSV, XLSX (column interpretation)
- Unstructured files: PDF, TXT (text interpretation)

---

### Test 2.3: Map Relationships Flow

**Purpose:** Verify relationship mapping works end-to-end

**Test Steps:**
1. Upload and parse file (via Content Realm tests)
2. Submit `map_relationships` intent with `parsed_file_id`
3. Verify DataAnalyzerService.map_relationships() called
4. Verify relationships mapped
5. Verify semantic graph created (if applicable)

**Success Criteria:**
- ✅ Relationships mapped successfully
- ✅ Relationship graph generated
- ✅ Relationships stored in SemanticDataAbstraction (if applicable)
- ✅ Relationship mapping event emitted

**Test Data:**
- Files with relationships: CSV with foreign keys, JSON with references

---

### Test 2.4: Query Data Flow

**Purpose:** Verify semantic data querying works end-to-end

**Test Steps:**
1. Upload, parse, and generate embeddings (via Content Realm tests)
2. Submit `query_data` intent with query string
3. Verify SemanticDataAbstraction queried
4. Verify query results returned
5. Verify results filtered by tenant

**Success Criteria:**
- ✅ Query executed successfully
- ✅ Query results returned (filtered by tenant)
- ✅ Results follow expected structure
- ✅ Query event emitted

**Test Data:**
- Query types: Semantic ID query, vector similarity search, filter query

---

### Test 2.5: Calculate Metrics Flow

**Purpose:** Verify metrics calculation works end-to-end

**Test Steps:**
1. Upload and parse file (via Content Realm tests)
2. Submit `calculate_metrics` intent with `parsed_file_id`
3. Verify MetricsCalculatorService.calculate_metrics() called
4. Verify metrics calculated (data quality, completeness, accuracy)
5. Verify metrics results returned

**Success Criteria:**
- ✅ Metrics calculated successfully
- ✅ Metrics include data quality, completeness, accuracy
- ✅ Metrics results follow expected structure
- ✅ Metrics calculation event emitted

**Test Data:**
- Structured files: CSV, XLSX (data quality metrics)
- Unstructured files: PDF, TXT (completeness metrics)

---

## 🧪 Test Suite 3: Operations Realm E2E

### Test 3.1: Optimize Process Flow

**Purpose:** Verify workflow optimization works end-to-end

**Test Steps:**
1. Upload workflow file (BPMN, DrawIO) via Content Realm
2. Parse workflow file (via Content Realm)
3. Submit `optimize_process` intent with `workflow_id`
4. Verify WorkflowConversionService.optimize_workflow() called
5. Verify optimization recommendations returned
6. Verify optimization artifacts stored (if applicable)

**Success Criteria:**
- ✅ Optimization completed successfully
- ✅ Optimization recommendations returned
- ✅ Recommendations follow expected structure
- ✅ Optimization event emitted

**Test Data:**
- Workflow files: BPMN, DrawIO, JSON workflows

---

### Test 3.2: Generate SOP Flow

**Purpose:** Verify SOP generation from workflow works end-to-end

**Test Steps:**
1. Upload and parse workflow file (via Content Realm)
2. Submit `generate_sop` intent with `workflow_id`
3. Verify WorkflowConversionService.generate_sop() called
4. Verify SOP generated from workflow
5. Verify SOP stored (if applicable)
6. Verify SOP reference registered in State Surface

**Success Criteria:**
- ✅ SOP generated successfully
- ✅ SOP follows expected format (Markdown, text)
- ✅ SOP linked to original workflow
- ✅ SOP generation event emitted

**Test Data:**
- Workflow files: BPMN, DrawIO, JSON workflows

---

### Test 3.3: Create Workflow Flow

**Purpose:** Verify workflow creation from SOP works end-to-end

**Test Steps:**
1. Upload and parse SOP file (Markdown) via Content Realm
2. Submit `create_workflow` intent with `sop_id`
3. Verify WorkflowConversionService.create_workflow() called
4. Verify workflow created from SOP
5. Verify workflow stored (if applicable)
6. Verify workflow reference registered in State Surface

**Success Criteria:**
- ✅ Workflow created successfully
- ✅ Workflow follows expected format (BPMN, JSON)
- ✅ Workflow linked to original SOP
- ✅ Workflow creation event emitted

**Test Data:**
- SOP files: Markdown, text files

---

### Test 3.4: Analyze Coexistence Flow

**Purpose:** Verify coexistence analysis works end-to-end

**Test Steps:**
1. Upload and parse workflow file (via Content Realm)
2. Submit `analyze_coexistence` intent with `workflow_id`
3. Verify CoexistenceAnalysisService.analyze_coexistence() called
4. Verify coexistence opportunities identified
5. Verify recommendations returned
6. Verify analysis artifacts stored (if applicable)

**Success Criteria:**
- ✅ Coexistence analysis completed successfully
- ✅ Coexistence opportunities identified
- ✅ Recommendations follow expected structure
- ✅ Coexistence analysis event emitted

**Test Data:**
- Workflow files: BPMN, DrawIO, JSON workflows with human+AI steps

---

### Test 3.5: Create Blueprint Flow

**Purpose:** Verify blueprint creation works end-to-end

**Test Steps:**
1. Upload and parse workflow file (via Content Realm)
2. Analyze coexistence (via Test 3.4)
3. Submit `create_blueprint` intent with `workflow_id`
4. Verify CoexistenceAnalysisService.create_blueprint() called
5. Verify blueprint created from analysis
6. Verify blueprint stored (if applicable)
7. Verify blueprint reference registered in State Surface

**Success Criteria:**
- ✅ Blueprint created successfully
- ✅ Blueprint follows expected format
- ✅ Blueprint linked to original workflow
- ✅ Blueprint creation event emitted

**Test Data:**
- Workflow files: BPMN, DrawIO, JSON workflows

---

## 🧪 Test Suite 4: Cross-Realm E2E

### Test 4.1: Content → Insights Flow

**Purpose:** Verify Content Realm output can be used by Insights Realm

**Test Steps:**
1. Upload and parse file (via Content Realm)
2. Submit `analyze_content` intent (Insights Realm) with `parsed_file_id` from Content Realm
3. Verify Insights Realm can access parsed file via State Surface
4. Verify analysis completed successfully
5. Verify cross-realm lineage maintained

**Success Criteria:**
- ✅ Insights Realm can access Content Realm artifacts
- ✅ State Surface provides cross-realm access
- ✅ Lineage maintained across realms
- ✅ Cross-realm event emitted

---

### Test 4.2: Content → Operations Flow

**Purpose:** Verify Content Realm output can be used by Operations Realm

**Test Steps:**
1. Upload and parse workflow file (via Content Realm)
2. Submit `optimize_process` intent (Operations Realm) with `workflow_id` from Content Realm
3. Verify Operations Realm can access parsed workflow via State Surface
4. Verify optimization completed successfully
5. Verify cross-realm lineage maintained

**Success Criteria:**
- ✅ Operations Realm can access Content Realm artifacts
- ✅ State Surface provides cross-realm access
- ✅ Lineage maintained across realms
- ✅ Cross-realm event emitted

---

### Test 4.3: Insights → Operations Flow

**Purpose:** Verify Insights Realm output can be used by Operations Realm

**Test Steps:**
1. Upload, parse, and analyze file (via Content + Insights Realms)
2. Submit `create_blueprint` intent (Operations Realm) with analysis results from Insights Realm
3. Verify Operations Realm can access Insights Realm artifacts via State Surface
4. Verify blueprint creation completed successfully
5. Verify cross-realm lineage maintained

**Success Criteria:**
- ✅ Operations Realm can access Insights Realm artifacts
- ✅ State Surface provides cross-realm access
- ✅ Lineage maintained across realms
- ✅ Cross-realm event emitted

---

## 🧪 Test Suite 5: Runtime Integration E2E

### Test 5.1: Full Intent Flow (Experience → Runtime → Realm)

**Purpose:** Verify complete intent flow from Experience Plane to Realm

**Test Steps:**
1. Create session via Experience Plane API
2. Submit intent via Experience Plane API
3. Verify intent routed to Runtime
4. Verify Runtime routes intent to correct Realm
5. Verify Realm processes intent
6. Verify response returned to Experience Plane
7. Verify execution logged in WAL
8. Verify events published to TransactionalOutbox

**Success Criteria:**
- ✅ Intent flow: Experience → Runtime → Realm → Runtime → Experience
- ✅ Execution logged in WAL (tenant + date partitioned)
- ✅ Events published to TransactionalOutbox
- ✅ Response returned to Experience Plane
- ✅ Execution status trackable via Runtime API

---

### Test 5.2: Multi-Tenant Isolation

**Purpose:** Verify strict tenant isolation across all realms

**Test Steps:**
1. Create sessions for Tenant A and Tenant B
2. Upload files for both tenants
3. Verify Tenant A cannot access Tenant B's files
4. Verify State Surface isolates by tenant
5. Verify WAL isolates by tenant
6. Verify all abstractions enforce tenant isolation

**Success Criteria:**
- ✅ Tenant A cannot access Tenant B's data
- ✅ State Surface isolates by tenant
- ✅ WAL isolates by tenant
- ✅ All abstractions enforce tenant isolation
- ✅ No cross-tenant data leakage

---

### Test 5.3: Execution Replay

**Purpose:** Verify execution can be replayed from WAL

**Test Steps:**
1. Execute intent (any realm)
2. Verify execution logged in WAL
3. Replay execution from WAL
4. Verify replayed execution produces same results
5. Verify State Surface state matches original execution

**Success Criteria:**
- ✅ Execution logged in WAL (all steps)
- ✅ Execution can be replayed from WAL
- ✅ Replayed execution produces same results
- ✅ State Surface state matches original execution
- ✅ Deterministic replay (same inputs → same outputs)

---

### Test 5.4: Error Handling and Recovery

**Purpose:** Verify error handling and recovery work correctly

**Test Steps:**
1. Submit intent with invalid parameters
2. Verify error returned to Experience Plane
3. Verify error logged in WAL
4. Verify error event published
5. Submit valid intent after error
6. Verify system recovers and processes valid intent

**Success Criteria:**
- ✅ Invalid intents rejected with clear error messages
- ✅ Errors logged in WAL
- ✅ Error events published
- ✅ System recovers after errors
- ✅ Valid intents processed after errors

---

## 📊 Test Execution Strategy

### Test Environment Setup

1. **Infrastructure Containers:**
   - Redis (WAL, State Surface, TransactionalOutbox)
   - ArangoDB (Semantic data, knowledge graph)
   - Supabase (File metadata, auth, tenancy)
   - GCS (File storage)
   - Consul (Service discovery)
   - Prometheus (Metrics)
   - OpenTelemetry Collector (Telemetry)

2. **Runtime Service:**
   - Start Runtime service with all 3 realms registered
   - Verify all realms registered successfully
   - Verify Public Works initialized successfully

3. **Test Data:**
   - Create test tenant
   - Create test user
   - Prepare test files (various types, sizes)

### Test Execution Order

1. **Phase 1: Content Realm Tests** (Tests 1.1 - 1.4)
   - Foundation for other realms
   - Must pass before cross-realm tests

2. **Phase 2: Insights Realm Tests** (Tests 2.1 - 2.5)
   - Depends on Content Realm
   - Can run in parallel with Operations Realm tests

3. **Phase 3: Operations Realm Tests** (Tests 3.1 - 3.5)
   - Depends on Content Realm
   - Can run in parallel with Insights Realm tests

4. **Phase 4: Cross-Realm Tests** (Tests 4.1 - 4.3)
   - Depends on all 3 realms
   - Validates cross-realm interactions

5. **Phase 5: Runtime Integration Tests** (Tests 5.1 - 5.4)
   - Full system integration
   - Validates Runtime governance

### Test Data Management

- **Setup:** Create test data before each test suite
- **Cleanup:** Clean up test data after each test suite
- **Isolation:** Each test uses unique identifiers (file_id, session_id, etc.)
- **Tenant Isolation:** Use separate tenants for isolation tests

### Success Criteria

**Overall Test Suite Success:**
- ✅ All Content Realm tests pass (100%)
- ✅ All Insights Realm tests pass (100%)
- ✅ All Operations Realm tests pass (100%)
- ✅ All Cross-Realm tests pass (100%)
- ✅ All Runtime Integration tests pass (100%)

**Individual Test Success:**
- ✅ All success criteria met
- ✅ No errors or warnings
- ✅ Execution time within acceptable limits
- ✅ State Surface state correct
- ✅ WAL entries correct
- ✅ Events published correctly

---

## 🔧 Test Implementation Notes

### Test Fixtures

- **Public Works Foundation:** Initialize once per test session
- **Runtime Components:** Initialize once per test session
- **Test Tenant:** Create per test suite
- **Test Files:** Create per test (cleanup after)

### Test Utilities

- **File Upload Helper:** Upload file and return file_id
- **Intent Submission Helper:** Submit intent and return execution_id
- **State Surface Helper:** Get file reference from State Surface
- **Verification Helpers:** Verify GCS, Supabase, ArangoDB state

### Test Assertions

- **File Storage:** Verify file exists in GCS
- **File Metadata:** Verify metadata exists in Supabase
- **State Surface:** Verify reference exists in State Surface
- **Execution:** Verify execution logged in WAL
- **Events:** Verify events published to TransactionalOutbox
- **Tenant Isolation:** Verify tenant boundaries enforced

---

## 📝 Next Steps

1. **Implement Test Suite 1:** Content Realm E2E tests
2. **Implement Test Suite 2:** Insights Realm E2E tests
3. **Implement Test Suite 3:** Operations Realm E2E tests
4. **Implement Test Suite 4:** Cross-Realm E2E tests
5. **Implement Test Suite 5:** Runtime Integration E2E tests
6. **Run All Tests:** Execute full test suite
7. **Fix Issues:** Address any failures
8. **Document Results:** Document test results and coverage

---

## ✅ Test Coverage Goals

- **Content Realm:** 100% intent coverage
- **Insights Realm:** 100% intent coverage
- **Operations Realm:** 100% intent coverage
- **Cross-Realm:** All interaction patterns
- **Runtime Integration:** All Runtime features

---

**Status:** 📋 **READY FOR IMPLEMENTATION**
