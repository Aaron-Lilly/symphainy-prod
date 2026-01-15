# Optimized Refactoring Strategy - All Smart City Roles

**Date:** January 2026  
**Status:** 📋 **STRATEGIC RECOMMENDATION**  
**Goal:** Refactor 9 Smart City roles (8 existing + Curator) and their abstractions efficiently

**Key Clarification:** No role-specific SDKs. All SDK methods go in Platform SDK.

---

## The Question

**Should we:**
1. ✅ Complete Security Guard fully first (establish pattern), then iterate on other 8?
2. ✅ Or is there a more efficient/logical approach?

---

## Analysis: Dependencies & Parallelization Opportunities

### Key Insight: Abstractions Are Independent Infrastructure

**Abstractions are infrastructure** - they don't depend on each other:
- Auth Abstraction ← Supabase
- Tenant Abstraction ← Supabase  
- File Management Abstraction ← GCS
- Session Abstraction ← Redis
- Event Management Abstraction ← Event Bus
- Workflow Abstraction ← Workflow Engine
- Telemetry Abstraction ← Telemetry System

**These can be refactored in parallel** - no dependencies between them.

### Key Insight: Primitives Follow a Pattern

**Once Security Guard pattern is established:**
- Primitive structure (policy decisions only)
- Platform SDK structure (boundary zone - single SDK, no role-specific SDKs)
- Registry usage (Policy Registry)
- Integration pattern (Runtime → Platform SDK → Primitive)

**All other primitives follow the same pattern** - can be replicated efficiently.

---

## Recommended Strategy: **Hybrid Approach**

### Phase 1: Establish Pattern (Security Guard Complete)

**Goal:** Get one complete, working example to validate the pattern

**Tasks:**
1. ✅ **Complete Security Guard abstractions:**
   - ✅ Auth Abstraction (done)
   - ⏳ Tenant Abstraction (add `get_user_tenant_info()`, remove business logic)
   - ⏳ Authorization Abstraction (create new, pure infrastructure)

2. ✅ **Complete Platform SDK (Security Guard methods):**
   - Implement `ensure_user_can()` in Platform SDK
   - Implement `validate_tenant_access()` in Platform SDK
   - Query Policy Registry
   - Prepare runtime contract shape
   - **Note:** No role-specific SDKs - all SDK methods go in Platform SDK

3. ✅ **Complete Security Guard Primitive:**
   - Implement `evaluate_auth()`
   - Implement `validate_tenant_access()`
   - Implement `check_permission()`
   - Implement `enforce_zero_trust()`
   - Pure policy decisions only

4. ✅ **Validate Pattern:**
   - Test Security Guard end-to-end
   - Verify pattern works
   - Document any adjustments needed

**Why This First:**
- Establishes the complete pattern
- Validates architectural decisions
- Creates a template for other roles
- Catches any issues early

**Time Estimate:** 2-3 days

---

### Phase 2: Batch Refactor All Abstractions (Parallel)

**Goal:** Refactor all Public Works abstractions to be pure infrastructure

**Tasks (Can be done in parallel):**

#### 2.1 Security Guard Abstractions (Complete from Phase 1)
- ✅ Auth Abstraction
- ✅ Tenant Abstraction
- ✅ Authorization Abstraction

#### 2.2 Data Steward Abstractions
- ⏳ File Management Abstraction (remove business logic)
- ⏳ Content Metadata Abstraction (remove business logic)
- ⏳ Semantic Data Abstraction (remove business logic)

#### 2.3 Traffic Cop Abstractions
- ⏳ Session Abstraction (remove business logic)

#### 2.4 Post Office Abstractions
- ⏳ Event Management Abstraction (remove business logic)
- ⏳ Messaging Abstraction (remove business logic)

#### 2.5 Conductor Abstractions
- ⏳ Workflow Orchestration Abstraction (remove business logic)

#### 2.6 Librarian Abstractions
- ⏳ Search Abstraction (create new, pure infrastructure)

#### 2.7 Nurse Abstractions
- ⏳ Telemetry Abstraction (remove business logic)

