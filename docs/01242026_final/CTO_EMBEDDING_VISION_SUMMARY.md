# CTO Embedding Vision - Executive Summary

**Date:** January 24, 2026  
**Status:** ✅ **ANALYSIS COMPLETE**  
**Purpose:** Quick reference for CTO feedback alignment

---

## Quick Answers

### 1. Is our platform architecture aligned? ✅ **70% - Needs Refinement**

**What We Have:**
- ✅ Schema-level deterministic (`DeterministicEmbeddingService` - schema fingerprints)
- ✅ Semantic embedding pipeline (conceptually)
- ✅ Intent-driven execution

**What's Missing:**
- ⚠️ Chunk-level deterministic identity (we have schema, need chunks)
- ⚠️ Chunk-based semantic embeddings
- ❌ Semantic profile system
- ❌ Pull-based semantic triggers
- ❌ Structured semantic outputs

**Gap:** We have schema fingerprints, but CTO wants **chunk-level deterministic identity** for text content.

---

### 2. Can we show/hydrate views for each step? ✅ **75% - Feasible**

**Parse Step:** ✅ Can display parsed content  
**Deterministic Step:** ⚠️ Need to add chunk-level deterministic (schema-level exists)  
**Semantic Step:** ⚠️ Need to refactor to structured outputs  
**On-Demand Hydration:** ⚠️ Need trigger boundary system

**Conclusion:** MVP is feasible, but requires:
1. Adding chunk-level deterministic chunking (Task 2.0)
2. Refactoring embedding service to chunk-based (Task 2.1)
3. Implementing semantic trigger boundary (Task 2.5)

---

### 3. Does it change Phase 2? ✅ **YES - Major Refactoring**

**Original Phase 2:** 3 tasks (6-8 hours)  
**Updated Phase 2:** 6 tasks (8-12 hours)

**New Tasks:**
- **Task 2.0:** Deterministic Chunking Layer (NEW - CRITICAL)
- **Task 2.4:** Semantic Profile System (NEW)
- **Task 2.5:** Semantic Trigger Boundary (NEW)

**Refactored Tasks:**
- **Task 2.1:** EmbeddingService → Chunk-based, idempotent, profile-aware
- **Task 2.2:** SemanticMeaningAgent → SemanticSignalExtractor (structured outputs)
- **Task 2.3:** Content Orchestrator → Split into deterministic + semantic intents

---

### 4. Infrastructure Recommendations ✅ **YES - 5 Additions**

1. **Chunking Library:** Use parser-structure-based chunking (custom, not LangChain heuristics)
2. **Deterministic Identity System:** Content-addressed chunk IDs (SHA256-based)
3. **Semantic Profile Registry:** Store profiles in Supabase, reference in all semantic artifacts
4. **Chunk Query Abstraction:** DuckDB abstractions for chunk queries
5. **Semantic Trigger Boundary:** Enforce pull-based semantic computation

---

## CTO's 5 Non-Negotiable Principles

1. **Deterministic before semantic** - All semantic work depends on stable chunk identity
2. **Semantic meaning is contextual and versioned** - Every semantic artifact has version/model/prompt
3. **No semantic computation without explicit trigger** - Pull-based, not push-based
4. **All semantics must reference stable deterministic identities** - Reference chunk_id, not raw text
5. **Hydration is cheaper than storage** - Compute on-demand, store chunk references

---

## Updated Phase 2 Tasks

### Task 2.0: Deterministic Chunking Layer (NEW)
- Create `DeterministicChunk` data class
- Implement parser-structure-based chunking
- Generate stable chunk IDs
- Track chunk lineage

### Task 2.1: EmbeddingService (REFACTORED)
- Accept `List[DeterministicChunk]` (not blobs)
- Add `semantic_profile` parameter
- Implement idempotency check
- Store by `chunk_id` reference

### Task 2.2: SemanticSignalExtractor (REFACTORED)
- Rename from SemanticMeaningAgent
- Return structured signals (not prose-first)
- Reference chunk IDs
- Only fire on explicit triggers

### Task 2.3: Content Orchestrator (REFACTORED)
- Split into two intents:
  - `extract_deterministic_structure` (no LLM)
  - `hydrate_semantic_profile` (on-demand)

### Task 2.4: Semantic Profile System (NEW)
- Create `SemanticProfile` registry
- Version profiles
- Reference in all semantic artifacts

### Task 2.5: Semantic Trigger Boundary (NEW)
- Enforce pull-based computation
- Log all semantic computations
- Prevent over-eager interpretation

---

## Key Implementation Changes

### Before (Original Plan)
```python
# Blob → Embeddings
embedding_result = await embedding_service.create_embeddings(
    parsed_content=parsed_content,  # Dict
    model_name="text-embedding-ada-002"
)
```

### After (CTO-Aligned)
```python
# Chunks → Embeddings (idempotent, profile-aware)
chunks = await deterministic_chunking_service.create_chunks(
    parsed_content=parsed_content,
    file_id=file_id
)

embedded_chunk_ids = await embedding_service.create_embeddings(
    chunks=chunks,  # List[DeterministicChunk]
    semantic_profile="default",
    model_name="text-embedding-ada-002"
)
```

---

## Cost Containment Strategy

**CTO's Vision:**
- Deterministic layer: Cheap, stable, acts as address space
- Semantic layer: Sparse, selective, versioned, replaceable
- Hydration: Paid for only when needed, targeted to specific chunks

**Our Implementation:**
- ✅ Idempotency checks (won't re-embed existing chunks)
- ✅ Profile-based separation (multiple interpretations per chunk)
- ✅ Trigger-based computation (only on explicit need)
- ✅ Chunk references (not text blobs in storage)

---

## Next Steps

1. ✅ **Review existing DeterministicEmbeddingService** - Understand schema-level work
2. ✅ **Add chunk-level deterministic chunking** - Task 2.0
3. ✅ **Refactor EmbeddingService** - Task 2.1
4. ✅ **Refactor SemanticSignalExtractor** - Task 2.2
5. ✅ **Split Content Orchestrator intents** - Task 2.3
6. ✅ **Add Semantic Profile System** - Task 2.4
7. ✅ **Add Semantic Trigger Boundary** - Task 2.5

---

**Last Updated:** January 24, 2026  
**Status:** ✅ **READY FOR IMPLEMENTATION**
