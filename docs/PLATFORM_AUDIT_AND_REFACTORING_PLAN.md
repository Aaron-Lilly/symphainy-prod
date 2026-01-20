# Comprehensive Platform Audit & Refactoring Plan

**Date:** January 20, 2026  
**Status:** 🔴 **CRITICAL AUDIT**  
**Purpose:** Identify all platform risks, gaps, and incomplete implementations

---

## Executive Summary

This audit reveals **critical gaps** between what tests pass and what's actually implemented. While many integration tests pass, several core capabilities are **placeholders** or **incomplete**, creating significant production risk.

### Critical Findings

1. **🔴 CRITICAL: Embedding Extraction is Placeholder** - Returns fake IDs, no actual embeddings created
2. **🟡 HIGH: Journey Realm artifacts not in Artifact Plane** - Blueprint test failure root cause
3. **🟡 HIGH: Missing EmbeddingService** - Referenced but doesn't exist
4. **🟡 MEDIUM: Incomplete error handling** - Many try/except blocks log but continue
5. **🟡 MEDIUM: MVP fallbacks everywhere** - Production code has "MVP" shortcuts
6. **🟢 LOW: Data architecture needs refinement** - Four-class model not fully implemented

---

## Part 1: Critical Implementation Gaps

### 1.1 Embedding Extraction - PLACEHOLDER ⚠️ CRITICAL (CORRECTED ANALYSIS)

**Location:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py:2589-2635`

**Current State:**
```python
async def _handle_extract_embeddings(...):
    # For MVP: Return placeholder
    # In full implementation: Create embeddings via EmbeddingService
    embedding_id = generate_event_id()
    arango_collection = "embeddings"
    arango_key = embedding_id
    
    # Track embeddings in Supabase for lineage
    await self._track_embedding(
        embedding_id=embedding_id,
        embedding_count=0,  # Will be updated when embeddings are actually created
        model_name="placeholder",  # Will be updated when embeddings are actually created
        ...
    )
```

**CORRECTED Understanding:**
- ✅ **Supabase `embeddings` table EXISTS** (migration: `001_create_insights_lineage_tables.sql`)
- ✅ **ArangoDB collection `structured_embeddings` EXISTS** (via `SemanticDataAbstraction`)
- ✅ **Old implementation exists** (`/symphainy_source/.../embedding_service.py`) showing full implementation
- ❌ **Current implementation is placeholder** - doesn't actually create embeddings
- ❌ **No `EmbeddingService` in current codebase** - old implementation not migrated

**What Actually Happens:**
1. `_handle_extract_embeddings()` generates fake `embedding_id`
2. `_track_embedding()` stores metadata in Supabase `embeddings` table (this works)
3. **NO actual embeddings created** - no vectors, no ArangoDB storage
4. Tests may pass because they check intent completion, not actual embedding creation

**Problems:**
- ❌ No actual embedding vectors are created
- ❌ No storage in ArangoDB `structured_embeddings` collection
- ❌ No `EmbeddingService` in current codebase (old one exists but not migrated)
- ❌ No connection to embedding models (HuggingFace, OpenAI, Cohere, etc.)
- ⚠️ Tests pass but don't validate actual embeddings exist

**Impact:**
- 🔴 **CRITICAL:** Any feature requiring embeddings will fail silently
- 🔴 **CRITICAL:** Semantic search, similarity matching, semantic interpretation all broken
- 🟡 **MEDIUM:** Tests pass because they check intent success, not embedding creation
- 🟡 **MEDIUM:** Supabase metadata tracking works, but no actual embeddings stored

**Evidence:**
- `_track_embedding` only stores metadata in Supabase
- No actual embedding vectors created
- No ArangoDB storage of embeddings
- `SemanticDataAbstraction` exists but not called

**Questions:**
1. **Q1:** Should embeddings be created immediately on `extract_embeddings` or deferred?
2. **Q2:** Which embedding model should we use? (OpenAI, Cohere, local model?)
3. **Q3:** Should embeddings be stored in ArangoDB or separate vector DB?
4. **Q4:** What's the relationship between `extract_embeddings` and `interpret_data`?

**Recommendations:**
1. **R1:** Create `EmbeddingService` in `content/enabling_services/`
2. **R2:** Implement actual embedding generation using configured model
3. **R3:** Store embeddings in ArangoDB (or vector DB) via `SemanticDataAbstraction`
4. **R4:** Update `_track_embedding` to store actual embedding metadata
5. **R5:** Add integration test that validates embeddings are actually created

---

### 1.2 Missing EmbeddingService

**Location:** Referenced in comments but doesn't exist

**Expected Location:** `symphainy_platform/realms/content/enabling_services/embedding_service.py`

**Current State:**
- ❌ File doesn't exist
- ❌ No service class
- ❌ No embedding creation logic

**What Should Exist:**
```python
class EmbeddingService:
    async def create_embeddings(
        self,
        parsed_content: Dict[str, Any],
        model_name: str = "text-embedding-ada-002",
        tenant_id: str
    ) -> Dict[str, Any]:
        # Actually create embeddings
        # Store in ArangoDB via SemanticDataAbstraction
        # Return embedding metadata
