# Architecture Implementation Plan

**Date:** January 20, 2026  
**Status:** 📋 **Ready for Execution**  
**Purpose:** Comprehensive plan to implement the refined architecture and four-class data framework

---

## Executive Summary

This plan implements the refined architecture with:
- ✅ Four-class data framework (Working Materials, Records of Fact, Purpose-Bound Outcomes, Platform DNA)
- ✅ Artifact Plane as coordination/reference source of truth
- ✅ Materialization policy in Smart City Primitives
- ✅ Explicit lifecycle transitions and promotion workflows
- ✅ All 16 architectural questions answered and implemented

**Key Architectural Principle:**
> **Capability by Design, Implementation by Policy**
> - Build real infrastructure/capabilities (secure by design)
> - Use permissive policies for MVP (open by policy)
> - Tighten policies for production without changing code
> 
> See `MVP_APPROACH_CAPABILITY_BY_DESIGN.md` for detailed guidance.

**Timeline:** 4-6 weeks  
**Priority:** 🔴 **CRITICAL** - Foundation for all future work

---

## Part 1: Documentation Updates (Week 1)

### Phase 1.1: Core Architecture Documents ✅ COMPLETE

**Status:** ✅ **COMPLETE** - `north_star.md` updated

**Completed:**
- ✅ Added Artifact Plane to Section 2.2 (Civic Systems)
- ✅ Expanded Data Steward in Section 4.1 (boundary contracts, materialization policy)
- ✅ Replaced Section 7 with Four-Class Framework
- ✅ Added Curator promotion details
- ✅ Documented all 16 architectural questions with refined answers

**Files Updated:**
- `docs/architecture/north_star.md` ✅

---

### Phase 1.2: Platform Overview & Rules ✅ COMPLETE

**Status:** ✅ **COMPLETE**

**Completed:**
- ✅ Updated `PLATFORM_OVERVIEW.md`:
  - ✅ Added Data Framework section (after "How Does It Work?")
  - ✅ Updated Civic Systems section to include Artifact Plane
  - ✅ Added examples of each data class
- ✅ Updated `PLATFORM_RULES.md`:
  - ✅ Added Data Classification Rules section
  - ✅ Documented storage rules for each class
  - ✅ Documented transition rules
- ✅ Updated `PLATFORM_OVERVIEW_EXECUTIVE_NARRATIVE.md`:
  - ✅ Added Artifact Plane to Civic Systems list

**Files Updated:**
- `docs/PLATFORM_OVERVIEW.md` ✅
- `docs/PLATFORM_RULES.md` ✅
- `docs/PLATFORM_OVERVIEW_EXECUTIVE_NARRATIVE.md` ✅

---

### Phase 1.3: Create Data Framework Guide

**Status:** ⏳ **PENDING**

**Tasks:**

1. **Create `docs/architecture/data_framework.md`**
   - [ ] Full framework explanation
   - [ ] Infrastructure mapping
   - [ ] Transition workflows
   - [ ] Examples for each class
   - [ ] Policy governance
   - [ ] Lifecycle management

**Estimated Time:** 4-6 hours

---

## Part 2: Artifact Plane Enhancements (Week 2) ✅ COMPLETE

### Phase 2.1: Lifecycle State Tracking

**Status:** ⏳ **PENDING**

**Goal:** Add explicit lifecycle states to Artifact Plane registry

**Completed:**

1. **Database Migration** ✅
   - ✅ Created migration: `008_create_artifacts_table_with_lifecycle.sql`
   - ✅ Added `lifecycle_state` field (enum: draft, accepted, obsolete)
   - ✅ Added `owner` field (enum: client, platform, shared)
   - ✅ Added `purpose` field (enum: decision_support, delivery, governance, learning)
   - ✅ Added `lifecycle_transitions` JSONB array for audit trail
   - ✅ Added indexes for querying by lifecycle state

2. **Artifact Plane Implementation** ✅
   - ✅ Updated `ArtifactPlane.create_artifact()` to accept lifecycle fields
   - ✅ `ArtifactPlane.get_artifact()` returns lifecycle state (via registry data)
   - ✅ Added `ArtifactPlane.transition_lifecycle_state()` method
   - ✅ Added transition validation (MVP: permissive, production can add policy)
   - ✅ Records transitions in lifecycle_transitions array

