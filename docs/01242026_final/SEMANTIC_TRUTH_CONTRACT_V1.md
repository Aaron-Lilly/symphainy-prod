# Semantic Truth Contract V1

**Date:** January 25, 2026  
**Version:** 1.0.0  
**Status:** ✅ **ACTIVE**

---

## Purpose

This contract defines what embeddings and semantic meaning guarantee in the Symphainy Platform. It serves as the single source of truth for semantic artifacts and their guarantees.

**CIO Requirement:** One short contract doc that defines what embeddings and semantic meaning guarantee.

---

## What Embeddings Guarantee

### 1. Chunk Identity
- ✅ Each embedding references a stable `chunk_id` (content-addressed, SHA256-based)
- ✅ Chunk IDs are deterministic: same content → same chunk ID
- ✅ Chunk IDs are stable across re-runs

### 2. Idempotency
- ✅ Re-embedding the same chunk with the same profile/model produces the same result
- ✅ Idempotency is enforced at the service level
- ✅ No duplicate embeddings are created for identical chunks

### 3. Profile Isolation
- ✅ Different semantic profiles produce different embeddings
- ✅ Profiles are versioned (`semantic_version`)
- ✅ Profile selection is explicit and auditable

### 4. Versioning
- ✅ All embeddings have `semantic_version` (platform-controlled)
- ✅ Version enables selective re-embedding when models/prompts change
- ✅ Version is included in all semantic artifacts

### 5. Reference-Based Storage
- ✅ Embeddings store by reference (`chunk_id`), not by text blob
- ✅ Text content is not duplicated in embedding storage
- ✅ Chunk metadata links to source file and parsing structure

---

## What Semantic Meaning Guarantees

### 1. Structured Output
- ✅ Semantic signals are structured, not prose-only
- ✅ Format: `key_concepts`, `inferred_intents`, `domain_hints`, `entities`, `ambiguities`
- ✅ JSON-serializable and machine-readable

### 2. Chunk References
- ✅ All semantic artifacts reference `chunk_id` (not raw text)
- ✅ `derived_from` field lists all contributing chunk IDs
- ✅ Lineage is traceable: file → parse → chunk → semantic signal

### 3. Deterministic Structure
- ✅ Same chunks → same semantic structure (modulo model variance)
- ✅ Structure is deterministic even if values vary slightly
- ✅ Re-running produces structurally identical output

### 4. Trigger-Based Computation
- ✅ Only computed on explicit triggers (no auto-fire)
- ✅ Triggers are auditable and logged
- ✅ Cost tracking shows selective hydration

### 5. Self-Describing Artifacts
- ✅ All artifacts include: `artifact_type`, `source_artifact_id`, `producing_agent`, `timestamp`, `tenant_id`
- ✅ Artifacts are self-contained and interpretable
- ✅ No external context required to understand artifact

---

## What Is Explicitly NOT Guaranteed Yet

### 1. Cross-Chunk Reasoning
- ❌ Not yet supported
- ❌ Semantic signals are per-chunk, not cross-chunk
- ❌ Future enhancement: Multi-chunk semantic analysis

### 2. Multi-Vector Per Chunk
- ❌ Not yet supported
- ❌ Each chunk has one embedding per profile/model
- ❌ Future enhancement: Multiple embedding strategies per chunk

### 3. Re-Ranking
- ❌ Not yet supported
- ❌ Search results are not re-ranked
- ❌ Future enhancement: Semantic re-ranking

### 4. Learned Chunking
- ❌ Not yet supported
- ❌ Chunking is structure-based, not learned
- ❌ Future enhancement: ML-based chunking optimization

### 5. Real-Time Updates
- ❌ Not yet supported
- ❌ Embeddings are computed on-demand, not real-time
- ❌ Future enhancement: Streaming semantic computation

---

## Handshake Between Systems

### Backend (Content Realm)
**Produces:**
- Deterministic chunks (stable IDs, structure-based)
- Semantic embeddings (chunk-referenced, profile-aware)
- Semantic signals (structured, chunk-referenced)

**Guarantees:**
- Deterministic outputs (same input → same output)
- Idempotent operations
- Explicit failure handling

### Experience SDK
**Consumes:**
- Semantic artifacts (embeddings, signals)
- Chunk metadata
- Semantic profiles

**Expects:**
- Structured, self-describing artifacts
- Stable chunk IDs
- Profile-aware outputs

### AGUI (Agentic GUI)
**Consumes:**
- Semantic signals (structured meaning)
- Chunk references
- Semantic profiles

**Compiles:**
- Semantic meaning (not text)
- Structured signals → UI components
- Profile-aware rendering

### Frontend Runtime
**Renders:**
- Semantic state (from AGUI compilation)
- Chunk-based UI components
- Profile-aware experiences

**Manages:**
- Runtime state (single source of truth)
- Semantic artifact hydration
- User intent → semantic triggers

---

## Contract Invariants

### Invariant 1: Deterministic Before Semantic
- ✅ Deterministic chunks MUST exist before semantic computation
- ✅ Semantic artifacts MUST reference chunk IDs
- ✅ No semantic computation without deterministic foundation

### Invariant 2: Explicit Triggers
- ✅ Semantic computation requires explicit trigger
- ✅ Triggers are logged and auditable
- ✅ No auto-fire on parse/ingest/upload

### Invariant 3: Profile Isolation
- ✅ Different profiles produce different embeddings
- ✅ Profiles are versioned and scoped
- ✅ Profile selection is explicit

### Invariant 4: Self-Describing Artifacts
- ✅ All artifacts include required metadata
- ✅ Artifacts are JSON-serializable
- ✅ No external context required

### Invariant 5: Honest Outcomes
- ✅ Failures are first-class outcomes
- ✅ Partial success is explicitly reported
- ✅ No silent failures

---

## Version History

**V1.0.0 (January 25, 2026)**
- Initial contract definition
- Based on CTO + CIO feedback
- Aligned with Phase 2 implementation

---

## Contract Validation

### How to Validate Contract Compliance

1. **Deterministic Test:** Re-run embedding + semantic meaning on same file twice
   - Expected: Outputs should be structurally identical (modulo model variance)

2. **Trigger Boundary Test:** Attempt semantic computation without explicit trigger
   - Expected: Should be rejected by SemanticTriggerBoundary

3. **Failure Handling Test:** Simulate partial embedding failure
   - Expected: Artifact should have `status: "partial"` and `failed_chunks` list

4. **Self-Describing Test:** Check all artifacts have required metadata
   - Expected: All artifacts have `artifact_type`, `source_artifact_id`, `producing_agent`, `timestamp`, `tenant_id`

---

**Last Updated:** January 25, 2026  
**Status:** ✅ **ACTIVE - PHASE 2 IMPLEMENTATION**
