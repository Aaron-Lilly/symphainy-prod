# Data Lifecycle Flow

**Date:** January 25, 2026  
**Status:** ✅ **COMPLETE**  
**Purpose:** Comprehensive mapping of data flow through the four-class data architecture

---

## Executive Summary

This document maps how data flows through the Symphainy platform's four-class data architecture:
1. **Working Materials** - Temporary, TTL-based data
2. **Records of Fact** - Persistent, promoted from Working Materials
3. **Purpose-Bound Outcomes** - Artifacts with lifecycle (roadmaps, POCs, blueprints)
4. **Ephemeral** - Session state, UI state, not persisted

---

## Four-Class Data Architecture

### 1. Working Materials

**Definition:** Temporary data with Time-To-Live (TTL) that is automatically purged when expired.

**Characteristics:**
- TTL-based expiration
- Automatically purged when expired
- Can be promoted to Records of Fact
- Stored temporarily during processing

**Examples:**
- Uploaded files (before materialization)
- Parsed file data (before promotion)
- Embeddings (before promotion)
- Interpretations (before promotion)
- Analysis results
- Process optimizations
- Coexistence analyses

**Storage:**
- Supabase (temporary tables)
- GCS (temporary buckets)
- Marked with TTL metadata

**TTL Enforcement:**
- ⚠️ **Status:** TTL tracked but not enforced (Task 5.1)
- **Action Required:** Implement automated purge job

---

### 2. Records of Fact

**Definition:** Persistent data that represents committed, verified information.

**Characteristics:**
- Persistent (no TTL)
- Promoted from Working Materials
- Represents verified/committed data
- Cannot be automatically purged

**Examples:**
- Materialized files (after `save_materialization`)
- Promoted embeddings
- Promoted interpretations
- Verified analysis results

**Storage:**
- Supabase (persistent tables)
- GCS (persistent buckets)
- No TTL metadata

**Promotion Workflow:**
- ⚠️ **Status:** Partially implemented (Task 5.2)
- **Action Required:** Ensure all embeddings and interpretations are stored as Records of Fact

---

### 3. Purpose-Bound Outcomes

**Definition:** Artifacts with explicit lifecycle states (draft, active, archived).

**Characteristics:**
- Lifecycle states: `draft` → `active` → `archived`
- Purpose, scope, owner metadata
- Transition history
- Runtime-enforced transitions

**Examples:**
- Roadmaps (`generate_roadmap`)
- POCs (`create_poc`)
- Blueprints (`create_blueprint`)
- SOPs (from Journey realm)
- Workflows (from Journey realm)

**Storage:**
- Supabase (artifact tables)
- Lifecycle metadata stored
- Transition history tracked

**Lifecycle Management:**
- ✅ **Status:** Complete (Task 5.3)
- **Intent:** `transition_artifact_lifecycle`
- **Valid Transitions:**
  - `draft` → `active`
  - `draft` → `archived`
  - `active` → `archived`

---

### 4. Ephemeral

**Definition:** Temporary state that is not persisted (session state, UI state).

**Characteristics:**
- Not persisted
- Session-scoped
- UI state only
- Lost on page reload (unless synced with Runtime)

**Examples:**
- UI component state
- Form input state
- Temporary selections
- Loading states
- Error messages

**Storage:**
- React component state
- Session state (temporary)
- Not stored in database

**Reconciliation:**
- Ephemeral state can be rehydrated from Runtime state
- Runtime is authoritative for durable state
- Frontend reconciles with Runtime on reload

---

## Data Flow Patterns

### Pattern 1: File Upload Flow

```
User Uploads File
  ↓
Working Material (temporary)
  - TTL: 24 hours (example)
  - Storage: Supabase temporary table
  ↓
User Clicks "Save"
  ↓
save_materialization intent
  ↓
Records of Fact (persistent)
  - No TTL
  - Storage: Supabase persistent table
  - Registered in materialization store
```

**Intents:**
- `ingest_file` → Working Material
- `save_materialization` → Records of Fact

**State Updates:**
- `state.realm.content.files` (Working Material)
- `state.realm.content.materializations` (Records of Fact)

---

### Pattern 2: Embedding Extraction Flow

```
File Parsed
  ↓
extract_embeddings intent
  ↓
Working Material (embeddings)
  - TTL: 7 days (example)
  - Storage: Supabase temporary table
  ↓
Promotion Trigger (automatic or manual)
  ↓
Records of Fact (embeddings)
  - No TTL
  - Storage: Supabase persistent table
```

**Intents:**
- `extract_embeddings` → Working Material
- Promotion (automatic or via separate intent) → Records of Fact

**State Updates:**
- `state.realm.content.embeddings` (Working Material → Records of Fact)