#### 2.8 City Manager Abstractions
- ⏳ Policy Abstraction (remove business logic, if exists)

#### 2.9 Curator Abstractions
- ⏳ Service Discovery Abstraction (create new, pure infrastructure)
- ⏳ Registry Abstraction (if needed)

**Why Batch:**
- Abstractions are independent (no dependencies)
- Same refactoring pattern (remove business logic, return raw data)
- Can be done in parallel by different developers
- More efficient than one-by-one

**Time Estimate:** 1-2 weeks (parallel work)

---

### Phase 3: Batch Refactor All Primitives + Platform SDK Methods (Sequential or Parallel)

**Goal:** Refactor all Smart City roles to primitives following Security Guard pattern

**Tasks (Can be done sequentially or in small batches):**

#### 3.1 Security Guard (Complete from Phase 1)
- ✅ Primitive
- ✅ Platform SDK methods

#### 3.2 Data Steward
- ⏳ Create `DataStewardPrimitive` (policy decisions: data access, lineage, lifecycle)
- ⏳ Add Data Steward methods to Platform SDK (boundary zone: file operations, metadata queries)
- ⏳ Use File Management, Content Metadata, Semantic Data abstractions

#### 3.3 Traffic Cop
- ⏳ Create `TrafficCopPrimitive` (policy decisions: session validation, rate limiting)
- ⏳ Add Traffic Cop methods to Platform SDK (boundary zone: session management, websocket handling)
- ⏳ Use Session Abstraction

#### 3.4 Post Office
- ⏳ Create `PostOfficePrimitive` (policy decisions: event routing, message validation)
- ⏳ Add Post Office methods to Platform SDK (boundary zone: event publishing, message delivery)
- ⏳ Use Event Management, Messaging abstractions

#### 3.5 Conductor
- ⏳ Create `ConductorPrimitive` (policy decisions: workflow validation, execution constraints)
- ⏳ Add Conductor methods to Platform SDK (boundary zone: workflow orchestration, saga coordination)
- ⏳ Use Workflow Orchestration Abstraction

#### 3.6 Librarian
- ⏳ Create `LibrarianPrimitive` (policy decisions: search access, result filtering)
- ⏳ Add Librarian methods to Platform SDK (boundary zone: search queries, result formatting)
- ⏳ Use Search Abstraction

#### 3.7 Nurse
- ⏳ Create `NursePrimitive` (policy decisions: telemetry access, trace filtering)
- ⏳ Add Nurse methods to Platform SDK (boundary zone: telemetry collection, trace management)
- ⏳ Use Telemetry Abstraction

#### 3.8 City Manager
- ⏳ Create `CityManagerPrimitive` (policy decisions: platform governance, policy validation)
- ⏳ Add City Manager methods to Platform SDK (boundary zone: policy management, platform configuration)
- ⏳ Use Policy Abstraction

#### 3.9 Curator
- ⏳ Create `CuratorPrimitive` (policy decisions: capability validation, service contract validation)
- ⏳ Add Curator methods to Platform SDK (boundary zone: capability registration, runtime view composition)
- ⏳ Use Service Discovery Abstraction

**Why Batch:**
- All follow the same pattern (established in Phase 1)
- Can be done sequentially (one role at a time) or in small batches
- Each role is independent (no dependencies between primitives)
- Platform SDK methods added incrementally (no role-specific SDKs)
- More efficient than doing Security Guard completely, then starting from scratch on others

**Time Estimate:** 2-3 weeks (sequential) or 1-2 weeks (parallel with 2-3 developers)

---

## Comparison: Two Approaches

### Approach A: Complete Security Guard First, Then Iterate

**Pros:**
- ✅ Establishes complete pattern
- ✅ Validates architecture early
- ✅ One role fully done before moving on

**Cons:**
- ❌ Abstractions get refactored multiple times (once for Security Guard, again for others)
- ❌ Slower overall (sequential)
- ❌ Risk of over-optimizing Security Guard pattern before seeing other roles

**Time Estimate:** 4-6 weeks total

---

