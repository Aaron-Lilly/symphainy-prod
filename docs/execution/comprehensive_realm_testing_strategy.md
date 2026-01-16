# Comprehensive Realm Testing Strategy: MVP Showcase & Composability

**Status:** Critical Foundation  
**Created:** January 2026  
**Goal:** Ensure ALL MVP showcase features work with REAL functionality AND remain composable

---

## Executive Summary

This strategy ensures **every feature** described in the MVP showcase works with **real infrastructure** and **real operations**, while maintaining **composability** for complex scenarios like 350k policies.

**Critical Principle:** If it doesn't work with real infrastructure, it won't work in production. If it doesn't compose, we'll rebuild for every scenario.

---

## MVP Showcase Feature Mapping

### Content Pillar (Content Realm)

| MVP Feature | Intent | Test Coverage | Real Infrastructure |
|------------|--------|---------------|---------------------|
| Upload files | `ingest_file` | ✅ E2E Test | GCS + Supabase |
| See parsed results | `parse_content` | ✅ E2E Test | GCS + Supabase lineage |
| See semantic interpretation | `extract_embeddings` | ✅ E2E Test | ArangoDB + Supabase lineage |

### Insights Pillar (Insights Realm)

**Phase 1: Data Quality**

| MVP Feature | Intent | Test Coverage | Real Infrastructure |
|------------|--------|---------------|---------------------|
| Combined parsing + embedding quality assessment | `assess_data_quality` | ⏳ E2E Test | GCS parsed data + ArangoDB embeddings + Supabase |
| Parsing issue identification | `assess_data_quality` (parsing dimension) | ⏳ E2E Test | GCS + Supabase |
| Data quality issue identification | `assess_data_quality` (data dimension) | ⏳ E2E Test | GCS + ArangoDB |
| Source issue identification | `assess_data_quality` (source dimension) | ⏳ E2E Test | GCS + Supabase |
| Root cause analysis | `assess_data_quality` (combined) | ⏳ E2E Test | GCS + ArangoDB + Supabase |

**Phase 2: Data Interpretation**

| MVP Feature | Intent | Test Coverage | Real Infrastructure |
|------------|--------|---------------|---------------------|
| Semantic self-discovery | `interpret_data_self_discovery` | ⏳ E2E Test | ArangoDB embeddings + GCS |
| Guided discovery (default guides) | `interpret_data_guided` (default) | ⏳ E2E Test | ArangoDB + Supabase guides |
| Guided discovery (user guides) | `interpret_data_guided` (user) | ⏳ E2E Test | ArangoDB + Supabase guides |
| PSO guide (default) | `interpret_data_guided` (PSO) | ⏳ E2E Test | ArangoDB + Supabase PSO guide |
| AAR guide (default) | `interpret_data_guided` (AAR) | ⏳ E2E Test | ArangoDB + Supabase AAR guide |
| Guide creation/upload | `register_guide` | ⏳ E2E Test | Supabase guides table |
| Matching results (matched/unmatched/missing) | `interpret_data_guided` (results) | ⏳ E2E Test | ArangoDB + Supabase |

**Phase 3: Business Analysis**

| MVP Feature | Intent | Test Coverage | Real Infrastructure |
|------------|--------|---------------|---------------------|
| Structured data analysis | `analyze_structured_data` | ⏳ E2E Test | GCS parsed data + ArangoDB |
| Unstructured data analysis | `analyze_unstructured_data` | ⏳ E2E Test | GCS parsed data + ArangoDB |
| Deep dive (Insights Liaison Agent) | `analyze_unstructured_data` (deep_dive) | ⏳ E2E Test | ArangoDB + Agent system |
| Data mapping (data mash virtual pipeline) | `create_virtual_mapping` | ⏳ E2E Test | ArangoDB graph + Supabase lineage |

### Operations/Journey Pillar (Journey Realm)