**Promotion:**
- ⚠️ **Status:** Promotion workflow needs verification (Task 5.2)
- **Action Required:** Ensure embeddings are promoted to Records of Fact

---

### Pattern 3: Interpretation Flow

```
File Parsed
  ↓
interpret_data_self_discovery OR interpret_data_guided intent
  ↓
Working Material (interpretation)
  - TTL: 7 days (example)
  - Storage: Supabase temporary table
  ↓
Promotion Trigger (automatic or manual)
  ↓
Records of Fact (interpretation)
  - No TTL
  - Storage: Supabase persistent table
```

**Intents:**
- `interpret_data_self_discovery` → Working Material
- `interpret_data_guided` → Working Material
- Promotion (automatic or via separate intent) → Records of Fact

**State Updates:**
- `state.realm.insights.interpretations[parsedFileId]` (Working Material → Records of Fact)

**Promotion:**
- ⚠️ **Status:** Promotion workflow needs verification (Task 5.2)
- **Action Required:** Ensure interpretations are promoted to Records of Fact

---

### Pattern 4: Artifact Creation Flow

```
Synthesis/Data Available
  ↓
generate_roadmap OR create_poc OR create_blueprint intent
  ↓
Purpose-Bound Outcome (draft)
  - Lifecycle: draft
  - Purpose: strategic_planning / proof_of_concept / coexistence_planning
  - Scope: business_transformation / validation / workflow_optimization
  - Owner: user_id
  - Storage: Supabase artifact table
  ↓
transition_artifact_lifecycle intent (draft → active)
  ↓
Purpose-Bound Outcome (active)
  - Lifecycle: active
  - Transition history updated
  ↓
transition_artifact_lifecycle intent (active → archived)
  ↓
Purpose-Bound Outcome (archived)
  - Lifecycle: archived (terminal)
  - Transition history updated
```

**Intents:**
- `generate_roadmap` → Purpose-Bound Outcome (draft)
- `create_poc` → Purpose-Bound Outcome (draft)
- `create_blueprint` → Purpose-Bound Outcome (draft)
- `transition_artifact_lifecycle` → Lifecycle state transition

**State Updates:**
- `state.realm.outcomes.roadmaps[roadmapId]` (with lifecycle)
- `state.realm.outcomes.pocProposals[pocId]` (with lifecycle)
- `state.realm.outcomes.blueprints[blueprintId]` (with lifecycle)

**Lifecycle:**
- ✅ **Status:** Complete (Task 5.3)
- **Lifecycle States:** draft → active → archived
- **Runtime Authority:** Transitions enforced via Runtime

---

### Pattern 5: Ephemeral → Working Material Flow

```
User Action (UI)
  ↓
Ephemeral State (form input, selection)
  ↓
submitIntent(intent_type, parameters)
  ↓
Runtime Execution
  ↓
Working Material (result)
  - TTL-based
  - Stored in database
  ↓
Realm State Update
  ↓
UI Update (from Runtime state)
```

**Example:**
- User enters SOP content (ephemeral)
- User clicks "Optimize Coexistence"
- `optimize_coexistence_with_content` intent
- Working Material (optimized result)
- `state.realm.journey.operations` updated
- UI displays result from Runtime state

---

## Data Class Transitions

### Working Materials → Records of Fact

**Promotion Triggers:**
1. **Explicit Save:** User clicks "Save" (e.g., `save_materialization`)
2. **Automatic Promotion:** Based on criteria (e.g., quality threshold, verification)
3. **Time-Based:** After certain period (e.g., 7 days)

**Promotion Criteria:**
- ⚠️ **Status:** Needs verification (Task 5.2)
- **Action Required:** Define and implement promotion criteria

**Examples:**
- File: `ingest_file` → `save_materialization`
- Embeddings: `extract_embeddings` → Promotion (automatic or manual)
- Interpretations: `interpret_data_*` → Promotion (automatic or manual)

---

### Records of Fact → Purpose-Bound Outcomes

**Creation Triggers:**
1. **Artifact Generation:** `generate_roadmap`, `create_poc`, `create_blueprint`
2. **Lifecycle Management:** Artifacts have explicit lifecycle states

**Lifecycle States:**
- `draft`: Initial state
- `active`: Active state
- `archived`: Terminal state

**Examples:**
- Roadmap: `generate_roadmap` → Purpose-Bound Outcome (draft)
- POC: `create_poc` → Purpose-Bound Outcome (draft)
- Blueprint: `create_blueprint` → Purpose-Bound Outcome (draft)

---

### Ephemeral → Working Material

