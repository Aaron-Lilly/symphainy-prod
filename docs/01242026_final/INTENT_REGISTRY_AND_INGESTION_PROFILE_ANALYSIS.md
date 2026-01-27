# Intent Registry and Ingestion Profile Analysis

**Date:** January 26, 2026  
**Context:** CTO guidance on durable intent context and ingestion_profile handling  
**Status:** 📋 **ANALYSIS COMPLETE - ARCHITECTURAL GAP IDENTIFIED**

---

## Executive Summary

The CTO's guidance reveals a **critical architectural gap**: we don't have a **durable intent execution log**. Currently, intents are executed immediately and execution state is ephemeral. We need to add a durable intent registry that supports **pending/resumable intents** where `ingestion_profile` lives.

**Key Insight:** `ingestion_profile` should live with the **intent**, not the artifact. This enables resumable workflows across sessions.

---

## Current State Analysis

### 1. Intent Registry (Current)

**File:** `symphainy_platform/runtime/intent_registry.py`

**What it does:**
- In-memory registry of intent handlers
- Maps `intent_type` → `handler_name`
- Used for runtime routing

**What it doesn't do:**
- ❌ Not durable (in-memory only)
- ❌ Doesn't store intent executions
- ❌ Doesn't support pending intents
- ❌ Doesn't persist intent context

**Assessment:** This is just a **handler registry**, not an **execution log**.

---

### 2. Execution State (Current)

**File:** `symphainy_platform/runtime/state_surface.py`

**What it does:**
- Stores execution state via `set_execution_state()`
- Stored in State Surface (ArangoDB)
- Includes artifacts, events, status

**What it doesn't do:**
- ❌ Ephemeral (session-scoped)
- ❌ Not queryable for "pending intents"
- ❌ Doesn't persist intent context (ingestion_profile)
- ❌ Can't resume across sessions

**Assessment:** This is **execution state**, not **intent registry**.

---

### 3. Ingestion Profile / Parsing Type (Current)

**Where it's used:**
- Passed as `parsing_type` parameter in `parse_content` intent
- Stored in `semantic_descriptor.parser_type` after parsing
- Not stored durably before parsing

**Problem:**
- ❌ If user uploads file and wanders off, `ingestion_profile` is lost
- ❌ No way to query "files with pending parse intents"
- ❌ Can't resume parsing tomorrow with same profile

**Assessment:** `ingestion_profile` is **ephemeral** - lost if not used immediately.

---

## CTO Guidance: What We Need

### 1. Durable Intent Registry / Execution Log

**Purpose:** Store intent executions (pending, in-progress, completed)

**Schema (CTO-recommended):**
```json
{
  "intent_id": "I1",
  "intent_type": "parse_content",
  "status": "pending",  // pending | in_progress | completed | failed
  "target_artifact": "A1",  // Artifact this intent operates on
  "context": {
    "ingestion_profile": "hybrid",
    "preferred_parser": "kreuzberg",
    "parse_options": {...}
  },
  "created_by": "user",
  "created_at": "...",
  "execution_id": "exec_123"  // If executed
}
```

**Key Features:**
- ✅ Durable (Supabase table)
- ✅ Resumable (can execute later)
- ✅ Queryable ("pending parse intents")
- ✅ Auditable (who, when, what)

---

### 2. Ingestion Profile Lives with Intent

**Current (WRONG):**
```
User uploads file → ingestion_profile in session → lost if session ends
```

**Should Be (CORRECT):**
```
User uploads file → Create source_file artifact
User selects ingestion_profile → Create pending parse_content intent
Intent persists → Can resume tomorrow
```

**Key Principle:**
> **Artifacts describe what *exists*. Intents describe what *should happen*.**

---

### 3. Lineage in Artifact Index

**Current:** Lineage scattered across multiple tables (`parsed_results`, `embedding_files`)

**Should Be:** Structured lineage in `artifact_index`:

```json
{
  "artifact_id": "A2",
  "artifact_type": "parsed_content",
  "lineage": {
    "derived_from": ["A1"],
    "derivation_intent": "parse_content",
    "derivation_run_id": "exec_456",
    "generation": 1,
    "root_artifact_id": "A1"
  }
}
```

---

## Architectural Gap

### Missing: Intent Execution Log Table

**We need:**
- `intent_executions` table in Supabase
- Stores intent context (ingestion_profile, parse_options, etc.)
- Supports pending/resumable intents
- Queryable for UI ("pending parse intents for this file")

**Current state:**
- ❌ No durable intent storage
- ❌ No pending intent support
- ❌ No resumable workflows
- ❌ Ingestion profile lost if not used immediately

---

## Recommended Implementation

### Phase 1: Create Intent Executions Table

**Table:** `intent_executions`