| MVP Feature | Intent | Test Coverage | Real Infrastructure |
|------------|--------|---------------|---------------------|
| Create workflow visuals from embeddings | `create_workflow` (with visual) | ⏳ E2E Test | ArangoDB embeddings + GCS visuals |
| Create SOP visuals from embeddings | `generate_sop` (with visual) | ⏳ E2E Test | ArangoDB embeddings + GCS visuals |
| Generate workflow from SOP (with visual) | `create_workflow` (from SOP) | ⏳ E2E Test | GCS SOP + ArangoDB + GCS workflow + visual |
| Generate SOP from workflow (with visual) | `generate_sop` (from workflow) | ⏳ E2E Test | GCS workflow + ArangoDB + GCS SOP + visual |
| Generate SOP from scratch (interactive chat) | `generate_sop_from_chat` | ⏳ E2E Test | Chat input + ArangoDB + GCS SOP + visual |
| Analyze coexistence (human+AI) | `analyze_coexistence` | ⏳ E2E Test | GCS workflows/SOPs + ArangoDB analysis |
| Create coexistence blueprint | `create_blueprint` | ⏳ E2E Test | GCS analysis + ArangoDB + GCS blueprint |
| Turn blueprint into platform journey | `create_solution` (from blueprint) | ⏳ E2E Test | GCS blueprint + Supabase solution |
| Complete lineage tracking | Lineage queries | ⏳ E2E Test | Supabase + Data Brain |

### Business Outcomes Pillar (Outcomes Realm)

| MVP Feature | Intent | Test Coverage | Real Infrastructure |
|------------|--------|---------------|---------------------|
| Create summary visual | `synthesize_outcome` (with visual) | ⏳ E2E Test | All realm outputs + GCS visual |
| Generate roadmap (with visual) | `generate_roadmap` (with visual) | ⏳ E2E Test | Realm summaries + GCS roadmap + visual |
| Generate POC proposal (with visual) | `create_poc` (with visual) | ⏳ E2E Test | Realm summaries + GCS proposal + visual |
| Turn roadmap into solution | `create_solution` (from roadmap) | ⏳ E2E Test | GCS roadmap + Supabase solution |
| Turn POC into solution | `create_solution` (from POC) | ⏳ E2E Test | GCS POC + Supabase solution |
| Complete lineage tracking | Lineage queries | ⏳ E2E Test | Supabase + Data Brain |

---

## Testing Architecture

### Test Infrastructure Requirements

1. **GCS Bucket** (test bucket, isolated)
2. **Supabase Database** (test database, isolated)
3. **ArangoDB** (test database, isolated)
4. **Real Test Data:**
   - COBOL copybooks
   - JSON files
   - CSV files
   - Workflow files
   - SOP files
   - Permit (PSO) documents
   - After Action Report (AAR) documents

### Test Data Strategy

- **Isolated Test Data:** Each test uses unique IDs
- **Cleanup:** Tests clean up after themselves
- **Realistic Data:** Use real file formats, real document types
- **Scale Testing:** Test with 1 file, 10 files, 100 files, 1000 files

---

## Content Realm E2E Tests

### Test Suite: `tests/integration/realms/content/test_content_realm_e2e.py`

#### Test 1: File Upload → GCS → Supabase Metadata
**Validates:** File uploaded, stored in GCS, metadata in Supabase

#### Test 2: File Parsing → GCS Results → Supabase Lineage
**Validates:** File parsed, results in GCS, lineage in Supabase (file → parsed_result)

#### Test 3: Embedding Generation → ArangoDB → Supabase Lineage
**Validates:** Embeddings in ArangoDB, lineage in Supabase (file → embeddings, many:1)

#### Test 4: Complete Flow (Upload → Parse → Embed)
**Validates:** Complete end-to-end flow with full lineage chain

#### Test 5: Multiple Files → Batch Operations
**Validates:** Same capabilities work for multiple files, batch operations efficient

---

## Insights Realm E2E Tests

### Test Suite: `tests/integration/realms/insights/test_insights_realm_e2e.py`

#### Phase 1: Data Quality Tests

