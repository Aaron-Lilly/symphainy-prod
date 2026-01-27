# Intent Contract: extract_embeddings

**Intent:** extract_embeddings  
**Intent Type:** `extract_embeddings`  
**Journey:** Deterministic Embedding Creation (`journey_content_deterministic_embedding`)  
**Realm:** Content Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🔴 **PRIORITY 1** - Foundation intent for Content Realm

---

## 1. Intent Overview

### Purpose
Extract semantic embeddings from deterministic embeddings. This creates vector embeddings suitable for semantic search and similarity matching. Requires deterministic embeddings as a prerequisite.

> **Note:** Original journey contract specified `save_embeddings`. This contract uses `extract_embeddings` to align with the actual implementation and frontend usage.

### Intent Flow
```
[Deterministic embeddings available]
    ↓
[extract_embeddings intent]
    ↓
[Validate deterministic_embedding_id exists]
    ↓
[Create semantic embeddings via EmbeddingService]
    ↓
[Store in ArangoDB (semantic storage)]
    ↓
[Track in Supabase for lineage]
    ↓
[Register artifact in State Surface]
    ↓
[Returns embedding_id, embeddings_count]
```

### Expected Observable Artifacts
- `embedding_id` - Semantic embedding artifact identifier
- `artifact_type: "embeddings"`
- `embeddings_count` - Number of embeddings created
- `parent_artifacts: [deterministic_embedding_id, parsed_file_id]` - Full lineage
- `embedding_model` - Model used (e.g., "sentence-transformers/all-mpnet-base-v2")

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `parsed_file_id` | `string` | Parsed content artifact identifier | Required, must exist |
| `deterministic_embedding_id` | `string` | Deterministic embedding artifact identifier | Required, must exist |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `embedding_options` | `object` | Embedding generation options | `{}` |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `session_id` | `string` | Session identifier | Runtime (required) |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "embeddings": {
      "result_type": "embeddings",
      "semantic_payload": {
        "embeddings_id": "emb_abc123",
        "embedding_reference": "embedding:tenant:session:emb_abc123",
        "parsed_file_id": "parsed_xyz789",
        "deterministic_embedding_id": "det_emb_456",
        "embeddings_count": 150,
        "embedding_model": "sentence-transformers/all-mpnet-base-v2"
      },
      "renderings": {}
    }
  },
  "events": [
    {
      "type": "embeddings_created",
      "embedding_id": "emb_abc123",
      "parsed_file_id": "parsed_xyz789",
      "embeddings_count": 150
    }
  ]
}
```

### Error Response

```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123"
}
```

---

## 4. Artifact Registration

### State Surface Registration
- **Artifact ID:** Generated `embedding_id`
- **Artifact Type:** `"embeddings"`
- **Lifecycle State:** `"PENDING"` (transitions to READY after indexing)
- **Produced By:** `{ intent: "extract_embeddings", execution_id: "<execution_id>" }`
- **Parent Artifacts:** `[deterministic_embedding_id, parsed_file_id]` (full lineage)
- **Semantic Descriptor:** `{ schema: "embeddings_v1", record_count: <count>, embedding_model: "sentence-transformers/all-mpnet-base-v2" }`
- **Materializations:** `[{ materialization_id: "mat_<id>", storage_type: "arango", uri: "structured_embeddings/<id>", format: "json" }]`

### Storage Location
- **ArangoDB:** Semantic embeddings stored in `structured_embeddings` collection
- **Supabase:** Lineage tracking in embeddings table

---

## 5. Idempotency

### Idempotency Key
```
semantic_embedding_fingerprint = hash(deterministic_embedding_id + parsed_file_id + model_name)
```

### Scope
- Per deterministic embedding, per model
- Same input = same semantic embeddings

### Behavior
- If same deterministic embeddings already have semantic embeddings, returns existing
- No duplicate computation
- Model-specific (different models = different embeddings)

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/content/orchestrators/content_orchestrator.py::ContentOrchestrator._handle_extract_embeddings`

### Key Implementation Steps
1. Validate `parsed_file_id` (required)
2. Validate `deterministic_embedding_id` (required)
3. Validate deterministic embedding exists via `DeterministicEmbeddingService.get_deterministic_embedding()`
4. Get file_id from parsed results for lineage tracking
5. Create semantic embeddings via `EmbeddingService.create_semantic_embeddings()`
6. Track in Supabase embeddings table
7. Register artifact in State Surface
8. Add ArangoDB materialization
9. Return structured artifact response