**Schema:**
```sql
CREATE TABLE public.intent_executions (
    intent_id TEXT NOT NULL PRIMARY KEY,
    intent_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    target_artifact_id TEXT,  -- Artifact this intent operates on
    context JSONB NOT NULL DEFAULT '{}',  -- ingestion_profile, parse_options, etc.
    created_by TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    execution_id TEXT,  -- If executed
    completed_at TIMESTAMP WITH TIME ZONE,
    error TEXT
);

CREATE INDEX idx_intent_executions_status ON public.intent_executions (status);
CREATE INDEX idx_intent_executions_target_artifact ON public.intent_executions (target_artifact_id);
CREATE INDEX idx_intent_executions_intent_type ON public.intent_executions (intent_type);
```

---

### Phase 2: Update Artifact Index with Lineage

**Add lineage column to `artifact_index`:**

```sql
ALTER TABLE public.artifact_index
ADD COLUMN lineage JSONB DEFAULT '{}';

CREATE INDEX idx_artifact_index_lineage ON public.artifact_index USING GIN (lineage);
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

---

### Phase 3: Intent Execution Flow

**New Flow:**
```
1. User uploads file
   → Create source_file artifact (artifact_index)
   → ingestion_profile NOT stored here

2. User selects ingestion_profile
   → Create pending parse_content intent (intent_executions)
   → context.ingestion_profile = "hybrid"
   → status = "pending"

3. User can resume later
   → Query intent_executions for pending intents
   → Execute intent with stored context
   → Create parsed_content artifact
   → Update lineage in artifact_index
```

---

### Phase 4: Update ContentOrchestrator

**When user uploads file:**
```python
# Create source_file artifact (no ingestion_profile)
await context.state_surface.register_artifact(...)

# ingestion_profile NOT stored here
```

**When user selects ingestion_profile:**
```python
# Create pending parse_content intent
await registry_abstraction.insert_record("intent_executions", {
    "intent_id": f"parse_{file_id}",
    "intent_type": "parse_content",
    "status": "pending",
    "target_artifact_id": file_id,
    "context": {
        "ingestion_profile": ingestion_profile,
        "parse_options": parse_options
    }
})
```

**When parsing executes:**
```python
# Get pending intent
pending_intent = await registry_abstraction.query_records(
    "intent_executions",
    filters={"target_artifact_id": file_id, "status": "pending"}
)

# Execute with stored context
ingestion_profile = pending_intent["context"]["ingestion_profile"]
parse_options = pending_intent["context"]["parse_options"]

# Parse file
parsed_result = await self.file_parser_service.parse_file(
    ...,
    parsing_type=ingestion_profile,
    parse_options=parse_options
)

# Update intent status
await registry_abstraction.update_record(
    "intent_executions",
    {"status": "completed", "execution_id": context.execution_id},
    filter_conditions={"intent_id": pending_intent["intent_id"]}
)

# Create parsed_content artifact with lineage
await context.state_surface.register_artifact(
    ...,
    parent_artifacts=[file_id]
)

# Update artifact_index with lineage
await self._index_artifact(
    ...,
    parent_artifacts=[file_id]
)
```

---

## Benefits

### ✅ Resumable Workflows
- User can upload file, wander off, resume tomorrow
- Intent context persists
- No session coupling

### ✅ Clean Artifact Identity
- Artifacts describe what exists
- Intents describe what should happen
- No semantic pollution

### ✅ Queryable Pending Intents
- "Show me files with pending parse intents"
- "Show me pending intents for this artifact"
- UI can display actionable items

### ✅ Proper Lineage
- Structured lineage in artifact_index
- Queryable via GIN index
- Clear derivation chain

---

## Migration Path

### Step 1: Create Tables
- [ ] Create `intent_executions` table
- [ ] Add `lineage` column to `artifact_index`
- [ ] Create indexes

### Step 2: Update Artifact Registration
- [ ] Remove ingestion_profile from artifact registration
- [ ] Add lineage to artifact_index writes

### Step 3: Implement Intent Execution Log
- [ ] Create pending intents when user selects ingestion_profile
- [ ] Query pending intents for UI
- [ ] Execute intents with stored context

### Step 4: Update UI
- [ ] Query pending intents for display
- [ ] Show "pending parse" indicators
- [ ] Enable resume functionality

---

## Key Principles (From CTO)

1. **Lineage belongs in Artifact Index** - as structured metadata
2. **Ingestion profile lives with intent** - not artifact
3. **Intents are durable and resumable** - not ephemeral
4. **Artifacts describe what exists** - Intents describe what should happen

---

## Next Steps

1. **Review this analysis**
2. **Create `intent_executions` table migration**
3. **Add `lineage` column to `artifact_index`**
4. **Implement intent execution log in RegistryAbstraction**
5. **Update ContentOrchestrator to create pending intents**

**Status:** ✅ **READY FOR IMPLEMENTATION**