```

**Impact:**
- 🔴 Blocks all embedding-dependent features
- 🔴 Semantic interpretation can't work
- 🔴 Data quality assessment incomplete

**Recommendations:**
1. **R1:** Create `EmbeddingService` class
2. **R2:** Integrate with embedding model provider (OpenAI, Cohere, etc.)
3. **R3:** Use `SemanticDataAbstraction` for storage
4. **R4:** Update `content_orchestrator` to use service

---

### 1.3 Journey Realm - Artifact Plane Not Integrated

**Location:** `symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py`

**Current State:**
- ❌ Blueprints stored via `ArtifactStorageProtocol` directly (not Artifact Plane)
- ❌ SOPs stored in execution state (not Artifact Plane)
- ❌ Workflows stored in execution state (not Artifact Plane)
- ❌ No `ArtifactPlane` initialization

**Impact:**
- 🔴 **CRITICAL:** `create_solution_from_blueprint` test fails (blueprint not found)
- 🔴 Blueprints can't be retrieved by Outcomes Realm
- 🔴 Artifacts scattered across execution state and storage

**Evidence:**
- `test_create_solution_from_blueprint.py` fails with "Blueprint not found"
- Outcomes Realm tries to retrieve from Artifact Plane, but Journey Realm doesn't store there

**Recommendations:**
1. **R1:** Initialize `ArtifactPlane` in `JourneyOrchestrator.__init__`
2. **R2:** Update `_handle_create_blueprint` to use Artifact Plane
3. **R3:** Update `_handle_generate_sop` to use Artifact Plane
4. **R4:** Update `_handle_create_workflow` to use Artifact Plane
5. **R5:** Test blueprint → solution flow

---

### 1.4 Insights Realm - Artifact Plane Not Integrated

**Location:** `symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py`

**Current State:**
- ❌ No `ArtifactPlane` initialization
- ❌ All artifacts stored in execution state
- ❌ Semantic interpretations, quality reports, analysis results not in Artifact Plane

**Impact:**
- 🟡 Artifacts can't be retrieved across sessions
- 🟡 No lifecycle management for insights artifacts
- 🟡 Inconsistent with Outcomes Realm pattern

**Recommendations:**
1. **R1:** Initialize `ArtifactPlane` in `InsightsOrchestrator`
2. **R2:** Migrate all artifact creation to Artifact Plane
3. **R3:** Update test files to retrieve from Artifact Plane

---

## Part 2: Architectural Gaps

### 2.1 Four-Class Data Architecture Not Fully Implemented

**User's Framework:**
1. **Working Materials** - Temporary, time-bound (FMS)
2. **Records of Fact** - Persistent meaning (embeddings, interpretations)
3. **Purpose-Bound Outcomes** - Intentional deliverables (Artifact Plane)
4. **Platform DNA** - Generalized capabilities (Solution Registry)

**Current State:**

#### Working Materials ✅ MOSTLY CORRECT
- ✅ FMS handles file ingestion
- ✅ Boundary contracts govern access
- ✅ TTL tracked in contracts
- ⚠️ **GAP:** TTL enforcement/purge automation missing

#### Records of Fact ⚠️ INCOMPLETE
- ⚠️ Embeddings are placeholders (not actually created)
- ⚠️ No explicit "promote to Record of Fact" workflow
- ⚠️ Boundary between parsed content (Working Material) and embeddings (Record of Fact) unclear
- ⚠️ "Persistence of meaning ≠ persistence of material" principle not enforced

#### Purpose-Bound Outcomes ⚠️ PARTIALLY IMPLEMENTED
- ✅ Outcomes Realm uses Artifact Plane
- ❌ Journey Realm doesn't use Artifact Plane
- ❌ Insights Realm doesn't use Artifact Plane
- ⚠️ **GAP:** Lifecycle states (draft → accepted → obsolete) not tracked
- ⚠️ **GAP:** Owner/purpose metadata not captured

#### Platform DNA ⚠️ DISCONNECTED
- ✅ Solution Registry exists
- ⚠️ **GAP:** No promotion workflow (Purpose-Bound Outcome → Platform DNA)
- ⚠️ **GAP:** De-identification/generalization logic missing
- ⚠️ **GAP:** Registry is in-memory (needs persistent Supabase registry)

**Questions:**
1. **Q5:** When does parsed content become a "Record of Fact"? (When embeddings created?)
2. **Q6:** Should embeddings persist even if source file expires? (Yes, per user's principle)
3. **Q7:** How do we track lifecycle states in Artifact Plane?
4. **Q8:** What's the promotion criteria for Platform DNA?

**Recommendations:**
1. **R6:** Implement explicit "promote to Record of Fact" workflow
2. **R7:** Add lifecycle states to Artifact Plane registry
3. **R8:** Add owner/purpose metadata to Artifact Plane
4. **R9:** Design Platform DNA promotion workflow
5. **R10:** Implement TTL enforcement for Working Materials

---

### 2.2 Error Handling - Too Permissive

**Location:** Throughout codebase

**Pattern Found:**
```python
try:
    # Critical operation
    result = await some_operation()