### Approach B: Hybrid (Recommended)

**Pros:**
- ✅ Establishes pattern with Security Guard (validates architecture)
- ✅ Batch refactors abstractions (parallel, efficient)
- ✅ Batch refactors primitives (follows established pattern)
- ✅ Faster overall (parallelization opportunities)
- ✅ Abstractions refactored once (not per role)

**Cons:**
- ⚠️ Requires coordination (but manageable)
- ⚠️ Need to ensure pattern is correct before batching (mitigated by Phase 1)

**Time Estimate:** 3-4 weeks total

---

## Recommended Execution Plan

### Week 1: Establish Pattern
- **Days 1-2:** Complete Security Guard abstractions (Tenant, Authorization)
- **Days 3-4:** Complete Platform SDK (Security Guard methods)
- **Days 5-6:** Complete Security Guard Primitive
- **Day 7:** Validate pattern, document, adjust if needed

### Week 2: Batch Abstractions (Parallel)
- **Days 1-3:** Refactor Data Steward abstractions (File, Metadata, Semantic)
- **Days 1-3:** Refactor Traffic Cop abstraction (Session)
- **Days 1-3:** Refactor Post Office abstractions (Event, Messaging)
- **Days 4-5:** Refactor Conductor abstraction (Workflow)
- **Days 4-5:** Refactor Librarian abstraction (Search)
- **Days 4-5:** Refactor Nurse abstraction (Telemetry)
- **Days 6-7:** Refactor City Manager abstraction (Policy)
- **Days 6-7:** Create Curator abstractions (Service Discovery)

### Week 3-4: Batch Primitives + Platform SDK Methods (Sequential or Small Batches)
- **Days 1-2:** Data Steward Primitive + Platform SDK methods
- **Days 3-4:** Traffic Cop Primitive + Platform SDK methods
- **Days 5-6:** Post Office Primitive + Platform SDK methods
- **Days 7-8:** Conductor Primitive + Platform SDK methods
- **Days 9-10:** Librarian Primitive + Platform SDK methods
- **Days 11-12:** Nurse Primitive + Platform SDK methods
- **Days 13-14:** City Manager Primitive + Platform SDK methods
- **Days 15-16:** Curator Primitive + Platform SDK methods

### Week 5: Integration & Testing
- Integration testing
- End-to-end validation
- Documentation

---

## Key Success Factors

1. **Complete Security Guard pattern first** - validates architecture
2. **Batch abstractions** - they're independent infrastructure
3. **Follow established pattern** - all primitives follow Security Guard pattern
4. **Single Platform SDK** - no role-specific SDKs, all methods in Platform SDK
5. **Parallelize where possible** - abstractions can be done in parallel
6. **Sequential primitives** - ensures quality, but can batch 2-3 at a time

---

## Decision Matrix

| Factor | Complete Security Guard First | Hybrid (Recommended) |
|--------|-------------------------------|----------------------|
| **Pattern Validation** | ✅ Early | ✅ Early (Phase 1) |
| **Abstraction Efficiency** | ❌ Refactored multiple times | ✅ Refactored once |
| **Primitive Efficiency** | ⚠️ Sequential | ✅ Follows pattern |
| **Parallelization** | ❌ Limited | ✅ High (abstractions) |
| **Risk** | ⚠️ Over-optimize one role | ✅ Validated pattern |
| **Time** | 4-6 weeks | 3-4 weeks |
| **Quality** | ✅ High | ✅ High |

---

## Recommendation: **Hybrid Approach**

**Complete Security Guard pattern first (Phase 1), then batch the rest (Phases 2-3).**

**Rationale:**
1. ✅ Establishes and validates the pattern early
2. ✅ Abstractions are independent - can be batch refactored efficiently
3. ✅ Primitives follow the same pattern - can be replicated efficiently
4. ✅ Single Platform SDK - no role-specific SDKs, cleaner architecture
5. ✅ Faster overall (3-4 weeks vs 4-6 weeks)
6. ✅ Better resource utilization (parallelization opportunities)

**This is the most efficient and logical approach.**
