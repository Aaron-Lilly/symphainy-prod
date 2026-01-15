# Librarian Refactoring Progress

**Date:** January 13, 2026  
**Status:** 🔄 In Progress (Semantic Data Abstraction Complete)

---

## ✅ Completed: Semantic Data Abstraction

### What Was Done
1. **Created `SemanticDataProtocol`** - Pure infrastructure interface
2. **Refactored `SemanticDataAbstraction`** - Pure infrastructure implementation
   - Removed: UUID generation, field validation, metadata enhancement, tenant filtering
   - Returns: Raw data from ArangoDB adapter
   - Accepts: Pre-built documents (with _key, metadata, etc.)

### Key Changes
- **Before:** Abstraction built documents, validated fields, added metadata
- **After:** Abstraction accepts pre-built documents, just stores them
- **Domain Logic:** Moved to Librarian Service (where it belongs)

---

## 🔄 Next: Knowledge Discovery Abstraction

### Current State
- **Location:** `symphainy_source/symphainy-platform/foundations/public_works_foundation/infrastructure_abstractions/knowledge_discovery_abstraction.py`
- **Size:** ~560 lines
- **Business Logic:** Search coordination, result merging, analytics tracking, recommendation merging

### Business Logic to Remove
1. **Search Coordination** (`execute_hybrid_search`, `_execute_hybrid_search`)
   - Hybrid search strategy selection
   - Multi-backend coordination
   - **Move to:** Librarian Service

2. **Result Merging** (`_merge_semantic_results`, `_merge_relationship_results`, `_merge_cluster_results`, `_merge_recommendation_results`)
   - Merging results from multiple backends
   - Ranking and deduplication
   - **Move to:** Librarian Service

3. **Analytics Tracking** (`_track_search_analytics`)
   - Search analytics tracking
   - **Move to:** Librarian Service (or defer to future phase)

4. **Search Mode Routing** (`search_knowledge`)
   - Routing based on search mode (exact, fuzzy, semantic, hybrid)
   - **Move to:** Librarian Service

### What Should Stay (Pure Infrastructure)
1. **Direct Adapter Calls**
   - `meilisearch_adapter.search()`
   - `redis_graph_adapter.find_semantic_similarity()`
   - `arango_adapter.find_semantic_similarity()`

2. **Raw Data Return**
   - No result merging
   - No analytics enhancement
   - Just raw adapter responses

### Refactored Interface (Proposed)
```python
# Pure infrastructure methods (direct adapter calls)
async def search_meilisearch(
    self,
    index: str,
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 10,
    offset: int = 0
) -> Dict[str, Any]:
    """Search Meilisearch - pure infrastructure."""
    return await self.meilisearch_adapter.search(index, query, filters, limit, offset)

async def search_redis_graph(
    self,
    graph: str,
    query: str,
    similarity_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """Search Redis Graph - pure infrastructure."""
    return await self.redis_graph_adapter.find_semantic_similarity(graph, query, similarity_threshold)

async def search_arango(
    self,
    query: str,
    similarity_threshold: float = 0.7,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """Search ArangoDB - pure infrastructure."""
    return await self.arango_adapter.find_semantic_similarity(query, similarity_threshold, max_results)
```

---

## 📋 Remaining Tasks

### 1. Refactor Knowledge Discovery Abstraction
- [ ] Split into pure infrastructure methods (direct adapter calls)
- [ ] Remove search coordination logic
- [ ] Remove result merging logic
- [ ] Remove analytics tracking
- [ ] Create `KnowledgeDiscoveryProtocol` (update if needed)

### 2. Add Platform SDK Methods
- [ ] `ensure_search_access()` - Search access authorization
- [ ] `ensure_knowledge_access()` - Knowledge access authorization
- [ ] `apply_tenant_filter()` - Tenant filtering translation logic

### 3. Create Librarian Primitive
- [ ] `evaluate_search_access()` - Search access policy decisions
- [ ] `evaluate_knowledge_access()` - Knowledge access policy decisions

### 4. Update Librarian Service
- [ ] Move embedding storage logic from abstraction to service
- [ ] Move search coordination logic from abstraction to service
- [ ] Use Platform SDK for tenant filtering and access control

### 5. Test
- [ ] Create E2E tests
- [ ] Verify equivalent or better functionality

---

## 🎯 Key Architectural Decisions

1. **Domain Logic Belongs in Service:**
   - Embedding storage operations → Librarian Service
   - Search coordination → Librarian Service
   - Result merging → Librarian Service

2. **Governance Logic Belongs in SDK + Primitive:**
   - Tenant filtering → Platform SDK
   - Access control → Platform SDK + Primitive

3. **Abstractions are Pure Infrastructure:**
   - Just adapter calls
   - Raw data return
   - No business logic

---

## 📝 Notes

- Knowledge Discovery Abstraction is large (~560 lines) and contains significant business logic
- The refactoring will split it into pure infrastructure methods
- Coordination/merging logic will move to Librarian Service
- This aligns with the principle that Smart City roles provide domain capabilities