except Exception as e:
    self.logger.warning(f"Failed: {e}")  # Just logs, continues
    # Execution continues with partial/fake data
```

**Examples:**
- `outcomes_orchestrator.py:307` - Artifact Plane storage failure → logs warning, continues
- `journey_orchestrator.py:171` - Visualization failure → logs warning, continues
- `content_orchestrator.py:2603` - Embedding extraction → returns placeholder

**Problems:**
- ⚠️ Failures are logged but execution continues
- ⚠️ Partial data returned without indication
- ⚠️ Tests may pass with fake data
- ⚠️ Production errors hidden

**Impact:**
- 🟡 Silent failures in production
- 🟡 Difficult to debug
- 🟡 Tests don't catch real issues

**Recommendations:**
1. **R11:** Distinguish between recoverable and critical errors
2. **R12:** Fail fast on critical operations (artifact storage)
3. **R13:** Return error indicators in responses
4. **R14:** Add validation checks before returning results

---

### 2.3 MVP Fallbacks - Capability by Design, Implementation by Policy ✅

**Location:** Policy evaluation infrastructure, materialization policies

**Architectural Principle Applied:**
> **Capability by Design, Implementation by Policy**
> - Build real, robust infrastructure (secure by design)
> - Use permissive policies for MVP (open by policy)
> - Tighten policies for production without code changes

**Examples (Intentional MVP Policies):**
- `MaterializationPolicyStore` - Real infrastructure, permissive MVP policy
- `CuratorPrimitives.validate_promotion()` - Real validation, permissive MVP policy
- `DataStewardPrimitives` - Real policy evaluation, permissive MVP defaults

**Status:**
- ✅ **Real infrastructure exists** (MaterializationPolicyStore, policy tables, evaluation logic)
- ✅ **MVP uses permissive policies** (allows all materialization types, permissive promotion)
- ✅ **Production can tighten without code changes** (update policy records in database)
- ✅ **No architectural debt** - infrastructure is production-ready

**Remaining Placeholders (Not Policy-Based):**
- ⚠️ Embedding extraction still placeholder (needs EmbeddingService implementation)
- ⚠️ Some error handling still too permissive (needs improvement)

**Recommendations:**
1. ✅ **R15:** Policy infrastructure complete - no migration needed
2. ⏳ **R16:** Replace embedding placeholder with real implementation (EmbeddingService)
3. ✅ **R17:** Policy-based approach eliminates need for feature flags
4. ✅ **R18:** Documented in architecture docs and developer guide

---

## Part 3: Test Coverage Gaps

### 3.1 Embedding Tests Missing

**Current State:**
- ❌ No test for `extract_embeddings` intent
- ❌ No validation that embeddings are actually created
- ❌ No test for embedding retrieval

**Impact:**
- 🔴 Critical functionality untested
- 🔴 Placeholder implementation not caught

**Recommendations:**
1. **R19:** Create `test_extract_embeddings.py`
2. **R20:** Validate embeddings are actually created (not placeholders)
3. **R21:** Test embedding retrieval from ArangoDB

---

### 3.2 Artifact Plane Tests Incomplete

**Current State:**
- ✅ Outcomes Realm tests pass (5/6)
- ❌ Journey Realm artifacts not tested with Artifact Plane
- ❌ Insights Realm artifacts not tested with Artifact Plane

**Impact:**
- 🟡 Inconsistent artifact storage patterns
- 🟡 Cross-realm artifact retrieval untested

**Recommendations:**
1. **R22:** Test Journey Realm artifacts in Artifact Plane
2. **R23:** Test Insights Realm artifacts in Artifact Plane
3. **R24:** Test cross-realm artifact retrieval

---

## Part 4: Database & Infrastructure

### 4.1 Embeddings Table Schema - EXISTS ✅ (CORRECTED)

**Current State:**
- ✅ **`embeddings` table EXISTS** (migration: `scripts/migrations/001_create_insights_lineage_tables.sql`)
- ✅ Schema matches code expectations:
  - `id` (UUID)
  - `tenant_id` (UUID)
  - `file_id` (UUID)
  - `parsed_result_id` (UUID reference)
  - `embedding_id` (TEXT)
  - `arango_collection` (TEXT)
  - `arango_key` (TEXT)
  - `embedding_count` (INTEGER)
  - `model_name` (TEXT)
- ✅ **ArangoDB collection `structured_embeddings` EXISTS** (via `SemanticDataAbstraction`)

**What This Means:**
- ✅ `_track_embedding()` can store metadata successfully
- ✅ Lineage tracking infrastructure is in place
- ❌ **BUT:** No actual embeddings are created/stored (placeholder implementation)

**Real Issue:**
- The infrastructure exists (Supabase table, ArangoDB collection)
- The implementation is missing (no actual embedding creation)
- Tests pass because metadata tracking works, but embeddings don't exist

**Recommendations:**
1. **R25:** ✅ Table exists - no migration needed
2. **R26:** ✅ ArangoDB collection exists (`structured_embeddings`)
3. **R27:** Migrate old `EmbeddingService` implementation to current codebase
4. **R28:** Update `_handle_extract_embeddings()` to actually create embeddings

---

### 4.2 TTL Enforcement ✅ IMPLEMENTED

**Current State (Updated):**
- ✅ TTL tracked in `data_boundary_contracts.materialization_ttl`
- ✅ Expiration time calculated (`materialization_expires_at`)
- ✅ **Automated purge/cleanup job implemented** (TTLEnforcementJob)
- ✅ **TTL enforcement working** (runs periodically, purges expired materials)

**Impact:**
- ✅ Working Materials expire per policy (architecture compliant)
- ✅ Storage growth controlled

**Implementation:**
- `symphainy_platform/civic_systems/smart_city/jobs/ttl_enforcement_job.py`
- Queries expired contracts
- Purges from GCS (if full_artifact or partial_extraction)
- Updates contract status to "expired"
- Updates Records of Fact with `source_expired_at`

**Recommendations:**
1. ✅ **R28:** TTL enforcement job created (COMPLETE)
2. ✅ **R29:** Purge expired Working Materials from GCS (COMPLETE)
3. ✅ **R30:** Update boundary contract status to "expired" (COMPLETE)

---

## Part 5: Implementation & Refactoring Plan

### Phase 1: Critical Fixes (Week 1) 🔴

**Priority: CRITICAL - Blocks Production**

#### 1.1 Implement EmbeddingService
- [ ] Create `content/enabling_services/embedding_service.py`
- [ ] Integrate with embedding model (OpenAI/Cohere)
- [ ] Implement `create_embeddings()` method
- [ ] Store embeddings in ArangoDB via `SemanticDataAbstraction`
- [ ] Update `content_orchestrator._handle_extract_embeddings()` to use service
- [ ] Create test `test_extract_embeddings.py`
- [ ] Validate embeddings are actually created

**Estimated Time:** 8-12 hours

#### 1.2 Fix Journey Realm Artifact Plane Integration
- [ ] Initialize `ArtifactPlane` in `JourneyOrchestrator`
- [ ] Update `_handle_create_blueprint` to use Artifact Plane
- [ ] Update `_handle_generate_sop` to use Artifact Plane
- [ ] Update `_handle_create_workflow` to use Artifact Plane
- [ ] Test blueprint → solution flow
- [ ] Verify `test_create_solution_from_blueprint` passes

**Estimated Time:** 4-6 hours

#### 1.3 Fix Insights Realm Artifact Plane Integration
- [ ] Initialize `ArtifactPlane` in `InsightsOrchestrator`
- [ ] Migrate all artifact creation to Artifact Plane
- [ ] Update test files to retrieve from Artifact Plane
- [ ] Verify all Insights Realm tests pass

**Estimated Time:** 4-6 hours

**Phase 1 Total:** 16-24 hours

---

### Phase 2: Architectural Refinement (Week 2) 🟡

**Priority: HIGH - Aligns with User's Vision**

#### 2.1 Implement Four-Class Data Architecture

**Working Materials:**
- [ ] Implement TTL enforcement job
- [ ] Create purge automation for expired materials
- [ ] Test TTL expiration

**Records of Fact:**
- [ ] Implement explicit "promote to Record of Fact" workflow
- [ ] Ensure embeddings persist even if source file expires
- [ ] Document boundary: parsed content (Working Material) → embeddings (Record of Fact)

**Purpose-Bound Outcomes:**
- [ ] Add lifecycle states to Artifact Plane registry (draft, accepted, obsolete)
- [ ] Add owner/purpose metadata to Artifact Plane
- [ ] Update Artifact Plane schema/migrations

**Platform DNA:**
- [ ] Design promotion workflow (Purpose-Bound Outcome → Platform DNA)
- [ ] Implement de-identification/generalization logic
- [ ] Create persistent Supabase registry (not in-memory)
- [ ] Integrate with Curator role

**Estimated Time:** 16-20 hours

#### 2.2 Improve Error Handling
- [ ] Distinguish recoverable vs critical errors
- [ ] Fail fast on critical operations
- [ ] Return error indicators in responses
- [ ] Add validation checks

**Estimated Time:** 4-6 hours

**Phase 2 Total:** 20-26 hours

---

### Phase 3: Cleanup & Production Readiness (Week 3) 🟢

**Priority: MEDIUM - Production Hardening**

#### 3.1 Remove MVP Placeholders
- [ ] Audit all "MVP", "placeholder", "TODO" comments
- [ ] Create "MVP → Production" migration checklist
- [ ] Replace placeholders with real implementations
- [ ] Add feature flags where needed

**Estimated Time:** 8-12 hours

#### 3.2 Complete Test Coverage
- [ ] Create embedding extraction tests
- [ ] Test cross-realm artifact retrieval
- [ ] Test TTL enforcement
- [ ] Test promotion workflows

**Estimated Time:** 6-8 hours

#### 3.3 Documentation & Validation
- [ ] Document four-class architecture
- [ ] Update migration plan with new architecture
- [ ] Create architecture decision records (ADRs)
- [ ] Validate all tests pass

**Estimated Time:** 4-6 hours

**Phase 3 Total:** 18-26 hours

---

## Part 6: Questions Requiring User Input

### Critical Questions

**Q1: Embedding Implementation**
- Should embeddings be created immediately on `extract_embeddings` or deferred?
- Which embedding model should we use? (OpenAI, Cohere, local model?)
- Should embeddings be stored in ArangoDB or separate vector DB?

**Q2: Records of Fact Boundary**
- When does parsed content become a "Record of Fact"? (When embeddings created?)
- Should embeddings persist even if source file expires? (Yes, per your principle)
- How do we handle lineage when source file is purged?

**Q3: Artifact Plane Lifecycle**
- What lifecycle states should we support? (draft → accepted → obsolete?)
- Who owns Purpose-Bound Outcomes? (client, platform, shared?)
- What purposes should we track? (decision support, delivery, governance, learning?)

**Q4: Platform DNA Promotion**
- What are the promotion criteria? (de-identified, generalizable, policy-approved?)
- Who validates promotion? (Curator role?)
- How do we de-identify client context?

**Q5: Error Handling Strategy**
- Should we fail fast on critical operations or continue with warnings?
- What's the distinction between recoverable and critical errors?
- How should we surface errors to users?

**Q6: MVP vs Production**
- What's the timeline for replacing MVP placeholders?
- Should we add feature flags for MVP vs production behavior?
- What's the priority order for replacing placeholders?

---

## Part 7: Risk Assessment

### Critical Risks (Updated Post-Architecture Implementation)

1. **🔴 Production Failure Risk: HIGH** (Unchanged)
   - Embedding extraction is placeholder → semantic features broken
   - Tests pass but functionality is fake
   - Users will experience silent failures
   - **Mitigation:** Implement EmbeddingService (Phase 1 priority)

2. **🟢 Data Loss Risk: LOW** (✅ Mitigated)
   - ✅ TTL enforcement implemented (TTLEnforcementJob)
   - ✅ Automated purge job runs periodically
   - ✅ Working Materials expire based on policy
   - **Remaining:** Monitor TTL enforcement in production

3. **🟢 Architectural Debt: LOW** (✅ Resolved)
   - ✅ Four-class architecture fully implemented
   - ✅ Consistent artifact storage patterns (Artifact Plane)
   - ✅ Clear boundaries between data classes
   - **Status:** Architecture is production-ready

4. **🟡 Test Coverage Gap: MEDIUM** (Partially Resolved)
   - ⏳ Critical functionality (embeddings) untested (still needed)
   - ✅ Placeholder implementations identified and documented
   - ✅ Integration tests for architecture added
   - **Remaining:** Add tests for EmbeddingService when implemented

---

## Part 8: Success Criteria

### Phase 1 Complete When:
- ✅ EmbeddingService implemented and tested
- ✅ Journey Realm artifacts in Artifact Plane
- ✅ Insights Realm artifacts in Artifact Plane
- ✅ All blueprint → solution tests pass
- ✅ Embeddings actually created (not placeholders)

### Phase 2 Complete When:
- ✅ Four-class architecture fully implemented
- ✅ TTL enforcement working
- ✅ Lifecycle states tracked
- ✅ Promotion workflows designed
- ✅ Error handling improved

### Phase 3 Complete When:
- ✅ All MVP placeholders replaced
- ✅ Test coverage complete
- ✅ Documentation updated
- ✅ All tests pass
- ✅ Production-ready

---

## Part 9: Immediate Next Steps

### This Week (Priority Order):

1. **🔴 CRITICAL: Implement EmbeddingService**
   - Blocks all semantic features
   - Highest impact on platform functionality

2. **🔴 CRITICAL: Fix Journey Realm Artifact Plane**
   - Blocks blueprint → solution flow
   - Test failure root cause

3. **🟡 HIGH: Fix Insights Realm Artifact Plane**
   - Completes artifact migration
   - Consistent with Outcomes Realm

4. **🟡 MEDIUM: Answer architectural questions**
   - Need user input on four-class boundaries
   - Blocks Phase 2 implementation

---

## Conclusion

**Status:** 🟡 **ARCHITECTURAL FOUNDATION COMPLETE - REMAINING WORK IDENTIFIED**

The platform has undergone **significant architectural improvements**:
- ✅ Four-class data framework fully implemented
- ✅ Artifact Plane lifecycle management complete
- ✅ Policy evaluation infrastructure (capability by design, implementation by policy)
- ✅ Promotion workflows implemented
- ✅ Records of Fact and Platform DNA registries created

**Remaining Critical Work:**
- 🔴 Embedding extraction still placeholder (highest priority)
- 🟡 Production hardening needed
- 🟢 Documentation updates

**Recommendation:** 
1. **Immediate:** Implement EmbeddingService (blocks semantic features)
2. **Short-term:** Production hardening (error handling, monitoring)
3. **Medium-term:** Performance optimization and scaling

**Timeline:** 1-2 weeks to production-ready (reduced from 3-4 weeks due to architectural completion)

**Key Architectural Principle Applied:**
> **Capability by Design, Implementation by Policy**
> - Real, robust infrastructure exists (secure by design)
> - MVP uses permissive policies (open by policy)
> - Production can tighten policies without code changes
> - No architectural debt from MVP shortcuts

---

**Last Updated:** January 20, 2026  
**Next Review:** After Phase 1 completion
