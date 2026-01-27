# Intent Execution Log Implementation Plan

**Date:** January 26, 2026  
**Context:** CTO guidance on durable intent context and ingestion_profile  
**Status:** 📋 **READY FOR IMPLEMENTATION**

---

## Summary

We need to add a **durable intent execution log** (`intent_executions` table) where `ingestion_profile` lives. This enables resumable workflows and proper separation of concerns.

---

## Current State

### ✅ What We Have

1. **Artifact Registry** - State Surface (ArangoDB)
   - Stores artifacts with `parent_artifacts` (lineage)
   - Authoritative for resolution

2. **Artifact Index** - Supabase (`artifact_index`)
   - Discovery/exploration layer
   - Has `parent_artifacts` (lineage)

3. **Execution State** - State Surface
   - Ephemeral execution state
   - Session-scoped

### ❌ What We're Missing

1. **Intent Execution Log** - No durable storage
   - No pending intent support
   - No resumable workflows
   - `ingestion_profile` lost if not used immediately

2. **Structured Lineage** - Current lineage is just array
   - Missing: `derivation_intent`, `derivation_run_id`, `generation`, `root_artifact_id`

---

## Implementation Plan

### Phase 1: Create Intent Executions Table

**Migration Script:** `intent_executions_migration.sql`

```sql
CREATE TABLE public.intent_executions (
    intent_id TEXT NOT NULL PRIMARY KEY,
    intent_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    target_artifact_id TEXT,  -- Artifact this intent operates on
    context JSONB NOT NULL DEFAULT '{}',  -- ingestion_profile, parse_options, etc.
    created_by TEXT,
    tenant_id UUID NOT NULL,
    session_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    execution_id TEXT,  -- If executed
    completed_at TIMESTAMP WITH TIME ZONE,
    error TEXT,
    
    CONSTRAINT intent_executions_status_check CHECK (
        status IN ('pending', 'in_progress', 'completed', 'failed', 'cancelled')
    )
);

CREATE INDEX idx_intent_executions_status ON public.intent_executions (status);
CREATE INDEX idx_intent_executions_target_artifact ON public.intent_executions (target_artifact_id);
CREATE INDEX idx_intent_executions_intent_type ON public.intent_executions (intent_type);
CREATE INDEX idx_intent_executions_tenant_status ON public.intent_executions (tenant_id, status);
CREATE INDEX idx_intent_executions_context ON public.intent_executions USING GIN (context);
```

---

### Phase 2: Enhance Lineage Structure

**Update `artifact_index` migration to include structured lineage:**

```sql
-- Add lineage column (if not exists)
ALTER TABLE public.artifact_index
ADD COLUMN IF NOT EXISTS lineage JSONB DEFAULT '{}';

-- Create GIN index for lineage queries
CREATE INDEX IF NOT EXISTS idx_artifact_index_lineage 
    ON public.artifact_index USING GIN (lineage);
```

**Lineage structure:**
```json
{
  "derived_from": ["artifact_id_1", "artifact_id_2"],
  "derivation_intent": "parse_content",
  "derivation_run_id": "exec_456",
  "generation": 1,
  "root_artifact_id": "artifact_id_1"
}
```

**Update ArtifactRecord to support structured lineage:**
- Keep `parent_artifacts` (backward compatible)
- Add `lineage` field (structured metadata)

---

### Phase 3: Update Artifact Indexing

**When indexing artifacts, include structured lineage:**

```python
# In ContentOrchestrator._index_artifact()
lineage = {
    "derived_from": parent_artifacts,
    "derivation_intent": produced_by.intent,
    "derivation_run_id": produced_by.execution_id,
    "generation": len(parent_artifacts),  # Simple generation count
    "root_artifact_id": parent_artifacts[0] if parent_artifacts else artifact_id
}

artifact_record = {
    "artifact_id": artifact_id,
    "artifact_type": artifact_type,
    "tenant_id": tenant_id,
    "lifecycle_state": lifecycle_state,
    "semantic_descriptor": {...},
    "produced_by": {...},
    "parent_artifacts": parent_artifacts,  # Keep for backward compatibility
    "lineage": lineage  # NEW: Structured lineage
}
```

---

### Phase 4: Implement Intent Execution Log

**Add methods to RegistryAbstraction:**

