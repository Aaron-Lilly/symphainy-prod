# Intent Execution Log Implementation Complete

**Date:** January 26, 2026  
**Status:** ✅ **IMPLEMENTATION COMPLETE**  
**Next:** Run intent_executions migration script, then test end-to-end

---

## Summary

Implementation of CTO's guidance on durable intent context and ingestion_profile handling is complete. We've added intent execution log support, structured lineage, and proper separation of concerns.

---

## ✅ Completed Work

### 1. Intent Executions Table Migration ✅

**File:** `docs/supabase_tablesandschemas/intent_executions_migration.sql`

- Creates `intent_executions` table
- Stores pending/resumable intents
- `ingestion_profile` lives in `context` JSONB field
- Supports status tracking (pending, in_progress, completed, failed, cancelled)
- Indexes for querying pending intents

---

### 2. RegistryAbstraction Intent Methods ✅

**File:** `symphainy_platform/foundations/public_works/abstractions/registry_abstraction.py`

**Added Methods:**
- `create_pending_intent()` - Create pending intent with context
- `get_pending_intents()` - Query pending intents (for UI)
- `update_intent_status()` - Update intent status (in_progress, completed, failed)

**Key Feature:** `ingestion_profile` stored in `context` field, not on artifact.

---

### 3. Structured Lineage in Artifact Indexing ✅

**File:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

**Updated `_index_artifact()` method:**
- Includes structured lineage metadata:
  ```json
  {
    "derived_from": ["artifact_id_1"],
    "derivation_intent": "parse_content",
    "derivation_run_id": "exec_456",
    "generation": 1,
    "root_artifact_id": "artifact_id_1"
  }
  ```
- Keeps `parent_artifacts` for backward compatibility
- Lineage stored in `artifact_index.lineage` column

---

### 4. ContentOrchestrator Pending Intent Support ✅

**File:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

**Added:**
- `create_pending_parse_intent()` - Create pending intent when user selects ingestion_profile
- Updated `_handle_parse_content()` to:
  - Check for pending intents first
  - Use pending intent context (ingestion_profile) if available
  - Update intent status to in_progress → completed

**Flow:**
```
1. User uploads file → Create source_file artifact (no ingestion_profile)
2. User selects ingestion_profile → Create pending parse_content intent
3. User can resume later → Query pending intents → Execute with stored context
```

---

## 📊 Architecture

### Intent Execution Flow (CTO Guidance)

```
1. User uploads file
   → ingest_file intent executed
   → source_file artifact created (artifact_index)
   → NO ingestion_profile stored here ✅

2. User selects ingestion_profile
   → create_pending_parse_intent() called
   → Pending intent created in intent_executions
   → context.ingestion_profile = "hybrid" ✅
   → status = "pending"

3. User can resume later (different session)
   → Query pending intents for file
   → Execute parse_content intent
   → Use stored ingestion_profile from pending intent ✅

4. Parsing executes
   → Update intent status: pending → in_progress → completed
   → Create parsed_content artifact
   → Include structured lineage in artifact_index ✅
```

### Key Principles (From CTO)

1. ✅ **Artifacts describe what exists** - No ingestion_profile on artifacts
2. ✅ **Intents describe what should happen** - ingestion_profile lives with intent
3. ✅ **Intents are durable and resumable** - Not ephemeral
4. ✅ **Lineage is structured metadata** - In artifact_index, not scattered

---

## 🔍 Code Changes

### RegistryAbstraction

**New Methods:**
```python
async def create_pending_intent(...)
async def get_pending_intents(...)
async def update_intent_status(...)
```

### ContentOrchestrator

**New Method:**
```python
async def create_pending_parse_intent(
    file_id: str,
    ingestion_profile: str,
    context: ExecutionContext,
    parse_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]
```

**Updated Method:**
```python
async def _handle_parse_content(...)
    # Checks for pending intent first
    # Uses ingestion_profile from pending intent context
    # Updates intent status through lifecycle
```