**Conversion Triggers:**
1. **Intent Submission:** User action triggers intent
2. **Runtime Execution:** Intent creates Working Material
3. **State Update:** Realm state updated with Working Material

**Examples:**
- Form input → `optimize_coexistence_with_content` → Working Material
- File selection → `parse_content` → Working Material
- Analysis request → `analyze_structured_data` → Working Material

---

## TTL Enforcement

### Current Status
- ⚠️ **TTL Tracked:** TTL metadata stored with Working Materials
- ⚠️ **TTL Not Enforced:** No automated purge job (Task 5.1)

### TTL Enforcement Design

**Purge Job:**
- Scheduled job (e.g., daily)
- Queries Working Materials with expired TTL
- Safeguards: Don't purge if referenced by active artifacts
- Logging: Log all purges

**TTL Values (Examples):**
- Uploaded files: 24 hours
- Parsed files: 7 days
- Embeddings: 7 days
- Interpretations: 7 days
- Analysis results: 30 days

**Implementation:**
- ⚠️ **Status:** Needs implementation (Task 5.1)
- **Action Required:** Create automated purge job

---

## Promotion Workflow

### Current Status
- ⚠️ **Partially Implemented:** Some data promoted, some not (Task 5.2)

### Promotion Workflow Design

**Automatic Promotion:**
- Quality threshold met
- Verification complete
- Time-based (after period)

**Manual Promotion:**
- User action (e.g., "Save as Record of Fact")
- Admin action
- Intent-based promotion

**Promotion Criteria:**
- Embeddings: Quality score > threshold
- Interpretations: Confidence score > threshold
- Analysis: Verified by user

**Implementation:**
- ⚠️ **Status:** Needs verification (Task 5.2)
- **Action Required:** Ensure all embeddings and interpretations are stored as Records of Fact

---

## State Reconciliation

### Ephemeral → Runtime State

**Rehydration:**
- On page reload, frontend rehydrates from Runtime state
- Runtime is authoritative for durable state
- Ephemeral state is speculative until Runtime confirms

**Example:**
```
User uploads file (ephemeral state)
  ↓
ingest_file intent submitted
  ↓
Runtime executes, updates state
  ↓
Frontend receives execution result
  ↓
Frontend updates realm state (from Runtime)
  ↓
UI displays from Runtime state (authoritative)
```

**Reconciliation Logic:**
- ✅ **Status:** Implemented in `PlatformStateProvider`
- **Pattern:** Runtime wins, frontend reconciles

---

## Data Storage Locations

### Working Materials
- **Supabase:** Temporary tables (with TTL metadata)
- **GCS:** Temporary buckets (with TTL metadata)
- **Redis:** Temporary cache (with TTL)

### Records of Fact
- **Supabase:** Persistent tables (no TTL)
- **GCS:** Persistent buckets (no TTL)
- **Materialization Store:** Registered in Supabase

### Purpose-Bound Outcomes
- **Supabase:** Artifact tables (with lifecycle metadata)
- **Lifecycle Store:** Lifecycle state and transition history

### Ephemeral
- **React State:** Component state
- **Session State:** Temporary session storage
- **Not Persisted:** Lost on reload (unless synced with Runtime)

---

## Data Flow Summary

### Complete Flow Example

```
1. User Uploads File
   → Ephemeral (form state)
   → ingest_file intent
   → Working Material (temporary, TTL: 24h)

2. User Saves File
   → save_materialization intent
   → Records of Fact (persistent, no TTL)

3. File Parsed
   → parse_content intent
   → Working Material (temporary, TTL: 7d)

4. Embeddings Extracted
   → extract_embeddings intent
   → Working Material (temporary, TTL: 7d)
   → Promotion (automatic or manual)
   → Records of Fact (persistent, no TTL)

5. Interpretation Created
   → interpret_data_self_discovery intent
   → Working Material (temporary, TTL: 7d)
   → Promotion (automatic or manual)
   → Records of Fact (persistent, no TTL)

6. Roadmap Generated
   → generate_roadmap intent
   → Purpose-Bound Outcome (draft)
   → transition_artifact_lifecycle (draft → active)
   → Purpose-Bound Outcome (active)
   → transition_artifact_lifecycle (active → archived)
   → Purpose-Bound Outcome (archived)
```

---

## Notes

1. **TTL Enforcement:** ⚠️ Needs implementation (Task 5.1)
2. **Promotion Workflow:** ⚠️ Needs verification (Task 5.2)
3. **Lifecycle Management:** ✅ Complete (Task 5.3)
4. **State Reconciliation:** ✅ Implemented
5. **Data Authority:** Runtime is authoritative for durable state

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** ✅ **COMPLETE** (Pending Tasks 5.1 and 5.2 verification)
