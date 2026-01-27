# Intent-to-Execution Flow

**Date:** January 25, 2026  
**Status:** ✅ **COMPLETE**  
**Purpose:** Complete execution path from user action to system state update

---

## Executive Summary

This document maps the complete execution flow from user action in the frontend to system state update, showing how intents flow through the platform architecture:
- Frontend → API Manager → Experience Plane Client → Runtime
- Runtime → Realm Orchestrator → Realm Services → Public Works
- Public Works → Infrastructure (Supabase, GCS, etc.)
- Result → Realm State Update → UI Update

---

## Complete Execution Flow

### High-Level Flow

```
User Action (UI Component)
  ↓
API Manager Method
  ↓
Parameter Validation ✅ (Issue 3 Fix)
  ↓
Session Validation ✅ (Issue 4 Fix)
  ↓
submitIntent(intent_type, parameters)
  ↓
Experience Plane Client
  ↓
Runtime (ExecutionLifecycleManager)
  ↓
Realm Orchestrator
  ↓
Realm Services
  ↓
Public Works Abstractions
  ↓
Infrastructure (Supabase, GCS, Redis, etc.)
  ↓
Execution Result
  ↓
Realm State Update (Runtime)
  ↓
PlatformStateProvider (Frontend)
  ↓
UI Update (from Runtime state)
```

---

## Detailed Flow Breakdown

### Phase 1: Frontend (User Action → Intent Submission)

#### Step 1: User Action
- **Location:** UI Component (e.g., `ContentPillarUpload.tsx`, `YourDataMash.tsx`)
- **Action:** User clicks button, selects file, enters data, etc.
- **State:** Ephemeral UI state (form inputs, selections)

#### Step 2: API Manager Method
- **Location:** `shared/managers/{Realm}APIManager.ts`
- **Method:** e.g., `ContentAPIManager.uploadFile()`, `InsightsAPIManager.visualizeLineage()`
- **Actions:**
  1. Get platform state: `const platformState = this.getPlatformState()`
  2. Parameter validation: ✅ `if (!param) throw new Error(...)`
  3. Session validation: ✅ `validateSession(platformState, "operation")`

#### Step 3: Intent Submission
- **Location:** `PlatformStateProvider.submitIntent()`
- **Method:** `platformState.submitIntent(intent_type, parameters)`
- **Flow:**
  ```typescript
  const execution = await platformState.submitIntent(
    "ingest_file",
    {
      file: fileObject,
      ingestion_type: 'upload'
    }
  );
  ```
- **Result:** `executionId` returned immediately (async execution)

#### Step 4: Execution Tracking
- **Location:** `PlatformStateProvider`
- **Action:** Track execution in `state.execution[executionId]`
- **State:** Execution status (pending, running, completed, failed)

---

### Phase 2: Experience Plane Client

#### Step 5: Experience Plane Client
- **Location:** `shared/services/ExperiencePlaneClient.ts`
- **Action:** Submit intent to Runtime via HTTP
- **Endpoint:** `/api/intent/submit`
- **Payload:**
  ```json
  {
    "intent_type": "ingest_file",
    "parameters": {
      "file": "...",
      "ingestion_type": "upload"
    },
    "session_id": "...",
    "tenant_id": "..."
  }
  ```
- **Response:** Execution ID and initial status

---

### Phase 3: Runtime (ExecutionLifecycleManager)

#### Step 6: Runtime Receives Intent
- **Location:** Backend Runtime (`ExecutionLifecycleManager`)
- **Action:** 
  1. Validate intent parameters
  2. Check session/tenant
  3. Create execution record
  4. Route to appropriate realm orchestrator

#### Step 7: Execution Lifecycle
- **Location:** `ExecutionLifecycleManager`
- **States:**
  - `pending`: Intent received, not yet executing
  - `running`: Currently executing
  - `completed`: Execution successful
  - `failed`: Execution failed
  - `cancelled`: Execution cancelled

#### Step 8: Realm Routing
- **Location:** `ExecutionLifecycleManager`
- **Action:** Route intent to appropriate realm orchestrator based on `intent_type`
- **Mapping:**
  - `ingest_file`, `parse_content`, etc. → Content Realm Orchestrator
  - `visualize_lineage`, `map_relationships`, etc. → Insights Realm Orchestrator
  - `optimize_coexistence_with_content`, etc. → Journey Realm Orchestrator
  - `generate_roadmap`, `create_poc`, etc. → Outcomes Realm Orchestrator

---

### Phase 4: Realm Orchestrator

#### Step 9: Realm Orchestrator
- **Location:** `realms/{realm}/orchestrators/{realm}_orchestrator.py`
- **Action:**
  1. Receive intent from Runtime
  2. Validate realm-specific parameters
  3. Coordinate realm services
  4. Manage realm-specific execution flow