**Test 1: Combined Quality Assessment**
**What it validates:**
- Combined parsing + embedding analysis works
- Quality assessment identifies parsing, data, and source issues
- Root cause analysis works

**Test Steps:**
1. Upload file with known issues (faded document, copybook mismatch, etc.)
2. Parse file via Content Realm
3. Generate embeddings via Content Realm
4. Call Insights Realm `assess_data_quality` intent
5. Verify parsing quality assessment
6. Verify data quality assessment
7. Verify source quality assessment
8. Verify root cause analysis identifies primary issue
9. Verify suggestions provided

**Test 2: Parsing Issue Identification**
**What it validates:**
- Parsing quality issues identified correctly
- Suggestions for parser configuration provided

**Test Steps:**
1. Upload file with parsing issues (missing fields, format mismatches)
2. Parse file
3. Call `assess_data_quality` intent
4. Verify parsing quality issues identified
5. Verify suggestions provided

**Test 3: Data Quality Issue Identification**
**What it validates:**
- Data quality issues identified correctly
- Faded documents, corrupted data detected

**Test Steps:**
1. Upload faded/corrupted document
2. Parse file
3. Generate embeddings
4. Call `assess_data_quality` intent
5. Verify data quality issues identified
6. Verify root cause is "data" not "parsing"

**Test 4: Source Issue Identification**
**What it validates:**
- Source quality issues identified correctly
- Copybook mismatches detected

**Test Steps:**
1. Upload file with copybook mismatch
2. Parse file
3. Call `assess_data_quality` intent
4. Verify source quality issues identified
5. Verify suggestions for copybook review

#### Phase 2: Data Interpretation Tests

**Test 5: Semantic Self Discovery**
**What it validates:**
- AI discovers entities and relationships without constraints
- Semantic summary generated

**Test Steps:**
1. Use parsed file and embeddings from Content Realm
2. Call Insights Realm `interpret_data_self_discovery` intent
3. Verify entities discovered
4. Verify relationships discovered
5. Verify semantic summary generated
6. Verify results stored in GCS

**Test 6: Guided Discovery - Default PSO Guide**
**What it validates:**
- Default PSO guide works
- Matched entities identified
- Unmatched data identified with suggestions

**Test Steps:**
1. Upload PSO document
2. Parse and generate embeddings
3. Call Insights Realm `interpret_data_guided` intent with default PSO guide
4. Verify matched entities (permit, applicant, property, etc.)
5. Verify unmatched data identified
6. Verify missing expected entities identified
7. Verify suggestions provided
8. Verify output matches PSO template

**Test 7: Guided Discovery - Default AAR Guide**
**What it validates:**
- Default AAR guide works
- Matched entities identified
- Unmatched data identified with suggestions

**Test Steps:**
1. Upload AAR document
2. Parse and generate embeddings
3. Call Insights Realm `interpret_data_guided` intent with default AAR guide
4. Verify matched entities (event, action, outcome, lesson_learned)
5. Verify unmatched data identified
6. Verify suggestions provided
7. Verify output matches AAR template

**Test 8: Guided Discovery - User Guide**
**What it validates:**
- User-created guide works
- Guide creation/upload works

**Test Steps:**
1. Create user guide (fact pattern + output template)
2. Register guide in Guide Registry
3. Upload custom document
4. Parse and generate embeddings
5. Call Insights Realm `interpret_data_guided` intent with user guide
6. Verify interpretation uses guide constraints
7. Verify output matches user template
8. Verify unmatched data identified

**Test 9: Guide Creation**
**What it validates:**
- Guide creation via API works
- Guide can be tested against sample data

**Test Steps:**
1. Create guide via Guide Registry API
2. Test guide against sample data
3. Verify guide works correctly
4. Verify guide stored in Supabase

#### Phase 3: Business Analysis Tests

**Test 10: Structured Data Analysis**
**What it validates:**
- Structured data analysis works
- Statistical analysis, pattern detection performed

