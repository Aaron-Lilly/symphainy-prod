# Artifact Retrieval Architecture Analysis

**Date:** January 19, 2026  
**Issue:** How to retrieve roadmap/POC/blueprint artifacts for solution creation

---

## Current Architecture Understanding

### Artifact Storage Flow

1. **Realm Returns Artifacts:**
   - Realms return `{ artifacts: {...}, events: [...] }`
   - Artifacts are structured with `result_type`, `semantic_payload`, `renderings`

2. **Runtime Stores Artifacts:**
   - Artifacts are stored in **execution state** (line 568 in execution_lifecycle_manager.py)
   - Execution state key: `execution:{tenant_id}:{execution_id}`
   - Artifacts live at: `execution_state["artifacts"]["roadmap"]` or `execution_state["artifacts"]["poc"]`

3. **Materialization Policy:**
   - Artifacts may also be persisted to artifact storage (GCS/Supabase) with `artifact_id`
   - But the primary storage is execution state

### The Problem

When creating a solution from a roadmap/POC:
- We have `roadmap_id` or `proposal_id` (from the artifact's semantic_payload)
- We need to retrieve the full artifact
- But we don't have the `execution_id` that created it
- So we can't call `get_execution_state(execution_id)` to get the artifact

### Current (Broken) Approach

We tried storing execution_id pointers in session state, but:
- Session state is ephemeral (24h TTL)
- Session state should store facts/references, not full data
- But storing execution_id pointers still feels wrong

---

## Architectural Principles

From `north_star.md`:

1. **Runtime owns execution and state** - Artifacts live in execution state
2. **Domain services don't own state** - Realms return artifacts, don't store them
3. **Surfaces report facts** - State Surface reports state, doesn't store business data
4. **Execution state is persistent** - Stored in ArangoDB (durable)
5. **Session state is ephemeral** - 24h TTL, for session-level facts

---

## Proposed Solutions

### Option 1: Include execution_id in Artifact semantic_payload

**Approach:**
- When roadmap/POC is created, include `execution_id` in `semantic_payload`
- When retrieving, extract `execution_id` from artifact's semantic_payload
- Use that to get full execution state

**Pros:**
- Artifact is self-contained
- No additional storage needed
- Follows "facts not files" - execution_id is a fact about the artifact

**Cons:**
- Requires modifying artifact structure
- Need to retrieve artifact first to get execution_id (chicken/egg?)

### Option 2: Use artifact_id for Direct Retrieval

**Approach:**
- Store roadmap/POC with `artifact_id = roadmap_id` or `artifact_id = proposal_id`
- Use `get_artifact(artifact_id)` to retrieve directly
- Artifact storage (GCS/Supabase) becomes the source of truth

**Pros:**
- Direct retrieval by ID
- No need to know execution_id
- Follows artifact storage pattern

**Cons:**
- Requires artifacts to be persisted (materialization policy)
- May not work if artifacts are CACHE or DISCARD

### Option 3: Search Execution State by Artifact Content

**Approach:**
- Add ability to search execution state by artifact content
- Query: "find execution where artifacts.roadmap.semantic_payload.roadmap_id = X"
- Retrieve that execution's artifacts

**Pros:**
- Uses execution state as source of truth
- No additional storage
- Follows architecture (execution state is persistent)

**Cons:**
- Requires search capability in State Surface
- May be slow for large numbers of executions
- Not currently implemented

### Option 4: Registry/Index of Artifact IDs

**Approach:**
- Create a registry: `artifact_id -> execution_id` mapping
- Store in execution state or separate registry
- Lookup artifact_id to get execution_id, then retrieve execution state

**Pros:**
- Fast lookup
- Clear separation of concerns
- Can be stored in execution state itself

**Cons:**
- Additional storage/complexity
- Need to maintain registry

---

## Recommended Solution: Option 1 + Option 3 Hybrid

**Primary:** Include `execution_id` in artifact's `semantic_payload` when created
- This makes the artifact self-documenting
- When we have the artifact (from execution state), we know its execution_id

**Fallback:** If we only have `roadmap_id`/`proposal_id`:
- The `roadmap_id`/`proposal_id` IS stored in the artifact's semantic_payload
- We could search execution state for executions containing that ID
- OR: Store a minimal registry in execution state: `artifact_registry: { roadmap_id: execution_id }`

**Implementation:**
1. When roadmap/POC created: Include `execution_id` in `semantic_payload`
2. When solution creation needs artifact:
   - If we have execution_id: Get execution state directly
   - If we only have roadmap_id: 
     - Try: Get execution state using roadmap_id as execution_id (if they match)
     - Try: Search session's recent executions for one containing roadmap_id
     - Try: Use artifact storage if artifact_id exists

---

## Questions for Architecture Review

1. **Should artifacts include their execution_id in semantic_payload?**
   - Makes them self-documenting
   - Follows "facts not files" principle

2. **Should we add search capability to State Surface?**
   - "Find execution where artifact contains X"
   - Or: "List recent executions for session"

3. **Should artifact_id be the same as roadmap_id/proposal_id?**
   - If so, we could use artifact storage as primary retrieval method

4. **What is the intended artifact retrieval pattern?**
   - By execution_id (current)
   - By artifact_id (needs implementation)
   - By content search (needs implementation)

---

**Next Steps:**
1. Review with architecture team
2. Implement recommended solution
3. Update tests