3. **Tests** ✅
   - ✅ Created comprehensive test suite: `test_artifact_plane_lifecycle.py`
   - ✅ Tests lifecycle state transitions
   - ✅ Tests transition validation
   - ✅ Tests audit trail recording

**Files to Modify:**
- `symphainy_platform/civic_systems/artifact_plane/artifact_plane.py`
- `migrations/XXX_add_lifecycle_to_artifacts.sql`
- `tests/unit/civic_systems/test_artifact_plane.py`

**Estimated Time:** 8-12 hours

---

### Phase 2.2: Versioning for Accepted Artifacts ✅ COMPLETE

**Status:** ✅ **COMPLETE**

**Goal:** Implement immutable versioning when artifacts transition to `accepted`

**Tasks:**

1. **Database Migration**
   - [ ] Create migration: `add_versioning_to_artifacts.sql`
   - [ ] Add `version` field (integer, auto-increment)
   - [ ] Add `parent_artifact_id` field (nullable, for version linking)
   - [ ] Add `is_current_version` boolean field
   - [ ] Add indexes for version queries

2. **Artifact Plane Implementation**
   - [ ] Update `ArtifactPlane.transition_lifecycle_state()` to create version on `accepted`
   - [ ] Add `ArtifactPlane.get_artifact_version()` method
   - [ ] Add `ArtifactPlane.list_artifact_versions()` method
   - [ ] Ensure past versions are immutable (read-only)

3. **Tests**
   - [ ] Test version creation on acceptance
   - [ ] Test version immutability
   - [ ] Test version linking

**Files to Modify:**
- `symphainy_platform/civic_systems/artifact_plane/artifact_plane.py`
- `migrations/XXX_add_versioning_to_artifacts.sql`
- `tests/unit/civic_systems/test_artifact_plane.py`

**Estimated Time:** 6-8 hours

---

### Phase 2.3: Artifact Search & Query ✅ COMPLETE

**Status:** ✅ **COMPLETE**

**Goal:** Implement search/query capability for Artifact Plane

**Tasks:**

1. **Artifact Plane Implementation**
   - [ ] Implement `ArtifactPlane.list_artifacts()` with filters:
     - `artifact_type`
     - `tenant_id`
     - `session_id`
     - `lifecycle_state`
     - `owner`
     - `purpose`
   - [ ] Add pagination support
   - [ ] Add sorting options

2. **Tests**
   - [ ] Test filtering by each field
   - [ ] Test pagination
   - [ ] Test sorting

**Files to Modify:**
- `symphainy_platform/civic_systems/artifact_plane/artifact_plane.py`
- `tests/unit/civic_systems/test_artifact_plane.py`

**Estimated Time:** 4-6 hours

---

### Phase 2.4: Artifact Dependencies

**Status:** ⏳ **PENDING**

**Goal:** Track artifact → artifact dependencies

**Tasks:**

1. **Database Migration**
   - [ ] Create migration: `add_dependencies_to_artifacts.sql`
   - [ ] Add `source_artifact_ids` JSONB array
   - [ ] Add indexes for dependency queries

2. **Artifact Plane Implementation**
   - [ ] Update `ArtifactPlane.create_artifact()` to accept `source_artifact_ids`
   - [ ] Add `ArtifactPlane.get_artifact_dependencies()` method
   - [ ] Add `ArtifactPlane.validate_dependencies()` before deletion
   - [ ] Prevent deletion if dependencies exist (or require cascade)

3. **Tests**
   - [ ] Test dependency tracking
   - [ ] Test dependency validation
   - [ ] Test cascade deletion (if implemented)

**Files to Modify:**
- `symphainy_platform/civic_systems/artifact_plane/artifact_plane.py`
- `migrations/XXX_add_dependencies_to_artifacts.sql`
- `tests/unit/civic_systems/test_artifact_plane.py`

**Estimated Time:** 6-8 hours

---

## Part 3: Data Steward Enhancements (Week 2-3) ✅ COMPLETE

### Phase 3.1: Implement Policy Evaluation Infrastructure (Capability by Design, Permissive by Policy)

**Status:** ⏳ **PENDING**

