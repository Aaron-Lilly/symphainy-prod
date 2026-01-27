# Phase 3: Breaking Changes Policy

**Date:** January 25, 2026  
**Status:** ✅ **ACTIVE POLICY**

---

## Core Principle

**Breaking changes are an opportunity to find hidden anti-patterns, NOT a risk to mitigate.**

---

## Policy

### ❌ DO NOT:
- Add backward compatibility unless it's fully aligned with new functional and architectural direction
- Create compatibility shims or adapters
- Maintain dual code paths (old + new)
- Gradually deprecate without clear removal timeline

### ✅ DO:
- Let breaking changes surface hidden anti-patterns
- Use fail-fast assertions to catch violations early
- Document migration paths clearly
- Embrace breaking changes as architectural enforcement
- Remove deprecated code aggressively

---

## Rationale

### Why No Backward Compatibility?

1. **Backward compatibility masks architectural debt**
   - Old patterns continue to exist alongside new patterns
   - Creates confusion about which pattern to use
   - Technical debt accumulates

2. **Breaking changes force explicit migration decisions**
   - Teams must consciously migrate
   - Migration decisions are explicit and documented
   - No ambiguity about which pattern to use

3. **Hidden anti-patterns are discovered when old code breaks**
   - Breaking changes reveal dependencies on old patterns
   - Forces discovery of hidden coupling
   - Surfaces architectural violations

4. **Clean break is better than gradual migration that never completes**
   - Gradual migrations often stall
   - Partial migrations create confusion
   - Clean break ensures complete migration

---

## Implementation

### Anti-Corruption Layer (Task 3.0.5)
- ✅ Fail-fast assertions in `SemanticDataAbstraction.get_semantic_embeddings()` - Rejects `parsed_file_id`
- ✅ Fail-fast assertions in `SemanticDataAbstraction.store_semantic_embeddings()` - Requires `chunk_id`
- ✅ Fail-fast assertions in `SemanticTriggerBoundary` - Rejects invalid triggers

**Result:** Legacy paths fail immediately, forcing migration.

### Deprecated Intents
- ✅ `extract_embeddings` - Deprecated with error-level logging
- ✅ Clear migration path documented
- ✅ No backward compatibility shims

**Result:** Usage is surfaced via error logs, migration is explicit.

### Service Updates
- ✅ All services updated to new pattern
- ✅ Old pattern code removed (not maintained alongside)
- ✅ No dual code paths

**Result:** Single source of truth, no confusion.

---

## Migration Strategy

### For Deprecated Intents:
1. **Log error** when deprecated intent is used
2. **Document migration path** clearly
3. **Remove deprecated code** after migration period
4. **No compatibility shims** - force explicit migration

### For Service Updates:
1. **Update to new pattern** completely
2. **Remove old pattern code** (don't maintain both)
3. **Fail fast** if old pattern is attempted
4. **Document new pattern** clearly

### For Data Migration:
1. **Data can coexist** (storage layer)
2. **Code must migrate** (application layer)
3. **Explicit migration** (not gradual)
4. **Validation ensures correctness**

---

## Examples

### ✅ Good: Breaking Change with Clear Migration
```python
# Old pattern (deprecated)
async def old_method(parsed_file_id: str):
    embeddings = await semantic_data.get_semantic_embeddings(
        filter_conditions={"parsed_file_id": parsed_file_id}
    )

# New pattern (required)
async def new_method(parsed_file_id: str):
    chunks = await deterministic_chunking_service.create_chunks(...)
    chunk_ids = [chunk.chunk_id for chunk in chunks]
    embeddings = await semantic_data.get_semantic_embeddings(
        filter_conditions={"chunk_id": {"$in": chunk_ids}}
    )
```

### ❌ Bad: Backward Compatibility Shim
```python
# ❌ DON'T DO THIS
async def get_embeddings(parsed_file_id: str, chunk_ids: Optional[List[str]] = None):
    if chunk_ids:
        # New pattern
        return await semantic_data.get_semantic_embeddings(
            filter_conditions={"chunk_id": {"$in": chunk_ids}}
        )
    else:
        # Old pattern (backward compatibility)
        return await semantic_data.get_semantic_embeddings(
            filter_conditions={"parsed_file_id": parsed_file_id}
        )
```

**Why Bad:**
- Maintains dual code paths
- Masks architectural debt
- Creates confusion
- Allows old pattern to persist

---

## Success Criteria

### Breaking Changes Are Successful If:
- ✅ All code uses new pattern (no old pattern code remains)
- ✅ Fail-fast assertions catch violations
- ✅ Migration paths are documented
- ✅ No backward compatibility shims exist
- ✅ Hidden anti-patterns are discovered and fixed

### Breaking Changes Are NOT Successful If:
- ❌ Old pattern code still exists alongside new pattern
- ❌ Compatibility shims are added
- ❌ Gradual migration stalls
- ❌ Hidden anti-patterns remain undiscovered

---

## Enforcement

### Code Review Checklist:
- [ ] No backward compatibility shims
- [ ] No dual code paths (old + new)
- [ ] Deprecated code is removed, not maintained
- [ ] Fail-fast assertions catch violations
- [ ] Migration paths are documented

### Testing Checklist:
- [ ] New pattern works correctly
- [ ] Old pattern fails fast (not silently)
- [ ] No compatibility code exists
- [ ] Migration examples are tested

---

**Last Updated:** January 25, 2026  
**Status:** ✅ **ACTIVE POLICY - NO BACKWARD COMPATIBILITY**