#### Step 10: Realm Services
- **Location:** `realms/{realm}/services/`
- **Action:** Execute domain-specific logic
- **Examples:**
  - Content Realm: File parsing, embedding extraction
  - Insights Realm: Quality assessment, interpretation, analysis
  - Journey Realm: Process optimization, coexistence analysis
  - Outcomes Realm: Synthesis, artifact generation

---

### Phase 5: Public Works Abstractions

#### Step 11: Public Works
- **Location:** `public_works/`
- **Action:** Provide infrastructure abstractions
- **Abstractions:**
  - Storage: `StorageAdapter` (Supabase, GCS)
  - Database: `DatabaseAdapter` (Supabase)
  - Cache: `CacheAdapter` (Redis)
  - LLM: `LLMAdapter` (OpenAI, etc.)

#### Step 12: Infrastructure Access
- **Location:** Infrastructure (Supabase, GCS, Redis, etc.)
- **Action:** Perform actual data operations
- **Operations:**
  - Store files in GCS
  - Store metadata in Supabase
  - Cache results in Redis
  - Call LLM APIs

---

### Phase 6: Result Processing

#### Step 13: Execution Result
- **Location:** Realm Services → Realm Orchestrator → Runtime
- **Result:**
  ```json
  {
    "status": "completed",
    "artifacts": {
      "file_id": "...",
      "boundary_contract_id": "..."
    },
    "error": null
  }
  ```

#### Step 14: Realm State Update (Runtime)
- **Location:** Runtime (ExecutionLifecycleManager)
- **Action:** Update realm state in Runtime
- **State:** `state.realm.{realm}.{key} = value`
- **Example:**
  ```typescript
  state.realm.content.files[fileId] = {
    file_id: fileId,
    name: fileName,
    // ...
  };
  ```

---

### Phase 7: Frontend State Reconciliation

#### Step 15: Execution Status Polling
- **Location:** `PlatformStateProvider`
- **Action:** Poll execution status until completion
- **Method:** `platformState.getExecutionStatus(executionId)`
- **Polling:** Every 1 second until `completed` or `failed`

#### Step 16: Realm State Sync
- **Location:** `PlatformStateProvider`
- **Action:** Sync realm state from Runtime
- **Method:** `platformState.getRealmState(realm, key)`
- **Reconciliation:** Runtime state is authoritative, frontend reconciles

#### Step 17: UI Update
- **Location:** UI Components
- **Action:** React to realm state changes
- **Pattern:** Components read from `state.realm.*`
- **Example:**
  ```typescript
  const files = state.realm.content.files || {};
  // UI displays files from Runtime state
  ```

---

## Execution Flow Examples

### Example 1: File Upload

```
1. User clicks "Upload" in ContentPillarUpload.tsx
   ↓
2. ContentAPIManager.uploadFile(file)
   - Parameter validation: ✅ if (!file) throw Error
   - Session validation: ✅ validateSession(platformState, "upload file")
   ↓
3. platformState.submitIntent("ingest_file", { file, ingestion_type: 'upload' })
   ↓
4. ExperiencePlaneClient.submitIntent()
   - POST /api/intent/submit
   - Payload: { intent_type: "ingest_file", parameters: {...}, session_id, tenant_id }
   ↓
5. Runtime (ExecutionLifecycleManager)
   - Create execution record
   - Route to Content Realm Orchestrator
   ↓
6. Content Realm Orchestrator
   - Validate parameters
   - Call Content Services
   ↓
7. Content Services
   - Store file in GCS (via Public Works StorageAdapter)
   - Store metadata in Supabase (via Public Works DatabaseAdapter)
   ↓
8. Public Works → Infrastructure
   - GCS: Store file
   - Supabase: Store metadata
   ↓
9. Execution Result
   - { status: "completed", artifacts: { file_id: "...", boundary_contract_id: "..." } }
   ↓
10. Runtime State Update
    - state.realm.content.files[fileId] = { file_id, name, ... }
    ↓
11. Frontend Polling
    - platformState.getExecutionStatus(executionId)
    - Status: "completed"
    ↓
12. Frontend State Sync
    - platformState.getRealmState("content", "files")
    - Sync with Runtime state
    ↓
13. UI Update
    - ContentPillarUpload.tsx reads from state.realm.content.files
    - UI displays uploaded file
```

---

### Example 2: Lineage Visualization

```
1. User clicks "Visualize Lineage" in YourDataMash.tsx
   ↓
2. InsightsAPIManager.visualizeLineage(fileId)
   - Parameter validation: ✅ if (!fileId) throw Error
   - Session validation: ✅ validateSession(platformState, "visualize lineage")
   ↓
3. platformState.submitIntent("visualize_lineage", { file_id: fileId })
   ↓
4. ExperiencePlaneClient.submitIntent()
   - POST /api/intent/submit
   ↓
5. Runtime (ExecutionLifecycleManager)
   - Route to Insights Realm Orchestrator
   ↓
6. Insights Realm Orchestrator
   - Call Insights Services (lineage visualization)
   ↓
7. Insights Services
   - Generate lineage graph
   - Store visualization in GCS (via Public Works)
   ↓
8. Public Works → Infrastructure
   - GCS: Store visualization
   - Supabase: Store lineage metadata
   ↓
9. Execution Result
   - { status: "completed", artifacts: { lineage_visualization: {...} } }
   ↓
10. Runtime State Update
    - state.realm.insights.lineageVisualizations[fileId] = lineageVisualization
    ↓
11. Frontend Polling & Sync
    - Get execution status
    - Sync realm state
    ↓
12. UI Update
    - YourDataMash.tsx reads from state.realm.insights.lineageVisualizations[fileId]
    - UI displays lineage graph (from Runtime state)
```

