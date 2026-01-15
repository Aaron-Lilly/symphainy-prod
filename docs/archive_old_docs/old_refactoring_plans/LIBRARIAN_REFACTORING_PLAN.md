# Librarian Refactoring Plan

**Date:** January 13, 2026  
**Status:** 🔄 In Progress

---

## Summary

Refactor Librarian role to align with new architecture:
- **Abstractions** → Pure infrastructure (remove business logic)
- **Platform SDK** → Governance translation logic (tenant filtering, access control)
- **Librarian Service** → Domain logic (semantic operations, embeddings, search coordination)
- **Librarian Primitive** → Policy decisions (search access, knowledge access)

---

## Key Insight: Domain Logic vs Governance Logic

**Domain Logic** (belongs in Librarian Service, not abstractions):
- Embedding storage/retrieval operations
- Semantic graph operations
- Search coordination (hybrid search, result merging)
- Content metadata storage (not extraction - that's Content Pillar)

**Governance Logic** (belongs in Platform SDK + Primitive):
- Tenant filtering
- Access control validation
- Search access policies
- Knowledge access policies

---

## Abstractions to Refactor

### 1. Semantic Data Abstraction

**Current State:**
- Contains business logic: UUID generation, field validation, metadata enhancement, tenant filtering
- Location: `symphainy_source/symphainy-platform/foundations/public_works_foundation/infrastructure_abstractions/semantic_data_abstraction.py`

**Business Logic to Remove:**
- ✅ UUID generation for embedding keys (`_key` generation)
- ✅ Field validation (column_name, embedding vectors)
- ✅ Metadata enhancement (created_at, tenant_id injection)
- ✅ Document structure building (should be done by Librarian service)
- ✅ Tenant filtering (should be done by Platform SDK)

**What Stays (Pure Infrastructure):**
- Direct ArangoDB adapter calls
- Raw data return (no business objects)
- Collection names (infrastructure concern)

**Refactored Interface:**
```python
async def store_semantic_embeddings(
    self,
    embedding_documents: List[Dict[str, Any]]  # Pre-built documents
) -> Dict[str, Any]:
    """Store embedding documents - pure infrastructure."""
    # Just call arango_adapter.create_documents()
    # No validation, no UUID generation, no metadata enhancement
```

---

### 2. Knowledge Discovery Abstraction

**Current State:**
- Contains business logic: Search strategy coordination, result merging, analytics tracking
- Location: `symphainy_source/symphainy-platform/foundations/public_works_foundation/infrastructure_abstractions/knowledge_discovery_abstraction.py`

**Business Logic to Remove:**
- ✅ Search strategy coordination (hybrid search logic)
- ✅ Result merging logic (semantic + exact search)
- ✅ Analytics tracking (business concern)
- ✅ Search mode routing (business logic)

**What Stays (Pure Infrastructure):**
- Direct adapter calls (Meilisearch, Redis Graph, ArangoDB)
- Raw data return
- Index/graph names (infrastructure concern)

**Refactored Interface:**
```python
async def search_meilisearch(
    self,
    index: str,
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 10,
    offset: int = 0
) -> Dict[str, Any]:
    """Search Meilisearch - pure infrastructure."""
    # Just call meilisearch_adapter.search()
    # No coordination, no merging, no analytics
```

---

### 3. Content Metadata Abstraction

**Status:** ✅ Already refactored (Data Steward phase)

**Note:** Librarian uses this for storage only (not extraction). The abstraction is already pure infrastructure.

---

### 4. Knowledge Governance Abstraction

**Status:** ✅ Already refactored (Data Steward phase)

**Note:** Librarian uses this for policy management. The abstraction is already pure infrastructure.

---

### 5. Messaging Abstraction

**Status:** ✅ Already pure (caching operations)

---

## Platform SDK Methods to Add

### Search Access Authorization
```python
async def ensure_search_access(
    self,
    action: str,  # "search_knowledge", "semantic_search", etc.
    user_id: str,
    tenant_id: str,
    query: Optional[str] = None,
    security_context: Optional[SecurityContext] = None
) -> Dict[str, Any]:
    """
    Ensure user can perform search operations.
    
    Translates Realm intent → runtime contract shape for Librarian Primitive.
    - Queries Policy Registry for search access policies
    - Prepares runtime contract shape
    """
```

### Knowledge Access Authorization
```python
async def ensure_knowledge_access(
    self,
    action: str,  # "read_embeddings", "read_semantic_graph", etc.
    user_id: str,
    tenant_id: str,
    resource: Optional[str] = None,  # content_id, file_id, etc.
    security_context: Optional[SecurityContext] = None
) -> Dict[str, Any]:
    """
    Ensure user can access knowledge assets.
    
    Translates Realm intent → runtime contract shape for Librarian Primitive.
    - Queries Policy Registry for knowledge access policies
    - Prepares runtime contract shape
    """
```

### Tenant Filtering (Translation Logic)
```python
async def apply_tenant_filter(
    self,
    filter_conditions: Dict[str, Any],
    tenant_id: str
) -> Dict[str, Any]:
    """
    Apply tenant filtering to search/query filters.
    
    This is translation logic - adds tenant_id to filter conditions.
    Harvested from SemanticDataAbstraction and KnowledgeDiscoveryAbstraction.
    """
    return {
        **filter_conditions,
        "tenant_id": tenant_id
    }
```

---

## Librarian Primitive to Create

**Location:** `civic_systems/smart_city/primitives/librarian/librarian_primitive.py`

```python
class LibrarianPrimitive:
    """
    Librarian Primitive - Policy-aware knowledge access.
    
    Pure primitive that makes policy decisions about:
    - Search access validation
    - Knowledge access validation
    """
    
    async def evaluate_search_access(
        self,
        security_context: SecurityContext,
        action: str,
        tenant_id: str,
        query: Optional[str] = None,
        policy_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate search access policy.
        
        Policy Logic Only:
        - Is user authorized for this search action?
        - Are policy rules satisfied?
        - Are there query restrictions?
        """
    
    async def evaluate_knowledge_access(
        self,
        security_context: SecurityContext,
        action: str,
        tenant_id: str,
        resource: Optional[str] = None,
        policy_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate knowledge access policy.
        
        Policy Logic Only:
        - Is user authorized for this knowledge action?
        - Are policy rules satisfied?
        - Are there resource restrictions?
        """
```

---

## Domain Logic Migration (Librarian Service)

**Key Principle:** Domain logic (semantic operations, embeddings, search coordination) belongs in **Librarian Service**, not abstractions.

### Embedding Storage Logic
**Move from:** `SemanticDataAbstraction.store_semantic_embeddings()`  
**Move to:** `LibrarianService.store_embeddings()` (already exists in modules/semantic_data_storage.py)

**What to Add:**
- UUID generation for embedding keys
- Field validation
- Document structure building
- Metadata enhancement (created_at, etc.)

**What to Keep in Abstraction:**
- Direct ArangoDB calls
- Raw data return

### Search Coordination Logic
**Move from:** `KnowledgeDiscoveryAbstraction.search_knowledge()`  
**Move to:** `LibrarianService.search_knowledge()` (already exists in modules/search.py)

**What to Add:**
- Hybrid search coordination
- Result merging logic
- Search mode routing

**What to Keep in Abstraction:**
- Direct adapter calls (Meilisearch, Redis Graph, ArangoDB)
- Raw data return

---

## Execution Steps

1. **Analyze Current Implementation**
   - ✅ Review SemanticDataAbstraction business logic
   - ✅ Review KnowledgeDiscoveryAbstraction business logic
   - ✅ Review Librarian service modules

2. **Refactor Semantic Data Abstraction**
   - Remove UUID generation
   - Remove field validation
   - Remove metadata enhancement
   - Remove tenant filtering
   - Return raw data only

3. **Refactor Knowledge Discovery Abstraction**
   - Remove search coordination
   - Remove result merging
   - Remove analytics tracking
   - Return raw data only

4. **Add Platform SDK Methods**
   - `ensure_search_access()`
   - `ensure_knowledge_access()`
   - `apply_tenant_filter()`

5. **Create Librarian Primitive**
   - `evaluate_search_access()`
   - `evaluate_knowledge_access()`

6. **Update Librarian Service**
   - Move embedding storage logic from abstraction to service
   - Move search coordination logic from abstraction to service
   - Use Platform SDK for tenant filtering and access control

7. **Create Protocols**
   - `SemanticDataProtocol` (update if needed)
   - `KnowledgeDiscoveryProtocol` (update if needed)

8. **Test**
   - Create E2E tests
   - Verify equivalent or better functionality

---

## Flagged for Future Phases ⏸️

**Domain Logic** (belongs in Realm services, not Smart City):
- ⏸️ Embedding generation (Content Pillar - Business Enablement)
- ⏸️ Semantic graph generation (Content Pillar - Business Enablement)
- ⏸️ Content analysis (Content Pillar - Business Enablement)
- ⏸️ Search result ranking algorithms (may be domain-specific)

---

## Key Learnings

1. **Domain Logic vs Governance Logic:**
   - Domain logic (semantic operations, embeddings) → Librarian Service
   - Governance logic (access control, tenant filtering) → Platform SDK + Primitive

2. **Abstractions are Pure Infrastructure:**
   - No business logic
   - No domain logic
   - Just adapter calls and raw data return

3. **Service Owns Domain Logic:**
   - Librarian service coordinates search, stores embeddings, manages semantic graphs
   - This is correct - Smart City roles provide domain capabilities

4. **Primitive Makes Policy Decisions:**
   - Librarian Primitive decides if user can search/access knowledge
   - Does not perform domain operations