**Test Steps:**
1. Use parsed structured data (CSV, JSON) from Content Realm
2. Call Insights Realm `analyze_structured_data` intent
3. Verify statistical analysis performed
4. Verify patterns detected
5. Verify results stored in GCS

**Test 11: Unstructured Data Analysis**
**What it validates:**
- Unstructured data analysis works
- Semantic analysis, topic modeling performed

**Test Steps:**
1. Use parsed unstructured data (PDF, text) from Content Realm
2. Call Insights Realm `analyze_unstructured_data` intent
3. Verify semantic analysis performed
4. Verify topics extracted
5. Verify results stored in GCS

**Test 12: Deep Dive with Insights Liaison Agent**
**What it validates:**
- Insights Liaison Agent engages for deep dive
- Interactive analysis works

**Test Steps:**
1. Upload data
2. Call Insights Realm `analyze_unstructured_data` intent with `deep_dive: true`
3. Verify Insights Liaison Agent engages
4. Verify interactive analysis works
5. Verify agent can answer questions
6. Verify agent provides detailed insights

**Test 13: Data Mapping (Data Mash Virtual Pipeline)**
**What it validates:**
- Virtual data mapping works
- Relationships created in ArangoDB graph
- No data ingestion

**Test Steps:**
1. Use multiple parsed files from Content Realm
2. Create mapping schema
3. Call Insights Realm `create_virtual_mapping` intent
4. Verify relationships created in ArangoDB graph
5. Verify lineage in Supabase (file → relationships)
6. Verify no data ingestion (virtual pipeline)
7. Query relationships via ArangoDB graph queries

**Test 14: Complete Lineage Chain Verification**
**What it validates:**
- Complete lineage chain from file → parse → embed → interpret → analyze
- All links present in Supabase
- All references registered in Data Brain
- Full provenance chain queryable

**Test Steps:**
1. Upload file
2. Parse file (verify parsed_results table entry)
3. Generate embeddings (verify embeddings table entry, links to file + parsed_result)
4. Interpret with guide (verify interpretations table entry, links to file + parsed_result + embedding + guide)
5. Analyze data (verify analyses table entry, links to file + parsed_result + interpretation + guide)
6. Query complete lineage chain via Supabase
7. Query complete lineage chain via Data Brain
8. Verify can trace embedding back to original file
9. Verify can trace interpretation back to guide used
10. Verify can trace analysis back to guide used
11. Verify full provenance chain is complete

---

## Journey Realm E2E Tests

### Test Suite: `tests/integration/realms/journey/test_journey_realm_e2e.py`

#### Test 1: Create Workflow Visuals from Embeddings
**What it validates:**
- Workflow visuals generated from semantic embeddings
- Visuals stored in GCS
- Lineage maintained (embeddings → workflow visual)

**Test Steps:**
1. Use embeddings from Content Realm
2. Call Journey Realm `create_workflow` intent (from SOP)
3. Verify workflow visual generated
4. Verify visual stored in GCS
5. Verify lineage in Supabase

#### Test 2: Create SOP Visuals from Embeddings
**What it validates:**
- SOP visuals generated from semantic embeddings
- Visuals stored in GCS
- Lineage maintained (embeddings → SOP visual)

**Test Steps:**
1. Use embeddings from Content Realm
2. Call Journey Realm `generate_sop` intent (from workflow)
3. Verify SOP visual generated
4. Verify visual stored in GCS
5. Verify lineage in Supabase

#### Test 3: Generate Workflow from SOP
**What it validates:**
- Workflow generated from SOP file
- Workflow stored in GCS
- Lineage maintained (SOP → workflow)

**Test Steps:**
1. Upload SOP file
2. Parse SOP file
3. Call Journey Realm `create_workflow` intent (from SOP)
4. Verify workflow generated
5. Verify workflow stored in GCS
6. Verify lineage in Supabase

#### Test 4: Generate SOP from Workflow
**What it validates:**
- SOP generated from workflow file
- SOP stored in GCS
- Lineage maintained (workflow → SOP)

