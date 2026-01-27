# Intent Contract: create_deterministic_embeddings

**Intent:** create_deterministic_embeddings  
**Intent Type:** `create_deterministic_embeddings`  
**Journey:** Deterministic Embedding Creation (`journey_content_deterministic_embedding`)  
**Realm:** Content Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🔴 **PRIORITY 1** - Foundation intent for Content Realm

---

## 1. Intent Overview

### Purpose
Create deterministic embeddings from parsed content. Deterministic embeddings capture structural patterns (schema fingerprint, pattern signature) that are reproducible and consistent across runs. These serve as the foundation for semantic embeddings.

### Intent Flow
```
[Parsed content available]
    ↓
[create_deterministic_embeddings intent]
    ↓
[Retrieve parsed content from FileParserService]
    ↓
[Create deterministic embeddings via DeterministicEmbeddingService]
    ↓
[Generate schema fingerprint and pattern signature]
    ↓
[Store in DuckDB (deterministic compute abstraction)]
    ↓
[Register artifact in State Surface]
    ↓
[Returns deterministic_embedding_id, schema_fingerprint, pattern_signature]
```

### Expected Observable Artifacts
- `deterministic_embedding_id` - Embedding artifact identifier
- `artifact_type: "deterministic_embeddings"`
- `schema_fingerprint` - Structural fingerprint of the data
- `pattern_signature` - Pattern-based signature
- `parent_artifacts: [parsed_file_id]` - Lineage to parsed content

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `parsed_file_id` | `string` | Parsed content artifact identifier | Required, must exist |

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
    "deterministic_embeddings_created": true,
    "parsed_file_id": "parsed_abc123",
    "deterministic_embedding_id": "det_emb_xyz789",
    "schema_fingerprint": "fp_abc123def456",
    "pattern_signature": "sig_789xyz"
  },
  "events": [
    {
      "type": "deterministic_embeddings_created",
      "parsed_file_id": "parsed_abc123",
      "deterministic_embedding_id": "det_emb_xyz789"
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
- **Artifact ID:** Generated `deterministic_embedding_id`
- **Artifact Type:** `"deterministic_embeddings"`
- **Lifecycle State:** `"PENDING"` (until semantic embeddings created)
- **Produced By:** `{ intent: "create_deterministic_embeddings", execution_id: "<execution_id>" }`
- **Parent Artifacts:** `[parsed_file_id]` (lineage to parsed content)
- **Semantic Descriptor:** `{ schema: "deterministic_embeddings_v1", parser_type: null, embedding_model: "deterministic" }`
- **Materializations:** `[{ materialization_id: "mat_<id>", storage_type: "duckdb", uri: "<duckdb_path>", format: "parquet" }]`

### Storage Location
- **DuckDB:** Deterministic embeddings stored via `DeterministicComputeAbstraction`
- **NOT ArangoDB:** Per architectural requirements, deterministic embeddings use DuckDB

---

## 5. Idempotency

### Idempotency Key
```
embedding_fingerprint = hash(parsed_file_id + schema_fingerprint)
```

### Scope
- Per parsed content, per schema fingerprint
- Same parsed content = same deterministic embeddings

### Behavior
- If same parsed content already has deterministic embeddings, returns existing
- No duplicate computation
- Deterministic = reproducible results

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/content/orchestrators/content_orchestrator.py::ContentOrchestrator._handle_create_deterministic_embeddings`

### Key Implementation Steps
1. Validate `parsed_file_id` (required)
2. Retrieve parsed content via `FileParserService.get_parsed_file()`
3. Create deterministic embeddings via `DeterministicEmbeddingService.create_deterministic_embeddings()`
4. Store in DuckDB via `DeterministicComputeAbstraction`
5. Register artifact in State Surface
6. Return structured artifact response

### Dependencies
- **Public Works:** `DeterministicComputeAbstraction` (for DuckDB storage)
- **State Surface:** `register_artifact()`, `add_materialization()`
- **FileParserService:** `get_parsed_file()`
- **DeterministicEmbeddingService:** `create_deterministic_embeddings()`

---

## 7. Frontend Integration

### Frontend Usage
Not directly used by frontend - called as part of embedding pipeline. Frontend uses `extract_embeddings` which requires `deterministic_embedding_id`.

### Pipeline Flow
```
ingest_file → save_materialization → parse_content → create_deterministic_embeddings → extract_embeddings
```

---

## 8. Error Handling

### Validation Errors
- `parsed_file_id` missing → ValueError
- Parsed content not found → ValueError

### Runtime Errors
- DeterministicEmbeddingService not available → RuntimeError
- Embedding creation failed → RuntimeError
- DuckDB storage failed → RuntimeError
- Artifact registration failed → RuntimeError

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "create_deterministic_embeddings"
}
```

---

## 9. Testing & Validation

### Happy Path
1. Parsed content available
2. `create_deterministic_embeddings` intent executes
3. Deterministic embeddings created
4. Stored in DuckDB
5. Artifact registered
6. Returns deterministic_embedding_id

### Boundary Violations
- Missing `parsed_file_id` → Validation error
- Parsed content not found → Validation error

### Failure Scenarios
- Embedding creation failure → RuntimeError
- DuckDB storage failure → RuntimeError
- Artifact registration failure → RuntimeError

---

## 10. Contract Compliance

### Required Artifacts
- `deterministic_embedding_id` - Required
- `schema_fingerprint` - Required
- `pattern_signature` - Required

### Required Events
- `deterministic_embeddings_created` - Required

### Lifecycle State
- Must create artifact with `lifecycle_state: "PENDING"`
- Must set `parent_artifacts: [parsed_file_id]` for lineage

### Storage Requirements
- **Must use DuckDB** for deterministic embeddings (per architectural requirements)
- NOT ArangoDB (reserved for semantic embeddings)

---

## 11. Cross-Reference Analysis

### Journey Contract Says
- Create deterministic embeddings from parsed content
- Store embeddings for subsequent semantic embedding creation

### Implementation Does
- ✅ Creates deterministic embeddings via DeterministicEmbeddingService
- ✅ Stores in DuckDB via DeterministicComputeAbstraction
- ✅ Registers artifact with lineage

### Frontend Expects
- Not directly used by frontend
- Required as prerequisite for `extract_embeddings`

### Gaps/Discrepancies
- None identified - implementation aligns with contract

---

**Last Updated:** January 27, 2026  
**Owner:** Content Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