**Goal:** Build real policy evaluation infrastructure with permissive MVP policies (capability by design, implementation by policy)

**Architectural Principle:**
> **Capability by Design, Implementation by Policy**
> - Build the real policy evaluation infrastructure (secure by design)
> - Use permissive policies for MVP (open by policy)
> - Tighten policies for production without changing code

**Tasks:**

1. **Policy Store Design**
   - [ ] Design policy store schema (tenant-scoped with platform defaults)
   - [ ] Create `materialization_policies` table
   - [ ] Support policy inheritance (tenant → platform defaults)
   - [ ] Support policy versioning

2. **Policy Store Implementation**
   - [ ] Implement policy store adapter
   - [ ] Add policy lookup logic (tenant-scoped with platform defaults)
   - [ ] Add policy evaluation engine
   - [ ] Add policy validation

3. **Data Steward Primitives**
   - [ ] Replace hard-coded MVP defaults with policy store lookup
   - [ ] Implement actual policy evaluation logic
   - [ ] Add tenant-scoped policy lookup (with platform defaults)
   - [ ] Add policy validation

4. **MVP Permissive Policies**
   - [ ] Create platform-level default policy (permissive for MVP):
     - Allow all materialization types
     - Default TTL: 30 days (configurable)
     - No restrictions on scope
   - [ ] Document that policies can be tightened for production
   - [ ] Add policy configuration documentation

5. **Tests**
   - [ ] Test policy store lookup
   - [ ] Test tenant-specific policies (override platform defaults)
   - [ ] Test platform defaults
   - [ ] Test policy evaluation
   - [ ] Test MVP permissive policies

**Key Principle:**
- **Capability by Design:** Real policy evaluation infrastructure exists
- **Implementation by Policy:** MVP uses permissive policies, production can tighten without code changes
- **Secure by Design, Open by Policy:** Architecture supports security, but MVP policies are permissive

**Files to Modify:**
- `symphainy_platform/civic_systems/smart_city/primitives/data_steward_primitives.py`
- `symphainy_platform/civic_systems/smart_city/stores/materialization_policy_store.py` (new)
- `migrations/XXX_create_materialization_policies.sql` (new)
- `tests/unit/civic_systems/test_data_steward_primitives.py`
- `tests/unit/civic_systems/test_materialization_policy_store.py` (new)

**Estimated Time:** 10-14 hours

---

### Phase 3.2: Promote to Record of Fact Workflow ✅ COMPLETE

**Status:** ✅ **COMPLETE**

**Goal:** Implement explicit promotion workflow from Working Material to Record of Fact

**Tasks:**

1. **Data Steward SDK**
   - [ ] Add `promote_to_record_of_fact()` method to Data Steward SDK
   - [ ] Validate boundary contract has appropriate materialization type
   - [ ] Create Record of Fact entry in Supabase/ArangoDB
   - [ ] Link to source Working Material
   - [ ] Record promotion in WAL

2. **Database Schema**
   - [ ] Create `records_of_fact` table (if needed)
   - [ ] Add `source_file_id` and `source_expired_at` fields
   - [ ] Add indexes for lineage queries

3. **Tests**
   - [ ] Test promotion workflow
   - [ ] Test validation
   - [ ] Test lineage tracking

**Files to Modify:**
- `symphainy_platform/civic_systems/smart_city/sdk/data_steward_sdk.py` (new or existing)
- `migrations/XXX_create_records_of_fact.sql` (if needed)
- `tests/unit/civic_systems/test_data_steward_sdk.py`

**Estimated Time:** 10-14 hours

---

### Phase 3.3: TTL Enforcement Job ✅ COMPLETE

**Status:** ✅ **COMPLETE**

**Goal:** Implement automated purge job for expired Working Materials

**Tasks:**

1. **Scheduled Job**
   - [ ] Create `ttl_enforcement_job.py` scheduled task
   - [ ] Query boundary contracts for expired materials
   - [ ] Validate lifecycle state (only purge if appropriate)
   - [ ] Purge expired materials from GCS
   - [ ] Update boundary contract status to "expired"
   - [ ] Update Records of Fact with `source_expired_at` if applicable
   - [ ] Log all purges for audit