```python
async def create_pending_intent(
    self,
    intent_id: str,
    intent_type: str,
    target_artifact_id: str,
    context: Dict[str, Any],  # ingestion_profile, parse_options, etc.
    tenant_id: str,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create pending intent in intent_executions table."""
    intent_record = {
        "intent_id": intent_id,
        "intent_type": intent_type,
        "status": "pending",
        "target_artifact_id": target_artifact_id,
        "context": context,
        "tenant_id": tenant_id,
        "created_by": user_id
    }
    return await self.insert_record("intent_executions", intent_record, {"tenant_id": tenant_id})

async def get_pending_intents(
    self,
    tenant_id: str,
    target_artifact_id: Optional[str] = None,
    intent_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get pending intents."""
    filters = {"tenant_id": tenant_id, "status": "pending"}
    if target_artifact_id:
        filters["target_artifact_id"] = target_artifact_id
    if intent_type:
        filters["intent_type"] = intent_type
    return await self.query_records("intent_executions", {"tenant_id": tenant_id}, filters)

async def update_intent_status(
    self,
    intent_id: str,
    status: str,
    execution_id: Optional[str] = None,
    error: Optional[str] = None,
    tenant_id: str
) -> Dict[str, Any]:
    """Update intent execution status."""
    updates = {"status": status, "updated_at": datetime.utcnow().isoformat()}
    if execution_id:
        updates["execution_id"] = execution_id
    if status == "completed":
        updates["completed_at"] = datetime.utcnow().isoformat()
    if error:
        updates["error"] = error
    return await self.update_record(
        "intent_executions",
        updates,
        {"tenant_id": tenant_id},
        {"intent_id": intent_id}
    )
```

---

### Phase 5: Update ContentOrchestrator

**When user uploads file (ingest_file):**
- Create source_file artifact (no ingestion_profile)
- Don't store ingestion_profile here

**When user selects ingestion_profile (new flow):**
```python
# Create pending parse_content intent
intent_id = f"parse_{file_id}_{generate_event_id()}"
await registry_abstraction.create_pending_intent(
    intent_id=intent_id,
    intent_type="parse_content",
    target_artifact_id=file_id,
    context={
        "ingestion_profile": ingestion_profile,  # "structured", "unstructured", "hybrid", etc.
        "parse_options": parse_options
    },
    tenant_id=context.tenant_id,
    user_id=context.user_id
)
```

**When parsing executes:**
```python
# Get pending intent for this file
pending_intents = await registry_abstraction.get_pending_intents(
    tenant_id=context.tenant_id,
    target_artifact_id=file_id,
    intent_type="parse_content"
)

if pending_intents:
    pending_intent = pending_intents[0]
    ingestion_profile = pending_intent["context"]["ingestion_profile"]
    parse_options = pending_intent["context"].get("parse_options", {})
    
    # Update intent status to in_progress
    await registry_abstraction.update_intent_status(
        intent_id=pending_intent["intent_id"],
        status="in_progress",
        tenant_id=context.tenant_id
    )
    
    # Parse with stored context
    parsed_result = await self.file_parser_service.parse_file(
        ...,
        parsing_type=ingestion_profile,
        parse_options=parse_options
    )
    
    # Update intent status to completed
    await registry_abstraction.update_intent_status(
        intent_id=pending_intent["intent_id"],
        status="completed",
        execution_id=context.execution_id,
        tenant_id=context.tenant_id
    )
    
    # Create parsed_content artifact with structured lineage
    await context.state_surface.register_artifact(
        ...,
        parent_artifacts=[file_id]
    )
    
    # Index with structured lineage
    await self._index_artifact(
        ...,
        parent_artifacts=[file_id],
        lineage={
            "derived_from": [file_id],
            "derivation_intent": "parse_content",
            "derivation_run_id": context.execution_id,
            "generation": 1,
            "root_artifact_id": file_id
        }
    )
```

---

## Benefits

### ✅ Resumable Workflows
- User uploads file → creates source_file artifact
- User selects ingestion_profile → creates pending intent
- User can resume tomorrow → intent persists

### ✅ Clean Separation
- Artifacts = what exists
- Intents = what should happen
- No semantic pollution

### ✅ Queryable
- "Show me files with pending parse intents"
- "Show me pending intents for this artifact"
- UI can display actionable items

### ✅ Proper Lineage
- Structured lineage in artifact_index
- Queryable via GIN index
- Clear derivation chain

---

## Migration Checklist

### Phase 1: Schema
- [ ] Create `intent_executions` table
- [ ] Add `lineage` column to `artifact_index`
- [ ] Create indexes

### Phase 2: Code
- [ ] Add intent execution methods to RegistryAbstraction
- [ ] Update ContentOrchestrator to create pending intents
- [ ] Update artifact indexing to include structured lineage

### Phase 3: Testing
- [ ] Test pending intent creation
- [ ] Test intent execution with stored context
- [ ] Test lineage structure in artifact_index

---

## Next Steps

1. **Create migration scripts** (intent_executions + lineage)
2. **Implement RegistryAbstraction methods**
3. **Update ContentOrchestrator flow**
4. **Test end-to-end**

**Status:** ✅ **READY FOR IMPLEMENTATION**