**Test Steps:**
1. Upload workflow file
2. Parse workflow file
3. Call Journey Realm `generate_sop` intent (from workflow)
4. Verify SOP generated
5. Verify SOP stored in GCS
6. Verify lineage in Supabase

#### Test 5: Generate SOP from Scratch (Interactive Chat)
**What it validates:**
- SOP generated from chat input
- SOP stored in GCS
- Chat interaction logged

**Test Steps:**
1. Provide chat input (SOP requirements)
2. Call Journey Realm `generate_sop` intent (from chat)
3. Verify SOP generated
4. Verify SOP stored in GCS
5. Verify chat interaction logged

#### Test 6: Analyze Coexistence (Human+AI)
**What it validates:**
- Coexistence analysis performed on workflows/SOPs
- Analysis results stored
- Human+AI optimization opportunities identified

**Test Steps:**
1. Use workflows/SOPs from previous tests
2. Call Journey Realm `analyze_coexistence` intent
3. Verify coexistence analysis performed
4. Verify optimization opportunities identified
5. Verify results stored in GCS
6. Verify lineage in Supabase

#### Test 7: Create Coexistence Blueprint
**What it validates:**
- Blueprint created from coexistence analysis
- Blueprint stored in GCS
- Lineage maintained (analysis → blueprint)

**Test Steps:**
1. Use coexistence analysis from Test 6
2. Call Journey Realm `create_blueprint` intent
3. Verify blueprint created
4. Verify blueprint stored in GCS
5. Verify lineage in Supabase

#### Test 8: Turn Blueprint into Platform Journey
**What it validates:**
- Platform journey created from blueprint
- Journey stored in Supabase (solution)
- Lineage maintained (blueprint → journey)

**Test Steps:**
1. Use blueprint from Test 7
2. Call Journey Realm `create_solution` intent (from blueprint)
3. Verify platform journey created
4. Verify journey stored in Supabase
5. Verify lineage in Supabase

---

## Outcomes Realm E2E Tests

### Test Suite: `tests/integration/realms/outcomes/test_outcomes_realm_e2e.py`

#### Test 1: Create Summary Visual
**What it validates:**
- Summary visual created from all realm outputs
- Visual stored in GCS
- All realm outputs aggregated

**Test Steps:**
1. Use outputs from Content, Insights, Journey realms
2. Call Outcomes Realm `synthesize_outcome` intent
3. Verify summary visual created
4. Verify visual stored in GCS
5. Verify all realm outputs aggregated

#### Test 2: Generate Roadmap
**What it validates:**
- Roadmap generated from realm summaries
- Roadmap stored in GCS
- Lineage maintained (realm outputs → roadmap)

**Test Steps:**
1. Use realm summaries from Test 1
2. Call Outcomes Realm `generate_roadmap` intent
3. Verify roadmap generated
4. Verify roadmap stored in GCS
5. Verify lineage in Supabase

#### Test 3: Generate POC Proposal
**What it validates:**
- POC proposal generated from realm summaries
- Proposal stored in GCS
- Lineage maintained (realm outputs → POC)

**Test Steps:**
1. Use realm summaries from Test 1
2. Call Outcomes Realm `create_poc` intent
3. Verify POC proposal generated
4. Verify proposal stored in GCS
5. Verify lineage in Supabase

#### Test 4: Turn Roadmap into Platform Solution
**What it validates:**
- Platform solution created from roadmap
- Solution stored in Supabase
- Lineage maintained (roadmap → solution)

**Test Steps:**
1. Use roadmap from Test 2
2. Call Outcomes Realm `create_solution` intent (from roadmap)
3. Verify platform solution created
4. Verify solution stored in Supabase
5. Verify lineage in Supabase

#### Test 5: Turn POC into Platform Solution
**What it validates:**
- Platform solution created from POC
- Solution stored in Supabase
- Lineage maintained (POC → solution)