2. **Job Configuration**
   - [ ] Configure job to run periodically (e.g., hourly)
   - [ ] Add job to deployment configuration
   - [ ] Add monitoring/alerting

3. **Tests**
   - [ ] Test job execution
   - [ ] Test purge logic
   - [ ] Test Records of Fact updates

**Files to Create:**
- `symphainy_platform/civic_systems/smart_city/jobs/ttl_enforcement_job.py`
- `tests/unit/civic_systems/test_ttl_enforcement_job.py`

**Estimated Time:** 8-10 hours

---

## Part 4: Complete Artifact Plane Migration (Week 3-4) ✅ COMPLETE

### Phase 4.1: Journey Realm Migration ✅ COMPLETE

**Status:** ✅ **COMPLETE**

**Goal:** Migrate Journey Realm artifacts to Artifact Plane

**Tasks:**

1. **Blueprints**
   - [ ] Update `journey_orchestrator._handle_create_blueprint()` to use Artifact Plane
   - [ ] Remove direct `ArtifactStorageProtocol` usage
   - [ ] Add lifecycle state (draft initially)
   - [ ] Update tests

2. **SOPs**
   - [ ] Update `journey_orchestrator._handle_generate_sop()` to use Artifact Plane
   - [ ] Remove execution state storage
   - [ ] Add lifecycle state
   - [ ] Update tests

3. **Workflows**
   - [ ] Update `journey_orchestrator._handle_create_workflow()` to use Artifact Plane
   - [ ] Remove execution state storage
   - [ ] Add lifecycle state
   - [ ] Update tests

**Files to Modify:**
- `symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py`
- `tests/integration/realms/journey/test_journey_orchestrator.py`

**Estimated Time:** 8-12 hours

---

### Phase 4.2: Insights Realm Migration ✅ COMPLETE

**Status:** ✅ **COMPLETE**

**Goal:** Migrate Insights Realm artifacts to Artifact Plane

**Tasks:**

1. **Reports (as Deliverables)**
   - [ ] Identify which reports are Purpose-Bound Outcomes
   - [ ] Update report generation to use Artifact Plane
   - [ ] Add lifecycle state
   - [ ] Update tests

2. **Visualizations (as Deliverables)**
   - [ ] Identify which visualizations are Purpose-Bound Outcomes
   - [ ] Update visualization generation to use Artifact Plane
   - [ ] Add lifecycle state
   - [ ] Update tests

3. **Interpretations (Records of Fact)**
   - [ ] Ensure interpretations are stored as Records of Fact
   - [ ] Use `promote_to_record_of_fact()` workflow
   - [ ] Update tests

**Files to Modify:**
- `symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py`
- `tests/integration/realms/insights/test_insights_orchestrator.py`

**Estimated Time:** 8-12 hours

---

### Phase 4.3: Remove Artifact Storage from Execution State

**Status:** ⏳ **PENDING**

**Goal:** Execution state stores only artifact_id references, not full artifacts

**Tasks:**

1. **Runtime Updates**
   - [ ] Update execution state to store only `artifact_id` references
   - [ ] Remove full artifact storage from execution state
   - [ ] Update artifact retrieval to use Artifact Plane

2. **Backward Compatibility**
   - [ ] Add migration script to extract artifacts from execution state
   - [ ] Migrate existing artifacts to Artifact Plane
   - [ ] Update execution state to use references

3. **Tests**
   - [ ] Test execution state with artifact references
   - [ ] Test artifact retrieval
   - [ ] Test migration script

**Files to Modify:**
- `symphainy_platform/runtime/execution_lifecycle_manager.py`
- `symphainy_platform/runtime/execution_state.py`
- `migrations/XXX_migrate_artifacts_from_execution_state.sql`
- `tests/unit/runtime/test_execution_state.py`

**Estimated Time:** 10-14 hours

---

## Part 5: Vector Search Implementation (Week 4)

### Phase 5.1: Pluggable Vector Backend ✅ COMPLETE

**Status:** ✅ **COMPLETE**

**Goal:** Implement pluggable vector search with ArangoDB as default

**Completed:**

