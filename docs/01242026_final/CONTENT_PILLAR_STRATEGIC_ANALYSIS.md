# Content Pillar Strategic Analysis: Artifact-Centric Architecture

**Date:** January 26, 2026  
**Context:** Strategic shift from file-centric to artifact-centric thinking  
**Status:** 🔴 **CRITICAL ARCHITECTURAL ALIGNMENT REQUIRED**

---

## Executive Summary

The CTO guidance reveals a **fundamental architectural misalignment** in the Content Pillar. We've been building an **artifact-based platform** but implementing it with **file-centric mental models**. This analysis identifies where we're violating our own architecture and provides a strategic path forward.

**Key Finding:** We need to retrofit artifact semantics throughout the entire content pillar, from Public Works abstractions to frontend components.

---

## 1. Current State Analysis

### 1.1 What We're Doing Right ✅

1. **Intent-Based API**: Frontend uses `submitIntent()` correctly
2. **Structured Artifacts**: Backend creates `semantic_payload` + `renderings` structure
3. **Execution Tracking**: Runtime tracks execution state
4. **Two-Phase Materialization**: Correct separation of upload vs. save

### 1.2 Where We're Violating Artifact-Centric Principles ❌

#### **Violation #1: Frontend Polls Execution Status, Not Artifacts**

**Current Flow:**
```typescript
// ContentAPIManager.ts - WRONG PATTERN
const status = await platformState.getExecutionStatus(executionId);
const fileArtifact = status.artifacts?.file?.semantic_payload;
const fileId = fileArtifact.file_id;
```

**Problem:**
- Frontend is asking "what's the execution status?" instead of "what artifact was produced?"
- Artifacts are buried in execution status, not first-class
- No artifact resolution API - everything is execution-centric

**Should Be:**
```typescript
// CORRECT PATTERN
const artifact = await platformState.resolveArtifact(artifactId);
// Runtime validates, resolves, returns content
```

#### **Violation #1a: UI Lists Files, Not Artifacts**

**Current Flow:**
```typescript
// ContentAPIManager.ts - WRONG PATTERN
async listFiles(): Promise<ContentFile[]> {
  // Queries "files" from storage/index
  // Returns file-centric objects
}
```

**Problem:**
- UI asks "what files exist?" instead of "what artifacts are eligible for the next intent?"
- File-centric mental model in UI
- Multiple listing methods (`listFiles()`, `listParsedFiles()`, etc.)

**Should Be:**
```typescript
// CORRECT PATTERN
async listArtifacts(filters: {
  artifact_type: string,
  lifecycle_state?: string,
  eligible_for?: string  // Next intent in journey
}): Promise<ArtifactListItem[]> {
  // Query artifact index (Supabase) for discovery
  // Returns artifact-centric objects with eligibility
}
```

**Key Insight (From CTO):**
> **UI dropdowns enumerate artifacts by eligibility; actions resolve artifacts by ID.**
> 
> Dropdowns should not list "files" — they should list *artifacts filtered by type + lifecycle + eligibility*.

#### **Violation #2: State Surface Stores File References, Not Artifacts**

**Current Implementation:**
```python
# state_surface.py - WRONG PATTERN
await context.state_surface.store_file_reference(
    file_reference=parsed_file_reference,
    storage_location=parsed_file_path,  # Just a pointer!
    metadata={...}
)
```

**Problem:**
- State Surface is a "pointer cache" not an "artifact registry"
- No artifact lifecycle state
- No artifact validation
- No artifact authority

**Should Be:**
```python
# CORRECT PATTERN
await context.state_surface.register_artifact(
    artifact_id=parsed_file_id,
    artifact_type="parsed_content",
    intent_execution_id=execution_id,
    lifecycle_state="READY",
    content_ref={
        "storage_type": "gcs",
        "uri": parsed_file_path,
        "format": "json"
    },
    semantic_payload={...},
    tenant_id=tenant_id
)
```

#### **Violation #3: Backend Creates Artifacts But Doesn't Register Them**

**Current Flow:**
```python
# content_orchestrator.py - INCOMPLETE
structured_artifact = create_structured_artifact(
    result_type="parsed_content",
    semantic_payload={...},
    renderings={...}
)
# Returns artifact in response, but...
# ❌ Never registers in State Surface as artifact
# ❌ Never stores artifact lifecycle state
```

**Problem:**
- Artifacts exist in execution response but not in artifact registry
- No way to resolve artifacts later by ID
- No artifact authority

