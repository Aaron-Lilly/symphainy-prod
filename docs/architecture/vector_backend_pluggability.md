# Vector Backend Pluggability

## Overview

The Semantic Data Abstraction layer supports pluggable vector backends, enabling the platform to use different vector databases without changing business logic.

## Architecture

```
SemanticDataAbstraction (Layer 1)
    ↓
VectorBackendProtocol (Interface)
    ↓
┌─────────────┬──────────────┬──────────────┐
│ ArangoDB    │ Pinecone     │ Weaviate     │
│ (Default)   │ (Optional)   │ (Optional)   │
└─────────────┴──────────────┴──────────────┘
```

## Current Implementation

**Default Backend:** ArangoDB
- Implemented in `ArangoAdapter.vector_search()`
- Uses ArangoDB's `COSINE_SIMILARITY()` function
- Fallback to L2 distance calculation if COSINE_SIMILARITY unavailable

## Interface Contract

All vector backends must implement `VectorBackendProtocol`:

```python
async def vector_search(
    collection_name: str,
    query_vector: List[float],
    vector_field: str = "embedding",
    filter_conditions: Optional[Dict[str, Any]] = None,
    limit: int = 10,
    similarity_threshold: Optional[float] = None
) -> List[Dict[str, Any]]
```

## Adding a New Backend

To add a new vector backend (e.g., Pinecone):

1. **Create Adapter:**
   ```python
   class PineconeAdapter:
       async def vector_search(...):
           # Implement Pinecone vector search
   ```

2. **Implement Protocol:**
   - Ensure adapter implements `VectorBackendProtocol`
   - Return documents with `similarity` scores

3. **Update SemanticDataAbstraction:**
   ```python
   semantic_abstraction = SemanticDataAbstraction(
       arango_adapter=PineconeAdapter(...)  # Swap adapter
   )
   ```

## Benefits

- **Swappability:** Change backends without changing business logic
- **Vendor Flexibility:** Use best vector database for each use case
- **Testing:** Mock backends for unit tests
- **Migration:** Gradually migrate between backends

## Notes

- Similarity scores should be normalized (0.0 to 1.0)
- Results should be sorted by similarity (highest first)
- Filter conditions are backend-specific (may need translation)