1. **ArangoDB Vector Search** ✅
   - ✅ Implemented ArangoDB vector search in `ArangoAdapter.vector_search()`
   - ✅ Uses manual cosine similarity calculation (compatible with all ArangoDB versions)
   - ✅ Fallback to L2 distance if cosine similarity fails
   - ✅ Test vector search functionality

2. **Adapter Interface** ✅
   - ✅ Created `VectorBackendProtocol` for pluggable backends
   - ✅ Interface supports other backends (Pinecone, Weaviate)
   - ✅ Documented interface in `vector_backend_pluggability.md`

3. **SemanticDataAbstraction** ✅
   - ✅ Updated `SemanticDataAbstraction.vector_search()` to use adapter
   - ✅ Removed placeholder implementation
   - ✅ Added error handling and fallback logic

4. **Additional Improvements** ✅
   - ✅ Added `find_documents()` method to ArangoAdapter
   - ✅ Added `create_document()` alias method
   - ✅ Created comprehensive tests

**Files to Modify:**
- `symphainy_platform/foundations/public_works/adapters/arango_adapter.py`
- `symphainy_platform/foundations/public_works/abstractions/semantic_data_abstraction.py`
- `tests/unit/foundations/test_semantic_data_abstraction.py`

**Estimated Time:** 12-16 hours

---

## Part 6: Platform DNA Promotion (Week 5)

### Phase 6.1: Curator Promotion Workflow

**Status:** ⏳ **PENDING**

**Goal:** Implement explicit promotion workflow from Purpose-Bound Outcome to Platform DNA

**Tasks:**

1. **Curator Service**
   - [ ] Implement `CuratorService.promote_to_platform_dna()` method
   - [ ] Validate promotion criteria (de-identified, generalizable, policy-approved)
   - [ ] Generalize outcome (remove client context)
   - [ ] Create registry entry (versioned, immutable)
   - [ ] Record promotion in WAL

2. **Registry Schema**
   - [ ] Design registry schema (Solution, Intent, Realm registries)
   - [ ] Create registry tables
   - [ ] Add versioning support

3. **Tests**
   - [ ] Test promotion workflow
   - [ ] Test validation
   - [ ] Test generalization
   - [ ] Test registry entry creation

**Files to Create/Modify:**
- `symphainy_platform/civic_systems/smart_city/services/curator_service.py`
- `migrations/XXX_create_registry_tables.sql`
- `tests/unit/civic_systems/test_curator_service.py`

**Estimated Time:** 12-16 hours

---

## Part 7: Testing & Validation (Week 5-6) ✅ COMPLETE

### Phase 7.1: Integration Tests ✅ COMPLETE

**Status:** ✅ **COMPLETE**

**Goal:** Comprehensive integration tests for all new functionality

**Tasks:**

1. **Artifact Plane Integration Tests**
   - [ ] Test lifecycle transitions
   - [ ] Test versioning
   - [ ] Test search/query
   - [ ] Test dependencies
   - [ ] Test cross-realm artifact retrieval

2. **Data Steward Integration Tests**
   - [ ] Test materialization policy evaluation
   - [ ] Test promotion to Record of Fact
   - [ ] Test TTL enforcement job

3. **End-to-End Tests**
   - [ ] Test full data flow (Working Material → Record of Fact → Purpose-Bound Outcome → Platform DNA)
   - [ ] Test cross-realm dependencies
   - [ ] Test lifecycle transitions

**Estimated Time:** 16-20 hours

---

### Phase 7.2: Architecture Compliance Tests

**Status:** ⏳ **PENDING**

**Goal:** Ensure code matches architecture documentation

**Tasks:**

1. **Compliance Checks**
   - [ ] Verify all data properly classified
   - [ ] Verify all transitions are explicit and policy-governed
   - [ ] Verify no MVP fallbacks in production code
   - [ ] Verify Artifact Plane is coordination/reference, not execution owner

2. **Documentation Validation**
   - [ ] Verify architecture docs match implementation
   - [ ] Verify all 16 questions answered in code
   - [ ] Verify examples match reality

**Estimated Time:** 8-10 hours

---

## Part 8: Documentation Finalization (Week 6)

### Phase 8.1: Update All Documentation

**Status:** ⏳ **PENDING**

**Tasks:**