#### **Violation #4: get_parsed_file is File Retrieval, Not Artifact Resolution**

**Current Implementation:**
```python
# file_parser_service.py - WRONG PATTERN
# Step 1: Get storage_location from State Surface (pointer)
# Step 2: Download from GCS (direct storage access)
# ❌ No artifact validation
# ❌ No lifecycle check
# ❌ No intent execution context
```

**Problem:**
- Treats parsed content as a "file" not an "artifact"
- Bypasses artifact semantics
- Direct storage access (violates platform abstraction)

**Should Be:**
```python
# CORRECT PATTERN
async def resolve_parsed_artifact(artifact_id: str, context: ExecutionContext):
    # Runtime resolves artifact via State Surface
    artifact = await context.state_surface.resolve_artifact(
        artifact_id=artifact_id,
        artifact_type="parsed_content",
        tenant_id=context.tenant_id
    )
    
    # Runtime validates:
    # - Artifact exists
    # - Lifecycle state = READY
    # - Access control (tenant, session)
    
    # Runtime retrieves content via content_ref
    content = await retrieve_artifact_content(artifact.content_ref)
    
    return content
```

#### **Violation #5: Public Works Abstractions Are Storage-Centric**

**Current Pattern:**
```python
# FileManagementAbstraction, FileStorageAbstraction
# These are storage operations, not artifact operations
```

**Problem:**
- Abstractions expose storage details (GCS paths, buckets)
- No artifact-level abstraction
- Application code knows about storage implementation

**Should Be:**
```python
# ArtifactAbstraction (new)
class ArtifactAbstraction:
    async def register_artifact(...)
    async def resolve_artifact(...)
    async def retrieve_artifact_content(...)
    # Storage is opaque
```

---

## 2. Strategic Gaps Analysis

### 2.1 Missing Infrastructure

| Component | Current State | Required State |
|-----------|--------------|----------------|
| **Artifact Registry** | ❌ Doesn't exist | ✅ State Surface artifact registry |
| **Artifact Resolution API** | ❌ Doesn't exist | ✅ Runtime.resolveArtifact() |
| **Artifact Lifecycle** | ❌ Not tracked | ✅ READY, ARCHIVED, DELETED states |
| **Artifact Authority** | ❌ Multiple sources | ✅ State Surface only |
| **Artifact Abstraction** | ❌ Storage abstractions only | ✅ ArtifactAbstraction in Public Works |

### 2.2 Mental Model Mismatches

| Current Thinking | Correct Thinking |
|-----------------|------------------|
| "Get the parsed file" | "Resolve the parsed_content artifact" |
| "Where is it stored?" | "What artifact was produced?" |
| "Query storage directly" | "Resolve via Runtime" |
| "File reference" | "Artifact registry entry" |
| "Execution status" | "Artifact resolution" |

---

## 3. Required Changes (Strategic Path Forward)

### 3.1 Phase 1: State Surface Artifact Registry (Foundation)

**Priority:** 🔴 **CRITICAL - Blocks everything else**

**Changes:**
1. Add `ArtifactRegistry` to State Surface
2. **Artifact schema (CTO-recommended, future-proof):**
   ```python
   ArtifactRecord = {
       # Identity
       "artifact_id": str,                 # Stable, global
       "artifact_type": str,               # file | parsed_content | embeddings | summary | etc.
       "tenant_id": str,

       # Provenance
       "produced_by": {
           "intent": str,                  # ingest_file, parse_content, extract_embeddings
           "execution_id": str,
       },
       "parent_artifacts": List[str],      # lineage (file → parsed → embeddings)

       # Lifecycle
       "lifecycle_state": str,             # PENDING | READY | FAILED | ARCHIVED | DELETED

       # Semantics (what it *means*)
       "semantic_descriptor": {
           "schema": str,                  # logical schema / version
           "record_count": Optional[int],
           "parser_type": Optional[str],
           "embedding_model": Optional[str],
           # NO storage info here
       },

       # Materialization (how it's stored)
       "materializations": [
           {
               "materialization_id": str,
               "storage_type": str,         # gcs | arango | duckdb | vector_store
               "uri": str,
               "format": str,               # json | parquet | csv | faiss
               "compression": Optional[str],
               "created_at": str,
           }
       ],

       # Timestamps
       "created_at": str,
       "updated_at": str,
   }
   ```

   **Key Design Principles:**
   - ✅ **Identity** independent of storage
   - ✅ **Semantics** separate from materialization
   - ✅ **Multiple materializations** supported (one artifact, many storage forms)
   - ✅ **Explicit lineage** via parent_artifacts
   - ✅ **Richer lifecycle** (PENDING, READY, FAILED, ARCHIVED, DELETED)