**Updated Method:**
```python
async def _index_artifact(...)
    # Includes structured lineage metadata
    # lineage = {
    #     "derived_from": [...],
    #     "derivation_intent": "...",
    #     "derivation_run_id": "...",
    #     "generation": 1,
    #     "root_artifact_id": "..."
    # }
```

---

## 📝 Next Steps

### Step 1: Run Migration Script

1. Open Supabase SQL Editor
2. Copy `intent_executions_migration.sql`
3. Execute script
4. Verify table and indexes created

### Step 2: Test Pending Intent Creation

```python
# Create pending intent when user selects ingestion_profile
result = await content_orchestrator.create_pending_parse_intent(
    file_id="file_123",
    ingestion_profile="hybrid",
    context=execution_context,
    parse_options={"option": "value"}
)

# Verify intent created in intent_executions table
```

### Step 3: Test Intent Execution

```python
# Submit parse_content intent
# Should find pending intent and use ingestion_profile from context
result = await submit_intent({
    "intent_type": "parse_content",
    "file_id": "file_123",
    # parsing_type not needed - comes from pending intent
})

# Verify:
# - Pending intent status updated: pending → in_progress → completed
# - Parsing uses ingestion_profile from pending intent
# - Artifact created with structured lineage
```

### Step 4: Test Resumable Workflow

```python
# Day 1: Upload file
file_result = await submit_intent({"intent_type": "ingest_file", ...})

# Day 1: Select ingestion_profile
pending_result = await create_pending_parse_intent(
    file_id=file_result["file_id"],
    ingestion_profile="hybrid",
    context=context
)

# Day 2: Resume (different session)
# Query pending intents
pending_intents = await registry.get_pending_intents(
    tenant_id=tenant_id,
    target_artifact_id=file_id
)

# Execute parse_content (uses stored ingestion_profile)
parse_result = await submit_intent({
    "intent_type": "parse_content",
    "file_id": file_id
    # ingestion_profile comes from pending intent ✅
})
```

---

## ✅ Success Criteria

### ✅ Implementation Complete When:

1. ✅ `intent_executions` table migration script created
2. ✅ RegistryAbstraction intent methods implemented
3. ✅ ContentOrchestrator creates pending intents
4. ✅ ContentOrchestrator uses pending intents when parsing
5. ✅ Structured lineage included in artifact indexing
6. ✅ All code compiles successfully

### ⏳ Remaining:

- [ ] Run `intent_executions_migration.sql` in Supabase
- [ ] Test pending intent creation
- [ ] Test intent execution with stored context
- [ ] Test resumable workflow (cross-session)

---

## 🎯 Architecture Benefits

### ✅ Clean Separation

- **Artifacts** = what exists (no ingestion_profile)
- **Intents** = what should happen (ingestion_profile lives here)
- **Lineage** = structured metadata in artifact_index

### ✅ Resumable Workflows

- User can upload file, wander off, resume tomorrow
- Intent context persists
- No session coupling

### ✅ Queryable

- "Show me files with pending parse intents"
- "Show me pending intents for this artifact"
- UI can display actionable items

### ✅ Proper Lineage

- Structured lineage in artifact_index
- Queryable via GIN index
- Clear derivation chain

---

## 📚 Files Modified

1. `docs/supabase_tablesandschemas/intent_executions_migration.sql` (NEW)
   - Intent executions table migration

2. `symphainy_platform/foundations/public_works/abstractions/registry_abstraction.py`
   - Added `create_pending_intent()`
   - Added `get_pending_intents()`
   - Added `update_intent_status()`

3. `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`
   - Added `create_pending_parse_intent()`
   - Updated `_handle_parse_content()` to use pending intents
   - Updated `_index_artifact()` to include structured lineage

---

## 🚀 Ready for Testing

**Status:** ✅ **Implementation Complete**

**Next:** Run migration script and test end-to-end!

The implementation follows CTO guidance:
- ✅ ingestion_profile lives with intent, not artifact
- ✅ Intents are durable and resumable
- ✅ Lineage is structured metadata
- ✅ Clean separation of concerns