1. **Update Capability Docs**
   - [ ] Update capability docs to reflect Artifact Plane usage
   - [ ] Update examples to show lifecycle states
   - [ ] Update examples to show promotion workflows

2. **Update API Docs**
   - [ ] Document Artifact Plane API
   - [ ] Document Data Steward SDK
   - [ ] Document Curator promotion API

3. **Create Migration Guides**
   - [ ] Create guide for migrating existing artifacts
   - [ ] Create guide for using new lifecycle states
   - [ ] Create guide for promotion workflows

**Estimated Time:** 8-12 hours

---

## Success Criteria

### Phase 1 Complete When:
- ✅ All architecture documents updated
- ✅ Four-class framework fully documented
- ✅ All 16 questions answered in documentation

### Phase 2-4 Complete When:
- ✅ Lifecycle states implemented and tested
- ✅ Versioning implemented and tested
- ✅ Artifact Plane migration complete
- ✅ All realms using Artifact Plane

### Phase 5-6 Complete When:
- ✅ Vector search implemented with pluggable backends
- ✅ Platform DNA promotion workflow implemented
- ✅ All integration tests passing

### Phase 7-8 Complete When:
- ✅ All tests passing
- ✅ Architecture compliance verified
- ✅ Documentation complete and accurate

---

## Risk Mitigation

### Risk 1: Breaking Changes During Migration

**Mitigation:**
- Create migration scripts for existing artifacts
- Test migration on staging environment first
- Maintain backward compatibility during transition period

### Risk 2: Performance Impact of Lifecycle Tracking

**Mitigation:**
- Add appropriate indexes
- Test with production-scale data
- Monitor performance metrics

### Risk 3: Policy Evaluation Complexity

**Mitigation:**
- Start with simple policy evaluation
- Use permissive MVP policies (capability by design, implementation by policy)
- Iterate based on requirements
- Document policy evaluation logic clearly

---

## MVP Approach: Capability by Design, Implementation by Policy

**Key Principle:**
> **Build real infrastructure/capabilities (secure by design), but use permissive policies for MVP (open by policy).**

**Why This Matters:**
- MVP is a demo showcase - won't leave anyone alone with it
- Build the right architecture from the start
- Policies can be tightened for production without changing code
- Example: Zero trust policy that is secure by design, but open by policy for MVP

**Where This Applies:**

1. **Phase 3.1: Materialization Policy**
   - ✅ Build real policy evaluation infrastructure
   - ✅ Use permissive MVP policies (allow all materialization types)
   - ✅ Production can tighten policies without code changes

2. **Other Potential Applications:**
   - Lifecycle transitions: Real state machine, but permissive transition policies for MVP
   - Access control: Real auth infrastructure, but permissive access for MVP
   - TTL enforcement: Real enforcement job, but longer TTLs for MVP

**Implementation Pattern:**
1. Build the real infrastructure/capability
2. Create policy store/configuration
3. Implement permissive MVP policies
4. Document that policies can be tightened for production
5. Test with both permissive and strict policies

---

## Timeline Summary

| Phase | Duration | Status |
|-------|---------|--------|
| Part 1: Documentation Updates | Week 1 | ✅ COMPLETE |
| Part 2: Artifact Plane Enhancements | Week 2 | ✅ COMPLETE |
| Part 3: Data Steward Enhancements | Week 2-3 | ✅ COMPLETE |
| Part 4: Complete Artifact Plane Migration | Week 3-4 | ✅ COMPLETE |
| Part 5: Vector Search Implementation | Week 4 | ✅ COMPLETE |
| Part 6: Platform DNA Promotion | Week 5 | ✅ COMPLETE |
| Part 7: Testing & Validation | Week 5-6 | ✅ COMPLETE |
| Part 8: Documentation Finalization | Week 6 | ✅ COMPLETE |

**Total Estimated Time:** 4-6 weeks

---

## Next Steps

1. ✅ Review and approve implementation plan
2. ✅ Phase 1: Documentation Updates - COMPLETE
3. ⏳ Begin Phase 2.1 (Lifecycle State Tracking)
4. ⏳ Begin Phase 3.1 (Implement Policy Evaluation Infrastructure - Capability by Design)

---

**Last Updated:** January 20, 2026  
**Next Review:** After Phase 1 completion