3. Methods:
   - `register_artifact()` - Register new artifact (lifecycle_state = PENDING initially)
   - `resolve_artifact(artifact_id, artifact_type, tenant_id)` - Resolve by ID with validation
   - `update_artifact_lifecycle()` - Update lifecycle state (PENDING → READY, etc.)
   - `add_materialization()` - Add additional materialization to existing artifact
   - ⚠️ **NO `list_artifacts()`** - Supabase is for exploration, State Surface is for resolution

**Impact:** Enables artifact authority and resolution with future-proof schema

---

### 3.2 Phase 2: Runtime Artifact Resolution API

**Priority:** 🔴 **CRITICAL - Enables frontend**

**Changes:**
1. Add `RuntimeAPI.resolve_artifact()` endpoint
2. Add `PlatformState.resolveArtifact()` in frontend
3. Resolution flow:
   ```
   Frontend: resolveArtifact(artifactId)
   → Runtime: validate access, resolve via State Surface
   → State Surface: return artifact registry entry
   → Runtime: retrieve content via content_ref
   → Runtime: return content to frontend
   ```

**Impact:** Frontend can resolve artifacts directly, no execution polling

---

### 3.3 Phase 3: Backend Artifact Registration

**Priority:** 🟡 **HIGH - Completes backend alignment**

**Changes:**
1. After intent execution, register artifacts in State Surface
2. Update `ContentOrchestrator` to register:
   - `file` artifacts (from `ingest_file`)
   - `parsed_content` artifacts (from `parse_content`)
   - `embeddings` artifacts (from `extract_embeddings`)
   - `materialization` artifacts (from `save_materialization`)
3. Remove direct storage access from application code

**Impact:** Artifacts become first-class, retrievable by ID

---

### 3.4 Phase 4: Refactor get_parsed_file to Artifact Resolution

**Priority:** 🟡 **HIGH - Fixes retrieval pattern**

**Changes:**
1. Replace `get_parsed_file()` with `resolve_artifact(artifact_id, artifact_type="parsed_content")`
2. Remove storage location fallback logic
3. Remove direct GCS access
4. Use Runtime artifact resolution

**Impact:** Correct artifact-centric retrieval pattern

---

### 3.5 Phase 5: Public Works Artifact Abstraction

**Priority:** 🟢 **MEDIUM - Completes abstraction layer**

**Changes:**
1. Add `ArtifactAbstraction` to Public Works
2. Abstraction methods:
   - `register_artifact()`
   - `resolve_artifact()`
   - `retrieve_artifact_content()` (opaque storage access)
3. Realms use `ArtifactAbstraction`, not storage abstractions directly

**Impact:** Storage becomes opaque, platform abstraction complete

---

### 3.6 Phase 6: Frontend Artifact-Centric API

**Priority:** 🟢 **MEDIUM - Completes frontend alignment**

**Changes:**
1. Replace execution status polling with artifact resolution
2. Update `ContentAPIManager`:
   ```typescript
   // OLD: Poll execution status
   const status = await getExecutionStatus(executionId);
   const fileId = status.artifacts?.file?.semantic_payload?.file_id;
   
   // NEW: Resolve artifact
   const fileArtifact = await resolveArtifact(artifactId, "file");
   const fileId = fileArtifact.semantic_payload.file_id;
   ```
3. **Replace file listing with artifact listing:**
   ```typescript
   // OLD: Multiple file-centric methods
   listFiles()
   listParsedFiles()
   
   // NEW: Single artifact listing with filters
   listArtifacts({
     artifact_type: "file",
     lifecycle_state: "READY",
     eligible_for: "parse_content"
   })
   ```
4. Artifacts become first-class in frontend state
5. UI dropdowns query artifact index (Supabase) for discovery
6. User actions resolve artifacts by ID via Runtime

**Impact:** Frontend aligns with artifact-centric model, UI becomes eligibility-based

---

## 4. Architectural Principles (Going Forward)

### 4.1 Artifact Authority

> **Runtime (via State Surface) is the sole authority for resolving artifacts.**

- ✅ State Surface: Artifact registry (authoritative)
- ✅ Supabase: Lineage/index (discovery only)
- ✅ Storage: Implementation detail (opaque)