### Dependencies
- **Public Works:** `SemanticSearchAbstraction` (for ArangoDB storage)
- **State Surface:** `register_artifact()`, `add_materialization()`
- **DeterministicEmbeddingService:** `get_deterministic_embedding()` (validation)
- **EmbeddingService:** `create_semantic_embeddings()`
- **Supabase:** Embeddings table (lineage tracking)

---

## 7. Frontend Integration

### Frontend Usage (ContentAPIManager.ts)
```typescript
// ContentAPIManager.extractEmbeddings()
const executionId = await platformState.submitIntent(
  "extract_embeddings",
  {
    parsed_file_id: parsedFileId,
    deterministic_embedding_id: deterministicEmbeddingId,
  }
);
```

### Expected Frontend Behavior
1. Deterministic embeddings created
2. User initiates embedding extraction
3. Submit `extract_embeddings` intent via `submitIntent()`
4. Track execution via `trackExecution()`
5. Wait for execution completion
6. Extract `embedding_id` from execution artifacts
7. Update UI to show file is ready for semantic search

---

## 8. Error Handling

### Validation Errors
- `parsed_file_id` missing → ValueError
- `deterministic_embedding_id` missing → ValueError with guidance to create deterministic embeddings first
- Deterministic embedding not found → ValueError

### Runtime Errors
- EmbeddingService not available → RuntimeError
- Embedding creation failed → RuntimeError
- ArangoDB storage failed → RuntimeError
- Artifact registration failed → RuntimeError

### Error Response Format
```json
{
  "error": "deterministic_embedding_id is required for extract_embeddings intent. Please create deterministic embeddings first using create_deterministic_embeddings intent.",
  "error_code": "VALIDATION_ERROR",
  "execution_id": "exec_abc123",
  "intent_type": "extract_embeddings"
}
```

---

## 9. Testing & Validation

### Happy Path
1. Deterministic embeddings available
2. `extract_embeddings` intent executes
3. Semantic embeddings created
4. Stored in ArangoDB
5. Tracked in Supabase
6. Artifact registered
7. Returns embedding_id and count

### Boundary Violations
- Missing `parsed_file_id` → Validation error
- Missing `deterministic_embedding_id` → Validation error with guidance
- Deterministic embedding not found → Validation error

### Failure Scenarios
- Embedding creation failure → RuntimeError
- ArangoDB storage failure → RuntimeError
- Artifact registration failure → RuntimeError

---

## 10. Contract Compliance

### Required Artifacts
- `embeddings` - Required with embedding_id and count

### Required Events
- `embeddings_created` - Required

### Lifecycle State
- Must create artifact with `lifecycle_state: "PENDING"`
- Must set full lineage: `parent_artifacts: [deterministic_embedding_id, parsed_file_id]`

### Prerequisite Validation
- **Must validate** deterministic embeddings exist before proceeding
- **Must provide helpful error message** if missing

### Storage Requirements
- **Must use ArangoDB** for semantic embeddings (per architectural requirements)
- Deterministic embeddings use DuckDB; semantic embeddings use ArangoDB

---

## 11. Cross-Reference Analysis

### Journey Contract Says
- Original contract specified `save_embeddings`
- Purpose: Save/create embeddings from deterministic embeddings

### Implementation Does
- ✅ Uses intent type `extract_embeddings` (not `save_embeddings`)
- ✅ Validates deterministic embeddings exist first
- ✅ Creates semantic embeddings via EmbeddingService
- ✅ Stores in ArangoDB
- ✅ Tracks in Supabase for lineage

### Frontend Expects
- ✅ Intent type: `extract_embeddings`
- ✅ Returns `embedding_id` and `embedding_reference`
- ✅ Execution tracking via `trackExecution()`

### Gaps/Discrepancies
- **NAMING:** Journey contract says `save_embeddings`, implementation uses `extract_embeddings`
- **Recommendation:** Update journey contract to use `extract_embeddings` to match implementation and frontend

---

## 12. Migration Notes

### From Journey Contract
The original journey contract specified `save_embeddings`. This contract documents `extract_embeddings` which is:
- What's actually implemented in the backend
- What the frontend uses
- A more accurate name (describes the action of extracting/creating embeddings)

### Recommended Journey Contract Update
```diff
- 2. `save_embeddings` - Step 2: Save embeddings
+ 2. `extract_embeddings` - Step 2: Extract semantic embeddings from deterministic embeddings
```

---

**Last Updated:** January 27, 2026  
**Owner:** Content Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