---

### Example 3: Coexistence Optimization

```
1. User enters SOP/Workflow content, clicks "Optimize" in CoexistenceBlueprint
   ↓
2. JourneyAPIManager.optimizeCoexistenceWithContent(sopContent, workflowContent)
   - Parameter validation: ✅ if (!sopContent || !workflowContent) throw Error
   - Session validation: ✅ validateSession(platformState, "optimize coexistence")
   ↓
3. platformState.submitIntent("optimize_coexistence_with_content", { sop_content, workflow_content })
   ↓
4. ExperiencePlaneClient.submitIntent()
   ↓
5. Runtime (ExecutionLifecycleManager)
   - Route to Journey Realm Orchestrator
   ↓
6. Journey Realm Orchestrator
   - Call Journey Services (coexistence optimization)
   ↓
7. Journey Services
   - Analyze coexistence
   - Optimize SOP/workflow
   - Generate blueprint
   - Store results (via Public Works)
   ↓
8. Public Works → Infrastructure
   - Supabase: Store optimization results
   ↓
9. Execution Result
   - { status: "completed", artifacts: { optimized_coexistence: { optimized_sop, optimized_workflow, blueprint } } }
   ↓
10. Runtime State Update
    - state.realm.journey.operations = { optimizedSop, optimizedWorkflow, blueprint, analysisComplete: true }
    ↓
11. Frontend Polling & Sync
    - Get execution status
    - Sync realm state
    ↓
12. UI Update
    - CoexistenceBlueprint reads from state.realm.journey.operations
    - UI displays optimized results (from Runtime state)
```

---

## State Authority Model

### Runtime Authority
- **Runtime is authoritative** for committed execution and durable state
- **Frontend state is speculative** until Runtime confirms
- **Reconciliation:** Frontend reconciles with Runtime on reload

### State Flow
```
Ephemeral (UI State)
  ↓
Intent Submission
  ↓
Runtime Execution
  ↓
Runtime State (Authoritative)
  ↓
Frontend State Sync
  ↓
UI Update (from Runtime state)
```

### Reconciliation Pattern
```typescript
// On page reload
useEffect(() => {
  const operations = getRealmState('journey', 'operations');
  if (operations?.optimizedSop && !optimizedSop) {
    setOptimizedSop(operations.optimizedSop); // Rehydrate from Runtime
  }
}, [getRealmState, optimizedSop]);
```

---

## Error Handling Flow

### Error Scenarios

#### 1. Parameter Validation Error
- **Location:** API Manager
- **Action:** Throw error before intent submission
- **Result:** Error displayed to user, intent not submitted

#### 2. Session Validation Error
- **Location:** API Manager
- **Action:** Throw error before intent submission
- **Result:** Error displayed to user, intent not submitted

#### 3. Runtime Execution Error
- **Location:** Runtime (ExecutionLifecycleManager)
- **Action:** Mark execution as `failed`
- **Result:** Error returned in execution result
- **Frontend:** Display error from execution result

#### 4. Realm Service Error
- **Location:** Realm Services
- **Action:** Return error to orchestrator
- **Result:** Error propagated to Runtime
- **Frontend:** Display error from execution result

---

## Execution Tracking

### Execution States
- **`pending`:** Intent received, not yet executing
- **`running`:** Currently executing
- **`completed`:** Execution successful
- **`failed`:** Execution failed
- **`cancelled`:** Execution cancelled

### Execution Tracking Pattern
```typescript
// Submit intent
const executionId = await platformState.submitIntent(intent_type, parameters);

// Track execution
platformState.trackExecution(executionId, {
  intent_type,
  parameters,
  status: 'pending'
});

// Poll for completion
const result = await platformState.getExecutionStatus(executionId);
// result.status: 'completed' | 'failed' | 'cancelled'
```

---

## Notes

1. **Intent-Based Architecture:** All operations (except `save_materialization`) use intent-based API
2. **Parameter Validation:** ✅ All intents validated before submission (Issue 3 Fix)
3. **Session Validation:** ✅ All intents validated for session (Issue 4 Fix)
4. **State Authority:** Runtime is authoritative for durable state
5. **Reconciliation:** Frontend reconciles with Runtime on reload
6. **Execution Tracking:** All executions tracked in `state.execution`

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** ✅ **COMPLETE**