### 4.2 Artifact Resolution Pattern

**For Actions (User selects artifact):**
```
User Action → resolveArtifact(artifactId)
→ Runtime validates (access, lifecycle, state)
→ State Surface resolves artifact registry entry
→ Runtime retrieves content via materialization (opaque)
→ Return content
```

**For UI Dropdowns (User browsing):**
```
UI Request → listArtifacts(filters: {
  artifact_type,
  lifecycle_state,
  eligible_for  // Next intent in journey
})
→ Query Supabase artifact index (discovery only)
→ Return artifact metadata (artifact_id, display_name, eligibility)
→ User selects artifact_id
→ Action resolves artifact via Runtime
```

**Key Principle:**
> **UI dropdowns enumerate artifacts by eligibility; actions resolve artifacts by ID.**

**No fallbacks. No direct storage access. No ambiguity.**

### 4.3 Artifact vs. File Mental Model

| Concept | Old (File-Centric) | New (Artifact-Centric) |
|---------|-------------------|------------------------|
| **Identity** | file_id | artifact_id |
| **Type** | file_type | artifact_type |
| **Storage** | storage_location (exposed) | materializations[] (opaque) |
| **State** | file status | lifecycle_state (PENDING/READY/FAILED/ARCHIVED/DELETED) |
| **Authority** | Multiple sources | State Surface only |
| **Retrieval** | "Get file from storage" | "Resolve artifact via Runtime" |
| **Semantics** | Mixed with storage | Separate semantic_descriptor |
| **Lineage** | Implicit | Explicit parent_artifacts |
| **UI Lists** | "List files" | "List artifacts by eligibility" |
| **UI Selection** | File-centric objects | Artifact-centric with eligibility |
| **Discovery** | Storage queries | Artifact index (Supabase) |
| **Resolution** | Direct storage access | Runtime artifact resolution |

### 4.4 Critical Alignment Message (From CTO)

> **From this point forward, *no code* should ever ask "where is this stored?"**
> **Code may only ask: "what artifact do I want to resolve, and is it valid?"**

This line will prevent 80% of future regressions.

---

## 5. Migration Strategy

### 5.1 Backward Compatibility

**Critical:** We can't break existing functionality during migration.

**Strategy:**
1. Add new artifact APIs alongside existing ones
2. Gradually migrate intents to register artifacts
3. Frontend can use both patterns during transition
4. Deprecate old patterns once migration complete

### 5.2 Phased Rollout

1. **Week 1**: State Surface artifact registry (backend only)
2. **Week 2**: Runtime artifact resolution API
3. **Week 3**: Backend artifact registration (new intents)
4. **Week 4**: Refactor get_parsed_file
5. **Week 5**: Frontend artifact resolution
6. **Week 6**: Deprecate old patterns

---

## 6. Success Criteria

### 6.1 Litmus Test (From CTO Guidance)

> "If I changed the storage backend tomorrow, would this code change?"

**Current State:** ❌ **FAILS** - Direct GCS access, storage_location exposure  
**Target State:** ✅ **PASSES** - Opaque content_ref, artifact abstraction

### 6.2 Architectural Alignment

- ✅ No fallback logic in artifact resolution
- ✅ No direct storage queries from application code
- ✅ State Surface is authoritative for artifacts (resolution only, not exploration)
- ✅ Supabase is discovery/index only (exploration and browsing)
- ✅ Storage is opaque implementation detail
- ✅ Artifact identity independent of storage
- ✅ Semantics separate from materialization
- ✅ Multiple materializations supported per artifact

### 6.3 Code Quality

- ✅ Artifacts are first-class (not buried in execution status)
- ✅ Frontend resolves artifacts directly
- ✅ Backend registers artifacts after intent execution
- ✅ No file-centric mental models in code

---

## 7. Risk Assessment

### 7.1 High Risk Areas

1. **State Surface Artifact Registry**: New infrastructure, must be correct
2. **Backward Compatibility**: Can't break existing functionality
3. **Migration Complexity**: Multiple systems need updates

### 7.2 Mitigation

1. **Incremental Migration**: Add new APIs, migrate gradually
2. **Comprehensive Testing**: Test artifact resolution end-to-end
3. **Documentation**: Clear migration guide for team

---

## 8. Recommendations

### 8.1 Immediate Actions (This Week)