**Test Steps:**
1. Use POC from Test 3
2. Call Outcomes Realm `create_solution` intent (from POC)
3. Verify platform solution created
4. Verify solution stored in Supabase
5. Verify lineage in Supabase

---

## MVP Showcase Integration Tests

### Test Suite: `tests/e2e/showcase/test_mvp_showcase_e2e.py`

#### Test 1: Complete Content Pillar Flow
**What it validates:**
- User uploads file via frontend
- File parsed and results displayed
- Embeddings generated and viewable

#### Test 2: Complete Insights Pillar Flow
**What it validates:**
- Quality assessment displayed
- Interactive analysis works (structured + unstructured)
- PSO analysis works
- AAR analysis works
- Data mapping (data mash) works

#### Test 3: Complete Operations/Journey Pillar Flow
**What it validates:**
- Workflow/SOP visuals generated
- Workflow ↔ SOP conversion works
- SOP from chat works
- Coexistence analysis works
- Blueprint creation works
- Journey creation from blueprint works

#### Test 4: Complete Business Outcomes Pillar Flow
**What it validates:**
- Summary visual created
- Roadmap generation works
- POC proposal generation works
- Solution creation from roadmap works
- Solution creation from POC works

#### Test 5: Complete Cross-Pillar Flow
**What it validates:**
- Content → Insights → Journey → Outcomes flow works
- All lineage maintained across pillars
- All artifacts accessible

---

## Composability Validation Tests

### Test Suite: `tests/e2e/composability/test_realm_composability.py`

#### Test 1: Single File → Multiple Realms
**What it validates:**
- Same file used across Content, Insights, Journey, Outcomes
- All realms can access same data
- Lineage maintained across realms

#### Test 2: Batch Operations (100 Files)
**What it validates:**
- Same parsing logic works for 100 files
- Same embedding logic works for 100 files
- Same analysis logic works for 100 files
- Lineage tracking works at scale

#### Test 3: 350k Scenario Preparation
**What it validates:**
- Same capabilities work for large-scale scenarios
- No reinvention needed
- Lineage tracking works at scale

---

## Implementation Priority

### Phase 1: Content Realm (Foundation)
1. ✅ File upload → GCS → Supabase
2. ✅ File parsing → GCS → Supabase lineage
3. ✅ Embedding generation → ArangoDB → Supabase lineage
4. ✅ Complete flow validation

### Phase 2: Insights Realm (Core Analysis)
1. ⏳ Quality assessment
2. ⏳ Interactive analysis (structured + unstructured)
3. ⏳ PSO analysis
4. ⏳ AAR analysis
5. ⏳ Data mapping (data mash virtual pipeline)

### Phase 3: Journey Realm (Operations)
1. ⏳ Workflow/SOP visuals
2. ⏳ Workflow ↔ SOP conversion
3. ⏳ SOP from chat
4. ⏳ Coexistence analysis
5. ⏳ Blueprint creation
6. ⏳ Journey creation from blueprint

### Phase 4: Outcomes Realm (Synthesis)
1. ⏳ Summary visual
2. ⏳ Roadmap generation
3. ⏳ POC proposal generation
4. ⏳ Solution creation (roadmap + POC)

### Phase 5: MVP Showcase Integration
1. ⏳ Complete pillar flows
2. ⏳ Cross-pillar integration
3. ⏳ Frontend → Backend integration

### Phase 6: Composability Validation
1. ⏳ Single file → multiple realms
2. ⏳ Batch operations (100 files)
3. ⏳ 350k scenario preparation

---

## Success Criteria

✅ **Real Functionality:**
- All operations use real infrastructure (GCS, Supabase, ArangoDB)
- No mocks for critical paths
- All data persists correctly

✅ **MVP Showcase:**
- All features described in MVP showcase work
- Frontend showcase works end-to-end
- All pillars functional

✅ **Composability:**
- Same capabilities work for 1 file and 350k files
- No reinvention needed for complex scenarios
- Lineage tracking works at any scale