1. ✅ **Design State Surface Artifact Registry schema**
2. ✅ **Implement artifact registry in State Surface**
3. ✅ **Add Runtime artifact resolution API**
4. ✅ **Update one intent (e.g., `parse_content`) to register artifacts**

### 8.2 Short-Term (Next 2 Weeks)

1. ✅ **Migrate all Content Realm intents to register artifacts**
2. ✅ **Refactor `get_parsed_file` to use artifact resolution**
3. ✅ **Add frontend `resolveArtifact()` API**

### 8.3 Medium-Term (Next Month)

1. ✅ **Add Public Works ArtifactAbstraction**
2. ✅ **Migrate frontend to artifact-centric patterns**
3. ✅ **Deprecate old file-centric patterns**

---

## 9. CTO Feedback Integration

### 9.1 Overall Assessment ✅

**CTO Verdict:** "This analysis is directionally and architecturally correct. In fact, it's better than 'correct': it shows the team now understands *why* the system felt wrong, not just *what* was broken."

**Key Validation:**
> "This analysis correctly reframes the Content Pillar around artifact authority, not file storage or execution state — and that is the right foundation."

**Critical Inversion:**
> "Artifacts are no longer *outputs of executions* — executions are *producers of artifacts*."

### 9.2 What's Locked In ✅

1. **Violation naming is correct** - These are model violations, not implementation bugs
2. **Separation of concerns table** - This is platform-grade separation, keep it
3. **Phased migration plan** - Realistic, avoids big-bang and permanent dual system traps

### 9.3 Refinements Applied ⚠️

1. **Artifact Schema** - Separated identity, semantics, and materialization
   - `semantic_descriptor` (what it means) separate from `materializations` (how it's stored)
   - Supports multiple materializations per artifact
   - Explicit lineage via `parent_artifacts`

2. **Lifecycle States** - Expanded to include PENDING and FAILED
   - `PENDING` - Registered but not yet materialized
   - `READY` - Valid and accessible
   - `FAILED` - Intent executed but artifact invalid
   - `ARCHIVED` - Retained but not active
   - `DELETED` - Marked for deletion

3. **State Surface Scope** - Clarified boundaries
   - ✅ State Surface: Resolution and authority (`resolve_artifact()`)
   - ✅ Supabase: Exploration and browsing (`list_artifacts()` queries)
   - ❌ State Surface: NOT a general listing engine

### 9.4 Future-Proof Schema (CTO-Recommended)

The refined schema (see Section 3.1) will scale cleanly to:
- Deterministic embeddings
- Semantic embeddings
- Re-parsing with new parsers
- Policy-driven retention
- Cross-artifact joins
- Multiple storage backends
- Partial materialization

### 9.5 UI Listing Pattern (CTO-Recommended)

**Critical Pattern:**
> **UI dropdowns enumerate artifacts by eligibility; actions resolve artifacts by ID.**

**Key Changes:**
- Dropdowns query artifact index (Supabase) by eligibility
- Single `listArtifacts(filters)` method replaces multiple file listing methods
- UI asks "what artifacts are eligible for next intent?" not "what files exist?"
- See `ARTIFACT_LISTING_UI_PATTERN.md` for complete pattern

**Impact:** UI becomes artifact-centric, eligibility-based, capability-driven

---

## 10. Conclusion

**The CTO is right:** We've been building an artifact-centric platform but implementing it with file-centric mental models. This creates architectural debt that will compound if not addressed.

**The fix is clear:** Make artifacts first-class throughout the stack, from Public Works abstractions to frontend components. State Surface becomes the artifact registry, Runtime becomes the artifact resolver, and storage becomes opaque.

**The path forward:** Incremental migration with backward compatibility, starting with State Surface artifact registry (using the refined schema) and working up through the stack.

**This is not a refactor — it's the moment your platform *becomes itself*.**

**Critical Alignment:**
> "From this point forward, *no code* should ever ask 'where is this stored?' Code may only ask: 'what artifact do I want to resolve, and is it valid?'"

---

## 11. Next Steps

1. ✅ **Analysis complete and CTO-validated**
2. ✅ **Artifact registry schema refined (CTO-recommended)**
3. ✅ **Implementation plan created** (see `ARTIFACT_REGISTRY_IMPLEMENTATION_PLAN.md`)
4. **Begin Phase 1: State Surface Artifact Registry**

**Status:** ✅ Ready for implementation

**Implementation Plan:** See `ARTIFACT_REGISTRY_IMPLEMENTATION_PLAN.md` for concrete steps, code structure, and migration strategy.
